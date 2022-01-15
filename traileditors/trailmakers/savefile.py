from .. import trailmakers

__all__ = [
    'Savefile',
]


class Savefile:
    def __init__(self):
        self.player_save_data = None
        self.latest_structure_identifier = None
        self.latest_structure_data = None

    @staticmethod
    def from_file(file):
        savefile = Savefile()

        savefile.player_save_data = trailmakers.protobuf.TrailmakersPlayerSaveData()
        savefile.player_save_data.ParseFromString(file.read())

        savefile.latest_structure_identifier = trailmakers.protobuf.StructureSaveIdentifierProto()
        savefile.latest_structure_identifier.ParseFromString(savefile.player_save_data.m_latestStructureIdentifierBytes)

        savefile.latest_structure_data = trailmakers.protobuf.StructureGraphSaveDataProto()
        savefile.latest_structure_data.ParseFromString(savefile.player_save_data.m_latestStructureData)

        return savefile
