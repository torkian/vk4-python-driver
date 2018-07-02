"""vk4out

This module handles the output of data extracted from Keyence Profilometry
vk4 data files and contained in VK4container objects. The data can be output in
a text comma separated values format, or in jpeg, png, and tiff image formats.
The data that can be output includes, height, light, RGB, and RGB + light
(RGB + laser) data.

Proper output of data is dependent on proper lists of arguments, assuming that
the output_data function is called from the vk4_driver module with a valid
input of command line arguments.

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

import numpy as np
from PIL import Image
import os


layer_dict = {'R': ['red', 'peak'], 'G': ['green', 'peak'], 'B': ['blue', 'peak'],
              'RL': ['red', 'light'], 'GL': ['green', 'light'], 'BL': ['blue', 'light']}


def output_file_name_maker(args):
    """output_file_name_maker

    Return output filename provided via command line or a string for an output
    filename in the form:

        file title + type argument + layers argument

    :param args: list of argparse arguments
    """
    path = os.getcwd() + '/out_files/'
    if not os.path.isdir(path):
        os.mkdir(path)

    if args.output is None:
        out_file_name = path + args.input[:-4] + '_' + args.type + '_' + args.layer
    else:
        out_file_name = path + args.output
    return out_file_name


def list_of_tuples(arr):
    """list_of_tuples

    This function converts a numpy array of 3 element lists containing RGB
    data into a list of tuples containing that same data for the purpose of
    straightforward image production using the PIL library

    :param: arr: numpy array of 3 element lists
    """
    tup_list = []
    for elem in arr:
        tup_list.append((elem[0], elem[1], elem[2]))
    return tup_list


def create_composite_rgb_values(vk4_container, layer_list):
    """create_composite_rgb_values

    This function takes an array of separated RGB values and returns an array
    of composite RGB values

    :param vk4_container: VK4container object
    :param layer_list: list of color layers
    """
    width = vk4_container.image_width
    height = vk4_container.image_height
    comp_rgb_array = np.zeros(width * height, dtype=np.uint32)

    for lay in layer_list:
        i = 0
        for rgb in lay:
            comp_rgb_array[i] = comp_rgb_array[i] + ((rgb[0] << 16) + (rgb[1] << 8) + (rgb[2]))
            i = i + 1
    print('****** composite rgb array ******')
    print(comp_rgb_array)

    return comp_rgb_array

""" currently not in use
def create_separate_rgb_values(vk4_container, layer_list):
    width = vk4_container.image_width
    height = vk4_container.image_height
    temp_array = np.zeros((width * height, 3), dtype = np.uint8)

    for lay in layer_list:
        i = 0
        for rgb in lay:
            temp_array[i][0] += rgb[0]
            temp_array[i][1] += rgb[1]
            temp_array[i][2] += rgb[2]
            i = i + 1

    dt = np.dtype("(1,3)u1")
    sep_array = np.zeros(width * height, dtype=object)
    i = 0
    for elem in temp_array:
        sep_array[i] = ' '.join([str(elem[0]), str(elem[1]), str(elem[2])])
        # sep_array[i] = (elem[0], elem[1], elem[2])
        i = i + 1
    print('****** separate rgb array ******')
    print(temp_array)

    return sep_array
"""

def create_array_from_rgb_layers(vk4_container, layer_list):
    """create_array_from_rgb_layers

    Iterates through list of RGB data arrays to create an array of lists
    containing particular combinations of RGB data. Returns the array

    :param vk4_container: VK4container object
    :param layer_list: list of color layers
    """
    width = vk4_container.image_width
    height = vk4_container.image_height

    new_array = np.zeros(((width * height), 3), dtype=np.uint8)
    for layer in layer_list:
        i = 0
        for rgb in layer:
            new_array[i][0] += rgb[0]
            new_array[i][1] += rgb[1]
            new_array[i][2] += rgb[2]
            i = i + 1
    print(6*"*" + " array for rgb image output " + 6*"*")
    print(new_array)

    # A list of tuples facilitates JPEG and PNG image production using PIL
    return new_array  # list_of_tuples(new_array)


def get_data_from_layers(vk4_container, layers, step, is_image=False):
    """get_data_from_layers

    Retrieves data from VK4container determined by layers argument, and appends
    that data to a list. If the output is supposed to be text this function
    returns an array of composite RGB color values. If the output is supposed
    to be an image, it returns a list of 3 element tuples representing RGB
    values

    :param vk4_container: VK4container object
    :param layers: string defining layers to retrieve
    :param step: defines step to iterate through layers argument
    :param is_image: True if output is to be an image
    """
    holder = []
    for x in range(0, len(layers), step):
        lay = layers[x:x + step]
        holder.append(vk4_container.get_single_color_values(layer_dict[lay][0], layer_dict[lay][1]))

    if is_image:
        return create_array_from_rgb_layers(vk4_container, holder)
    else:
        return create_composite_rgb_values(vk4_container, holder)
        # return create_separate_rgb_values(vk4_container, holder)


def output_data(vk4_container, args):
    """output_data

    Determines what data to retrieve from VK4container object and outputs that
    data as defined by the arguments provided with args

    :param vk4_container: VK4container
    :param args: list of argparse arguments
    """
    layer = args.layer
    is_image_dict = {'csv': False, 'hcsv': False, 'jpeg': True, 'png': True, 'tiff': True}
    single_noncomposite_layer_options = {'H': vk4_container.height_data,
                                         'L': vk4_container.light_intensity_data}

    print("Output type: %s" % args.type)
    is_image = is_image_dict[args.type]

    # If the data of interest is height or light intensity values, we can
    # retrieve those directly from the VK4container's height_data and
    # light_intensity_data dicts. Otherwise call get_data_from_layers()
    # to retrieve the RGB layers of interest.
    if len(layer) == 1 and layer in single_noncomposite_layer_options:
        data = single_noncomposite_layer_options[layer]['data']
    elif layer[0] == 'L' or (len(layer) > 1 and layer[1] == 'L'):
        lay = 'L'.join(layer[1:]) + 'L'
        data = get_data_from_layers(vk4_container, lay, 2, is_image)
    else:
        data = get_data_from_layers(vk4_container, layer, 1, is_image)

    if is_image:
        output_image(vk4_container, args, data)
    else:
        output_csv(vk4_container, args, data)


def output_csv(vk4_container, args, data):
    """output_csv

    Outputs data to file in comma separated values format

    :param vk4_container: VK4container object
    :param args: list of argparse arguments
    :param data: numpy array of values
    """
    out_file_name = output_file_name_maker(args) + '.csv'

    width = vk4_container.image_width
    height = vk4_container.image_height

    data = np.reshape(data, (height, width))

    with open(out_file_name, 'w') as out_file:
        if args.type == 'hcsv':
            header = create_file_meta_data(vk4_container, args)
            np.savetxt(out_file, header, delimiter=',', fmt='%s')
            out_file.write('\n')
        np.savetxt(out_file, data, delimiter=',', fmt='%d')

    # with open("test_sep.csv", 'w') as out_file:
     #   np.savetxt(out_file, data2, delimiter=',', fmt='%s')


def scale_data(vk4_container, args, data):
    """scale_data

    Scales height data according to the formula: z length per digit * 1 picometer
    Scales light data according to the formula: 0.5^(bit-depth)
    Stores scaled data in a new array and returns it.

    :param vk4_container: VK4container object
    :param args: list of argparse arguments
    :param data: numpy array of image data
    """
    layer = args.layer
    scale = 0.0
    if layer == 'L':
        bit_depth = vk4_container.light_intensity_data['bit_depth']
        scale = 0.5 ** bit_depth
    elif layer == 'H':
        picometer = 1.0e-12
        z_length_per_digit = \
            vk4_container.measurement_conditions['z_length_per_digit']
        scale = picometer * z_length_per_digit

    width = vk4_container.image_width
    height = vk4_container.image_height

    new_array = np.zeros((width * height), dtype=np.float32)
    i = 0
    for val in data:
        new_array[i] = val * scale
        i = i + 1

    return new_array


def output_image(vk4_container, args, data):
    """output_image

    Outputs data to file in jpeg, png, or tiff format

    :param vk4_container: VK4container object
    :param args: list of argparse arguments
    :param data: list of tuples for jpeg and png images
    """
    not_rgb_list = ['L', 'H']
    out_type = args.type
    layer = args.layer

    out_file_name = output_file_name_maker(args) + '.' + out_type

    width = vk4_container.image_width
    height = vk4_container.image_height
    if layer in not_rgb_list:
        data = scale_data(vk4_container, args, data)
        image = Image.fromarray(np.reshape(data, (height, width)), 'F')
    else:
        image = Image.fromarray(np.reshape(data, (height, width, 3)), 'RGB')
    image.info = create_file_meta_data(vk4_container, args)
    image.save(out_file_name, args.type.upper())


def create_file_meta_data(vk4_container, args):
    """create_file_meta_data

    Creates a list of pertinent data associated with the vk4 file the
    VK4container is created and returned formatted as an array for attachment
    to csv files or a dictionary for attatchment to image files.

    :param vk4_container: VK4container object
    :param args: list of argparse arguments
    """
    header_list = list()
    header_list.append(args.layer)
    header_list.append('\n')
    header_list.append('File name')
    header_list.append(args.input)
    header_list.append('Title')
    header_list.append(args.input[:-4])
    header_list.append('Measurement date')
    header_list.append(str(vk4_container.measurement_conditions['month']) + '\\' +
                       str(vk4_container.measurement_conditions['day']) + '\\' +
                       str(vk4_container.measurement_conditions['year']))
    header_list.append('Measurement time')
    header_list.append(str(vk4_container.measurement_conditions['hour']) + ':' +
                       str(vk4_container.measurement_conditions['minute']) + ':' +
                       str(vk4_container.measurement_conditions['second']))
    # User mode?
    header_list.append('Objective lens')
    header_list.append(vk4_container.string_data['lens_name'] + ' ' +
                       str(vk4_container.measurement_conditions['lens_magnification'] / 10.0) + 'x')
    header_list.append('Numerical Aperture')
    header_list.append(vk4_container.measurement_conditions['num_aperture'] / 1000.0)
    # Size?  Standard?
    # Mode?  Surface profile?
    # RPD?  OFF?
    header_list.append('Quality')
    header_list.append('Skip 4 lines')
    header_list.append('Pitch (um)')
    header_list.append(vk4_container.measurement_conditions['pitch'] / 1000.0)
    header_list.append('Z measurement distance (um)')
    header_list.append(vk4_container.measurement_conditions['distance'] / 1000.0)
    # Double scan?  OFF?
    header_list.append('Brightness 1')
    header_list.append(vk4_container.measurement_conditions['PMT_gain'])
    header_list.append('Brightness 2')
    br_2 = vk4_container.measurement_conditions['PMT_gain_2']
    header_list.append('---') if br_2 == 0 else header_list.append(br_2)
    # Not sure how they got ND filter to 30% in example csv
    header_list.append('ND filter (%)')
    header_list.append(vk4_container.measurement_conditions['ND_filter'] * 30)
    header_list.append('Optical zoom')
    header_list.append(vk4_container.measurement_conditions['optical_zoom'] / 10.0)
    # Average count? 1 time?
    # Filter? OFF?
    # Fine mode? ON?
    header_list.append('Line count')
    l_count = vk4_container.measurement_conditions['number_of_lines']
    header_list.append(l_count)

    header_list.append('Line position1')
    if l_count == 0:
        header_list.append('---')
    else:
        header_list.append(vk4_container.measurement_conditions['reserved_1'][0])

    header_list.append('Line position2')
    if l_count == 0:
        header_list.append('---')
    else:
        header_list.append(vk4_container.measurement_conditions['reserved_1'][1])

    header_list.append('Line position3')
    if l_count == 0:
        header_list.append('---')
    else:
        header_list.append(vk4_container.measurement_conditions['reserved_1'][2])

    header_list.append('Camera gain (db)')
    header_list.append(vk4_container.measurement_conditions['camera_gain'] * 6)
    header_list.append('Shutter speed')
    header_list.append(vk4_container.measurement_conditions['shutter_speed'])
    header_list.append('White balance mode')
    wb_mode = vk4_container.measurement_conditions['white_balance_mode']
    header_list.append('Auto') if wb_mode == 1 else header_list.append(wb_mode)
    header_list.append('White balance R')
    header_list.append(vk4_container.measurement_conditions['white_balance_red'])
    header_list.append('White balance B')
    header_list.append(vk4_container.measurement_conditions['white_balance_blue'])
    header_list.append('Intensity correction mode')
    header_list.append('Gamma correction')
    header_list.append('Gamma correction value')
    header_list.append(vk4_container.measurement_conditions['gamma'] / 100.0)
    header_list.append('Gamma offset (%)')
    header_list.append(vk4_container.measurement_conditions['gamma_correction_offset'] /
                       65536.0)
    # W/B inversion?  OFF?
    # Head type?  VK-X110?
    # Correct intensity eccentricity?  OFF?
    # Correct field curvature? OFF?
    header_list.append('XY calibration (nm/pixel)')
    header_list.append(vk4_container.measurement_conditions['x_length_per_pixel'] / 1000.0)
    header_list.append('Z calibration (nm/digit)')
    header_list.append(vk4_container.measurement_conditions['z_length_per_digit'] / 1000.0)
    # Saturation?
    # Contrast?
    # Brightness?
    # AI noise elimination?  Auto(ON)?
    # Angled surface noise filter?  Auto(OFF)?
    header_list.append('Width')
    header_list.append(vk4_container.image_width)
    header_list.append('Height')
    header_list.append(vk4_container.image_height)
    # Skip amount?  1?

    out_type = args.type
    if out_type == 'hcsv':
        return np.reshape(header_list, (len(header_list) // 2, 2))
    else:
        # Can use a dict to attach info to an image using PILs Image module
        meta_dict = dict()
        for n in range(0, len(header_list), 2):
            meta_dict[header_list[n]] = header_list[n + 1]
        return meta_dict

