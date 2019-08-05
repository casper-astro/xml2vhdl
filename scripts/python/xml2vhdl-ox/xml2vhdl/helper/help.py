# -*- coding: utf8 -*-
"""

******************
``helper/help.py``
******************

`GNU General Public License v3`_ © 2015-2019 University of Oxford & contributors

.. _GNU General Public License v3: _static/LICENSE

``help.py`` is a helper module provided to version and help information.

"""
import re
import textwrap

version = [
           1.16, "Replaced optparse with argparse",
           1.15, "Added parameter for bus prefix",
           1.14, "Added Wishbone code generation",
           1.13, "Major code rewrite",
           1.12, "corrected error when command line option -a is used (attribute list generation)",
           1.11, "-r command line option",
           1.10, "reimplemented hw_ignore attribute",
           1.9,  "corrected single char input from user",
           1.8,  "print BRAM check, check of BRAM init file in VHDL",
           1.7,  "hw_dp_ram_init_file_check attribute for skipping ram init file existence check",
           1.6,  "converted sys.exit() to sys.exit(1)",
           1.5,  "dp_ram initilaization from bin/hex file",
           1.4,  "dp_ram implementation, simple test bench creation, history log, commented \"hw_ignore\" attribute,\
                  recursive iteration on links, command line parameters, generic reset values, \
                  templates modification for consistent line spacing, rearranged template files read/write",
           1.3,  "ipb mapping correction, substituted \".\" with \"_\"",
           1.2,  "newline character management",
           1.1,  "bus library reference correction",
           1.0,  "first release",
          ]

allowed_attribute_value = {}
allowed_attribute_value['link'] = ["string"]
allowed_attribute_value['address'] = ["hex_value"]
allowed_attribute_value['mask'] = ["hex_value"]
allowed_attribute_value['permission'] = ['r', 'w', 'rw']
allowed_attribute_value['hw_permission'] = ['w', 'we', 'no']
allowed_attribute_value['hw_rst'] = ['no', 'hex_value', 'vhdl_name']
allowed_attribute_value['hw_prio'] = ['bus', 'logic']
allowed_attribute_value['array'] = ["int_value"]
allowed_attribute_value['array_offset'] = ["hex_value"]
allowed_attribute_value['size'] = ["int_value"]
allowed_attribute_value['description'] = ["string"]
allowed_attribute_value['hw_dp_ram'] = ['yes', 'no']
allowed_attribute_value['hw_dp_ram_bus_lat'] = ['1', '2']
allowed_attribute_value['hw_dp_ram_logic_lat'] = ['1', '2']
allowed_attribute_value['hw_dp_ram_width'] = ['1 to 32']
allowed_attribute_value['hw_dp_ram_init_file'] = ["string"]
allowed_attribute_value['hw_dp_ram_init_file_check'] = ['yes', 'no']
allowed_attribute_value['hw_dp_ram_init_file_format'] = ["hex", "bin"]
allowed_attribute_value['hw_ignore'] = ['yes', 'no']

default_attribute_value = {}
default_attribute_value['link'] = "\"\""
default_attribute_value['address'] = "0x0"
default_attribute_value['mask'] = "No default value. It must be specified"
default_attribute_value['permission'] = "'rw'"
default_attribute_value['hw_permission'] = "no"
default_attribute_value['hw_rst'] = "0x0"
default_attribute_value['hw_prio'] = "logic"
default_attribute_value['array'] = "Must be specified if this attribute is used"
default_attribute_value['array_offset'] = "Must be specified if 'array' attribute is used"
default_attribute_value['size'] = "1"
default_attribute_value['description'] = "\"\""
default_attribute_value['hw_dp_ram'] = "no"
default_attribute_value['hw_dp_ram_bus_lat'] = "1"
default_attribute_value['hw_dp_ram_logic_lat'] = "1"
default_attribute_value['hw_dp_ram_width'] = "32"
default_attribute_value['hw_dp_ram_init_file'] = "\"\""
default_attribute_value['hw_dp_ram_init_file_check'] = "yes"
default_attribute_value['hw_dp_ram_init_file_format'] = "hex"
default_attribute_value['hw_ignore'] = "no"

attribute_description = {}
attribute_description['link'] = \
    "It links the specified XML file to the current node."
attribute_description['address'] = \
    "Current node relative offset. The absolute offset is calculated walking from the current node \
    to the root node and accumulating 'address' of each encountered node."
attribute_description['mask'] = \
    "It specifies the number of bits and their position in a register. This attribute must be specified \
    for nodes that are registers or bit-field."
attribute_description['permission'] = \
    "It controls the access type from the bus side."
attribute_description['hw_permission'] = \
    "It controls the access type from logic side. When 'w', the logic continuously write into \
    the registers. When 'we', the logic writes to the register by asserting a write enable.\
    When 'no' the logic cannot write to the register. The logic can always read the register"
attribute_description['hw_rst'] = \
    "It specifies the reset value of the register. When 'no' the register is not reset. In case the node is \
    a bit-field and its 'hw_rst' value is not specified, the node inherits 'hw_rst' from its parent. When the \
    specified value is a name, the script generates a a VHDL generic that is used to assign the reset value to \
    corresponding register."
attribute_description['hw_prio'] = \
    "It controls the priority between logic and bus when a simultaneous write (at the same clock edge) occurs."
attribute_description['array'] = \
    "It replicates the underlying node structure by the specified number of times. The offset between each array \
    element is specified by attribute 'array_offset'"
attribute_description['array_offset'] = \
    "It specifies the offset between each element in the array."
attribute_description['size'] = \
    "It specifies the node size in terms of 32 bits words. A size greater than 1 implies the instantiation of an\
    independent ipb bus that can be connected to a user supplied component or alternatively to an automatically \
    generated dual port RAM when hw_dp_ram=\"yes\"."
attribute_description['description'] = \
    "Node description"
attribute_description['hw_dp_ram'] = \
    "When 'yes' it instantiates a dual port RAM using the related ipb bus in the generated top level."
attribute_description['hw_dp_ram_bus_lat'] = \
    "Bus side read latency of instantiated dual port RAM"
attribute_description['hw_dp_ram_logic_lat'] = \
    "User logic side read latency of instantiated dual port RAM"
attribute_description['hw_dp_ram_width'] = \
    "RAM data width"
attribute_description['hw_dp_ram_init_file'] = \
    "Initialize instantiated BRAM with supplied initialization file"
attribute_description['hw_dp_ram_init_file_check'] = \
    "Check if linked initialization file exists"
attribute_description['hw_dp_ram_init_file_format'] = \
    "Initialization file format. Supported formats are binary and hexadecimal.\
    Each line in the initialization file corresponds to a memory location, the number \
    of bits and of each initialization word must match the memory width."
attribute_description['hw_ignore'] = \
    "When 'yes' it disables VHDL generation for current node and all child nodes. \
    The affected nodes will be included in generated XML."


def print_help():
    print()
    print("Supported XML attributes:")
    print()
    for n in sorted(allowed_attribute_value.keys()):
        print("'" + n + "'")
        dedented_text = textwrap.dedent("Description: " + re.sub(r" +", ' ', attribute_description[n])).strip()
        print(textwrap.fill(dedented_text, initial_indent='      ', subsequent_indent='      ' + ' ' * 13,
                            width=80))
        print("      Allowed values: " + " | ".join(allowed_attribute_value[n]))
        print("      Default value:  " + default_attribute_value[n])
        print()


def print_log():
    print()
    print("History Log:")
    print()
    for n in range(len(version) // 2):
        print("version " + str(version[2 * n]))
        dedented_text = textwrap.dedent(re.sub(r" +", ' ', version[2 * n + 1])).strip()
        print(textwrap.fill(dedented_text, width=80))
        print()


def get_version():
    return str(version[0])
