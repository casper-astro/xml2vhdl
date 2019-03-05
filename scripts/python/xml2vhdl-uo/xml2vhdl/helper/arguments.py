# -*- coding: utf8 -*-
"""

***********************
``helper/arguments.py``
***********************

`LICENSE`_ © 2018-2019 Science and Technology Facilities Council & contributors

.. _LICENSE: _static/LICENSE_STFC

``arguments.py`` is a helper module provided to define and configure the argument passing and parsing for the
main modules.


"""
import os
import yaml
import argparse

import customlogging as log
logger = log.config_logger(name=__name__)

import version as my_version
rev = filter(str.isdigit, "$Rev$")  # Do Not Modify this Line
version = my_version.Version(0, 6, 0, svn_rev=rev, disable_svn_logging=True)
__version__ = version.get_version()
__str__ = my_version.about(__name__, __version__, version.revision)


class Arguments(object):
    """Creates arguments for passing files and configuration data to the script.

    A Class which configures and retrieves Arguments for use by a python script. Dictionaries
    retrieved from YAML files are added as attributes to this class with no sub-processing.
    Information including the filename of each YAML file parsed is also added as an attribute.

    See :ref:`arguments`

    Attributes:

    """
    def __init__(self):
        self.logger = log.config_logger(name=__name__, class_name=self.__class__.__name__)
        _parser = self._create_parser()
        self._add_arguments(_parser)
        args = self._get_args(_parser)
        log.sect_break(self.logger)
        self.logger.info('Loading Arguments from Command Line...')
        log.sect_break(self.logger)
        self._set_args_as_attrs(args)

    def __repr__(self):
        return "{self.__class__.__name__}()".format(self=self)

    def __str__(self):
        return "{} is a {self.__class__.__name__} object".format(__name__, self=self)

    @staticmethod
    def _create_parser():
        """

        Creates an argparse object

        :return:
        """
        return argparse.ArgumentParser()

    @staticmethod
    def _add_arguments(parser):
        """Adds Arguments to provide to python script, using the argparse module.

        Args:
            parser (obj): argparse object

        Returns:
            None

        """
        parser.add_argument("-l", "--log",
                            dest="log",
                            action="store_true",
                            help="Print version and history log.")
        parser.add_argument("-i", "--input_file",
                            dest="input_file",
                            action="append",
                            default=list(),
                            help="XML input files. It is possible to specify several files by repeating \
                                    this option.")
        parser.add_argument("-d", "--input_folder",
                            dest="input_folder",
                            action="append",
                            default=list(),
                            help="Paths to input files folders. It is possible to specify several folders by \
                                    repeating this option. The script runs on all XML files in included \
                                    folders.")
        parser.add_argument("-p", "--path",
                            dest="path",
                            action="append",
                            default=list(),
                            help="Paths to linked XML files. It is possible to specify multiple paths by \
                                    repeating this option.")
        parser.add_argument("-v", "--vhdl_output",
                            dest="vhdl_output",
                            default="",
                            help="Generated VHDL output folder.")
        parser.add_argument("-x", "--xml_output",
                            dest="xml_output",
                            default="",
                            help="Generated XML output folder.")
        parser.add_argument("-b", "--bus_library",
                            dest="bus_library",
                            default="work",
                            help="Generated code will reference the specified bus VHDL library. \
                                    Default is: 'work'.")
        parser.add_argument("-s", "--slave_library",
                            dest="slave_library",
                            default="work",
                            help="Generated code will reference the specified slave VHDL library. \
                                    Default is: 'work'.")
        parser.add_argument("-n", "--bus_definition_number",
                            dest="bus_definition_number",
                            default="0",
                            help="Bus definition index. '0' = axi4lite(32bit) [default], \
                                    '1' = wishbone(16bit), \
                                    '2' = wishbone(32bit)")
        parser.add_argument("--relative_output_path",
                            dest="relative_output_path",
                            default="",
                            help="Use a relative output path, to input XML file, path for the output folder, \
                                    it overrides '-v' ('--vhdl_output') and '-x' ('--xml_output) options")
        # Specific for Slaves:
        parser.add_argument("-a", "--attributes",
                            dest="xml_help",
                            action="store_true",
                            help="Prints supported XML attributes and exits.")
        parser.add_argument("--relocate_path",
                            dest="relocate_path",
                            default="",
                            help="Relocate BRAM init file absolute path. Example: \
                                    --relocate_path 'c:\\->d:\\work'")
        parser.add_argument("-c", "--constant",
                            dest="constant",
                            action="append",
                            default=list(),
                            help="Constant passed to script. The script will substitute the specified \
                                    constant value in the XML file. Example '-c constant1=0x1234'. ")
        parser.add_argument("--tb",
                            dest="tb",
                            action="store_true",
                            help="Generate a simple test bench in the 'sim' sub-folder.")
        # Specific for ICs
        parser.add_argument("-t", "--top",
                            dest="vhdl_top",
                            default="",
                            help="Top Level IC for VHDL generation. If this option is not specified VHDL \
                                    is generated for the root node IC.")
        parser.add_argument("-r", "--vhdl_record_name",
                            dest="vhdl_record_name",
                            default="t_axi4lite_mmap_slaves",
                            help="VHDL record name containing slaves memory map. \
                                    Default is: 't_axi4lite_mmap_slaves'.")
        parser.add_argument("--zip",
                            dest="zip",
                            action="store_true",
                            help="Only generate a BRAM Hex init file containing the zip compressed \
                                    XML input file")

    @staticmethod
    def _get_args(parser):
        """Fetches the arguments from a argparse object

        Args:
            parser (obj): argparse object

        Returns:
            None

        """
        args = parser.parse_args()
        return args

    def _set_args_as_attrs(self, args):
        """Sets attributes from args.

        Args:
            args:

        returns:
            None

        """
        for arg in vars(args):
            self.logger.debug('Setting Attribute from Arg: --{arg} ({val})'
                              .format(arg=arg, val=getattr(args, arg)))
            setattr(self, arg, getattr(args, arg))

