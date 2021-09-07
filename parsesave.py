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
