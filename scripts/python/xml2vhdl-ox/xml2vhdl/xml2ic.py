# -*- coding: utf8 -*-
"""

*************
``xml2ic.py``
*************

`GNU General Public License v3`_ © 2015-2019 University of Oxford & contributors

.. _GNU General Public License v3: _static/LICENSE

``xml2ic.py`` is a module provided to automatically generate ``AXI4-Lite`` Memory Mapped locations from
``XML`` descriptions, and is responsible for generating inter-connect (IC) blocks.

Todo:
    * error checking
    * documentation
    * regression test

"""
import re
import os
import sys
import zlib
import copy
import shutil
import binascii
import textwrap
import numpy as np
import xml.dom.minidom
import lxml.etree as ET
from . import helper
from .helper import arguments
from .xml2htmltable import xml2html

from .helper import customlogging as xml2vhdl_logging
logger = xml2vhdl_logging.config_logger(__name__)

version = [1.8, "Replaced optparse with argparse",
           1.7, "major refactoring",
           1.6, "merge node correction",
           1.5, "bram init file containing zip compressed xml",
           1.4, "converted sys.exit() to sys.exit(1)",
           1.3, "merge attribute implementation",
           1.2, "byte size correction",
           1.1, "ic cascade support",
           1.0, "first release"]


# specific function
def ignore_check_offset(node_x, node_y):
    """

    Args:
        node_x (???):
        node_y (???):

    Returns:
         (???):

    """
    ret = False
    if is_leaf(node_x) and node_y == node_x.getparent():
        ret = True
    elif is_leaf(node_y) and node_x == node_y.getparent():
        ret = True
    elif is_leaf(node_x) and is_leaf(node_y) and node_x.getparent() == node_y.getparent():
        ret = True
    return ret


# different function
def check_offset(root):
    """

    Args:
        root (???):

    Returns:
        None

    """
    # for node in root.findall('node'):
    for x in root.findall('node'):
        # print x.get('id')
        # print x.get('absolute_offset')
        x_address = int(x.get('absolute_offset'), 16)
        x_size = get_byte_size(x)  # int(x.get('byte_size'))
        for y in root.findall('node'):
            y_address = int(y.get('absolute_offset'), 16)
            y_size = get_byte_size(y)  # int(y.get('byte_size'))
            if x != y and ignore_check_offset(x,y) == False:
                if x_address >= y_address and x_address < y_address + y_size:
                    logger.error("conflicting addresses:")
                    logger.error("\t{}"
                                 .format(get_absolute_id(x), hex(x_address)))
                    logger.error("\t{}"
                                 .format(get_absolute_id(x), hex(y_address)))
                    sys.exit(1)
                if x_address + x_size - 1 >= y_address and x_address + x_size - 1 < y_address + y_size:
                    logger.error("conflicting addresses:")
                    logger.error("\t{}"
                                 .format(get_absolute_id(x), hex(x_address)))
                    logger.error("\t{}"
                                 .format(get_absolute_id(x), hex(y_address)))
                    sys.exit(1)


# different function
def check_offset_requirement(root):
    """

    Args:
        root (???):

    Returns:
        None

    """
    for x in root.findall('node'):
        if x.get('absolute_offset') != None:
            this_addr = int(x.get('absolute_offset'), 16)
            this_size = get_byte_size(x)
            # print x.get('id')
            # print this_addr
            # print this_size
            # print
            if this_addr & (this_size-1) != 0:
                logger.error("It should be (absolute_offset & (size-1)) = 0")
                logger.error("\t{} doesn't meet this requirement!"
                             .format(get_absolute_id(x)))
                logger.error("\t{} absolute offset is: {}"
                             .format(get_absolute_id(x), hex(this_addr)))
                logger.error("\t{} size is: {} bytes"
                             .format(get_absolute_id(x), this_size))
                sys.exit(1)


# specific function
def get_xml_file(link, path_list):
    """

    Args:
        link (???):
        path_list (list of str):

    Returns:
         (???):

    """
    link_found = ""
    for path in path_list:
        if path != "":
            path += "/"
            if os.path.isfile(helper.string_io.normalize_path(path + link)):
                link_found = helper.string_io.normalize_path(path + link)
                break
    if link_found == "":
        if os.path.isfile(helper.string_io.normalize_path(link)):
            link_found = link
        else:
            logger.error('Link "{}" Not Found!'
                         .format(link))
            sys.exit(1)
    return link_found


# specific function
def get_absolute_offset(node):
    """

    Args:
        node (obj):

    Returns:
        None

    """
    if node.get('address') != None:
        offset = int(node.get('address'), 16)
    else:
        offset = 0
    current_node = node
    while True:
        parent_node = current_node.getparent()
        if parent_node == None:
            break
        else:
            if parent_node.get('address') != None:
                offset += int(parent_node.get('address'), 16)
        current_node = parent_node
    return helper.string_io.hex_format(offset)


# specific function
def get_absolute_id(node, excluded_levels=[]):
    """

    Args:
        node (obj):
        excluded_levels (list of ???):

    Returns:
        (???):

    """
    id = node.get('id')
    current_node = node
    level = 0
    while True:
        parent_node = current_node.getparent()
        if parent_node is None:
            break
        else:
            if parent_node.get('id') != None and level not in excluded_levels:
                id = parent_node.get('id') + "." + id
        current_node = parent_node
        level += 1
    return id


# specific function
def depth(node):
    """
    Args:
        node (obj):

    Returns:
         (int):

    """
    d = 0
    while node is not None:
        d += 1
        node = node.getparent()
    return d


# specific function
def is_leaf(node):
    """

    Args:
        node (obj):

    Returns:
        (bool):

    """
    if node.findall("node") == []:
        ret = True
    else:
        ret = False
    return ret
      
def get_byte_size(node):
    """

    Args:
        node (obj):

    Returns:
        (int):

    """
    x = node.get('byte_size')
    try:
        byte_size = int(x)
    except:
        try:
            byte_size = int(x, 16)
        except:
            if node.get('byte_size') != None:
                logger.error('Unsupported byte size attribute at node "{node_id}"'
                             .format(node_id=node.get('id')))
                sys.exit(1)
            else:
                byte_size = None
    return byte_size


def get_node_size(node):
    """Return the node total size

    Args:
        node (obj):

    Returns:
         (int):

    """
    add_max = 0
    for x in node.findall('node'):
        add = int(x.get('address'), 16)
        if get_byte_size(x) == None:
            return -1
        elif get_byte_size(x) > 1:
            add += get_byte_size(x)
        if abs(add) > abs(add_max):
            add_max = add
    n = 0
    while True:
        if abs(2**n) >= abs(add_max):
            break
        else:
            n += 1
    return 2**n


def dec_check_bit(add_list, bit):
    """

    Args:
        add_list (list of ???):
        bit (???):

    Returns:
        (int): position of not-equal bit among addresses in add_list, returns ``-1``
        if there are not different bits

    """
    for b in reversed(list(range(0, bit))):
        for add0 in add_list:
            for add1 in add_list:
                if add0[b] != add1[b]:
                    return b
    return -1


def dec_get_last_bit(bit_path):
    """

    Args:
        bit_path (str):

    Returns:
        (int):

    """
    bit_list = bit_path.split("_")
    ret = bit_list[len(bit_list)-1]
    ret = re.sub(r'v.*', "", ret)
    ret = int(ret)

    logger.debug('get_last_bit input:  {input}'.format(input=ret))
    logger.debug('get_last_bit output: {output}'.format(output=bit_path))

    if ret == -1:
        ret = 32
    return ret


def dec_route_add(tree_dict):
    """

    Args:
        tree_dict (dict):

    Returns:
        tuple: tuple containing:
                * int: 1 to indicate ``done`` complete.
                * dict:

    """
    done = 0
    logger.debug('tree_dict: {tree_dict}'.format(tree_dict=tree_dict))
    for path in list(tree_dict.keys()):
        add_list = tree_dict[path]
        b = dec_check_bit(add_list,dec_get_last_bit(path))
        if b > -1:
            list_0 = []
            list_1 = []
            for add in add_list:
                bit_dict = {}
                if add[b] == 0:
                    list_0.append(add)
                else:
                    list_1.append(add)
            logger.debug('{path} XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'.format(path=path))
            logger.debug('{add_list_len}'.format(add_list_len=len(add_list)))
            logger.debug('{list_0_len}'.format(list_0_len=len(list_0)))
            logger.debug('{list_1_len}'.format(list_1_len=len(list_1)))
            logger.debug('{list_01_len}'.format(list_01_len=len(list_0) + len(list_1)))
            bit_dict["0"] = list_0
            bit_dict["1"] = list_1
            tree_dict[path + "_" + str(b) + "v0"] = list_0
            tree_dict[path + "_" + str(b) + "v1"] = list_1
            tree_dict[path] = []
            done = 1

    logger.debug('tree_dict: {tree_dict}'.format(tree_dict=tree_dict))
    return done, tree_dict


def get_decoder_mask(address_list):
    """

    Args:
        address_list (list of int):

    Returns:
        (dict):

    """
    # addresses = []
    # for x in get_object(["block","register_with_bitfield","register_without_bitfield"]):
        # addresses.append(global_dict[str(x)]['addressable'])
    addresses = address_list

    add_num = len(addresses)
    logger.info('Addresses are: {}'
                .format(add_num))
    baddr = np.zeros((add_num, 32), dtype=int)
    decode_dict = {}
    tree_dict = {}
   
    # building address array
    a = 0
    for add in sorted(addresses):
        bit_mask = 0x80000000
        for n in range(32):
            if add & bit_mask != 0:
                baddr[a, 31-n] = 1
            bit_mask = bit_mask >> 1
        a = a + 1

    logger.debug('baddr: {baddr}'.format(baddr=baddr))
   
    tree_dict["-1v0"] = baddr
   
    while True:
        done, tree_dict = dec_route_add(tree_dict)
        if done == 0:
            break
  
    for bit_path in tree_dict:
        if tree_dict[bit_path] != []:
            add_bits = tree_dict[bit_path][0]
            add = ""
            for n in reversed(list(range(32))):
                add = add + str(add_bits[n])
            bit_list = bit_path.split("_")
            mask = 0
            for bit in bit_list:
                x = int(re.sub(r'v.*', "", bit))
                if x >= 0:
                    mask = mask | (1 << x)
            decode_dict[str(int(add, 2))] = mask

    logger.debug('Decode Dict:')
    for address in sorted(decode_dict.keys()):
        logger.debug('\taddr:')
        logger.debug('\t{address}'.format(address=address))
        logger.debug('\tmask:')
        logger.debug('\t{mask}'.format(mask=hex(decode_dict[address])))

    return decode_dict


class Xml2Ic:
    """

    """
    def __init__(self, options, args):
        self.logger = xml2vhdl_logging.config_logger(name=__name__, class_name=self.__class__.__name__)
        bus = helper.bus_definition.BusDefinition(int(options.bus_definition_number))

        self.logger.info('-' * 80)
        self.logger.info('xml2ic.py version {}"'
                         .format(version[0]))

        self.logger.info('Processing Paths:')
        for n in options.path:
            logger.info('\t{path}'
                        .format(path=os.path.abspath(n)))

        cmd_str = ""
        for k in sys.argv:
            if k[0] == "-":
                cmd_str += "\n"
            cmd_str += k + " "
        # print cmd_str

        if options.log is True:
            self.logger.info('-' * 80)
            self.logger.info("History Log:")
            self.logger.info('-' * 80)
            for n in range(len(version)//2):
                self.logger.info("version {}"
                                 .format(version[2*n]))
                dedented_text = textwrap.dedent(re.sub(r" +", ' ', version[2*n+1])).strip()
                self.logger.info(textwrap.fill(dedented_text, width=80))
                self.logger.info('-' * 80)
            sys.exit()

        input_file_list = []
        input_folder_list = options.input_folder
        if input_folder_list != []:
            input_file_list = helper.string_io.file_list_generate(input_folder_list, '.xml')
        for n in options.input_file:
            input_file_list.append(n)

        if args != []:
            self.logger.error("Unexpected argument: {}"
                              .format(args[0]))
            self.logger.error("-h for help")
            sys.exit(1)

        if input_file_list == []:
            self.logger.error("No input file!")
            self.logger.error("-h for help")
            sys.exit(1)

        for input_file_name in input_file_list:
            # input_file_name = options.input_file
            vhdl_output_folder = helper.string_io.normalize_output_folder(options.vhdl_output)
            if options.xml_output == "":
                output_file_name = input_file_name
            else:
                output_file_name = helper.string_io.normalize_path(input_file_name).split("/")[-1]
            xml_output_folder = os.path.abspath(helper.string_io.normalize_output_folder(options.xml_output))

            tree = ET.parse(input_file_name)
            root = tree.getroot()

            if options.zip == True:
                myxml = xml.dom.minidom.parseString(ET.tostring(root))  # or xml.dom.minidom.parse('xmlfile.xml')
                myxml = myxml.toprettyxml()
                myxml = re.sub(r"\t", "   ", myxml)
                myxml = re.sub(r"> *", ">", myxml)
                myxml = re.sub(r"\n\s*\n", "\n\n", myxml)
                myxml = re.sub("\n\n", "\n", myxml)

                xml_file_name = output_file_name
                xml_file_name = re.sub(r".*?\.", "", xml_file_name[::-1])[::-1]
                xml_file_name = xml_file_name + "_output.xml"

                xml_compressed = zlib.compress(myxml.encode('utf8'))
                xml_compressed = binascii.hexlify(xml_compressed)
                xml_compressed = helper.string_io.hex_format(len(xml_compressed)/2) + xml_compressed
                bram_init = ""
                if len(xml_compressed) % 8 != 0:
                    xml_compressed += "0"*(8-(len(xml_compressed) % 8))
                for n in range(0, len(xml_compressed)/8):
                    word = xml_compressed[8*n:8*n+8]
                    bram_init += word + "\n"
                bram_init_file_name = re.sub(r".*?\.", "", xml_file_name[::-1])[::-1]
                bram_init_file_name = bram_init_file_name + ".hex"
                bram_init_file = open(helper.string_io.normalize_path(os.path.join(xml_output_folder,
                                                                                   bram_init_file_name)), "w")
                bram_init_file.write(bram_init)
                bram_init_file.close()
                self.logger.info("Done!")
                self.logger.info('-' * 80)
                sys.exit()

            # resolve links

            while True:
                todo = 0
                for node in root.iter('node'):
                    if 'hw_type' in list(node.attrib.keys()):
                        hw_type = node.attrib['hw_type']
                    else:
                        hw_type = ""
                    if 'link' in list(node.attrib.keys()) and not ('link_done' in list(node.attrib.keys())):
                        link = get_xml_file(node.attrib['link'], options.path)
                        link_tree = ET.parse(link)
                        link_root = link_tree.getroot()
                        # if hw_type == "transparent_ic":
                        #     for child in link_root:
                        #         node.extend(child)
                        # else:
                        node.extend(link_root)
                        if node.get("hw_type") == "transparent_ic":
                            node.set("hw_type", "transparent_ic_to_merge")
                        elif link_root.get("hw_type") == "ic":
                            node.set("hw_type", "ic_to_merge")
                        if link_root.get('byte_size') != None:
                            node.set('byte_size', link_root.get('byte_size'))
                        node.set('link_done', node.attrib['link'])
                        node.attrib.pop('link')
                        todo = 1
                if todo == 0:
                    break

            # while True:
            #     todo = 0
            #     for node in root.iter('node'):
            #         if 'hw_type' in node.attrib.keys():
            #             hw_type = node.attrib['hw_type']
            #         else:
            #             hw_type = ""
            #         if 'link' in node.attrib.keys() and not ('link_done' in node.attrib.keys()):
            #             link = get_xml_file(node.attrib['link'], options.path)
            #             link_tree = ET.parse(link)
            #             link_root = link_tree.getroot()
            #
            #             node.extend(link_root)
            #             node.set("hw_type", "ic_to_merge")
            #             if link_root.get('byte_size') != None:
            #                 node.set('byte_size', link_root.get('byte_size'))
            #             node.set('link_done', node.attrib['link'])
            #             node.attrib.pop('link')
            #             todo = 1
            #
            #
            #             # if hw_type == "transparent_ic":
            #             #     print link_root.get("id")
            #             #     raw_input()
            #             #     for child in link_root:
            #             #         print child
            #             #
            #             #         xmlaaa = xml.dom.minidom.parseString(ET.tostring(child))  # or xml.dom.minidom.parse('xmlfile.xml')
            #             #         pretty_xml_as_string = xmlaaa.toprettyxml()
            #             #
            #             #
            #             #
            #             #         print pretty_xml_as_string
            #             #         raw_input()
            #             #
            #             #         node.extend(child)
            #             # else:
            #             #     node.extend(link_root)
            #             #     node.set("hw_type", "ic_to_merge")
            #             #
            #             # if link_root.get('byte_size') != None:
            #             #     node.set('byte_size', link_root.get('byte_size'))
            #             # node.set('link_done', node.attrib['link'])
            #             # node.attrib.pop('link')
            #             # todo = 1
            #     if todo == 0:
            #         break

            # write Address and absolute id and absolute offset
            for node in root.iter('node'):
                if node != root:
                    absolute_id = get_absolute_id(node)
                    node.set('absolute_id', absolute_id)
                    absolute_offset = get_absolute_offset(node)
                    node.set('absolute_offset', absolute_offset)
                if node.get('address') != None:
                    node.set('address', "0x" + helper.string_io.hex_format(int(node.get('address'), 16)))

            # check byte size on first level child nodes
            for node in root.findall("node"):
                if node != root:
                    # print node.get('absolute_id')
                    # print node.get('absolute_offset')
                    if node.get('byte_size') == None and node.get('size') != None:
                        node.set('byte_size', str(int(node.get('size')) * 4))
                    elif node.get('byte_size') == None:
                        self.logger.error("Unknown byte size for node: {node}"
                                          .format(node=absolute_id))
                        self.error('Exiting...')
                        sys.exit(1)

            check_offset(root)
            check_offset_requirement(root)

            root.set('byte_size', str(get_node_size(root)))

            #
            # VHDL generation
            #
            vhdl_start_node = None
            if options.vhdl_top != "":
                self.logger.info('Searching for VHDL Top-Level: {top_level}'
                                 .format(top_level=options.vhdl_top))
                for node in root.iter('node'):
                    self.logger.debug('node: {node}'.format(node=node.get('absolute_id')))
                    if node.get('absolute_id') == options.vhdl_top:
                        vhdl_start_node = node
                        self.logger.info("VHDL Top-Level found!")
                        break
                if root.get('id') == options.vhdl_top:
                    vhdl_start_node = root

                if vhdl_start_node is None:
                    self.logger.warning('VHDL Top-Level not found: {top_level}'
                                        .format(top_level=options.vhdl_top))

                    vhdl_start_node = root
                    options.vhdl_top = root.get('id')

                    self.logger.warning("\tUsing root node: {node}"
                                        .format(node=options.vhdl_top))
                    # self.logger.error('Exiting...')
                    # sys.exit(1)
                else:
                    self.logger.info("VHDL top level found!")

                vhdl_id = []
                vhdl_address = []
                for node in vhdl_start_node.findall('node'):
                    vhdl_id.append(node.get('id'))
                    vhdl_address.append(int(node.get('address'), 16))
                vhdl_decoder_mask = get_decoder_mask(vhdl_address)
                max_len = helper.string_io.get_max_len(vhdl_id)
                snippet = "type " + options.vhdl_record_name + " is (\n"
                for address in sorted(vhdl_address):
                    id = vhdl_id[vhdl_address.index(address)]
                    snippet += "\t" + "id_" + id + helper.string_io.add_space(id, max_len) + ",\n"
                snippet = snippet[0:-2]
                snippet += "\n);\n"
                snippet = helper.string_io.indent(snippet, 1)
                snippet = re.sub(r"\t", "   ", snippet)
                slave_type = snippet

                snippet = "("
                for address in sorted(vhdl_address):
                    snippet += "X\"" + helper.string_io.hex_format(address) + "\","
                snippet = snippet[0:-1]
                snippet += ")"
                slave_base_addr = snippet

                snippet = "("
                for address in sorted(vhdl_address):
                    snippet += "X\"" + helper.string_io.hex_format(vhdl_decoder_mask[str(address)]) + "\","
                snippet = snippet[0:-1]
                snippet += ")"
                slave_mask = snippet
                #
                # MMAP PACKAGE
                #
                vhdl_package_name = bus.name + "_" + options.vhdl_top + "_mmap_pkg"

                vhdl_template = helper.string_io.read_template_file(os.path.dirname(os.path.abspath(__file__)) + "/template/" + "xml2vhdl" + "_mmap.template.vhd")
                vhdl_str = vhdl_template
                vhdl_str = vhdl_str.replace("<BUS>", bus.name)
                vhdl_str = vhdl_str.replace("<BUS_LIBRARY>", options.bus_library)
                vhdl_str = vhdl_str.replace("<TOP_LEVEL>", options.vhdl_top)
                vhdl_str = vhdl_str.replace("<VHDL_RECORD>", options.vhdl_record_name)
                vhdl_str = re.sub("<PKG_NAME>", vhdl_package_name, vhdl_str)
                vhdl_str = re.sub("<SLAVE_TYPE>", slave_type, vhdl_str)
                vhdl_str = re.sub("<SLAVE_BASE_ADDR>", slave_base_addr, vhdl_str)
                vhdl_str = re.sub("<SLAVE_MASK>", slave_mask, vhdl_str)

                vhdl_file_name = vhdl_package_name + ".vhd"
                helper.string_io.write_vhdl_file(vhdl_file_name, vhdl_output_folder, vhdl_str)
                #
                # IC PACKAGE
                #
                vhdl_template = helper.string_io.read_template_file(os.path.dirname(os.path.abspath(__file__)) + "/template/" + bus.name + "/xml2vhdl_ic_pkg.template.vhd")
                vhdl_str = vhdl_template
                vhdl_str = vhdl_str.replace("<BUS>", bus.name)
                vhdl_str = vhdl_str.replace("<BUS_LIBRARY>", options.bus_library)
                vhdl_str = vhdl_str.replace("<TOP_LEVEL>", options.vhdl_top)

                vhdl_file_name = bus.name + "_" + options.vhdl_top + "_ic_pkg.vhd"
                helper.string_io.write_vhdl_file(vhdl_file_name, vhdl_output_folder, vhdl_str)
                #
                # IC
                #
                vhdl_template = helper.string_io.read_template_file(os.path.dirname(os.path.abspath(__file__)) + "/template/" + bus.name + "/xml2vhdl_ic.template.vhd",)
                vhdl_str = vhdl_template
                vhdl_str = vhdl_str.replace("<BUS>", bus.name)
                vhdl_str = vhdl_str.replace("<BUS_CLK>", bus.clock)
                vhdl_str = vhdl_str.replace("<BUS_RST>", bus.reset)
                vhdl_str = vhdl_str.replace("<BUS_RST_VAL>", bus.reset_val)
                vhdl_str = vhdl_str.replace("<BUS_LIBRARY>", options.bus_library)
                vhdl_str = vhdl_str.replace("<DSN_LIBRARY>", options.slave_library)
                vhdl_str = vhdl_str.replace("<TOP_LEVEL>", options.vhdl_top)

                vhdl_file_name = bus.name + "_" + options.vhdl_top + "_ic.vhd"
                helper.string_io.write_vhdl_file(vhdl_file_name, vhdl_output_folder, vhdl_str)
                #
                # EXAMPLE
                #
                slave_inst = ""
                for id in vhdl_id:
                    snippet = "\n" + bus.name + "_" + id + "_inst: entity work." + bus.name + "_" + id + "\n"
                    snippet += "port map(\n"
                    snippet += "\t" + "<BUS_CLK> => <BUS_CLK>,\n"
                    snippet += "\t" + "<BUS_RST> => <BUS_RST>,\n"
                    snippet += "\t" + "<BUS>_mosi => axi4lite_mosi_arr(axi4lite_mmap_get_id(id_" + id + ")),\n"
                    snippet += "\t" + "<BUS>_miso => axi4lite_miso_arr(axi4lite_mmap_get_id(id_" + id + "))\n"
                    snippet += ");\n"
                    slave_inst += snippet

                slave_inst = helper.string_io.indent(slave_inst,1)
                slave_inst = re.sub(r"\t", "   ", slave_inst)

                vhdl_template = helper.string_io.read_template_file(os.path.dirname(os.path.abspath(__file__)) + "/template/" + "xml2vhdl" + "_example.template.vhd")
                vhdl_str = vhdl_template
                vhdl_str = re.sub("<SLAVE_INST>", slave_inst,vhdl_str)
                vhdl_str = vhdl_str.replace("<BUS>", bus.name)
                vhdl_str = vhdl_str.replace("<BUS_LIBRARY>", options.bus_library)
                vhdl_str = vhdl_str.replace("<DSN_LIBRARY>", options.slave_library)
                vhdl_str = vhdl_str.replace("<BUS_CLK>", bus.clock)
                vhdl_str = vhdl_str.replace("<BUS_RST>", bus.reset)
                vhdl_str = vhdl_str.replace("<TOP_LEVEL>", options.vhdl_top)
                vhdl_str = re.sub("<PKG_NAME>", vhdl_package_name, vhdl_str)
                vhdl_str = re.sub("<SLAVE_TYPE>", snippet, vhdl_str)
                #print vhdl_str

                vhdl_file_name = bus.name + "_" + options.vhdl_top + "_example.vho"
                helper.string_io.write_vhdl_file(vhdl_file_name, vhdl_output_folder, vhdl_str)
            #
            # XML generation
            # Merge nodes. It merges nodes flattening the XML hierarchical level.
            #
            for node in root.findall('node'):  # find all children node
                if node.get('hw_type') == "ic_to_merge":
                    # node_id = node.get('id')
                    for x in node.findall('node'):
                        id = x.get('id')
                        add = int(x.get('address'), 16)
                        merge_root = copy.deepcopy(x)
                        for child in merge_root.iter('node'):
                            if child.get('address') != None:
                                child.set('id', id + "_" + child.get('id'))
                                child.set('address', "0x" + helper.string_io.hex_format(int(child.get('address'), 16) + add))
                            abs_id = child.get("absolute_id").replace(".", "^", depth(x))  # depth is number of nodes to get to the root
                            abs_id = abs_id.replace("^", ".", depth(x) - 1)
                            abs_id = abs_id.replace("^", "_", 1)
                            child.set('absolute_id', abs_id)
                        node.remove(x)
                        node.extend(merge_root)
                        node.set('hw_type', node.get('hw_type').replace("to_merge", "merged"))
                elif node.get('hw_type') == "transparent_ic_to_merge":
                    node_id = node.get('id')
                    for x in node.findall('node'):
                        id = x.get('id')
                        add = int(node.get('address'), 16)
                        merge_root = copy.deepcopy(x)
                        merge_root.set('address', "0x" + helper.string_io.hex_format(int(merge_root.get('address'), 16) + add))
                        for child in merge_root.iter('node'):
                            abs_id = child.get("absolute_id")
                            abs_id = abs_id.replace("." + node_id + ".", ".")
                            child.set('absolute_id', abs_id)
                        root.append(merge_root)
                    root.remove(node)
                    node.set('hw_type', node.get('hw_type').replace("to_merge", "merged"))

            # setting root's children nodes as merge-able:
            root.set('hw_type', "ic")

            myxml = xml.dom.minidom.parseString(ET.tostring(root))  # or xml.dom.minidom.parse('xmlfile.xml')
            myxml = myxml.toprettyxml()
            myxml = re.sub(r"\t", "   ", myxml)
            myxml = re.sub(r"> *", ">", myxml)
            myxml = re.sub(r"\n\s*\n", "\n\n", myxml)
            myxml = re.sub("\n\n", "\n", myxml)

            myxml += "<!-- This file has been automatically generated using xml_map_gen.py version " + str(version[0]) + " /!-->\n"

            xml_base_name = output_file_name
            xml_base_name = re.sub(r".*?\.", "", xml_base_name[::-1])[::-1]
            xml_base_name = xml_base_name + "_output.xml"
            xml_file_name = os.path.abspath(helper.string_io.normalize_path(os.path.join(xml_output_folder,
                                                                                         xml_base_name)))
            self.logger.info('Writing XML output file: {xml_output_file}'
                             .format(xml_output_file=xml_file_name))
            xml_file = open(xml_file_name, "w")
            xml_file.write(myxml)
            xml_file.close()

            html_dir_name = helper.string_io.normalize_output_folder(xml_output_folder + "/html")
            html_file_name = helper.string_io.normalize_path(os.path.join(html_dir_name,
                                                                          xml_base_name.replace("_output.xml", "_output.html")))
            self.logger.info('Generating HTML Tables from: {}'
                             .format(xml_file_name))
            xml2html(xml_file_name, html_file_name, cmd_str)
            shutil.copy(os.path.join(os.path.dirname(__file__), 'regtables.css'), html_dir_name)

            self.logger.info('Generated HTML File: {}'
                             .format(html_file_name))
            xml_compressed = zlib.compress(myxml.encode('utf8'))
            #xml_compressed = binascii.hexlify(xml_compressed)
            xml_compressed = helper.string_io.hex_format(len(xml_compressed)//2) + xml_compressed.hex()
            bram_init = ""
            if len(xml_compressed) % 8 != 0:
                xml_compressed += "0"*(8-(len(xml_compressed) % 8))
            for n in range(0, len(xml_compressed)//8):
                word = xml_compressed[8*n:8*n+8]
                bram_init += word + "\n"
            bram_init_file_name = re.sub(r".*?\.", "", xml_base_name[::-1])[::-1]
            bram_init_file_name = bram_init_file_name + ".hex"
            bram_init_file = open(helper.string_io.normalize_path(os.path.join(xml_output_folder,
                                                                               bram_init_file_name)), "w")
            bram_init_file.write(bram_init)
            bram_init_file.close()

            self.logger.info("Done!")
            self.logger.info('-' * 80)


#
#
# MAIN STARTS HERE
#
#
if __name__ == '__main__':
    args = arguments.Arguments()
    xml2ic_inst = Xml2Ic(args, list())
    del xml2ic_inst
