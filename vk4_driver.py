"""vk4 data extractor

This driver is designed to extract data from Keyence Profilometry vk4 formatted
files. The driver is capable of extracting user specified layers of data from
the vk4 file and outputting it in text-based csv format or jpeg and png image
files

Example
-------
Run as a script from the command line taking a vk4 file as input followed by an
output file type, the data layers to extract and an optional argument for an
output file name.

    $ python3 vk4_driver.py -ifilename -ttype -llayers (optional) -ofilename

    e.g.
        $ python3 vk4_driver.py -iFY09\ DE02\ 270\ SW\ \(Stitch\ 6mm\ from\
            Weld\)\ After\ 2nd\ Cleaning_Y1_X1.vk4  -tcsv -lRG

        This example pulls red and green peak color data from the input vk4
        file and outputs a .csv file with the default output filename

Use python3 vk4_driver.py -h for argument options

Note
----
    Executing this driver requires the vk4out, VK4container and vk4extract
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
27 June 2018

"""

import argparse
import os
import VK4container as vk4in
import vk4out


def main():
    parser = argparse.ArgumentParser(description="vk4 File Format Data" +
                                     "Extraction Tool")
    # group = parser.add_mutually_exclusive_group(required=True)

    parser.add_argument('-i', '--input', required=True, help="Specify input " +
                        "file to read.")
    parser.add_argument('-t', '--type', required=True, help="Specify output " +
                        "type. Options: csv, hcsv (csv file with metadata " +
                        "header), jpeg, png, tiff.")

    parser.add_argument('-l', '--layer', required=True, help="Specify data " +
                        "layer for output. Options: R, G, B, RL, GL, BL, L, " +
                        "H, RGB, LRGB")

    parser.add_argument('-o', '--output', help="Specify the output file " +
                        "basename (extension will be generated). If this " +
                        "argument is not specified, the basename will remain " +
                        "the same as the input basename")

    # TODO define mutually exclusive arguments

    args = parser.parse_args()
    print(args.input)
    in_file_name = args.input.strip("'")

    print("****** Command line args ******")
    print(args)

    # path = "/home/wylie/PycharmProjects/vk4/"
    # path = os.getcwd() + '/'


    with open(in_file_name, 'rb') as in_file:
        vk4_container = vk4in.VK4container(in_file)

    vk4out.output_data(vk4_container, args)


if __name__ == '__main__':
    main()
