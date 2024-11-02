#
# <-- pr4m0d -->
# https://pram0d.com
# https://twitter.com/pr4m0d
# https://github.com/psomashekar
#
# Copyright (c) 2024 Pramod Somashekar
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

# This script is used on top of the MRA tool to repack the gfx section of the Technos ROMs "Wrestlefest" and "Double Dragon 3".
# The reason this needs to be done is because the Technos format is separated into multiple planes that sprawl widely across the ROM.
# Therefore, it is not practical to do live decoding without first arranging the graphics into a more contiguous format as there will be too many reads just to get one line of pixel data.
# Also, not practical to create a loader in HDL that post-processes the data.

import os
import sys
import shutil

def decode_gfx(num_objects, num_planes, object_x_size, object_y_size, plane_offs, x_offs, y_offs, spacing, source_file, dest_file, source_addr, source_size, dest_addr):
    with open(source_file, "rb") as sf:
        sf.seek(source_addr)
        src_data = sf.read(source_size)
        dest_data = [0] * (num_objects * object_x_size * object_y_size)

    for object_number in range(num_objects): #repack all objects
        dest_object = [0] * (object_x_size * object_y_size) #create a temp object array to store the new data

        for plane in range(num_planes): #4 planes of data
            plane_bit = 1 << (num_planes - 1 - plane)
            plane_base_addr = (object_number * spacing) + plane_offs[plane]

            for y in range(object_y_size):
                yaddr = plane_base_addr + y_offs[y]
                dest_object_pos = y * object_x_size

                for x in range(object_x_size):
                    bit_num = (yaddr+x_offs[x])
                    try:
                        if (src_data[bit_num // 8] & (0x80 >> (bit_num % 8))) > 0:
                            dest_object[dest_object_pos+x] |= plane_bit
                    except:
                        print("Error at object number: " + str(object_number) + " plane: " + str(plane) + " x: " + str(x) + " y: " + str(y))
                        print("bit_num: " + str(bit_num) + " byte_num: " + str(bit_num // 8) + " bit_pos: " + str(bit_num % 8))
                        print("plane_base_addr: " + str(plane_base_addr) + " yaddr: " + str(yaddr) + " x_offs: " + str(x_offs[x]) + " y_offs: " + str(y_offs[y]))
                        return
        
        #write the data
        dest_data[(object_number * object_x_size * object_y_size) : ((object_number + 1) * object_x_size * object_y_size)] = dest_object
    
    with open(dest_file, "r+b") as df:
        df.seek(dest_addr)
        df.write(bytes(dest_data))

# Wrestlefest decoding reference table
CharPlaneOffsets_WF = [0, 2, 4, 6]
CharXOffsets_WF = [1, 0, 65, 64, 129, 128, 193, 192]
CharYOffsets_WF = [0, 8, 16, 24, 32, 40, 48, 56]
TilePlaneOffsets_WF = [8, 0, 0x200008, 0x200000]
TileXOffsets_WF = [0, 1, 2, 3, 4, 5, 6, 7, 256, 257, 258, 259, 260, 261, 262, 263]
TileYOffsets_WF = [0, 16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176, 192, 208, 224, 240]
SpritePlaneOffsets_WF = [0, 0x1000000, 0x2000000, 0x3000000]
SpriteXOffsets_WF = [0, 1, 2, 3, 4, 5, 6, 7, 128, 129, 130, 131, 132, 133, 134, 135]
SpriteYOffsets_WF = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120]

WF_base_gfx_offs = 0x110000
WF_char_gfx_size = 0x20000
WF_tile_gfx_size = 0x80000
WF_sprite_gfx_size = 0x800000

# Double dragon 3 decoding reference table
TilePlaneOffsets_DD3 = [0, 0x200000, 0x400000, 0x600000]
TileXOffsets_DD3 = [0, 1, 2, 3, 4, 5, 6, 7, 128, 129, 130, 131, 132, 133, 134, 135]
TileYOffsets_DD3 = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120]
SpritePlaneOffsets_DD3 = [0, 0x800000, 0x1000000, 0x1800000]
SpriteXOffsets_DD3 = [0, 1, 2, 3, 4, 5, 6, 7, 128, 129, 130, 131, 132, 133, 134, 135]
SpriteYOffsets_DD3 = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120]

DD3_base_gfx_offs = 0x110000
DD3_tile_gfx_size = 0x100000
DD3_sprite_gfx_size = 0x400000

# Combatribes decoding reference table
TilePlaneOffsets_CT = [0, 0x200000, 0x400000, 0x600000]
TileXOffsets_CT = [0, 1, 2, 3, 4, 5, 6, 7, 128, 129, 130, 131, 132, 133, 134, 135]
TileYOffsets_CT = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120]
SpritePlaneOffsets_CT = [0, 0x800000, 0x1000000, 0x1800000]
SpriteXOffsets_CT = [0, 1, 2, 3, 4, 5, 6, 7, 128, 129, 130, 131, 132, 133, 134, 135]
SpriteYOffsets_CT = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120]

CT_base_gfx_offs = 0xD0000
CT_tile_gfx_size = 0x100000
CT_sprite_gfx_size = 0x400000

#first copy the file over
shutil.copy(sys.argv[1], sys.argv[2])
if(sys.argv[3] == "wrestlefest"):
    decode_gfx(0x1000, 4, 8, 8, CharPlaneOffsets_WF, CharXOffsets_WF, CharYOffsets_WF, 0x100, sys.argv[1], sys.argv[2], WF_base_gfx_offs, WF_char_gfx_size, 0x110000) #character rom offs
    decode_gfx(0x1000, 4, 16, 16, TilePlaneOffsets_WF, TileXOffsets_WF, TileYOffsets_WF, 0x200, sys.argv[1], sys.argv[2], WF_base_gfx_offs + WF_char_gfx_size, WF_tile_gfx_size, 0x150000) #tile rom offs
    decode_gfx(0x10000, 4, 16, 16, SpritePlaneOffsets_WF, SpriteXOffsets_WF, SpriteYOffsets_WF, 0x100, sys.argv[1], sys.argv[2], WF_base_gfx_offs + WF_char_gfx_size + WF_tile_gfx_size, WF_sprite_gfx_size, 0x250000) #sprite rom offs
elif(sys.argv[3] == "doubledragon3"):
    decode_gfx(0x2000, 4, 16, 16, TilePlaneOffsets_DD3, TileXOffsets_DD3, TileYOffsets_DD3, 0x100, sys.argv[1], sys.argv[2], DD3_base_gfx_offs, DD3_tile_gfx_size, 0x110000) #tile rom offs
    decode_gfx(0x4800, 4, 16, 16, SpritePlaneOffsets_DD3, SpriteXOffsets_DD3, SpriteYOffsets_DD3, 0x100, sys.argv[1], sys.argv[2], DD3_base_gfx_offs + DD3_tile_gfx_size, DD3_sprite_gfx_size, 0x310000) #sprite rom offs
elif(sys.argv[3] == "combatribes"):
    decode_gfx(0x2000, 4, 16, 16, TilePlaneOffsets_CT, TileXOffsets_CT, TileYOffsets_CT, 0x100, sys.argv[1], sys.argv[2], CT_base_gfx_offs, CT_tile_gfx_size, 0xD0000) #tile rom offs
    decode_gfx(0x4800, 4, 16, 16, SpritePlaneOffsets_CT, SpriteXOffsets_CT, SpriteYOffsets_CT, 0x100, sys.argv[1], sys.argv[2], CT_base_gfx_offs + CT_tile_gfx_size, CT_sprite_gfx_size, 0x2D0000) #sprite rom offs