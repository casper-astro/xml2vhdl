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

# TODO:
#  - reset record value
#  - error checking
#  - documentation
#  - regression test
import os
import helper.help
import helper.slave
import helper.xml_gen
import helper.string_io
import helper.xml_utils
import helper.line_options
import helper.bus_definition
import xml.etree.ElementTree as ET
from xml2slave import Xml2Slave
from xml2ic import Xml2Ic


def xml2vhdl_exec(options, args, xml_file_name,type):
    xml_file_path = helper.string_io.normalize_path(os.path.dirname(os.path.abspath(xml_file_name)))
    options.input_folder = []
    options.input_file = [helper.string_io.normalize_path(os.path.abspath(xml_file_name))]
    if options.relative_output_path != "":
        options.vhdl_output = xml_file_path + "/" + options.relative_output_path
        options.xml_output = xml_file_path + "/" + options.relative_output_path
    if options.xml_output not in options.path:
        options.path.append(options.xml_output)
    if type == "ic" or type == "transparent_ic":
        options.vhdl_top = options.input_file[0].split(".")[0]
        xml2ic = Xml2Ic(options, args)
        del xml2ic
    else:
        xml2slave = Xml2Slave(options, args)
        del xml2slave
    return options.path

if __name__ == '__main__':
    parser = helper.line_options.set_parser()
    (line_options, line_args) = parser.parse_args()

    xml_list = []
    input_folder_list = line_options.input_folder
    if input_folder_list != []:
        xml_list = helper.string_io.file_list_generate(input_folder_list, '.xml')
    for n in line_options.input_file:
        xml_list.append(n)

    # building dependency tree
    depend_tree = []
    for xml in xml_list:
        tree = ET.parse(xml)
        root = tree.getroot()
        depend = {"file": xml, "id": root.get('id'), "depend_on": [], "output": os.path.basename(xml).replace(".xml", "_output.xml")}
        for node in root.iter():
            link = node.get('link')
            hw_type = node.get('hw_type')
            if link != None and hw_type != "netlist":  # do not need to compile netlists, however the XML must be in the path
                if link not in depend['depend_on']:
                    depend['depend_on'].append(link)
        depend_tree.append(depend)

    # retrieving XML files from dependency tree bottom to up to create compile order
    compile_order = []
    while True:
        stop = 1
        for xml in depend_tree:
            if xml['depend_on'] == []:
                compile_order.append(xml)
                depend_tree.remove(xml)
                stop = 0
            else:
                for file_link in xml['depend_on']:
                    for xml_done in compile_order:
                        if file_link == xml_done['output']:
                            # print "Dependency found"
                            try:
                                xml['depend_on'].remove(file_link)
                            except:
                                pass
                            stop = 0
        if stop == 1:
            break

    # Checking if there are unresolved dependencies
    if depend_tree != []:
        print "Unresolved dependencies found: "
        for n in depend_tree:
            print n
        raw_input("Press a key to continue...")

    print "Compile order: "
    for n in compile_order:
        print n['id']

    external_list = []
    xml_path_list = []
    for xml in compile_order:
        print "Analysing", xml['file']
        tree = ET.parse(xml['file'])
        root = tree.getroot()
        if root.get('hw_type') == "external":
            external_list.append(xml['file'])
        else:
            line_options.path = xml2vhdl_exec(line_options, line_args, xml['file'], root.get('hw_type'))
    print external_list
