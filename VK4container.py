"""VK4container

This module houses the VK4container class. Each VK4container object stores
data associated with a particular Keyence Profilometry vk4 data file. The
data is extracted using functions in the vk4extract module and primarily
stored in dictionaries.

Author
------
Wylie Gunn

Created
-------
11 June 2018

Last Modified
-------------
26 June 2018

"""
import struct
import numpy as np
import vk4extract


class VK4container(object):
    def __init__(self, in_file):
        self.in_file = in_file

        self.extension = in_file.read(4)
        self.dll_version = struct.unpack('<I', in_file.read(4))[0]
        self.file_type = struct.unpack('<I', in_file.read(4))[0]
        self.offsets = vk4extract.extract_offsets(in_file)
        self.measurement_conditions = \
            vk4extract.extract_measurement_conditions(self.offsets, self.in_file)
        self.rgb_peak_data = \
            vk4extract.extract_color_data(self.offsets, 'peak', self.in_file)
        self.rgb_light_data = \
            vk4extract.extract_color_data(self.offsets, 'light', self.in_file)
        self.light_intensity_data = \
            vk4extract.extract_img_data(self.offsets, 'light', self.in_file)
        self.height_data = \
            vk4extract.extract_img_data(self.offsets, 'height', self.in_file)
        self.string_data = \
            vk4extract.extract_string_data(self.offsets, self.in_file)

        self.image_width = self.rgb_light_data['width']
        self.image_height = self.rgb_light_data['height']

    def __str__(self):
        return self.string_data['title']

    def __repr__(self):
        return 'VK4container(' + self.string_data['title'] + ')'

    def get_single_color_values(self, color, rgb_type):
        """get_single_color_values

        This method extracts a single channel of RGB data from the data arrays
        stored in either the rgb_peak_data or rgb_list_data attributes. It
        returns an array containing a 3 element list for each pixel. The list
        contains the value of the color channel corresponding to the color
        argument and 0's for the other two channels

        :param color: string pertaining to channel ('red', 'green', or 'blue')
        :param rgb_type: string pertaining to color type ('peak' or 'light')
        """
        color_array = np.zeros(((self.image_width * self.image_height), 3), dtype=np.uint8)
        color_dict = {'red': 0, 'green': 1, 'blue': 2}
        if rgb_type == 'peak':
            rgb_array = self.rgb_peak_data['data']
        elif rgb_type == 'light':
            rgb_array = self.rgb_light_data['data']
        else:
            print("Invalid color type: '%s' ; 'peak' or 'light' only" % rgb_type)
            return None

        col_offset = color_dict[color]
        i = 0
        for rgb in rgb_array:
            color_array[i][col_offset] = rgb[col_offset]
            i = i + 1
        print("****** array of %s %s values ******" % (color, rgb_type))
        print(color_array)
        return color_array
