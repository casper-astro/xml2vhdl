# -*- coding: utf8 -*-
"""

*********************
``xml2htmltables.py``
*********************

`GNU General Public License v3`_ © 2015-2019 University of Oxford & contributors

.. _GNU General Public License v3: _static/LICENSE

``xml2htmltables.py`` is a module provided to automatically generate HTML tables from generated ``AXI4-Lite``
Memory-Maps which can be embedded into documentation.

Todo:
    * error checking
    * documentation
    * regression test

"""
import xml.etree.ElementTree as ET
from optparse import OptionParser
import os

from .helper import customlogging as xml2vhdl_logging
logger = xml2vhdl_logging.config_logger(__name__)


def hex_format(input):
    return format(input, '08x')


def field_index(input):
    input_bin = format(input, '032b')
    for idx, val in enumerate(input_bin):
        if val == '1':
            first_index = -idx + 31
    return first_index


def field_size(input):
    input_bin = format(input, '032b')
    consect_ones = 0
    for idx, val in enumerate(input_bin):
        if val == '1':
            consect_ones = consect_ones + 1
    return consect_ones


def create_multifield_table_header():
    inputlist = []
    inputlist.append('<!DOCTYPE html>')
    inputlist.append('<html>')
    inputlist.append('<head>')
    inputlist.append('<link rel="stylesheet" href="regtables.css">')
    inputlist.append('</head>')
    inputlist.append('<body>')
    inputlist.append('<h2>Auto Generated Register Tables</h2>')
    inputlist.append('<p>The following tables have been automatically generated using the XML file used '
                     'to create the Memory-Mapped Register locations.')
    inputlist.append('Descriptions have been extracted from the XML file used to generate the '
                     'Memory-Mapped Registers and their corresponding fields.</p>')
    return inputlist


def create_multifield_table(inputlist, title, offset):
    inputlist.append('<h3>{} - {} Register</h3>'
                     .format(offset, title))
    inputlist.append('<h4>Layout</h4>')
    inputlist.append('<table width="75%" class="doxtable">')
    inputlist.append('<thead>')
    inputlist.append('<tr>')   
    inputlist.append('<th colspan="4" align="left">Register</th>')
    inputlist.append('<td colspan="28" align="left" id="{}"><tt><a href="#abstabentry{}">{}</a></tt></td>'
                     .format(title, title, title))
    inputlist.append('</tr>')
    inputlist.append('<tr>')
    inputlist.append('<th colspan="4" align="left">Offset</th>')
    inputlist.append('<td colspan="28" align="left"><tt>{}</tt></td>'
                     .format(offset))
    inputlist.append('</tr>')
    inputlist.append('<tr>')    
    for n in range(0, 8):
        inputlist.append('<td height="2px" width="12.5%" colspan="4"></td>')
    inputlist.append('</tr>')
    inputlist.append('<tr>')
    for n in range(31, -1, -1):
        inputlist.append('<td align="center"><tt>{}</tt></td>'
                         .format(n))
    inputlist.append('</tr>')
    inputlist.append('</thead>')
    return inputlist

def create_absolute_addr_table(inputlist):
    inputlist.append('<h3>All Register</h3>')
    inputlist.append('<p>The Absolute Addresses are shown at this level of hierachy. '
                     'They may change if a connection')
    inputlist.append('to an upstream AXI4-Lite is made.</p>')
    inputlist.append('<table width="75%" class="doxtable" id="absolutetable">')
    inputlist.append('<thead>')
    inputlist.append('<tr>')   
    inputlist.append('<th width="75%" align="left">Register</th>')
    inputlist.append('<th width="25%" align="right">Absolute Address</th>')
    inputlist.append('</tr>')
    inputlist.append('</thead>')
    return inputlist

def pop_absolute_addr_table(htmltable, fieldlist):
    duplicates = []
    no_duplicates = []
    
    for item in fieldlist:
        duplicates.append([item[0], item[1]])
        
    for item in duplicates:
        if item not in no_duplicates:
            no_duplicates.append(item)
    
    for field in no_duplicates:        
        htmltable.append('<tr>')   
        htmltable.append('<td align="left" id="abstabentry{}"><tt><a href="#{}">{}</a></tt></td>'
                         .format(field[0],field[0],field[0]))
        htmltable.append('<td align="right"><tt>{}</tt></td>'
                         .format(field[1]))
        htmltable.append('</tr>')
    
    htmltable.append('</table>')
        
    return htmltable

def generate_absolute_addr_table(inputlist):
    
    absolutehtmltable = []
    absolutehtmltable = create_multifield_table_header()
    absolutehtmltable = create_absolute_addr_table(absolutehtmltable)
    absolutehtmltable = pop_absolute_addr_table(absolutehtmltable, inputlist)
    
    return absolutehtmltable
    
def close_multifield_table(inputlist):
    inputlist.append('</table>')
    return inputlist

def create_multifield_table_footer(inputlist):
    inputlist.append('</body>')
    inputlist.append('</html>')
    return inputlist

def generate_multifield_html_table(fieldlist):
    
    # multifieldtableitems = fieldlist[::-1]
    
    last_register = ""
    current_index = 0
    multifieldhtmltableentry = []
    # multifieldhtmltableentry = create_multifield_table_header(multifieldhtmltableentry)
    existing_table = 0
    
    current_register_description_list = []
    
    for field in fieldlist:
        register_name = field[0]
        address = field[1]
        bit = field[2]
        colspan = field[3]
        bit_incr = int(bit)+int(colspan)-1
        permission = field[4]
        name = field[5]
        description = field[6]
        mask = field[7]
        reset_value = field[8]
        span = field[9]
        
        # Do we need a new table?
        if(last_register != register_name):
            logger.debug('New Register: {}, Changed from: {}'
                         .format(register_name, last_register))
            last_register = register_name
            if existing_table == 0:
                create_multifield_table(multifieldhtmltableentry, register_name, address)
                current_register_description_list = []
                current_register_description_list.append(field) 
                multifieldhtmltableentry.append('<tr>')
                current_index = 31
                null_flag = 0
                null_colspan = 0
                total_bit_count = 0
                existing_table = 1
            else:
                # Finalise Previous Table:             
                logger.debug('Finalising Table for Register: {}'
                             .format(register_name))
                while total_bit_count < 32:    
                    null_flag = 1    
                    null_colspan = null_colspan + 1
                    total_bit_count = total_bit_count + 1
                if null_flag == 1:
                    if span == 1:
                        newentry = ('<td colspan="{}" height="200px" bgcolor="#BFC9CA"><span></span></td>'
                                    .format(null_colspan))
                    else:
                        newentry = ('<td colspan="{}" bgcolor="#BFC9CA"></td>'
                                    .format(null_colspan))
                    multifieldhtmltableentry.append(newentry)
                    multifieldhtmltableentry.append('</tr>')
                    null_colspan = 0
                    total_bit_count = 0
                    null_flag = 0
                else:
                    multifieldhtmltableentry.append('</tr>')                
                
                logger.debug('close_multifield_table Table for Register: {}'
                             .format(register_name))
                close_multifield_table(multifieldhtmltableentry)
                logger.debug('pop_multifield_descriptions_table Table for Register: {}'
                             .format(register_name))
                pop_multifield_descriptions_table(multifieldhtmltableentry, current_register_description_list)
                close_multifield_table(multifieldhtmltableentry)
                current_register_description_list = []
                current_register_description_list.append(field)
                create_multifield_table(multifieldhtmltableentry, register_name, address)
                multifieldhtmltableentry.append('<tr>')
                current_index = 31
                null_flag = 0
                null_colspan = 0
                total_bit_count = 0
        else:
            current_register_description_list.append(field)           
            existing_table = 1
        
        logger.debug('Processing Register: {}, Field: {}'
                     .format(register_name, name))
        
        # print '[DEBUG]bit_incr: {}'.format(bit_incr)
        while current_index > int(bit_incr):
            null_flag = 1        
            null_colspan = null_colspan + 1
            current_index = current_index - 1
            
        if null_flag  == 1:
            if span == 1:            
                newentry = ('<td colspan="{}" height="200px" bgcolor="#BFC9CA"><span></span></td>'
                            .format(null_colspan))
            else:
                newentry = ('<td colspan="{}" bgcolor="#BFC9CA"></td>'
                            .format(null_colspan))
            total_bit_count = total_bit_count + null_colspan
            multifieldhtmltableentry.append(newentry)
            null_colspan = 0
            null_flag = 0
                
        if current_index == int(bit_incr):
            if span == 1:            
                newentry = ('<td colspan="{}" height="200px" align="center" id="desctabentry{}">'
                            '<span><tt><a href="#{}">{}</a></tt></span></td>'
                            .format(colspan, name, name, name))
            else:
                newentry = ('<td colspan="{}" align="center" id="desctabentry{}"><tt>'
                            '<a href="#{}">{}</a></tt></td>'
                            .format(colspan, name, name, name))
            multifieldhtmltableentry.append(newentry)
            total_bit_count = total_bit_count + colspan
            current_index = current_index - colspan
                
    # This is to handle the last bit field(s) being empty     
    while total_bit_count < 32:    
        null_flag = 1    
        null_colspan = null_colspan + 1
        total_bit_count = total_bit_count + 1
    
    if null_flag == 1:
        if span == 1:
            newentry = ('<td colspan="{}" height="200px" bgcolor="#BFC9CA"><span></span></td>'
                        .format(null_colspan))
        else:
            newentry = ('<td colspan="{}" bgcolor="#BFC9CA"></td>'
                        .format(null_colspan))
        multifieldhtmltableentry.append(newentry)
        null_colspan = 0
        total_bit_count = 0
        null_flag = 0
        
    logger.debug('Finalising Register with Empty LSB for Register: {}'
                 .format(register_name))
    multifieldhtmltableentry.append('</tr>')
    close_multifield_table(multifieldhtmltableentry)
    pop_multifield_descriptions_table(multifieldhtmltableentry, current_register_description_list)
    close_multifield_table(multifieldhtmltableentry)
    create_multifield_table_footer(multifieldhtmltableentry)
    
    return multifieldhtmltableentry


def pop_multifield_descriptions_table(htmltable, fieldlist):
    
    descriptionheader = 0
    logger.debug('<Description Table Generation>')
    if descriptionheader == 0:
        htmltable.append('<h4>Description(s):</h4>')
        descriptionheader = 1
    
    # Remove Duplicates (this is a workaround rather than a solution.)
    no_duplicates = []
    
    for item in fieldlist:
        if item not in no_duplicates:
            no_duplicates.append(item)
        else:
            logger.debug('<Description Table Generation>: Duplicate Removed: {}'
                         .format(item))
    
    for field in no_duplicates:
        logger.debug('<Description Table Generation>: {}'
                     .format(field))
        register_name = field[0]
        address = field[1]
        bit = field[2]
        colspan = field[3]
        permission = field[4]
        name = field[5]
        description = field[6]
        mask = field[7]
        reset_value = field[8]
        span = field[9]
        
        bit_upper = int(bit)+int(colspan)-1
        bit_lower = int(bit)
        
        htmltable.append('<table width="50%" class="doxtable">')
        htmltable.append('<thead>')
        htmltable.append('<tr>')
        htmltable.append('<th align="center" width="100%" colspan="2">{}</th>'
                         .format(name))
        htmltable.append('</tr>')        
        htmltable.append('<tr>')
        # htmltable.append('<th align="left" width="70%">{} Description</th>'.format(name))
        htmltable.append('<th align="left" width="15%">Register Name</th>')
        htmltable.append('<td align="left" width="85%"><tt>{}[{}:{}]</tt></td>'
                         .format(register_name,bit_upper,bit_lower))
        htmltable.append('</tr>')
        htmltable.append('<tr>')
        htmltable.append('<th align="left" width="15%">Offset</th>')
        htmltable.append('<td align="left" width="15%"><tt>{}</tt></td>'
                         .format(address))
        htmltable.append('</tr>')
        htmltable.append('<tr>')
        htmltable.append('<th align="left" width="15%">Field Name</th>')
        htmltable.append('<td align="left" width="15%" id="{}"><tt><a href="#desctabentry{}">{}</a></tt></td>'
                         .format(name, name, name))
        htmltable.append('</tr>')
        htmltable.append('<tr>')
        htmltable.append('<th align="left" width="15%">Mask</th>')
        htmltable.append('<td align="left" width="15%"><tt>{}</tt></td>'
                         .format(mask))
        htmltable.append('</tr>')
        htmltable.append('<tr>')
        htmltable.append('<th align="left" width="15%">Permission</th>')
        htmltable.append('<td align="left" width="15%"><tt>{}</tt></td>'
                         .format(permission))
        htmltable.append('</tr>')
        htmltable.append('<tr>')
        htmltable.append('<th align="left" width="15%">Reset</th>')
        htmltable.append('<td align="left" width="15%"><tt>{}</tt></td>'
                         .format(reset_value))
        htmltable.append('</tr>')
        htmltable.append('<tr>')
        htmltable.append('<th align="left" width="15%">Description</th>')
        htmltable.append('<td align="left" width="85%">{}</td>'
                         .format(description))
        htmltable.append('</tr>')
        htmltable.append('</thead>')
    # htmltable.append('</table>')
    return htmltable


class xml2html:
    def __init__(self, input_file, output_file="", cmd_string=""):

        self.input_file = input_file

        # if output_file is not given, change extension and write in the same folder
        if output_file == "":
            filename, file_extension = os.path.splitext(self.input_file)
            self.output_file = filename + ".html"
        else:
            self.output_file = output_file

        # print output_file
        # print self.output_file

        # create output directory if necessary
        if not os.path.isdir(os.path.dirname(self.output_file)) and os.path.dirname(self.output_file) != "":
            os.makedirs(os.path.dirname(self.output_file))

        tree = ET.parse(self.input_file)

        root = tree.getroot()

        alltableitems = []

        multifieldtableheader = []
        multifieldtableitems = []
        sorted_multifieldtableitems = []

        for node in root.iter('node'):
            if 'address' in list(node.attrib.keys()):
                if 'mask' in list(node.attrib.keys()):
                    mask = hex_format(int(node.get('mask'), 16))
                    span = 0
                    if node.get('absolute_id'):
                        addroffset = hex_format(int(node.get('absolute_offset'), 16))
                        newfield = [node.get('absolute_id'),
                                    "0x" + addroffset.upper(),
                                    field_index(int(node.get('mask'), 16)),
                                    field_size(int(node.get('mask'), 16)),
                                    node.get('permission'),
                                    node.get('id'),
                                    node.get('description'),
                                    node.get('mask'),
                                    node.get('hw_rst'), span]
                    else:
                        addroffset = hex_format(int(node.get('address'), 16))
                        newfield = [node.get('id'),
                                    "0x" + addroffset.upper(),
                                    field_index(int(node.get('mask'), 16)),
                                    field_size(int(node.get('mask'), 16)),
                                    node.get('permission'),
                                    node.get('id'),
                                    node.get('description'),
                                    node.get('mask'),
                                    node.get('hw_rst'), span]

                    alltableitems.append(newfield)
                else:
                    if 'description' in list(node.attrib.keys()):
                        # print '[Multi-Field Register]', node.get('id')
                        if node.get('absolute_id'):
                            multiaddroffset = hex_format(int(node.get('absolute_offset'), 16))
                        else:
                            multiaddroffset = hex_format(int(node.get('address'), 16))
                        # span = 1
                        for field in node.iter('node'):                           
                            if 'mask' in list(field.attrib.keys()):
                                span = 1                                
                                if field.get('absolute_id'):
                                    newfield = [node.get('absolute_id'),
                                                "0x" + multiaddroffset.upper(),
                                                field_index(int(field.get('mask'), 16)),
                                                field_size(int(field.get('mask'), 16)),
                                                field.get('permission'),
                                                field.get('id'),
                                                field.get('description'),
                                                field.get('mask'),
                                                field.get('hw_rst'), span]
                                else:
                                    newfield = [node.get('id'),
                                                "0x"+multiaddroffset.upper(),
                                                field_index(int(field.get('mask'), 16)),
                                                field_size(int(field.get('mask'), 16)),
                                                field.get('permission'),
                                                field.get('id'),
                                                field.get('description'),
                                                field.get('mask'),
                                                field.get('hw_rst'), span]
                            else:
                                span = 0                        
                                if field.get('absolute_id'):                 
                                    newfield = [node.get('absolute_id'),
                                                "0x" + multiaddroffset.upper(),
                                                field_index(int("0xFFFFFFFF", 16)),
                                                field_size(int("0xFFFFFFF", 16)),
                                                field.get('permission'),
                                                field.get('id'),
                                                field.get('description'),
                                                "0xFFFFFFFF",
                                                field.get('hw_rst'), span]
                                else:
                                    newfield = [node.get('id'),
                                                "0x" + multiaddroffset.upper(),
                                                field_index(int("0xFFFFFFFF", 16)),
                                                field_size(int("0xFFFFFFFF", 16)),
                                                field.get('permission'),
                                                field.get('id'),
                                                field.get('description'),
                                                "0xFFFFFFFF",
                                                field.get('hw_rst'), span]

                            alltableitems.append(newfield)


        # Reverse the order of the control bit fields so that it is LSB to MSB
        sorted_alltableitems = []
        sorted_alltableitems = sorted(alltableitems, key=lambda x:(x[1], -x[2]))
        # alltableitems.sort(key=lambda x: (x[0], x[2]))

        for line in sorted_alltableitems:
            logger.debug('Sorted alltableitems: {}'.format(line))

        absolutehtmltable= []
        absolutehtmltable = create_multifield_table_header()
        absolutehtmltable = generate_absolute_addr_table(sorted_alltableitems)
        multifieldhtmltable = generate_multifield_html_table(sorted_alltableitems)

        target = open(self.output_file, 'w')

        for line in absolutehtmltable:
            logger.debug('<absolutehtmltable>: {}'.format(line))
            target.write(line)
            target.write('\n')

        for line in multifieldhtmltable:
            target.write(line)
            target.write('\n')

        target.close()


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-i", "--input_file",
                      dest="input_file",
                      default="",
                      help="XML input file")
    parser.add_option("-o", "--output_file",
                      dest="output_file",
                      default="",
                      help="HTML output file")
    parser.add_option("-c", "--cmd_string",
                      dest="cmd_string",
                      default="",
                      help="Command string to be included in the HTML file")

    (options, args) = parser.parse_args()

    if not os.path.isfile(options.input_file):
        logger.error("Input file " + options.input_file + " doesn't exist!")
        exit(-1)

    logger.info('Generating HTML Tables for: {}'
                .format(options.input_file))
    xml2html(options.input_file, options.output_file, options.cmd_string)
    logger.info('Output HTML File: {}'
                .format(options.output_file))
