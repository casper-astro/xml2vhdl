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

from optparse import OptionParser

def set_parser():
    parser = OptionParser()
    parser.add_option("-l", "--log",
                      action="store_true",
                      dest="log",
                      default=False,
                      help="Print version and history log.")
    parser.add_option("-i", "--input_file",
                      action="append",
                      dest="input_file",
                      default=[],
                      help="XML input files. It is possible to specify several files repeating this option.")
    parser.add_option("-d", "--input_folder",
                      action="append",
                      dest="input_folder",
                      default=[],
                      help="Paths to input files folders. It is possible to specify several folders repeating this option. \
                      The script runs on all XML files in included folders.")
    parser.add_option("-p", "--path",
                      action="append",
                      dest="path",
                      default=[],
                      help="Paths to linked XML files. It is possible to specify multiple several files repeating \
                      this option.")
    parser.add_option("-v", "--vhdl_output",
                      dest="vhdl_output",
                      default="",
                      help="Generated VHDL output folder.")
    parser.add_option("-x", "--xml_output",
                      dest="xml_output",
                      default="",
                      help="Generated XML output folder.")
    parser.add_option("-b", "--bus_library",
                      dest="bus_library",
                      default="work",
                      help="Generated code will reference the specified bus VHDL library. Default is \"work\".")
    parser.add_option("-s", "--slave_library",
                      dest="slave_library",
                      default="work",
                      help="Generated code will reference the specified slave VHDL library. Default is \"work\".")
    parser.add_option("-n", "--bus_definition_number",
                      dest="bus_definition_number",
                      default="0",
                      help="Bus definition index. 0 = axi4lite(32bit), 1= wishbone(16bit), 2 = wishbone(32bit)")
    parser.add_option("--relative_output_path",
                      dest="relative_output_path",
                      default="",
                      help="Use a relative (respect to input XML file) path for the output folder, it overrides -v and -x options")
    # specific for Slave
    parser.add_option("-a", "--attributes",
                      action="store_true",
                      dest="xml_help",
                      default=False,
                      help="Prints supported XML attributes and exits.")
    parser.add_option("--relocate_path",
                      dest="relocate_path",
                      default="",
                      help="Relocate BRAM init file absolute path. Example: -r \"c:\\->d:\\work\"")
    parser.add_option("-c", "--constant",
                      action="append",
                      dest="constant",
                      default=[],
                      help="Constant passed to script. The script will substitute the specified constant value in the \
                      XML file. Example \"-c constant1=0x1234\". ")
    parser.add_option("--tb",
                      action="store_true",
                      dest="tb",
                      default=False,
                      help="Generate a simple test bench in sim sub-folder.")
    # specific for IC
    parser.add_option("-t", "--top",
                      dest="vhdl_top",
                      default="",
                      help="Top Level IC for VHDL generation. If this option is not specified, VHDL is generated for the root node IC.")
    parser.add_option("-r", "--vhdl_record_name",
                      dest="vhdl_record_name",
                      default="t_axi4lite_mmap_slaves",
                      help="VHDL record name containing slaves memory map.")
    parser.add_option("--zip",
                      action="store_true",
                      dest="zip",
                      default=False,
                      help="Only generate a BRAM Hex init file containing the zip compressed XML input file")
    return parser