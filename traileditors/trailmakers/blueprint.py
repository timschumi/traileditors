import io
import lz4.frame
import math
import PIL.Image
import struct
from ..compressor import smaz
from ..parser import dotnet
from .. import trailmakers

__all__ = [
    'Blueprint',
]


# Data is stored at the very end of the image (left to right and bottom to top).
# The values are encoded in the RGB values of that pixel.
def get_byte(image, n):
    pixel = n // 3

    x = pixel % image.width
    y = image.height - 1 - (pixel // image.width)

    px = image.getpixel((x, y))

    return px[n % 3].to_bytes(1, byteorder='big')


class Blueprint:
    def __init__(self):
        self.SaveGameInPNGInfo = None
        self.StructureGraphSaveDataProto = None
        self.StructureSaveIdentifierProto = None
        self.StructureMetaDataProto = None

    @staticmethod
    def from_image(image: PIL.Image):
        blueprint = Blueprint()

        # Get the top right pixel.
        # This contains the length of the serialized SaveGameInPNGInfo object.
        info_len_px = image.getpixel((image.width - 1, 0))
        info_len_bytes = bytes(info_len_px)
        info_len = struct.unpack(">I", info_len_bytes)[0]

        info = b"".join([get_byte(image, i) for i in range(info_len)])
        parsed_info = dotnet.SerializedMessage(io.BytesIO(info))

        blueprint.SaveGameInPNGInfo = parsed_info.object

        # The encoder stops writing data after the end of the SaveGameInPNGInfo struct
        # and will only continue writing the remaining data when the next pixel starts.
        data_offset = int(math.ceil(info_len / 3)) * 3

        data = b"".join([get_byte(image, data_offset + i) for i in range(blueprint.SaveGameInPNGInfo.structureByteSize)])

        data = lz4.frame.decompress(data)

        blueprint.StructureGraphSaveDataProto = trailmakers.protobuf.StructureGraphSaveDataProto()
        blueprint.StructureGraphSaveDataProto.ParseFromString(data)

        data_offset += blueprint.SaveGameInPNGInfo.structureByteSize

        data = b"".join([get_byte(image, data_offset + i) for i in range(blueprint.SaveGameInPNGInfo.structureIdentifierSize)])

        blueprint.StructureSaveIdentifierProto = trailmakers.protobuf.StructureSaveIdentifierProto()
        blueprint.StructureSaveIdentifierProto.ParseFromString(data)

        data_offset += blueprint.SaveGameInPNGInfo.structureIdentifierSize

        data = b"".join([get_byte(image, data_offset + i) for i in range(blueprint.SaveGameInPNGInfo.structureMetaByteSize)])

        data = smaz.decompress(io.BytesIO(data))

        blueprint.StructureMetaDataProto = trailmakers.protobuf.StructureMetaDataProto()
        blueprint.StructureMetaDataProto.ParseFromString(data)

        return blueprint
