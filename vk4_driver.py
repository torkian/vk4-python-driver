"""Vk4 data extractor

This driver is designed to extract data from Keyence Profilometry Vk4 formatted
files. The driver is capable of extracting user specified layers of data from
the Vk4 file and outputting it in text-based csv format or jpeg and png image
files

Example
-------
Run as a script from the command line taking a Vk4 file as input followed by an
output file type, the data layers to extract and an optional argument for an
output file name.

    $ python3 Vk4_driver.py -ifilename -ttype -llayers (optional) -ofilename
        (optional) -v
    e.g.
        $ python3 Vk4_driver.py -iFY09\ DE02\ 270\ SW\ \(Stitch\ 6mm\ from\
            Weld\)\ After\ 2nd\ Cleaning_Y1_X1.Vk4  -tcsv -lRG

        This example pulls red and green peak color data from the input Vk4
        file and outputs a .csv file with the default output filename

Use python3 Vk4_driver.py -h for argument options

Note
----
    Executing this driver requires the Vk4out, Vk4container and Vk4extract
    modules

    Image output for height and light intensity data is only possible for
    tiff type files. All other type and layer combinations should work.

    Currently, csv output for RGB data (color peak and color + light) is
    composed as the value of the three byte integer representing the
    individual pixel, as opposed to individual 8 bit integer values for each
    color channel.

Author
------
Wylie Gunn

Created
-------
6 June 2018

Last Modified
-------------
19 July 2018

"""

import argparse
import logging
import vk4out
import VkContainer


def config_logging(debug_level):
    log_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)8s %(name)s | %(message)s')
    log_handler.setFormatter(formatter)

    log = logging.getLogger("vk4_driver")
    log.addHandler(log_handler)
    log.setLevel(debug_level)

    return log


def main():

    parser = argparse.ArgumentParser(description="Vk4 File Format Data" +
                                     "Extraction Tool\n")
    # group = parser.add_mutually_exclusive_group(required=True)

    parser.add_argument('-i', '--input', required=True, help="Specify input " +
                        "file to read.\n")
    parser.add_argument('-t', '--type', required=True, help="Specify output " +
                        "type. Options: csv, hcsv (csv file with metadata " +
                        "header), jpeg, png, tiff.\n")

    parser.add_argument('-l', '--layer', required=True, help="Specify data " +
                        "layer for output. Options: R, G, B, RL, GL, BL, L, " +
                        "H, RGB, LRGB. Different combinations of R, G, or B; " +
                        "or L followed by combinations of R, G, or B are " +
                        "allowed - e.g. RB, LGB, LRB, G.")

    parser.add_argument('-o', '--output', help="Specify the output file " +
                        "basename (extension will be generated). If this " +
                        "argument is not specified, the basename will remain " +
                        "the same as the input basename")

    parser.add_argument('-v', '--verbose', help="Specify logging level as " +
                        "verbose, meaning at DEBUG level, otherwise logging " +
                        "acts at INFO level. See documentation on python's " +
                        "logging module for more information.",
                        action='store_true')

    # TODO define mutually exclusive arguments

    args = parser.parse_args()

    log_dict = {True: logging.DEBUG, False: logging.INFO}

    log_level = log_dict[args.verbose]
    log = config_logging(log_level)
    log.info("In main() after parsing command line arguments")
    log.debug("In main()\n\tCommand line args:\n\t{}".format(args))

    in_file_name = args.input.strip("'")

    layers = args.layer
    log.debug("In main()\n\tLayers: {}\tlen(layers): {}".format(layers, len(layers)))

    if len(layers) == 1 and (layers == 'L' or layers == 'H'):  # Height or Light data layers
        build = layers
    elif len(layers) > 1 and (layers[0] == 'L' or layers[1] == 'L'):  # RGB + light data layers
        build = 'rgb_light'
    else:  # RGB peak data layers
        build = 'rgb_peak'

    builder_dict = {'L': VkContainer.Vk4BuilderLight,
                    'H': VkContainer.Vk4BuilderHeight,
                    'rgb_light': VkContainer.Vk4BuilderRGBlight,
                    'rgb_peak': VkContainer.Vk4BuilderRGBpeak}

    log.info("Opening file - %s" % in_file_name)

    with open(in_file_name, 'rb') as in_file:
        builder = builder_dict[build](in_file)
        director = VkContainer.VkDirector(builder)
        vk4_container = director.build()
        log.debug("Vk4_container:\n\tVkContainer type:\n\t{}".format(type(vk4_container)))

    log.info("Closing file - %s" % in_file_name)

    vk4out.output_data(vk4_container, args)

    log.info("Exiting main()")
    log.info("Program completed execution")


if __name__ == '__main__':
    main()


