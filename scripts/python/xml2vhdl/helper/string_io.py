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

import customlogging as xml2vhdl_logging
logger = xml2vhdl_logging.config_logger(__name__)


# getchar from user input
class _Getch:
    """Gets a single character from standard input.  Does not echo to the screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


# format an hexadecimal as 32 bit with leading 0's
def hex_format(input_str, leading_zeros=8):
    return format(input_str, '0' + str(leading_zeros) + 'x')


# normalize a path name substituting back-slashes with slashes
def normalize_path(input_path):
    input_path = re.sub(r"\\", "/", input_path)
    input_path = re.sub(r"/+", "/", input_path)
    return input_path


# normalize a text substituting "\r\n" with "\n"
def normalize_template(input_text):
    input_text = re.sub(r"\r\n", "\n", input_text)
    return input_text


# normalize ad create output sub-folder
def normalize_output_folder(folder, ask="no"):
    output_folder = normalize_path(folder)
    if output_folder != "":
        if not os.path.exists(output_folder):
            if ask == "no":
                os.makedirs(output_folder)
            else:
                logger.warning('{output_folder} does not exist! Press [Y | y] to create it, any other key to abort'
                               .format(output_folder=os.path.abspath(output_folder)))
                key = _Getch()
                if key().lower() == "y":
                    logger.info('Creating: {output_folder}'
                                .format(output_folder=os.path.abspath(output_folder)))
                    os.makedirs(output_folder)
                else:
                    logger.error('Exiting...')
                    sys.exit(1)
        output_folder += "/"
    return output_folder


# generate a list of files having ext extension contained in the path_list list of folder
def file_list_generate(path_list, ext):
    ret = []
    for p in path_list:
        result = [os.path.join(dp, f) for dp, dn, fn in os.walk(normalize_path(p)) for f in fn if os.path.splitext(f)[1] == ext]
        for n in result:
            ret.append(normalize_path(n))
    return ret


# read template file
def read_template_file(file_name):
    template_file = open(file_name, "rU")
    text = template_file.read()
    text = normalize_template(text)
    template_file.close()
    return text


# write VHDL output file
def write_vhdl_file(file_name, vhdl_output_folder, text):
    file_name = normalize_path(vhdl_output_folder + file_name)
    logger.info('Writing VHDL output file: {file_name}'
                .format(file_name=os.path.abspath(file_name)))
    vhdl_file = open(file_name, "w")
    vhdl_file.write(text)
    vhdl_file.close()


# return the maximum length in a list of string
def get_max_len(name_list):
    length = 0
    for name in name_list:
        if length < len(name):
            length = len(name)
    return length


# add a blank after the string name, final string length is max_name_len
def add_space(name, max_name_len):
    target = max_name_len + 1
    space_num = target - len(name)
    return " "*space_num


# format a string adding suitable number of blank characters
def str_format(name, length):
    return add_space(name, length-1) + name


# indent a block with tab_num tabs, the empty string is not indented
def indent(input_string, tab_num):
    stripped = ""
    tabs = "\t"*tab_num
    if input_string == "":
        return input_string
    if input_string[-1] == "\n":
        stripped = "\n"
        input_string = input_string[:-1]
    indented = tabs + input_string
    indented = indented.replace("\n", "\n" + tabs)
    if stripped != "":
        indented += stripped
    return indented

# replace characters for signals
def replace_sig(string):
    replaced = string
    replaced = re.sub(r"\|.*?/", "", replaced)
    replaced = re.sub(r"\*", "", replaced)
    replaced = re.sub(r"\.\.", ".", replaced)
    replaced = re.sub(r"\. ", " ", replaced)
    replaced = re.sub(r"\.;", ";", replaced)
    replaced = re.sub(r"<<", "(", replaced)
    replaced = re.sub(r">>", ")", replaced)
    replaced = replaced.replace(").(", ")(")
    replaced = replaced.replace(". ", " ")
    return replaced


# replace characters for constants
def replace_const(string):
    replaced = string
    replaced = re.sub(r"\|", "", replaced)
    replaced = re.sub(r"/", "", replaced)
    replaced = re.sub(r"\*", "", replaced)
    replaced = re.sub(r"<<", "_", replaced)
    replaced = re.sub(r">>", "", replaced)
    replaced = replaced.replace(").(", ")(")
    replaced = replaced.replace(". ", " ")
    return replaced
