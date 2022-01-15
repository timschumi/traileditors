#!/usr/bin/python

from google.protobuf import text_format
import sys
import PIL.Image
from traileditors import trailmakers

image = PIL.Image.open(sys.argv[1])

blueprint = trailmakers.Blueprint.from_image(image)

print(f"[*] SaveGameInPNGInfo dump:")
print(f"     - version: {blueprint.SaveGameInPNGInfo.version}")
print(f"     - creator: \"{blueprint.SaveGameInPNGInfo.creator}\"")
print(f"     - structureByteSize: {blueprint.SaveGameInPNGInfo.structureByteSize}")
print(f"     - structureIdentifierSize: {blueprint.SaveGameInPNGInfo.structureIdentifierSize}")
print(f"     - structureMetaByteSize: {blueprint.SaveGameInPNGInfo.structureMetaByteSize}")

print(f"[*] StructureGraphSaveDataProto dump:")
print(text_format.MessageToString(blueprint.StructureGraphSaveDataProto, indent=4))

print(f"[*] StructureSaveIdentifierProto dump:")
print(text_format.MessageToString(blueprint.StructureSaveIdentifierProto, indent=4))

print(f"[*] StructureMetaDataProto dump:")
print(text_format.MessageToString(blueprint.StructureMetaDataProto, indent=4))
