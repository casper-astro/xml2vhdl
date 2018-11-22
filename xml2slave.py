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
import re
import sys
import math
import numpy as np
import helper.help
import helper.slave
import helper.xml_gen
import helper.string_io
import helper.xml_utils
import helper.line_options
import helper.bus_definition
from optparse import OptionParser

class Xml2Slave:
    def __init__(self, options, args):
        bus = helper.bus_definition.BusDefinition(int(options.bus_definition_number))
        print "Selected bus:"
        print "    name: " + str(bus.name)
        print "    width: " + str(bus.data_bit_size) + "bit"

        print "xml2vhdl.py version " + helper.help.get_version()

        cmd_str = ""
        for k in sys.argv:
            if k[0] == "-":
                cmd_str += "\n"
            cmd_str += k + " "

        if options.xml_help:
            helper.help.print_help()
            sys.exit()

        if options.log:
            helper.help.print_log()
            sys.exit()

        if options.xml_output == "":
            options.xml_output = options.vhdl_output

        vhdl_output_folder = helper.string_io.normalize_output_folder(options.vhdl_output)
        xml_output_folder = helper.string_io.normalize_output_folder(options.xml_output)
        if options.tb:
            sim_output_folder = helper.string_io.normalize_output_folder(vhdl_output_folder + "sim")

        input_file_list = []
        input_folder_list = options.input_folder
        if input_folder_list != []:
            input_file_list = helper.string_io.file_list_generate(input_folder_list, '.xml')
        for n in options.input_file:
            input_file_list.append(n)

        if args != []:
            print "Unexpected argument: ", args[0]
            print "-h for help"
            print "-a for supported XML attributes"
            sys.exit(1)

        if input_file_list == []:
            print "No input file!"
            print "-h for help"
            print "-a for supported XML attributes"
            sys.exit(1)

        for input_file_name in input_file_list:
            print "-----------------------------------------------------------------"
            print "Analysing \"" + input_file_name + "\""

            # XML processing
            xml_mm = helper.xml_utils.XmlMemoryMap(input_file_name, data_bus_size=bus.data_bit_size)
            xml_mm.resolve_link(options.path)
            xml_mm.write_ram_init_abs_path(input_file_name, options.path, options.relocate_path)
            xml_mm.resolve_command_line_parameters(options.constant)
            xml_mm.check_wide_blocks()
            xml_mm.exclude_hw_ignore()
            xml_mm.unroll_arrays()
            xml_mm.split_wide_registers()

            # dictionary processing
            slave = helper.slave.Slave(data_bus_size=bus.data_bit_size, size_indicate_bytes=bus.size_indicate_bytes)
            slave.populate_dict(xml_mm.root)
            print "Hierarchical levels are " + str(slave.get_hierarchical_level_number())
            print "Nodes are " + str(slave.get_node_number())
            print "Checking reserved words..."
            slave.check_reserved_words()
            print "fill_child..."
            slave.fill_child()
            print "fill_complete_id..."
            slave.fill_complete_id()
            print "fill_absolute_offset..."
            slave.fill_absolute_offset()
            print "fill_type..."
            slave.fill_type()
            print "fill_addressable..."
            slave.fill_addressable()
            print "check_offset..."
            slave.check_offset()
            slave.check_address_requirement()
            print "check_bitfield..."
            slave.check_bitfield()
            print "fill_decoder_mask..."
            slave.fill_decoder_mask()
            print "propagate_reset_value..."
            slave.propagate_reset_value()
            print "default_reset..."
            slave.default_reset()
            reset_generics_dict = slave.get_reset_generics()
            print "default_permission..."
            slave.default_permission()
            max_id_len = slave.get_max_id_len()
            if slave.get_nof_not_ignored_registers() == 0:
                nof_registers_block = 0
            else:
                nof_registers_block = 1
            nof_memory_block = slave.get_nof_not_ignored_blocks()
            nof_hw_dp_ram = 0
            #
            # XML GENERATION
            #
            helper.xml_gen.xml_build_output(slave, xml_output_folder, cmd_str, os.path.basename(input_file_name).replace(".xml", "_output.xml"))
            #
            # VHDL GENERATION
            #
            if nof_memory_block == 0 and nof_registers_block == 0:
                print "No VHDL to generate, no valid nodes are present!"
                print "Done!"
                print
                return # sys.exit(0)
            #
            # RECORDS and ARRAY
            #
            records = ""
            snippet = ""
            for node_id in slave.reverse_dict_key:
                node_dict = slave.dict[node_id]
                if node_dict['child_key']:
                    if node_dict['array']:
                        if node_dict['array_idx'] == "0":
                            if node_dict['complete_id'].find("*") == -1:
                                snippet = "\t" + "type t_" + bus.bus_prefix + node_dict['complete_id'].replace(".", "_") + " is array (0 to " + node_dict['array'] + "-1) of "
                                for child in [node_dict['child_key'][0]]:
                                    child_dict = slave.dict[str(child)]
                                    if not child_dict['child_key']:
                                        if child_dict['range'][0] == -1:
                                            snippet += "std_logic;\n"
                                        else:
                                            snippet += "std_logic_vector(" + str(child_dict['range'][0]-child_dict['range'][1]) + " downto 0);\n"
                                    else:
                                        snippet += "t_" + bus.bus_prefix + child_dict['complete_id'].replace(".", "_") + ";\n"
                                snippet += "\n"
                                records += snippet
                    else:
                        if node_dict['complete_id'].find("*") == -1:
                            to_be_done = 0
                            for child in node_dict['child_key']:
                                child_dict = slave.dict[str(child)]
                                if child_dict['size'] == str(bus.atom):
                                    to_be_done = 1
                            if to_be_done == 1:
                                snippet = "\t" + "type t_" + bus.bus_prefix + node_dict['complete_id'].replace(".", "_") + " is record\n"
                                for child in sorted(node_dict['child_key']):
                                    child_dict = slave.dict[str(child)]
                                    if child_dict['size'] == str(bus.atom):
                                        # if the child is a leaf, define it as base type (std_logic or std_logic_vector)
                                        if not child_dict['child_key']:
                                            if child_dict['range'][0] == -1:
                                                snippet += "\t\t" + child_dict['this_id'] + ": std_logic;\n"
                                            else:
                                                if slave.is_split_register(child_dict) is False:
                                                    snippet += "\t\t" + child_dict['this_id'] + ": std_logic_vector(" + str(child_dict['range'][0]-child_dict['range'][1]) + " downto 0);\n"
                                        else:
                                            if child_dict['array_idx'] == "0" or child_dict['array_idx'] is None:
                                                snippet += "\t\t" + child_dict['this_id'] + ": t_" + bus.bus_prefix + child_dict['complete_id'].replace(".", "_") + ";\n"
                                    # else define another record
                                snippet += "\tend record;\n\n"
                                records += snippet
            records = re.sub(r"<<[0-9]*>>", "", records)
            records = re.sub(r"\|", "", records)
            records = re.sub(r"/", "", records)
            #
            # RECORDS and ARRAY DECODED
            #
            records_decoded = ""
            snippet = ""
            for node_id in slave.reverse_dict_key:
                node_dict = slave.dict[node_id]
                if node_dict['child_key']:
                    if node_dict['array']:
                        if node_dict['array_idx'] == "0":
                            if node_dict['complete_id'].find("*") == -1:
                                snippet = "\t" + "type t_" + bus.bus_prefix + node_dict['complete_id'].replace(".", "_") + "_decoded is array (0 to " + node_dict['array'] + "-1) of "
                                for child in [node_dict['child_key'][0]]:
                                    child_dict = slave.dict[str(child)]
                                    if not child_dict['child_key']:
                                        snippet += "std_logic;\n"
                                    else:
                                        snippet += "t_" + bus.bus_prefix + child_dict['complete_id'].replace(".", "_") + "_decoded;\n"
                                snippet += "\n"
                                records_decoded += snippet
                    else:
                        if node_dict['complete_id'].find("*") == -1:
                            snippet = "\t" + "type t_" + bus.bus_prefix + node_dict['complete_id'].replace(".", "_") + "_decoded is record\n"
                            for child in sorted(node_dict['child_key']):
                                child_dict = slave.dict[str(child)]
                                # if the child is a leaf, define it as base type (std_logic or std_logic_vector)
                                if not child_dict['child_key']:
                                    snippet += "\t\t" + child_dict['this_id'] + ": std_logic;\n"
                                else:
                                    if child_dict['array_idx'] == "0" or child_dict['array_idx'] is None:
                                        snippet += "\t\t" + child_dict['this_id'] + ": t_" + bus.bus_prefix + child_dict['complete_id'].replace(".", "_") + "_decoded;\n"
                                    # else define another record
                            snippet += "\tend record;\n\n"
                            records_decoded += snippet
            records_decoded = re.sub(r"<<[0-9]*>>", "", records_decoded)
            records_decoded = re.sub(r"\|", "", records_decoded)
            records_decoded = re.sub(r"/", "", records_decoded)
            #
            # REGISTER DESCRIPTOR RECORDS
            #
            descr_records = ""
            snippet = "\t" + "type t_" + bus.bus_prefix + xml_mm.root.get('id') + "_descr is record\n"
            for node_id in slave.get_object(["block", "register_without_bitfield", "bitfield"]):
                node_dict = slave.dict[node_id]
                if slave.is_wide_register(node_dict) is False:
                    snippet += "\t\t" + node_dict['addressable_id'].replace(".", "_") + ": t_reg_descr;\n"
            snippet += "\tend record;\n\n"
            descr_records += snippet
            descr_records = helper.string_io.replace_const(descr_records)
            #
            # REGISTER DESCRIPTOR INIT
            #
            descr_records_init = ""
            snippet = "\t" + "constant " + bus.bus_prefix + xml_mm.root.get('id') + "_descr: t_" + bus.bus_prefix + xml_mm.root.get('id') + "_descr := (\n"
            for node_id in slave.get_object(["block", "register_without_bitfield", "bitfield"]):
                node_dict = slave.dict[node_id]
                if slave.is_wide_register(node_dict) is False:  # check if it is a wide register. In that case it should be split
                    addressable_id = node_dict['addressable_id'].replace(".", "_")
                    addressable_id = helper.string_io.replace_const(addressable_id)
                    snippet += "\t\t" + addressable_id + helper.string_io.add_space(addressable_id, max_id_len) + " => ("
                    if node_dict['addressable'] is None:
                        snippet += "X\"00000000\","
                    else:
                        # print node_dict['addressable']
                        snippet += "X\"" + helper.string_io.hex_format(node_dict['addressable']) + "\","
                    if node_dict['range'][0] >= 0:
                        snippet += helper.string_io.str_format(str(node_dict['range'][0]), 2) + ","
                    else:
                        snippet += helper.string_io.str_format(str(node_dict['range'][1]), 2) + ","
                    snippet += helper.string_io.str_format(str(node_dict['range'][1]), 2) + ","
                    if node_dict['hw_rst'] == "no":
                        snippet += "X\"" + helper.string_io.hex_format(0, slave.data_byte_size*2) + "\",   no_reset,"
                    else:
                        try:
                            reset_val = helper.string_io.hex_format(int(node_dict['hw_rst'], 16), slave.data_byte_size*2)
                        except:
                            reset_val = helper.string_io.hex_format(0, slave.data_byte_size*2)
                        snippet += "X\"" + reset_val + "\",async_reset,"
                    if node_dict['decoder_mask'] is None:
                        snippet += "X\"" + helper.string_io.hex_format(slave.dict[node_dict['parent_key']]['decoder_mask']) + "\","
                    else:
                        snippet += "X\"" + helper.string_io.hex_format(node_dict['decoder_mask']) + "\","
                    snippet += node_dict['permission'] + "),\n"
            snippet = re.sub(r",$", "", snippet)
            snippet = snippet.replace("_split$", "        ")
            snippet = snippet.replace("$", "")
            snippet += "\t);\n\n"
            descr_records_init += snippet
            #
            # RESET ASSIGN
            #
            reset_assign = ""
            snippet = ""
            for node_id in slave.get_object(["register_without_bitfield", "bitfield"]):
                node_dict = slave.dict[str(node_id)]

                try:
                    hw_rst = int(node_dict['hw_rst'], 16)
                except:
                    hw_rst = node_dict['hw_rst']

                if hw_rst == "no":
                    pass
                elif type(hw_rst) == str and slave.is_split_register(node_dict):  # generic
                    pass
                elif type(hw_rst) != str and slave.is_wide_register(node_dict):
                    pass
                else:
                    snippet = node_dict['complete_id']
                    snippet = helper.string_io.replace_sig(snippet)
                    if slave.is_split_register(node_dict):
                        snippet += "(" + str(node_dict['range'][0]) + " downto " + str(node_dict['range'][1]) + ")"
                        snippet = re.sub(r"_\$.*?\$", "", snippet)
                    try:
                        int(node_dict['hw_rst'], 16)
                        if node_dict['range'][0] == -1:
                            snippet += " <= " + bus.bus_prefix + xml_mm.root.get('id') + "_descr." + node_dict['addressable_id'].replace(".", "_") + ".rst_val(0)" + ";\n"
                        else:
                            snippet += " <= " + bus.bus_prefix + xml_mm.root.get('id') + "_descr." + node_dict['addressable_id'].replace(".", "_") + ".rst_val(" + str(node_dict['range'][0]-node_dict['range'][1]) + " downto 0)" + ";\n"
                    except:
                        snippet += " <= " + node_dict['hw_rst'] + ";\n"

                    snippet = helper.string_io.replace_const(snippet)

                    reset_assign += snippet
            #
            # DEFAULT DECODED
            #
            default_decoded = ""
            snippet = ""
            for node_id in slave.get_object(["register_without_bitfield", "bitfield"]):
                node_dict = slave.dict[str(node_id)]
                snippet = node_dict['complete_id']
                snippet = helper.string_io.replace_sig(snippet)
                #if slave.is_split_register(node_dict):
                #    snippet += "(" + str(node_dict['range'][0]) + " downto " + str(node_dict['range'][1]) + ")"
                #    snippet = re.sub(r"_\$.*?\$", "", snippet)
                try:
                    int(node_dict['hw_rst'], 16)
                    if node_dict['range'][0] == -1:
                        snippet += " <= '0';\n"
                    else:
                        snippet += " <= '0';\n"
                except:
                    snippet += " <= " + "'0'" + ";\n"

                snippet = helper.string_io.replace_const(snippet)

                default_decoded += snippet
            #
            # RESET GENERICS PROCEDURE
            #
            #
            # RESET GENERICS DEFINITION
            #
            generics_definition = ""
            reset_generics_definition = ""
            slave_generics_definition = ""
            reset_generics_procedure = ""
            reset_generics_map = ""
            slave_generics_map = ""
            for key in sorted(reset_generics_dict.keys()):
                if reset_generics_dict[key] == "std_logic":
                    reset_generics_definition += "\t" + key + ": " + reset_generics_dict[key] + " := '0';\n"
                    reset_generics_procedure += ";\n" + helper.string_io.indent(key + ": " + reset_generics_dict[key], 8)
                else:
                    reset_generics_definition += "\t" + key + ": " + reset_generics_dict[key] + " := (others=>'0');\n"
                    reset_generics_procedure += ";\n" + helper.string_io.indent(key + ": " + reset_generics_dict[key], 8)
                reset_generics_map += ",\n" + helper.string_io.indent(key, 8)
            for generic in bus.slave_generics:
                slave_generics_definition += "\t" + generic['name'] + ": " + generic['type'] + ";\n"
                slave_generics_map += "\t" + generic['name'] + " => " + generic['name'] + ",\n"
            generics_definition = slave_generics_definition + reset_generics_definition
            if generics_definition != "":
                generics_definition = "generic(\n" + generics_definition
                generics_definition += ");\n"
                generics_definition = generics_definition.replace(";\n);", "\n);")
            if slave_generics_map != "":
                slave_generics_map = "generic map(\n" + slave_generics_map
                slave_generics_map += ")\n"
                slave_generics_map = slave_generics_map.replace(",\n)", "\n)")
            # print reset_generics_definition
            # print reset_generics_procedure
            # print reset_generics_map

            #
            # FULL DECODER ASSIGN
            #
            full_decoder_assign = ""
            snippet = ""
            for node_id in slave.get_object(["block", "register_without_bitfield", "bitfield"]):
                node_dict = slave.dict[str(node_id)]
                if slave.is_wide_register(node_dict) is False:
                    if_str = "if " + bus.bus_prefix + "<slave_name>_decoder(" + bus.bus_prefix + "<slave_name>_descr.<addressable_id>,addr) = true and en = '1' then\n"
                    snippet = node_dict['complete_id'].replace(".", "_decoded.", 1) + " := '0';\n"
                    reg_name = re.sub(r"_\$.*?\$", "", node_dict['complete_id'])
                    if node_dict['last_split'] == "1":
                        snippet += reg_name.replace(".", "_decoded.", 1) + " := '0';\n"
                    snippet = helper.string_io.replace_sig(snippet)

                    snippet += if_str.replace('<slave_name>', slave.dict['0']['this_id'])
                    snippet = snippet.replace('<addressable_id>', node_dict['addressable_id'].replace(".", "_"))
                    snippet = helper.string_io.replace_const(snippet)

                    snippet += "\t" + node_dict['complete_id'].replace(".", "_decoded.", 1) + " := '1';\n"
                    if node_dict['last_split'] == "1":
                        snippet += "\t" + reg_name.replace(".", "_decoded.", 1) + " := '1';\n"
                    snippet += "end if;\n\n"

                    snippet = helper.string_io.replace_sig(snippet)

                    full_decoder_assign += snippet
            #
            # WRITE TO REGISTERS
            #
            write_reg = ""
            snippet = ""
            for node_id in slave.get_object(["register_without_bitfield", "bitfield"]):
                node_dict = slave.dict[str(node_id)]
                if slave.is_wide_register(node_dict) is False:
                    if_str = "if <slave_name>_decoded.<addressable_id> = '1' then\n"
                    if (node_dict['permission'] == "rw" or node_dict['permission'] == "w") and node_dict['size'] == str(bus.atom):
                        snippet = if_str.replace('<slave_name>', slave.dict['0']['this_id'])
                        snippet = snippet.replace('<addressable_id>', node_dict['addressable_id'])

                        if node_dict['range'][0] == -1:
                            snippet += "\t" + node_dict['complete_id'] + " <= data(" + str(node_dict['range'][1]) + ");\n"
                        else:
                            if slave.is_split_register(node_dict):
                                reg_name = re.sub(r"_\$.*?\$", "", node_dict['complete_id'])
                                snippet += "\t" + reg_name + "(" + str(node_dict['range'][0]) + " downto " + str(node_dict['range'][1]) + ")" + \
                                           " <= data(" + str(int(node_dict['range'][0]) - bus.data_bit_size * int(node_dict['split'])) + " downto " + \
                                                         str(int(node_dict['range'][1]) - bus.data_bit_size * int(node_dict['split'])) + ");\n"
                            else:
                                snippet += "\t" + node_dict['complete_id'] + " <= data(" + str(node_dict['range'][0]) + " downto " + str(node_dict['range'][1]) + ");\n"

                        snippet += "end if;\n\n"

                        snippet = helper.string_io.replace_sig(snippet)

                        write_reg += snippet
            #
            # READ FROM REGISTERS
            #
            read_reg = ""
            snippet = ""
            for node_id in slave.get_object(["register_without_bitfield", "bitfield"]):
                node_dict = slave.dict[str(node_id)]
                if slave.is_wide_register(node_dict) is False:
                    if_str = "if <slave_name>_decoded.<addressable_id> = '1' then\n"
                    if (node_dict['permission'] == "rw" or node_dict['permission'] == "r") and node_dict['size'] == str(bus.atom):
                        snippet = if_str.replace('<slave_name>', slave.dict['0']['this_id'])
                        snippet = snippet.replace('<addressable_id>', node_dict['addressable_id'])

                        if node_dict['range'][0] == -1:
                            snippet += "\tret(" + str(node_dict['range'][1]) + ") := " + node_dict['complete_id'] + ";\n"
                        else:
                            if slave.is_split_register(node_dict):
                                reg_name = re.sub(r"_\$.*?\$", "", node_dict['complete_id'])
                                snippet += "\tret(" + str(int(node_dict['range'][0]) - bus.data_bit_size * int(node_dict['split'])) + " downto " + \
                                                      str(int(node_dict['range'][1]) - bus.data_bit_size * int(node_dict['split'])) + ") := "
                                snippet += reg_name + "(" + str(node_dict['range'][0]) + " downto " + str(node_dict['range'][1]) + ")" + ";\n"
                            else:
                                snippet += "\tret(" + str(node_dict['range'][0]) + " downto " + str(node_dict['range'][1]) + ") := " + node_dict['complete_id'] + ";\n"
                        snippet += "end if;\n\n"

                        snippet = helper.string_io.replace_sig(snippet)

                        read_reg += snippet
            #
            # FW WRITE TO REGISTERS
            #
            hw_write_reg_logic_prio = ""
            hw_write_reg_bus_prio = ""
            snippet = ""
            hw_doesnt_write = 1
            for node_id in slave.get_object(["register_without_bitfield", "bitfield"]):
                node_dict = slave.dict[str(node_id)]
                if slave.is_split_register(node_dict) is False:
                    if node_dict['hw_permission'] == "we" and node_dict['size'] == str(bus.atom):
                        hw_doesnt_write = 0
                        this_id = bus.bus_prefix + node_dict['complete_id']
                        snippet = "if " + this_id.replace(".", "_in_we.", 1) + " = '1' then\n"
                        snippet += "\t" + this_id.replace(".", "_int.", 1) + " <= " + this_id.replace(".", "_in.", 1) + ";\n"
                        snippet += "end if;\n"

                    if node_dict['hw_permission'] == "w" and node_dict['size'] == str(bus.atom):
                        hw_doesnt_write = 0
                        this_id = bus.bus_prefix + node_dict['complete_id']
                        snippet = this_id.replace(".", "_int.", 1) + " <= " + this_id.replace(".", "_in.", 1) + ";\n"

                snippet = helper.string_io.replace_sig(snippet)
                if node_dict['hw_prio']:
                    hw_write_reg_logic_prio += snippet
                else:
                    hw_write_reg_bus_prio += snippet
                snippet = ""
            #
            # MUX ASSIGN
            #
            mux_assign = ""
            snippet = ""
            memory_blocks = 0
            for node_id in slave.get_object(["block"]):
                node_dict = slave.dict[str(node_id)]
                if_str = "if " + bus.bus_prefix + "<slave_name>_decoder(" + bus.bus_prefix + "<slave_name>_descr.<addressable_id>,addr) = true then\n"
                snippet = if_str.replace('<slave_name>', slave.dict['0']['this_id'])
                snippet = snippet.replace('<addressable_id>', node_dict['addressable_id'].replace(".", "_"))

                snippet += "\tret(" + str(nof_registers_block+memory_blocks) + ") := '1';\n"
                snippet += "end if;\n\n"

                snippet = helper.string_io.replace_sig(snippet)

                memory_blocks += 1

                mux_assign += snippet

            if nof_registers_block > 0 and nof_memory_block > 0:
                mux_assign += "if ret(ret'length-1 downto 1) = \"" + nof_memory_block*"0" + "\" then\n"
                mux_assign += "\tret(0) := '1';\n"
                mux_assign += "end if;\n\n"

            ipb_mapping_record = ""
            ipb_mapping_record_init = ""
            memory_blocks_inst = ""
            memory_blocks_port = ""
            if nof_memory_block > 0:
                snippet = "type t_ipb_" + xml_mm.root.get('id') + "_mapping is record\n"
                for node_id in slave.get_object(["block"]):
                    node_dict = slave.dict[str(node_id)]
                    snippet += "\t" + node_dict['addressable_id'].replace(".", "_") + ": integer;\n"
                snippet += "end record;\n"
                ipb_mapping_record = snippet

                snippet = "constant c_ipb_" + xml_mm.root.get('id') + "_mapping: t_ipb_" + xml_mm.root.get('id') + "_mapping := (\n"
                idx = 0
                for node_id in slave.get_object(["block"]):
                    node_dict = slave.dict[str(node_id)]
                    if idx > 0:
                        snippet += ",\n"
                    snippet += "\t" + node_dict['addressable_id'].replace(".", "_") + "=> " + str(nof_registers_block+idx)
                    idx += 1
                snippet += "\n);\n"
                ipb_mapping_record_init = snippet

                for node_id in slave.get_object(["block"]):
                    node_dict = slave.dict[str(node_id)]
                    if node_dict['permission'] == "r" or node_dict['permission'] == "rw":
                        ipb_read = "true"
                    else:
                        ipb_read = "false"
                    if node_dict['permission'] == "w" or node_dict['permission'] == "rw":
                        ipb_write = "true"
                    else:
                        ipb_write = "false"
                    if node_dict['hw_dp_ram'] == "yes":
                        nof_hw_dp_ram += 1
                        snippet = "ipb_<name>_dp_ram_inst: entity " + options.slave_library + ".ipb_" + xml_mm.root.get('id') + "_dp_ram\n"
                        snippet += "generic map(\n"
                        snippet += "\tram_add_width => <size>,\n"
                        snippet += "\tram_dat_width => <dat_width>,\n"
                        snippet += "\tipb_read => " + ipb_read + ",\n"
                        snippet += "\tipb_write => " + ipb_write + ",\n"
                        snippet += "\tipb_read_latency => <ipb_lat>,\n"
                        snippet += "\tuser_read_latency => <user_lat>,\n"
                        snippet += "\tinit_file => \"<init_file>\",\n"
                        snippet += "\tinit_file_format => \"<init_file_format>\"\n"
                        snippet += ")\n"
                        snippet += "port map(\n"
                        snippet += "\tipb_clk  => " + bus.clock + ",\n"
                        snippet += "\tipb_miso => ipb_miso_arr(c_ipb_" + xml_mm.root.get('id') + "_mapping.<name>),\n"
                        snippet += "\tipb_mosi => ipb_mosi_arr(c_ipb_" + xml_mm.root.get('id') + "_mapping.<name>),\n"

                        snippet += "\t" + "user_clk => " + xml_mm.root.get('id') + "_<name>_clk,\n"
                        snippet += "\t" + "user_en => " + xml_mm.root.get('id') + "_<name>_en,\n"
                        snippet += "\t" + "user_we => " + xml_mm.root.get('id') + "_<name>_we,\n"
                        snippet += "\t" + "user_add => " + xml_mm.root.get('id') + "_<name>_add,\n"
                        snippet += "\t" + "user_wdat => " + xml_mm.root.get('id') + "_<name>_wdat,\n"
                        snippet += "\t" + "user_rdat => " + xml_mm.root.get('id') + "_<name>_rdat\n"

                        snippet += ");\n\n"
                        size = np.log2(int(node_dict['size']) / bus.atom)
                        snippet = snippet.replace("<size>", str(int(math.ceil(size))))
                        snippet = snippet.replace("<dat_width>", str(int(node_dict['hw_dp_ram_width'])))
                        snippet = snippet.replace("<ipb_lat>", str(int(node_dict['hw_dp_ram_bus_lat'])))
                        snippet = snippet.replace("<user_lat>", str(int(node_dict['hw_dp_ram_logic_lat'])))
                        snippet = snippet.replace("<init_file>", str(node_dict['hw_dp_ram_init_file']))
                        snippet = snippet.replace("<init_file_format>", str(node_dict['hw_dp_ram_init_file_format']))
                        snippet = snippet.replace("<name>", node_dict['addressable_id'].replace(".", "_"))

                        memory_blocks_inst += snippet
                        memory_blocks_inst = "--\n--\n--\n" + memory_blocks_inst

                        snippet = "\n" + xml_mm.root.get('id') + "_<name>_clk: in std_logic:='0';"
                        snippet += "\n" + xml_mm.root.get('id') + "_<name>_en: in std_logic:='0';"
                        snippet += "\n" + xml_mm.root.get('id') + "_<name>_we: in std_logic:='0';"
                        snippet += "\n" + xml_mm.root.get('id') + "_<name>_add: in std_logic_vector(<size> downto 0):=(others=>'0');"
                        snippet += "\n" + xml_mm.root.get('id') + "_<name>_wdat: in std_logic_vector(<dat_width> downto 0):=(others=>'0');"
                        snippet += "\n" + xml_mm.root.get('id') + "_<name>_rdat: out std_logic_vector(<dat_width> downto 0);"
                        snippet = snippet.replace("<size>", str(int(math.ceil(size))-1))
                        snippet = snippet.replace("<dat_width>", str(int(node_dict['hw_dp_ram_width'])-1))
                        snippet = snippet.replace("<ipb_lat>", str(int(node_dict['hw_dp_ram_bus_lat'])))
                        snippet = snippet.replace("<user_lat>", str(int(node_dict['hw_dp_ram_logic_lat'])))
                        snippet = snippet.replace("<name>", node_dict['addressable_id'].replace(".", "_"))

                        memory_blocks_port += snippet
                    else:
                        memory_blocks_port += "\n" + "ipb_" + xml_mm.root.get('id') + "_<name>_miso: in t_ipb_miso;"
                        memory_blocks_port += "\n" + "ipb_" + xml_mm.root.get('id') + "_<name>_mosi: out t_ipb_mosi;"
                        memory_blocks_port = memory_blocks_port.replace("<name>", node_dict['addressable_id'].replace(".", "_"))
                        snippet = "ipb_miso_arr(c_ipb_" + xml_mm.root.get('id') + "_mapping.<name>) <= ipb_" + xml_mm.root.get('id') + "_<name>_miso;\n"
                        snippet += "ipb_" + xml_mm.root.get('id') + "_<name>_mosi <= ipb_mosi_arr(c_ipb_" + xml_mm.root.get('id') + "_mapping.<name>);\n"
                        snippet = snippet.replace("<name>", node_dict['addressable_id'].replace(".", "_"))
                        memory_blocks_inst += snippet
                        memory_blocks_inst = "--\n--\n--\n" + memory_blocks_inst
            #
            # Replacing relevant fields in skeleton package file
            #
            vhdl_text = helper.string_io.read_template_file(os.path.dirname(os.path.abspath(__file__)) + "/template/" + "xml2vhdl" + "_slave_pkg.template.vhd")

            vhdl_text = vhdl_text.replace("<BUS>", bus.name)
            vhdl_text = vhdl_text.replace("<BUS_PREFIX_>", bus.bus_prefix)
            vhdl_text = vhdl_text.replace("<BUS_CLK>", bus.clock)
            vhdl_text = vhdl_text.replace("<BUS_RST>", bus.reset)
            vhdl_text = vhdl_text.replace("<BUS_RST_VAL>", bus.reset_val)
            vhdl_text = vhdl_text.replace("<BUS_LIBRARY>", options.bus_library)
            vhdl_text = vhdl_text.replace("<DATA_BUS_BIT_SIZE-1>", str(bus.data_bit_size-1))
            vhdl_text = vhdl_text.replace("<SLAVE_LIBRARY>", options.slave_library)
            vhdl_text = vhdl_text.replace("<SLAVE_NAME>", xml_mm.root.get('id'))
            vhdl_text = vhdl_text.replace("<RECORDS>\n", records)
            vhdl_text = vhdl_text.replace("<RECORDS_DECODED>\n", records_decoded)
            vhdl_text = vhdl_text.replace("<DESCRIPTOR_RECORDS>\n", descr_records)
            vhdl_text = vhdl_text.replace("<DESCRIPTOR_RECORDS_INIT>\n", descr_records_init)
            vhdl_text = vhdl_text.replace("<RESET_GENERICS_PROCEDURE>", helper.string_io.indent(reset_generics_procedure, 0))
            vhdl_text = vhdl_text.replace("<RESET_ASSIGN>\n", helper.string_io.indent(reset_assign, 2))
            vhdl_text = vhdl_text.replace("<DEFAULT_DECODED>\n", helper.string_io.indent(default_decoded, 2))
            vhdl_text = vhdl_text.replace("<FULL_DECODER_ASSIGN>\n", helper.string_io.indent(full_decoder_assign, 2))
            vhdl_text = vhdl_text.replace("<WRITE_ASSIGN>\n", helper.string_io.indent(write_reg, 2))
            vhdl_text = vhdl_text.replace("<READ_ASSIGN>\n", helper.string_io.indent(read_reg, 2))
            vhdl_text = vhdl_text.replace("<MUX_ASSIGN>\n", helper.string_io.indent(mux_assign, 3))
            vhdl_text = vhdl_text.replace("<NOF_REGISTER_BLOCKS>", str(nof_registers_block))
            vhdl_text = vhdl_text.replace("<NOF_MEMORY_BLOCKS>", str(nof_memory_block))
            vhdl_text = vhdl_text.replace("<IPB_MAPPING_RECORD>\n", helper.string_io.indent(ipb_mapping_record, 1))
            vhdl_text = vhdl_text.replace("<IPB_MAPPING_RECORD_INIT>\n", helper.string_io.indent(ipb_mapping_record_init, 1))
            if nof_registers_block == 0:
                vhdl_text = re.sub(r'<REMOVE_IF_BLOCK_ONLY_START>(.|\n)*?<REMOVE_IF_BLOCK_ONLY_END>\n', "", vhdl_text)
            else:
                vhdl_text = re.sub(r'<REMOVE_IF_BLOCK_ONLY_START>\n', "", vhdl_text)
                vhdl_text = re.sub(r'<REMOVE_IF_BLOCK_ONLY_END>\n', "", vhdl_text)
            vhdl_text = vhdl_text.replace("_split$", "")
            vhdl_text = vhdl_text.replace("$", "")
            vhdl_text = vhdl_text.replace("\t", "   ")

            helper.string_io.write_vhdl_file(bus.bus_prefix + xml_mm.root.get('id') + "_pkg.vhd", vhdl_output_folder, vhdl_text)
            #
            # Replacing relevant fields in template SLAVE file
            #
            vhdl_text = helper.string_io.read_template_file(os.path.dirname(os.path.abspath(__file__)) + "/template/" + "xml2vhdl" + "_slave.template.vhd")

            vhdl_text = vhdl_text.replace("<BUS>", bus.name)
            vhdl_text = vhdl_text.replace("<BUS_PREFIX_>", bus.bus_prefix)
            vhdl_text = vhdl_text.replace("<BUS_CLK>", bus.clock)
            vhdl_text = vhdl_text.replace("<BUS_RST>", bus.reset)
            vhdl_text = vhdl_text.replace("<BUS_RST_VAL>", bus.reset_val)
            vhdl_text = vhdl_text.replace("<BUS_MOSI_TYPE>", bus.mosi_type)
            vhdl_text = vhdl_text.replace("<BUS_MISO_TYPE>", bus.miso_type)
            vhdl_text = vhdl_text.replace("<BUS_LIBRARY>", options.bus_library)
            vhdl_text = vhdl_text.replace("<SLAVE_LIBRARY>", options.slave_library)
            vhdl_text = vhdl_text.replace("<SLAVE_NAME>", xml_mm.root.get('id'))
            vhdl_text = vhdl_text.replace("<GENERICS_DEFINITION>\n", helper.string_io.indent(generics_definition, 1))
            vhdl_text = vhdl_text.replace("<RESET_GENERICS_MAP>", helper.string_io.indent(reset_generics_map, 0))
            vhdl_text = vhdl_text.replace("<SLAVE_GENERICS_MAP>\n", helper.string_io.indent(slave_generics_map, 1))
            vhdl_text = vhdl_text.replace("<MEMORY_BLOCKS_PORT>", helper.string_io.indent(memory_blocks_port, 2))
            vhdl_text = vhdl_text.replace("<MEMORY_BLOCKS_INST>", helper.string_io.indent(memory_blocks_inst, 1))
            vhdl_text = vhdl_text.replace("<HW_WRITE_REG_LOGIC_PRIO>", helper.string_io.indent(hw_write_reg_logic_prio, 3))
            vhdl_text = vhdl_text.replace("<HW_WRITE_REG_BUS_PRIO>", helper.string_io.indent(hw_write_reg_bus_prio, 3))
            if nof_registers_block == 0:
                vhdl_text = re.sub(r'<REMOVE_IF_BLOCK_ONLY_START>(.|\n)*?<REMOVE_IF_BLOCK_ONLY_END>\n', "", vhdl_text)
            else:
                vhdl_text = re.sub(r'<REMOVE_IF_BLOCK_ONLY_START>\n', "", vhdl_text)
                vhdl_text = re.sub(r'<REMOVE_IF_BLOCK_ONLY_END>\n', "", vhdl_text)
            if hw_doesnt_write == 1:
                vhdl_text = re.sub(r'<REMOVE_IF_NO_FW_WRITE_START>(.|\n)*?<REMOVE_IF_NO_FW_WRITE_END>\n', "", vhdl_text)
            else:
                vhdl_text = re.sub(r'<REMOVE_IF_NO_FW_WRITE_START>\n', "", vhdl_text)
                vhdl_text = re.sub(r'<REMOVE_IF_NO_FW_WRITE_END>\n', "", vhdl_text)
            vhdl_text = vhdl_text.replace(";\n);", "\n\t);")
            vhdl_text = vhdl_text.replace("\t", "   ")

            helper.string_io.write_vhdl_file(bus.name + "_" + xml_mm.root.get('id') + ".vhd", vhdl_output_folder, vhdl_text)
            #
            # Replacing relevant fields in template MUXDEMUX file
            #
            vhdl_text = helper.string_io.read_template_file(os.path.dirname(os.path.abspath(__file__)) + "/template/" + "xml2vhdl" + "_slave_muxdemux.template.vhd")

            vhdl_text = vhdl_text.replace("<BUS>", bus.name)
            vhdl_text = vhdl_text.replace("<BUS_PREFIX_>", bus.bus_prefix)
            vhdl_text = vhdl_text.replace("<BUS_CLK>", bus.clock)
            vhdl_text = vhdl_text.replace("<BUS_RST>", bus.reset)
            vhdl_text = vhdl_text.replace("<BUS_RST_VAL>", bus.reset_val)
            vhdl_text = vhdl_text.replace("<SLAVE_NAME>", xml_mm.root.get('id'))
            vhdl_text = vhdl_text.replace("<BUS_LIBRARY>", options.bus_library)
            vhdl_text = vhdl_text.replace("<SLAVE_LIBRARY>", options.slave_library)
            vhdl_text = vhdl_text.replace("\t", "   ")

            helper.string_io.write_vhdl_file(bus.name + "_" + xml_mm.root.get('id') + "_muxdemux.vhd", vhdl_output_folder, vhdl_text)
            #
            # Replacing relevant fields in template SIM MASTER file
            #
            if options.tb:
                vhdl_text = helper.string_io.read_template_file(os.path.dirname(os.path.abspath(__file__)) + "/template/" + bus.name + "/" + "xml2vhdl" + "_sim_ms.template.vhd")

                tb_add = ""
                for node_id in slave.get_object(["block", "register_without_bitfield", "bitfield"]):
                    node_dict = slave.dict[node_id]
                    if node_dict['addressable'] is not None:
                        tb_add += "X\"" + helper.string_io.hex_format(node_dict['addressable']) + "\""
                        break

                vhdl_text = vhdl_text.replace("<BUS>", bus.name)
                vhdl_text = vhdl_text.replace("<BUS_PREFIX_>", bus.bus_prefix)
                vhdl_text = vhdl_text.replace("<BUS_CLK>", bus.clock)
                vhdl_text = vhdl_text.replace("<BUS_RST>", bus.reset)
                vhdl_text = vhdl_text.replace("<BUS_RST_VAL>", bus.reset_val)
                vhdl_text = vhdl_text.replace("<SLAVE_NAME>", xml_mm.root.get('id'))
                vhdl_text = vhdl_text.replace("<BUS_LIBRARY>", options.bus_library)
                vhdl_text = vhdl_text.replace("<SLAVE_LIBRARY>", options.slave_library)
                vhdl_text = vhdl_text.replace("<TB_ADD>", tb_add)
                vhdl_text = vhdl_text.replace("\t", "   ")

                helper.string_io.write_vhdl_file(bus.name + "_" + xml_mm.root.get('id') + "_sim_ms.vhd", vhdl_output_folder, vhdl_text)
                #
                # Replacing relevant fields in template TB file
                #
                vhdl_text = helper.string_io.read_template_file(os.path.dirname(os.path.abspath(__file__)) + "/template/" + "xml2vhdl" + "_tb.template.vhd")

                memory_blocks_signal = memory_blocks_port
                memory_blocks_signal = memory_blocks_signal.replace("\n", "\nsignal ")
                memory_blocks_signal = memory_blocks_signal.replace(" in ", " ")
                memory_blocks_signal = memory_blocks_signal.replace(" out ", " ")

                memory_blocks_signal_list = memory_blocks_signal.split("\n")
                memory_blocks_portmap = ""
                for signal in memory_blocks_signal_list:
                    signal = signal.replace("signal ", "")
                    x = signal.split(":")
                    if x[0] != "":
                        memory_blocks_portmap += "\n" + x[0] + " => " + x[0] + ","

                vhdl_text = vhdl_text.replace("<BUS>", bus.name)
                vhdl_text = vhdl_text.replace("<BUS_PREFIX_>", bus.bus_prefix)
                vhdl_text = vhdl_text.replace("<BUS_CLK>", bus.clock)
                vhdl_text = vhdl_text.replace("<BUS_RST>", bus.reset)
                vhdl_text = vhdl_text.replace("<BUS_RST_VAL>", bus.reset_val)
                vhdl_text = vhdl_text.replace("<SLAVE_NAME>", xml_mm.root.get('id'))
                vhdl_text = vhdl_text.replace("<BUS_LIBRARY>", options.bus_library)
                vhdl_text = vhdl_text.replace("<SLAVE_LIBRARY>", options.slave_library)
                vhdl_text = vhdl_text.replace("<MEMORY_BLOCKS_SIGNAL>", helper.string_io.indent(memory_blocks_signal, 1))
                vhdl_text = vhdl_text.replace("<MEMORY_BLOCKS_PORTMAP>", helper.string_io.indent(memory_blocks_portmap, 2))
                if nof_registers_block == 0:
                    vhdl_text = re.sub(r'<REMOVE_IF_BLOCK_ONLY_START>(.|\n)*?<REMOVE_IF_BLOCK_ONLY_END>\n', "", vhdl_text)
                else:
                    vhdl_text = re.sub(r'<REMOVE_IF_BLOCK_ONLY_START>\n', "", vhdl_text)
                    vhdl_text = re.sub(r'<REMOVE_IF_BLOCK_ONLY_END>\n', "", vhdl_text)
                if hw_doesnt_write == 1:
                    vhdl_text = re.sub(r'<REMOVE_IF_NO_FW_WRITE_START>(.|\n)*?<REMOVE_IF_NO_FW_WRITE_END>\n', "", vhdl_text)
                else:
                    vhdl_text = re.sub(r'<REMOVE_IF_NO_FW_WRITE_START>\n', "", vhdl_text)
                    vhdl_text = re.sub(r'<REMOVE_IF_NO_FW_WRITE_END>\n', "", vhdl_text)
                vhdl_text = vhdl_text.replace(";\n);", "\n\t);")
                vhdl_text = vhdl_text.replace(",\n);", "\n\t);")
                vhdl_text = vhdl_text.replace("\t", "   ")

                helper.string_io.write_vhdl_file(bus.name + "_" + xml_mm.root.get('id') + "_tb.vhd", vhdl_output_folder, vhdl_text)
            #
            # Replacing relevant fields in template IPB_RAM
            #
            if nof_hw_dp_ram > 0:
                vhdl_text = helper.string_io.read_template_file(os.path.dirname(os.path.abspath(__file__)) + "/template/" + "xml2vhdl" + "_dp_ram.template.vhd")

                vhdl_text = vhdl_text.replace("<BUS>", bus.name)
                vhdl_text = vhdl_text.replace("<BUS_PREFIX_>", bus.bus_prefix)
                vhdl_text = vhdl_text.replace("<BUS_LIBRARY>", options.bus_library)
                vhdl_text = vhdl_text.replace("<SLAVE_NAME>", xml_mm.root.get('id'))

                helper.string_io.write_vhdl_file("ipb" + "_" + xml_mm.root.get('id') + "_dp_ram.vhd", vhdl_output_folder, vhdl_text)

        print "Done!"
        print
#
#
# MAIN STARTS HERE
#
#
if __name__ == '__main__':
    parser = helper.line_options.set_parser()
    (line_options, line_args) = parser.parse_args()

    xml2slave_inst = Xml2Slave(line_options, line_args)
    del xml2slave_inst
