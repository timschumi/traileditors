#!/usr/bin/python

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

# Not sure why this is needed, but otherwise the lz4 data starts at offset 1
# instead of offset 0
info_len += 1

print(f"[*] Length of SaveGameInPNGInfo object: {hex(info_len)} ({info_len})")

info = b"".join([get_byte(i) for i in range(info_len)])

f = open(sys.argv[1] + ".info.bin", 'wb')
f.write(info)
f.close()

data = b"".join([get_byte(info_len + i) for i in range(0x634)])

f = open(sys.argv[1] + ".data.bin", 'wb')
f.write(data)
f.close()
