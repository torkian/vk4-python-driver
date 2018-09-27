"""VkContainer

This module houses the VkContainer class. Each VkContainer object stores
data associated with a particular Keyence Profilometry vk data file. The
data is extracted using functions in the vk4extract module and primarily
stored in dictionaries.

VkContainer objects are constructed using a builder pattern. Therefore a
user can create VkContainer objects storing different image data depending
on their needs.

Currently, this class only supports VkContainer objects created from vk4
formatted data files, however, the builder pattern leaves open the 
possibility of using it create VkContainers from other vk file formats.

Author
------
Wylie Gunn

Created
-------
17 July 2018

Last Modified
-------------
19 July 2018

"""

import logging
import numpy as np
import vk4extract as vk4in

log = logging.getLogger("vk4_driver.VkContainer")


class VkContainer(object):

    def __init__(self):
        self.extension = None  # seek(0) in_file.read(4)
        self.dll_version = None  # seek(4) struct.unpack('<I', in_file.read(4))[0]
        self.file_type = None  # seek(8) struct.unpack('<I', in_file.read(4))[0]
        self.offsets = None  # seek(12) vk4extract.extract_offsets(in_file)
        self.measurement_conditions = None
        self.rgb_peak_data = None
        self.rgb_light_data = None
        self.light_intensity_data = None
        self.height_data = None
        self.string_data = None
        self.image_width = None
        self.image_height = None

    def __str__(self):
        return self.string_data['title']

    def __repr__(self):
        return 'VkContainer(' + self.string_data['title'] + ')'

    def get_single_color_values(self, color, rgb_type):
        """get_single_color_values

        This method extracts a single channel of RGB data from the data arrays
        stored in either the rgb_peak_data or rgb_light_data attributes. It
        returns an array containing a 3 element list for each pixel. The list
        contains the value of the color channel corresponding to the color
        argument and 0's for the other two channels

        :param color: string pertaining to channel ('red', 'green', or 'blue')
        :param rgb_type: string pertaining to color type ('peak' or 'light')
        """
        log.debug("Entering get_single_color_values()")
        log.debug("Params::\tcolor: %s\trgb_type: %s " % (color, rgb_type))
        color_array = np.zeros(((self.image_width * self.image_height), 3), dtype=np.uint8)
        color_dict = {'red': 0, 'green': 1, 'blue': 2}

        if rgb_type == 'peak':
            rgb_array = self.rgb_peak_data['data']
        elif rgb_type == 'light':
            rgb_array = self.rgb_light_data['data']
        else:
            log.debug("Invalid color type: '%s' ; 'peak' or 'light' only" % rgb_type)
            return None

        col_offset = color_dict[color]
        i = 0
        for rgb in rgb_array:
            color_array[i][col_offset] = rgb[col_offset]
            i = i + 1
        log.debug("In get_single_color_values()\n\tArray of {} {} values:\n{}"
                  .format(color, rgb_type, color_array))

        log.debug("Exiting get_single_color_values()")
        return color_array


class VkDirector(object):
    """VkDirector

    This class constructs various VkContainer object determined by the
    particular VkBuilder object passed when the director is created.

    Each VkContainer will contain offsets extracted from the vk file, which
    are necessary to extract any further data from the file. In addition to
    this, each VkContainer will store metadata extracted from the vk file.
    Then, depending on the builder passed, the VkContainer will store
    various image data.
    """
    def __init__(self, builder):
        log.debug("In VkDirector's __init__()\n\tBuilder type: {}"
                  .format(type(builder)))
        self.builder = builder
        self.builder_type = str(type(self.builder))
        self.builder_type = self.builder_type[self.builder_type.find('\'') + 1:-2]

    def build(self):
        """build

        Build a VkContainer according to the builder's blueprints in the
        build_options dict
        """
        build_options = {'VkContainer.Vk4Builder':
                             ('rgb_peak', 'rgb_light', 'height', 'light'),
                         'VkContainer.Vk4BuilderRGBpeak': ('rgb_peak',),
                         'VkContainer.Vk4BuilderRGBlight': ('rgb_light',),
                         'VkContainer.Vk4BuilderHeight': ('height',),
                         'VkContainer.Vk4BuilderLight': ('light',)}

        build_layers = build_options[self.builder_type]

        self.builder.get_offsets()
        self.builder.meas_conds()
        self.builder.string_data()

        build_switch = {'rgb_peak': self.builder.rgb_peak,
                        'rgb_light': self.builder.rgb_light,
                        'height': self.builder.height,
                        'light': self.builder.light}

        for layer in build_layers:
            build_switch[layer]()

        self.builder.image_height()
        self.builder.image_width()

        return self.builder.get_result()


class VkBuilder(object):
    """VkBuilder

    Interface for VkBuilder builder classes
    """
    def offsets(self): pass

    def meas_conds(self): pass

    def rgb_light(self): pass

    def rgb_peak(self): pass

    def height(self): pass

    def light(self): pass

    def string_data(self): pass

    def image_height(self): pass

    def image_width(self): pass

    def get_result(self): pass


class Vk4Builder(VkBuilder):
    """Vk4Builder

    Builder class that houses methods to construct VkContainer objects
    from vk4 files.

    VkContainers constructed from this builder, contain all non-thumbnail
    image data contained in a vk4 file (RGB peak, RGB + light, Height, and
    light values).
    """
    def __init__(self, in_file):
        log.debug("Building vk4 VkContainer object")
        self.vk4 = VkContainer()
        self.in_file = in_file
        self.offsets = vk4in.extract_offsets(self.in_file)

    def get_offsets(self):
        self.vk4.offsets = self.offsets

    def meas_conds(self):
        self.vk4.measurement_conditions = \
            vk4in.extract_measurement_conditions(self.offsets, self.in_file)

    def rgb_peak(self):
        self.vk4.rgb_peak_data = \
            vk4in.extract_color_data(self.offsets, 'peak', self.in_file)

    def rgb_light(self):
        self.vk4.rgb_light_data = \
            vk4in.extract_color_data(self.offsets, 'light', self.in_file)

    def light(self):
        self.vk4.light_intensity_data = \
            vk4in.extract_img_data(self.offsets, 'light', self.in_file)

    def height(self):
        self.vk4.height_data = \
            vk4in.extract_img_data(self.offsets, 'height', self.in_file)

    def string_data(self):
        self.vk4.string_data = \
            vk4in.extract_string_data(self.offsets, self.in_file)

    def image_height(self):
        self.vk4.image_height = self.vk4.rgb_peak_data['height']

    def image_width(self):
        self.vk4.image_width = self.vk4.rgb_peak_data['width']

    def get_result(self):
        return self.vk4


class Vk4BuilderHeight(Vk4Builder):
    """Vk4BuilderHeight

    Builder class that houses methods to construct VkContainer objects
    from vk4 files.

    Contains height image data.
    """
    def image_height(self):
        self.vk4.image_height = self.vk4.height_data['height']

    def image_width(self):
        self.vk4.image_width = self.vk4.height_data['width']


class Vk4BuilderLight(Vk4Builder):
    """Vk4BuilderHeight

    Builder class that houses methods to construct VkContainer objects
    from vk4 files.

    Contains light image data.
    """
    def image_height(self):
        self.vk4.image_height = self.vk4.light_intensity_data['height']

    def image_width(self):
        self.vk4.image_width = self.vk4.light_intensity_data['width']


class Vk4BuilderRGBpeak(Vk4Builder):
    """Vk4BuilderHeight

    Builder class that houses methods to construct VkContainer objects
    from vk4 files.

    Contains RGB peak image data.
    """
    def image_height(self):
        self.vk4.image_height = self.vk4.rgb_peak_data['height']

    def image_width(self):
        self.vk4.image_width = self.vk4.rgb_peak_data['width']


class Vk4BuilderRGBlight(Vk4Builder):
    """Vk4BuilderHeight

    Builder class that houses methods to construct VkContainer objects
    from vk4 files.

    Contains RGB + light image data.
    """
    def image_height(self):
        self.vk4.image_height = self.vk4.rgb_light_data['height']

    def image_width(self):
        self.vk4.image_width = self.vk4.rgb_light_data['width']

