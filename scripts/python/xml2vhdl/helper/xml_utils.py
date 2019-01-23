# -*- coding: utf8 -*-
"""

***********************
``helper/xml_utils.py``
***********************

`GNU General Public License v3`_ © 2015-2019 University of Oxford & contributors

.. _GNU General Public License v3: _static/LICENSE

``xml_utils.py`` is a helper module providing methods and classes for handling ``XML`` files.

"""
# import re
import os
import sys
import copy
import help
# import shutil
import string_io
# import xml.dom.minidom
import xml.etree.ElementTree as ET

import customlogging as xml2vhdl_logging
logger = xml2vhdl_logging.config_logger(__name__)


def get_parameters_dict(constants):
    """create command line parameters dictionary

    Args:
        constants (???):

    Returns:
         (dict):

    """
    param_dict = {}
    for c in constants:
        x = c.split("=")
        if len(x) != 2:
            logger.error('Constant not correctly specified. Expected format is "constant=value"')
            logger.error('Exiting...')
            sys.exit(1)
        else:
            param_dict[x[0]] = x[1]
    # print param_dict
    for key in param_dict.keys():
        if key in help.allowed_attribute_value.keys():
            logger.error('Constant has not allowed name: {key}'
                         .format(key=key))
            logger.error('Exiting...')
            sys.exit(1)
        if param_dict[key] in help.allowed_attribute_value.keys():
            logger.error('Constant has not allowed value: {value}'
                         .format(value=param_dict[key]))
            logger.error('Exiting...')
            sys.exit(1)
    return param_dict


class XmlMemoryMap:
    """

    """
    def __init__(self, input_file_name, data_bus_size=32, size_indicate_bytes=0):
        self.logger = xml2vhdl_logging.config_logger(name=__name__, class_name=self.__class__.__name__)
        self.tree = ET.parse(input_file_name)
        self.root = self.tree.getroot()
        self.data_bit_size = data_bus_size
        self.data_byte_size = data_bus_size / 8
        self.data_full_mask = 2**self.data_bit_size - 1
        if size_indicate_bytes == 0:
            self.atom = 1
        else:
            self.atom = self.data_byte_size

    def resolve_link(self, path_list):
        """Resolve links

        Iterate through nodes till there are no links to be resolved

        Args:
            path_list (list of str):

        Returns:
             None

        """
        while True:
            found = 0
            for node in self.root.iter('node'):
                if 'link' in node.attrib.keys():
                    found = 1
                    link = node.attrib['link']
                    link_found = ""
                    for path in path_list:
                        if path != "":
                            path += "/"
                        if os.path.isfile(string_io.normalize_path(os.path.join(path, link))):
                            link_found = string_io.normalize_path(os.path.join(path, link))
                            break
                    if link_found == "":
                        if os.path.isfile(string_io.normalize_path(link)):
                            link_found = link
                        else:
                            self.logger.error('Link "{link}" not found!'
                                              .format(link=link))
                            self.logger.error('Exiting...')
                            sys.exit(1)
                    node.set('link_done', node.attrib['link'])
                    node.attrib.pop('link')
                    link_tree = ET.parse(link_found)
                    link_root = link_tree.getroot()
                    node.extend(link_root)
            if found == 0:
                break

    def write_ram_init_abs_path(self, input_file_name, path_list, relocate_path):
        """write absolute path in ram init file attribute

        Args:
            input_file_name (str):
            path_list (list of str):
            relocate_path (str):

        Returns:
            None

        """
        for node in self.root.iter('node'):
            if 'hw_dp_ram_init_file' in node.attrib.keys():
                init_file = node.attrib['hw_dp_ram_init_file']
                abs_path = ""
                xml_path = os.path.dirname(os.path.abspath(input_file_name))
                for path in path_list:
                    if path != "":
                        path += "/"
                    if os.path.isfile(string_io.normalize_path(os.path.join(path, init_file))):
                        abs_path = string_io.normalize_path(os.path.abspath(string_io.normalize_path(os.path.join(path, init_file))))
                        break
                if abs_path == "":
                    abs_path = string_io.normalize_path(os.path.join(xml_path, init_file))
                if node.attrib['hw_dp_ram_init_file_check'] != "no":
                    self.logger.info('Checking if BRAM init file exists: {abs_path}'
                                     .format(abs_path=abs_path))
                    if not os.path.isfile(abs_path):
                        self.logger.error('BRAM init file not found: {init_file}'
                                          .format(init_file=init_file))
                        self.logger.error('Exiting...')
                        sys.exit(1)
                else:
                    self.logger.warning('Check of BRAM init file bypassed: {abs_path}'
                                        .format(abs_path=abs_path))
                if relocate_path != "":
                    x = relocate_path.split("->")
                    abs_path = abs_path.replace(x[0], x[1], 1)
                node.set('hw_dp_ram_init_file', os.path.abspath(abs_path))

    def resolve_command_line_parameters(self, command_line_constant):
        """Resolve command line parameters

        Args:
            command_line_constant (???):

        Returns:
            None

        """
        param_dict = get_parameters_dict(command_line_constant)
        if param_dict != {}:
            for node0 in self.root.iter('node'):
                attrib_dict = node0.attrib
                for attrib in attrib_dict:
                    if attrib_dict[attrib] in param_dict.keys():
                        node0.set(attrib, param_dict[attrib_dict[attrib]])

    def exclude_hw_ignore(self):
        """Exclude node with "hw_ignore" attribute set

        :Returns:
            None

        """
        for node0 in self.root.iter('node'):
            if node0.get('hw_ignore') == "yes":
                for node1 in node0.iter('node'):
                    node1.set('hw_ignore', 'yes')
                    # print "ignored!"

    def unroll_arrays(self):
        """Unroll arrays

        Returns:
            None

        """
        for node0 in self.root.iter('node'):
            for node1 in node0.findall('node'):
                if 'array' in node1.attrib.keys():
                    array = int(node1.attrib['array'])
                    if array > 0:
                        self.logger.debug('-' * 80)
                        self.logger.debug('{id}'.format(id=node0.get('id')))
                        self.logger.debug('{array}'.format(array=array))
                        for n in range(1, array):
                            # nodex_tree = copy_tree(node1)
                            nodex = copy.deepcopy(node1)
                            self.logger.debug('{nodex}'.format(nodex=nodex))
                            nodex.set('array_idx', str(n))
                            nodex.set('id', node1.get('id') + "<<" + str(n) + ">>")
                            nodex.set('address', hex(int(node1.get('address'), 16) + int(node1.get('array_offset'), 16) * n))
                            for subnode in nodex.findall('node'):
                                subnode.set('id', "|" + subnode.get('id') + "/*")
                            node0.append(nodex)
                        node1.set('array_idx', '0')
                        node1.set('id', node1.get('id') + "<<0>>")
                        for subnode in node1.findall('node'):
                            subnode.set('id', "|" + subnode.get('id') + "/")

    def split_wide_registers(self):
        """Split wide register in multiple registers

        Returns:
            None:

        """
        for node in self.root.iter('node'):
            for child in node:
                if child.get('mask') != None:
                    slice_id = 0
                    mask = int(child.get('mask'), 16)
                    orig_id = child.get('id')
                    hw_rst = child.get('hw_rst')
                    try:
                        hw_rst = int(hw_rst, 16)
                    except:
                        pass
                    if (mask >> self.data_bit_size) != 0:
                        while True:
                            nodex = copy.deepcopy(child)
                            nodex.set('id', orig_id + "_$s" + str(slice_id) + "_split$")
                            nodex.set('address', hex(int(child.get('address'), 16) + self.data_byte_size*(slice_id)))
                            nodex.set('mask', hex(mask & self.data_full_mask).rstrip("L"))
                            nodex.set('split', str(slice_id))
                            mask >>= self.data_bit_size
                            if mask == 0:
                                nodex.set('last_split', "1")
                            if hw_rst is None:
                                pass
                            elif hw_rst == "no":
                                nodex.set('hw_rst', hw_rst)
                            elif type(hw_rst) is not str:
                                nodex.set('hw_rst', hex(hw_rst & self.data_full_mask).rstrip("L"))
                                hw_rst >>= self.data_bit_size
                            else:
                                nodex.set('hw_rst', hw_rst)  # generic
                            self.logger.debug('Address: {address}'.format(address=nodex.get('address')))
                            self.logger.debug('ID:      {id}'.format(id=nodex.get('id')))
                            self.logger.debug('Mask:    {mask}'.format(mask=nodex.get('mask')))
                            node.append(nodex)
                            slice_id += 1

                            if mask == 0:
                                break

    def check_wide_blocks(self):
        """OB check for blocks that are wider than data bus and resize them

        Returns:
            None

        """
        for node in self.root.iter('node'):
            if node.get('mask') != None and node.get('size') != None:
                if int(node.get('mask'), 16) > self.data_full_mask and int(node.get('size')) > self.atom:
                    node.set('mask', hex(self.data_full_mask).lstrip("L"))
