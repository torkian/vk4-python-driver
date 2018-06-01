"""vk4 data extractor

This module is designed to extract raw data from keyence vk4 formatted files. 
Currently it produces dictionaries associated with 4 primary blocks of image
data: RGB peak color values, RGB light color values, light values, and height
values. The image data for each of these is stored in a numpy array. In
addition to this, the module can be used to output this image data in .csv
file format

Example
-------
Run as a script from the command line assumes a vk4 filename as a single
command line argument in the form of 'FYO9 DE02 270 SW (Stitch 6mm from weld)
After 2nd Cleaning_Y1_X1.vk4' where the values following Y and X will be 
different for each seperate file.

    $ python vk4_datapull.py filename

Notes
-----
    This module is dependent on the readbinary module. That module wraps useful
    python struct module unpack functions in functions with more readable names

Author
------
Wylie Gunn

Created
-------
30 May 2018

Last Modified
-------------
1 June 2018
"""

# import struct
import sys
import numpy as np
from PIL import Image
import readbinary as rb

#path = "/home/wylie/RCI/Savannah_River/vk4/"
path = ""
in_file_name = sys.argv[1]
in_file = open(path + in_file_name)
out_file_name = in_file_name[:9] + in_file_name[-10:-4]
print (out_file_name) 

#header information
extension = in_file.read(4)
dll_version = rb.read_uint32(in_file)
file_type = rb.read_uint32(in_file)


def list_of_tuples(arr):
    """ This function converts a numpy array of 3 element lists containing RGB
    data into a list of tuples containing that same data for the purpose of easy
    production of images using the Pillow library 
    """

    tup_list = []
    for elem in arr:
        tup_list.append( (elem[0] , elem[1], elem[2]) )
    return tup_list

def create_composite_rgb_values(data_dict):
    """This function takes an array of seperated RGB values and returns
    an array of composite RGB values
    """
 
    w = data_dict['width']
    h = data_dict['height']
    new_array = np.zeros(w*h, dtype=np.uint32)
    i=0
    for rgb in data_dict['data']:
        new_array[i] = ( (rgb[0] << 16) + (rgb[1] << 8) + (rgb[2]) )   
        i=i+1
    return new_array

def output_data_csv(data_dict, out_file_name):
    """This function outputs array data in .csv format text file with a name
    associated with both the name of the vk4 file it was extracted from as well
    as the type of data that is contains
    """

    w = data_dict['width']
    h = data_dict['height']
    name = '_' + data_dict['name']
    if data_dict['bit_depth'] == 24:
        data = create_composite_rgb_values(data_dict)
    else:
        data = data_dict['data'] 
    data = np.reshape(data, (h, w))
    np.savetxt(out_file_name + name + '.csv', data, delimiter=',')

#offsets
def get_offsets(in_file):
    offsets = {}
    offsets['meas_conds'] = rb.read_uint32(in_file)
    offsets['color_peak'] = rb.read_uint32(in_file)
    offsets['color_light'] = rb.read_uint32(in_file)
    offsets['light'] = rb.read_uint32(in_file)
    in_file.seek(8, 1)
    offsets['height'] = rb.read_uint32(in_file)
    in_file.seek(8, 1)
    offsets['clr_peak_thumb'] = rb.read_uint32(in_file)
    offsets['clr_thumb'] = rb.read_uint32(in_file)
    offsets['light_thumb'] = rb.read_uint32(in_file)
    offsets['height_thumb'] = rb.read_uint32(in_file)
    offsets['assembly_info'] = rb.read_uint32(in_file)
    offsets['line_measure'] = rb.read_uint32(in_file)
    offsets['line_thickness'] = rb.read_uint32(in_file)
    offsets['string_data'] = rb.read_uint32(in_file)
    #not sure if reserved is necessary
    offsets['reserved'] = rb.read_uint32(in_file)
    return offsets

# color light RGB data
def pull_color_light(offset_dict):
    cl = {}
    cl['name'] = 'rgb_light'
    in_file.seek(offset_dict['color_light'])
    cl['width'] = rb.read_uint32(in_file)
    cl['height'] = rb.read_uint32(in_file)
    cl['bit_depth'] = rb.read_uint32(in_file)
    #in_file.seek(8,1)
    cl['compression'] = rb.read_uint32(in_file)
    cl['data_byte_size'] = rb.read_uint32(in_file)

    rgb_color_light_arr = np.zeros( ((cl['width']*cl['height']), (cl['bit_depth']/8)), 
                                      dtype=np.uint8 )
    
    i=0
    for val in range(cl['width']*cl['height']):
        rgb = []
        for channel in range(3):
            rgb.append(ord(in_file.read(1)))
        rgb_color_light_arr[i] = rgb
        i=i+1

    cl['data'] = rgb_color_light_arr
    # print(rgb_color_light_arr)
    return cl

# color peak RGB data
def pull_color_peak(offset_dict):
    cp = {}
    cp['name'] = 'rgb_peak'
    in_file.seek(offset_dict['color_peak'])
    cp['width'] = rb.read_uint32(in_file)
    cp['height'] = rb.read_uint32(in_file)
    cp['bit_depth'] = rb.read_uint32(in_file)
    cp['compression'] = rb.read_uint32(in_file)
    cp['data_byte_size'] = rb.read_uint32(in_file)

    rgb_color_peak_arr = np.zeros( ((cp['width']*cp['height']), (cp['bit_depth']/8)),
                                     dtype=np.uint8 )
 
    i=0
    for val in range(cp['width']*cp['height']):
        rgb = []
        for channel in range(3):
            rgb.append(ord(in_file.read(1)))
        rgb_color_peak_arr[i] = rgb
        i=i+1

    cp['data'] = rgb_color_peak_arr
    # print(rgb_color_peak_arr)
    return cp

# light 
def pull_light_data(offset_dict):
    ld = {}
    ld['name'] = 'light'
    in_file.seek(offset_dict['light'])
    ld['width'] = rb.read_uint32(in_file)
    ld['height'] = rb.read_uint32(in_file)
    ld['bit_depth'] = rb.read_uint32(in_file)
    ld['compression'] = rb.read_uint32(in_file)
    ld['data_byte_size'] = rb.read_uint32(in_file)
    ld['pallete_range_min'] = rb.read_uint32(in_file)
    ld['pallete_range_max'] = rb.read_uint32(in_file)
    #the pallete section of the hexdump is 768 bytes long has 256 3-byte
    #repeats, for now I will store them as a 1d array of uint8 values 
    light_pallete = np.zeros( 768, dtype=np.uint8 )

    i=0
    for val in range(768):
        light_pallete[i] = ord(in_file.read(1))
        i=i+1
    ld['pallete'] = light_pallete

    light_arr = np.zeros( (ld['width']*ld['height']), dtype=np.uint16 )
    i=0
    for val in range(ld['width']*ld['height']):
        light_arr[i] = rb.read_uint16(in_file)
        i=i+1
    ld['data']=light_arr
    # print(light_arr)
    return ld

# height data
def pull_height_data(offset_dict):
    hd = {}
    hd['name'] = 'height'
    in_file.seek(offset_dict['height'])
    hd['width'] = rb.read_uint32(in_file)
    hd['height'] = rb.read_uint32(in_file)
    hd['bit_depth'] = rb.read_uint32(in_file)
    hd['compression'] = rb.read_uint32(in_file)
    hd['data_byte_size'] = rb.read_uint32(in_file)
    hd['pallete_range_min'] = rb.read_uint32(in_file)
    hd['pallete_range_max'] = rb.read_uint32(in_file)
    #the pallete section of the hexdump is 768 bytes long has 256 3-byte
    #repeats, for now I will store them as a 1d array of uint8 values 
    height_pallete = np.zeros( 768, dtype=np.uint8 )
    
    i=0
    for val in range(768):
        height_pallete[i] = ord(in_file.read(1))
        i=i+1
    hd['pallete'] = height_pallete

    height_arr = np.zeros( (hd['width']*hd['height']), dtype=np.uint32 )
    i=0
    for val in range(hd['width']*hd['height']):
        height_arr[i] = rb.read_int32(in_file)
        i=i+1
    hd['data']=height_arr
    # print(height_arr)
    return hd

offsets = get_offsets(in_file)
color_peak_data =  pull_color_peak(offsets)
color_light_data = pull_color_light(offsets)
light_data = pull_light_data(offsets)
height_data = pull_height_data(offsets)

""" ###create a test image###  ###ignore for now###
img_array = np.reshape(color_peak_data['data'], (768, 1024))
image = Image.fromarray(img_array, 'RGB')
#image.putdata(height_data['data'])
if image.mode != 'RGB':
    image = image.convert('RGB')
image.save("test_color_peak.jpeg", "JPEG")
"""


output_data_csv(color_peak_data, out_file_name)
output_data_csv(color_light_data, out_file_name)
output_data_csv(light_data, out_file_name)
output_data_csv(height_data, out_file_name)

