# This file is part of XML2VHDL
# Copyright (C) 2015
# University of Oxford <http://www.ox.ac.uk/>
# Department of Physics
# 
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import re
import os
import sys
import copy
import help
import shutil
import string_io
import xml.dom.minidom
import xml.etree.ElementTree as ET


# create command line parameters dictionary
def get_parameters_dict(constants):
    param_dict = {}
    for c in constants:
        x = c.split("=")
        if len(x) != 2:
            print "Constant not correctly specified. Expected format is \"constant=value\""
            sys.exit(1)
        else:
            param_dict[x[0]] = x[1]
    # print param_dict
    for key in param_dict.keys():
        if key in help.allowed_attribute_value.keys():
            print "Constant has not allowed name: " + key
            sys.exit(1)
        if param_dict[key] in help.allowed_attribute_value.keys():
            print "Constant has not allowed value: " + param_dict[key]
            sys.exit(1)
    return param_dict


class XmlMemoryMap:
    def __init__(self, input_file_name, data_bus_size=32, size_indicate_bytes=0):
        self.tree = ET.parse(input_file_name)
        self.root = self.tree.getroot()
        self.data_bit_size = data_bus_size
        self.data_byte_size = data_bus_size / 8
        self.data_full_mask = 2**self.data_bit_size - 1
        if size_indicate_bytes == 0:
            self.atom = 1
        else:
            self.atom = self.data_byte_size

        # resolve link, iterate through nodes till there are no links to be resolved
    def resolve_link(self, path_list):
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
                        if os.path.isfile(string_io.normalize_path(path + link)):
                            link_found = string_io.normalize_path(path + link)
                            break
                    if link_found == "":
                        if os.path.isfile(string_io.normalize_path(link)):
                            link_found = link
                        else:
                            print "Error! Link \"" + link + "\" not found!"
                            sys.exit(1)
                    node.set('link_done', node.attrib['link'])
                    node.attrib.pop('link')
                    link_tree = ET.parse(link_found)
                    link_root = link_tree.getroot()
                    node.extend(link_root)
            if found == 0:
                break

    # write absolute path in ram init file attribute
    def write_ram_init_abs_path(self, input_file_name, path_list, relocate_path):
        for node in self.root.iter('node'):
            if 'hw_dp_ram_init_file' in node.attrib.keys():
                init_file = node.attrib['hw_dp_ram_init_file']
                abs_path = ""
                xml_path = os.path.dirname(os.path.abspath(input_file_name))
                for path in path_list:
                    if path != "":
                        path += "/"
                    if os.path.isfile(string_io.normalize_path(path + init_file)):
                        abs_path = string_io.normalize_path(os.path.abspath(string_io.normalize_path(path + init_file)))
                        break
                if abs_path == "":
                    abs_path = string_io.normalize_path(xml_path + "/" + init_file)
                if node.attrib['hw_dp_ram_init_file_check'] != "no":
                    print "Checking if BRAM init file normalize_path " + abs_path + " exists"
                    if not os.path.isfile(abs_path):
                        print "Error! BRAM init file \"" + init_file + "\" not found!"
                        sys.exit(1)
                else:
                    print "Check of BRAM init file " + abs_path + " bypassed!"
                if relocate_path != "":
                    x = relocate_path.split("->")
                    abs_path = abs_path.replace(x[0], x[1], 1)
                node.set('hw_dp_ram_init_file', os.path.abspath(abs_path))

    # resolve command line parameters
    def resolve_command_line_parameters(self, command_line_constant):
        param_dict = get_parameters_dict(command_line_constant)
        if param_dict != {}:
            for node0 in self.root.iter('node'):
                attrib_dict = node0.attrib
                for attrib in attrib_dict:
                    if attrib_dict[attrib] in param_dict.keys():
                        node0.set(attrib, param_dict[attrib_dict[attrib]])

    # exclude node with "hw_ignore" attribute set
    def exclude_hw_ignore(self):
        for node0 in self.root.iter('node'):
            if node0.get('hw_ignore') == "yes":
                for node1 in node0.iter('node'):
                    node1.set('hw_ignore', 'yes')
                    # print "ignored!"

    # unroll arrays
    def unroll_arrays(self):
        for node0 in self.root.iter('node'):
            for node1 in node0.findall('node'):
                if 'array' in node1.attrib.keys():
                    array = int(node1.attrib['array'])
                    if array > 0:
                        # print "----------------------------------------------------"
                        # print node0.get('id')
                        # print array
                        for n in range(1, array):
                            # nodex_tree = copy_tree(node1)
                            nodex = copy.deepcopy(node1)
                            # print "NODEX"
                            # print nodex
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

    # split wide register in multiple registers
    def split_wide_registers(self):
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
                            # print nodex.get('address')
                            # print nodex.get('id')
                            # print nodex.get('mask')
                            node.append(nodex)
                            slice_id += 1

                            if mask == 0:
                                break

    # OB check for blocks that are wider than data bus and resize them
    def check_wide_blocks(self):
        for node in self.root.iter('node'):
            if node.get('mask') != None and node.get('size') != None:
                if int(node.get('mask'), 16) > self.data_full_mask and int(node.get('size')) > self.atom:
                    node.set('mask', hex(self.data_full_mask).lstrip("L"))
