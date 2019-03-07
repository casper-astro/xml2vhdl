# -*- coding: utf8 -*-
"""

***************
``xml2vhdl.py``
***************

`GNU General Public License v3`_ © 2015-2019 University of Oxford & contributors

.. _GNU General Public License v3: _static/LICENSE

``xml2vhdl.py`` is a module provided to automatically generate ``AXI4-Lite`` Memory Mapped locations from
``XML`` descriptions.

Todo:
    * reset record value
    * error checking
    * documentation
    * regression test

"""
import os
import helper.help
import helper.slave
import helper.xml_gen
import helper.string_io
import helper.xml_utils
import helper.arguments as arguments
import helper.bus_definition
import xml.etree.ElementTree as ET
from xml2slave import Xml2Slave
from xml2ic import Xml2Ic

import helper.customlogging as xml2vhdl_logging
logger = xml2vhdl_logging.config_logger(__name__)


def xml2vhdl_exec(options, cli_args, xml_file_name, gen_type):
    xml_file_path = helper.string_io.normalize_path(os.path.dirname(os.path.abspath(xml_file_name)))
    options.input_folder = list()
    options.input_file = [helper.string_io.normalize_path(os.path.abspath(xml_file_name))]
    if options.relative_output_path != "":
        options.vhdl_output = os.path.join(xml_file_path, options.relative_output_path)
        options.xml_output = os.path.join(xml_file_path, options.relative_output_path)
    if options.xml_output not in options.path:
        options.path.append(options.xml_output)
    if gen_type == "ic" or gen_type == "transparent_ic":
        options.vhdl_top = options.input_file[0].split(".")[0]
        xml2ic = Xml2Ic(options, cli_args)
        del xml2ic
    else:
        xml2slave = Xml2Slave(options, cli_args)
        del xml2slave
    return options.path


class Xml2VhdlGenerate(object):
    """

    """
    def __init__(self, args):
        self.logger = xml2vhdl_logging.config_logger(name=__name__, class_name=self.__class__.__name__)
        xml_list = list()
        input_folder_list = args.input_folder

        if input_folder_list:
            xml_list = helper.string_io.file_list_generate(input_folder_list, '.xml')
        for n in args.input_file:
            xml_list.append(n)

        # building dependency tree
        depend_tree = list()
        for xml in xml_list:
            tree = ET.parse(xml)
            root = tree.getroot()
            depend = {"file": xml,
                      "id": root.get('id'),
                      "depend_on": [],
                      "output": os.path.basename(xml).replace(".xml", "_output.xml")}
            for node in root.iter():
                link = node.get('link')
                hw_type = node.get('hw_type')
                if link is not None and hw_type != "netlist":
                    # do not need to compile netlists, however the XML must be in the path
                    if link not in depend['depend_on']:
                        depend['depend_on'].append(link)
            depend_tree.append(depend)

        # retrieving XML files from dependency tree bottom to up to create compile order
        compile_order = list()
        while True:
            stop = 1
            for xml in depend_tree:
                if not xml['depend_on']:
                    compile_order.append(xml)
                    depend_tree.remove(xml)
                    stop = 0
                else:
                    for file_link in xml['depend_on']:
                        for xml_done in compile_order:
                            if file_link == xml_done['output']:
                                # print "Dependency found"
                                xml['depend_on'].remove(file_link)
                                stop = 0
            if stop == 1:
                break

        # Checking if there are unresolved dependencies
        if depend_tree:
            self.logger.critical("Unresolved dependencies found: ")
            for n in depend_tree:
                self.logger.critical('\t{n}'
                                     .format(n=n))

        self.logger.info('-' * 80)
        self.logger.info("Compile order:")
        for n in compile_order:
            self.logger.info('\t{id}'
                             .format(id=n['id']))

        external_list = list()
        xml_path_list = list()
        for xml in compile_order:
            self.logger.info("Analysing: {file}"
                             .format(file=xml['file']))
            tree = ET.parse(xml['file'])
            root = tree.getroot()
            if root.get('hw_type') == "external":
                external_list.append(xml['file'])
            else:
                args.path = xml2vhdl_exec(args, list(), xml['file'], root.get('hw_type'))
        logger.info(external_list)


if __name__ == '__main__':
    Xml2VhdlGenerate(arguments.Arguments())
    logger.info('Successfully Generated VHDL from XML.')

