#!/usr/bin/python

from google.protobuf import text_format
import sys
from traileditors import trailmakers

with open(sys.argv[1], "rb") as f:
    savefile = trailmakers.Savefile.from_file(f)

print(f"[*] TrailmakersPlayerSaveData dump:")
print(text_format.MessageToString(savefile.player_save_data, indent=4))

print(f"[*] m_latestStructureIdentifierBytes dump:")
print(text_format.MessageToString(savefile.latest_structure_identifier, indent=4))

print(f"[*] m_latestStructureData dump:")
print(text_format.MessageToString(savefile.latest_structure_data, indent=4))
