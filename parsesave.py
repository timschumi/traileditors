#!/usr/bin/python

from lib import trailmakers_pb2
from google.protobuf import text_format
import sys

f = open(sys.argv[1], "rb")
data = f.read()
f.close()

player_save = trailmakers_pb2.TrailmakersPlayerSaveData()
player_save.ParseFromString(data)
print(f"[*] TrailmakersPlayerSaveData dump:")
print(text_format.MessageToString(player_save, indent=4))

latest_structure_ident = trailmakers_pb2.StructureSaveIdentifierProto()
latest_structure_ident.ParseFromString(player_save.m_latestStructureIdentifierBytes)
print(f"[*] m_latestStructureIdentifierBytes dump:")
print(text_format.MessageToString(latest_structure_ident, indent=4))

latest_structure_data = trailmakers_pb2.StructureGraphSaveDataProto()
latest_structure_data.ParseFromString(player_save.m_latestStructureData)
print(f"[*] m_latestStructureData dump:")
print(text_format.MessageToString(latest_structure_data, indent=4))
