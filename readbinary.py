""" Binary Byte Reader Functions

This module simply wraps several useful byte unpacking functions from
the python struct module with more readable function names

Author
------
Wylie Gunn

Created
-------
31 May 2018

Last Modified
-------------
1 June 2018

"""

import struct

def read_char(in_file):
    return struct.unpack('<c', in_file.read(1))[0]

def read_int16(in_file):
    return struct.unpack('<h', in_file.read(2))[0]

def read_int32(in_file):
    return struct.unpack('<i', in_file.read(4))[0]

def read_uchar(in_file):
    return struct.unpack('<b', in_file.read(1))[0]

def read_uint16(in_file):
    return struct.unpack('<H', in_file.read(2))[0]

def read_uint32(in_file):
    return struct.unpack('<I', in_file.read(4))[0]


  
