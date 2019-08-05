# -*- coding: utf8 -*-
"""

*********************
``helper/xml_gen.py``
*********************

`GNU General Public License v3`_ © 2015-2019 University of Oxford & contributors

.. _GNU General Public License v3: _static/LICENSE

``xml_gen.py`` is a helper module providing methods for generating ``XML`` output files.

"""
import os
import re
import shutil
from . import help
from . import string_io
import xml.dom.minidom
import xml.etree.ElementTree as ET
# from xml2htmltable import xml2html

from . import customlogging as xml2vhdl_logging
logger = xml2vhdl_logging.config_logger(__name__)


# add a child to parent node
def xml_add(parent):
    sub = ET.SubElement(parent, 'node')
    return sub


# fill a node
def xml_fill_node(slave, node, key):
    root_id = slave.dict["0"]['this_id']
    this_id = slave.dict[str(key)]['complete_id']
    this_id = re.sub(r"\|.*?/", "", this_id)
    this_id = string_io.replace_const(this_id)
    this_id = this_id.replace(".", "_")
    this_id = re.sub(r"_+", "_", this_id)
    this_id = re.sub(r"_$", "", this_id)
    # print "root",root_id
    # print "this",id
    if this_id.find(root_id) == 0:
        this_id = this_id.replace(root_id + "_", "", 1)
    node.set('id',             this_id)
    if slave.dict[str(key)]['address'] is not None:
        node.set('address',        "0x" + string_io.hex_format(slave.dict[str(key)]['absolute_offset']))
    if slave.dict[str(key)]['mask'] is not None:
        node.set('mask', slave.dict[str(key)]['mask'])
    node.set('size', slave.dict[str(key)]['size'])
    node.set('permission', slave.dict[str(key)]['permission'])
    node.set('hw_rst', slave.dict[str(key)]['hw_rst'])
    node.set('description', slave.dict[str(key)]['description'])


# build output XML
def xml_build_output(slave, xml_output_folder, cmd_str, xml_out_file_name=""):
    xml_root = ET.Element('node')
    xml_root.set('id', slave.dict["0"]['this_id'])
    xml_root.set('byte_size', str(slave.get_size()))
    for x in slave.get_object(["block", "register_with_bitfield", "register_without_bitfield"]):
        this_dict = slave.dict[x]
        sub = xml_add(xml_root)
        xml_fill_node(slave, sub, x)
        if this_dict['type'] == "register_with_bitfield":
            for child in this_dict['child_key']:
                subsub = xml_add(sub)
                xml_fill_node(slave, subsub, child)
                subsub.set('id', slave.dict[str(child)]['this_id'])

    myxml = xml.dom.minidom.parseString(ET.tostring(xml_root))  # or xml.dom.minidom.parse('xmlfile.xml')
    if xml_out_file_name == "":
        xml_base_name = slave.dict["0"]['this_id'] + "_output.xml"
    else:
        xml_base_name = xml_out_file_name
    xml_file_name = string_io.normalize_path(os.path.abspath(os.path.join(xml_output_folder, xml_base_name)))
    logger.info('Processing: {xml_file_name}'
                .format(xml_file_name=xml_file_name))

    xml_file = open(xml_file_name, "w")
    xml_text = myxml.toprettyxml()
    xml_text += "<!-- This file has been automatically generated using xml2vhdl.py version " + help.get_version() + " /!-->\n"
    xml_file.write(xml_text)
    xml_file.close()

    # html_dir_name = string_io.normalize_output_folder(os.path.join(xml_output_folder, "html"))
    # html_file_name = string_io.normalize_path(os.path.join(html_dir_name,
    #                                                        xml_base_name.replace("_output.xml", "_output.html")))
    # xml2html(xml_file_name, html_file_name, cmd_str)
    # shutil.copy(os.path.join(os.path.dirname(__file__),'../regtables.css'), html_dir_name)
