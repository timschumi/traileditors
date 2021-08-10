#!/usr/bin/python

from lib import dotnet
import io
import lz4.frame
import math
import sys
import struct
import PIL.Image

image = PIL.Image.open(sys.argv[1])

# Data is stored at the very end of the image (left to right and bottom to top).
# The values are encoded in the RGB values of that pixel.
def get_byte(n):
    pixel = n // 3

    x = pixel % image.width
    y = image.height - 1 - (pixel // image.width)

    px = image.getpixel((x, y))

    return px[n % 3].to_bytes(1, byteorder='big')

# Get the top right pixel.
# This contains the length of the serialized SaveGameInPNGInfo object.
info_len_px = image.getpixel((image.width - 1, 0))
info_len_bytes = bytes(info_len_px)
info_len = struct.unpack(">I", info_len_bytes)[0]

print(f"[*] Length of SaveGameInPNGInfo object: {hex(info_len)} ({info_len})")

info = b"".join([get_byte(i) for i in range(info_len)])
parsed_info = dotnet.SerializedMessage(io.BytesIO(info))

save_game_info = parsed_info.object

print(f"[*] SaveGameInPNGInfo dump:")
print(f"     - version: {save_game_info.version}")
print(f"     - creator: \"{save_game_info.creator}\"")
print(f"     - structureByteSize: {save_game_info.structureByteSize}")
print(f"     - structureIdentifierSize: {save_game_info.structureIdentifierSize}")
print(f"     - structureMetaByteSize: {save_game_info.structureMetaByteSize}")

# The encoder stops writing data after the end of the SaveGameInPNGInfo struct
# and will only continue writing the remaining data when the next pixel starts.
data_offset = int(math.ceil(info_len / 3)) * 3

data = b"".join([get_byte(data_offset + i) for i in range(save_game_info.structureByteSize)])

data = lz4.frame.decompress(data)

f = open(sys.argv[1] + ".structure.bin", 'wb')
f.write(data)
f.close()

data_offset += save_game_info.structureByteSize

data = b"".join([get_byte(data_offset + i) for i in range(save_game_info.structureIdentifierSize)])

f = open(sys.argv[1] + ".ident.bin", 'wb')
f.write(data)
f.close()

data_offset += save_game_info.structureIdentifierSize

data = b"".join([get_byte(data_offset + i) for i in range(save_game_info.structureMetaByteSize)])

f = open(sys.argv[1] + ".meta.bin", 'wb')
f.write(data)
f.close()
