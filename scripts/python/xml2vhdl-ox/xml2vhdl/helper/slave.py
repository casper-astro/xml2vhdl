# -*- coding: utf8 -*-
"""

*******************
``helper/slave.py``
*******************

`GNU General Public License v3`_ © 2015-2019 University of Oxford & contributors

.. _GNU General Public License v3: _static/LICENSE

``slave.py`` is a helper module providing methods and classes used to generate slave components from ``XML``

"""
import re
import os
import sys
import string
import string_io
import reserved_word
import numpy as np

import customlogging as xml2vhdl_logging
logger = xml2vhdl_logging.config_logger(__name__)


def reverse_key_order(input_dict):
    """Return a reversed ordered list of keys

    Args:
        input_dict (dict):

    Returns:
        (list): Reversed list of keys on input_dict

    """
    key_list = []
    for node_id in sorted([int(x) for x in input_dict.keys()]):
        key_list.append(str(node_id))
    return list(reversed(key_list))


def dec_check_bit(add_list, bit):
    """Return position of first not-equal bit among addresses in add_list

    Args:
        add_list (list):

        bit (???):

    Returns:
         (???): first not-equal bit among addresses in add_list or -1 if there are not different bits

    """
    for b in reversed(range(0, bit)):
        for add0 in add_list:
            for add1 in add_list:
                if add0[b] != add1[b]:
                    return b
    return -1


def dec_get_last_bit(bit_path):
    """

    Args:
        bit_path (???):

    Returns:
         (???):

    """
    bit_list = bit_path.split("_")
    ret = bit_list[len(bit_list)-1]
    ret = re.sub(r'v.*', "", ret)
    ret = int(ret)
    logger.debug('get_last_bit input: {ret}'.format(ret=ret))
    logger.debug('get_last_bit output: {bit_path}'.format(bit_path=bit_path))
    if ret == -1:
        ret = 32
    return ret


def dec_route_add(tree_dict):
    """

    Args:
        tree_dict (???):

    Returns:
        (???):

    """
    done = 0
    logger.debug('tree_dict: {tree_dict}'.format(tree_dict=tree_dict))
    for path in tree_dict.keys():
        add_list = tree_dict[path]
        b = dec_check_bit(add_list,  dec_get_last_bit(path))
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


class Slave:
    """Creates a AXI4-Lite Slave

    """
    def __init__(self, data_bus_size=32, size_indicate_bytes=0):
        self.logger = xml2vhdl_logging.config_logger(name=__name__, class_name=self.__class__.__name__)
        self.dict = {}
        self._key_table = {}
        self._node_num = 0
        self._level = 0
        self.reverse_dict_key = []
        self.decode_dict = {}
        self.size_indicate_bytes = size_indicate_bytes
        self.data_bit_size = data_bus_size
        self.data_byte_size = self.data_bit_size / 8
        self.atom = self.get_atomicity()
        self.size_normalizer = self.get_size_normalizer()
        self.default_mask = "0x" + "FF"*self.data_byte_size

    def reset(self):
        """Reset the slave

        Returns:
            None

        """
        self.dict = {}
        self._key_table = {}
        self._node_num = 0
        self._level = 0
        self.reverse_dict_key = []
        self.decode_dict = {}

    def get_atomicity(self):
        """

        Returns:
            (???):

        """
        if self.size_indicate_bytes == 0:
            return 1
        else:
            return self.data_byte_size

    def get_size_normalizer(self):
        """

        Returns:
            (???):

        """
        if self.size_indicate_bytes == 0:
            return self.data_byte_size
        else:
            return 1

    def get_range_from_mask(self, mask, split="0"):
        """Return range from mask

        Args:
            mask (???):
            split (???):

        Returns:
            (???):

        """
        if split is None:
            split = 0
        else:
            split = int(split)
        mask_int = int(mask, 16)
        bit_idx = 0
        range_lo = -1
        range_hi = -1
        while mask_int != 0:
            if (mask_int & 0x1) != 0:
                if range_lo == -1:
                    range_lo = bit_idx
                else:
                    range_hi = bit_idx
            mask_int /= 2
            bit_idx += 1
        range_hi += split * self.data_bit_size
        range_lo += split * self.data_bit_size
        return range_hi, range_lo

    def populate_node_dictionary(self, xml_node, xml_parent_node, hier_level):
        """Populate the node dictionary

        Args:
            xml_node (???):
            xml_parent_node (???):
            hier_level (???):

        Returns:
             (???):

        """
        this_dict = dict()
        this_dict['hier_level'] = hier_level
        this_dict['this_node'] = xml_node
        this_dict['parent_node'] = xml_parent_node
        this_dict['this_id'] = xml_node.get('id')

        if xml_parent_node is not None:
            this_dict['parent_id'] = xml_parent_node.get('id')
        else:
            this_dict['parent_id'] = None
        this_dict['complete_id'] = None
        this_dict['addressable_id'] = None
        this_dict['prev_id'] = None
        this_dict['address'] = xml_node.get('address')
        this_dict['decoder_mask'] = None
        this_dict['absolute_offset'] = None
        this_dict['mask'] = xml_node.get('mask')
        this_dict['permission'] = xml_node.get('permission')
        this_dict['hw_permission'] = xml_node.get('hw_permission')
        this_dict['hw_rst'] = xml_node.get('hw_rst')
        if xml_node.get('mask') is not None:
            this_dict['range'] = self.get_range_from_mask(xml_node.get('mask'), xml_node.get('split'))
        else:
            this_dict['range'] = [self.data_bit_size - 1, 0]
        if xml_node.get('hw_prio') == "bus":
            this_dict['hw_prio'] = False
        else:
            this_dict['hw_prio'] = True
        child_list = []
        for child in xml_node:
            child_list.append(child.get('id'))
        this_dict['child_id'] = child_list
        this_dict['parent_key'] = None
        this_dict['child_key'] = []
        this_dict['addressable'] = None
        this_dict['link'] = xml_node.get('link')
        this_dict['array'] = xml_node.get('array')
        this_dict['array_offset'] = xml_node.get('array_offset')
        this_dict['array_idx'] = xml_node.get('array_idx')
        if xml_node.get('size') is None:
            this_dict['size'] = str(self.atom)
        else:
            this_dict['size'] = str(xml_node.get('size'))
        this_dict['type'] = "undef"
        if xml_node.get('description') is None:
            this_dict['description'] = "Missing description"
        else:
            this_dict['description'] = xml_node.get('description')
        this_dict['hw_dp_ram'] = xml_node.get('hw_dp_ram')
        if xml_node.get('hw_dp_ram_bus_lat') is None:
            this_dict['hw_dp_ram_bus_lat'] = "1"
        else:
            this_dict['hw_dp_ram_bus_lat'] = xml_node.get('hw_dp_ram_bus_lat')
        if xml_node.get('hw_dp_ram_logic_lat') is None:
            this_dict['hw_dp_ram_logic_lat'] = "1"
        else:
            this_dict['hw_dp_ram_logic_lat'] = xml_node.get('hw_dp_ram_logic_lat')
        if xml_node.get('hw_dp_ram_width') is None:
            this_dict['hw_dp_ram_width'] = str(self.data_bit_size)
        else:
            this_dict['hw_dp_ram_width'] = xml_node.get('hw_dp_ram_width')
        if xml_node.get('hw_dp_ram_init_file') is None:
            this_dict['hw_dp_ram_init_file'] = ""
        else:
            this_dict['hw_dp_ram_init_file'] = xml_node.get('hw_dp_ram_init_file')
        if xml_node.get('hw_dp_ram_init_file_format') is None:
            this_dict['hw_dp_ram_init_file_format'] = "hex"
        else:
            this_dict['hw_dp_ram_init_file_format'] = xml_node.get('hw_dp_ram_init_file_format')
        if xml_node.get('split') is not None:
            this_dict['split'] = xml_node.get('split')
        else:
            this_dict['split'] = "-1"
        if xml_node.get('last_split') is not None:
            this_dict['last_split'] = xml_node.get('last_split')
        else:
            this_dict['last_split'] = "0"

        this_dict['hw_ignore'] = xml_node.get('hw_ignore')
        return this_dict

    def populate_subnodes(self, node, target_level, current_level):
        """# populate all subnodes of a node of hierarchical level defined by target_level

        Args:
            node (???):
            target_level (???):
            current_level (???):

        Returns:
             (???):

        """
        if node is None:
            return -1
        else:
            for subnode in node:
                if current_level == target_level:
                    self.dict[str(self._node_num)] = self.populate_node_dictionary(subnode,
                                                                                   node,
                                                                                   current_level + 1)
                    self._key_table[str(subnode)] = int(self._node_num)
                    self._node_num += 1
                else:
                    self.populate_subnodes(subnode, target_level, current_level + 1)

    def populate_dict(self, root_node):
        """Populate the dictionary

        Args:
            root_node (???):

        Returns:
            (???):

        """
        self.reset()
        # populate root
        self.dict[str(0)] = self.populate_node_dictionary(root_node, None, 0)
        self._key_table[str(root_node)] = 0
        self._level = 0
        self._node_num = 1
        old_node_num = 1

        # populate all nodes recursively till there are no added nodes
        while True:
            self.populate_subnodes(root_node, self._level, 0)
            if old_node_num != self._node_num:
                self._level += 1
                old_node_num = self._node_num
            else:
                break
        self.reverse_dict_key = reverse_key_order(self.dict)

    def get_node_number(self):
        return self._node_num

    def get_hierarchical_level_number(self):
        return self._level

    def get_object(self, object_type_list, include_ignored=True):
        """Return a list of requested objects with specified type

        Specific types are:

        * ``block``
        * ``register_without_bitfield``
        * ``bitfield``

        Args:
            object_type_list (list of str):
            include_ignored (bool, optional): Default value is ``True``

        Returns:
            (list): Sorted list of requested object types

        """
        node_list = []
        sorted_list = []
        for node_id in reverse_key_order(self.dict):
            node_id = str(node_id)
            if (self.dict[node_id]['type'] in object_type_list) or (self.dict[node_id]['type'] != "undef" and object_type_list == ["all"]):
                if self.dict[node_id]['hw_ignore'] != "yes" or include_ignored:
                    node_list.append([self.dict[node_id]['addressable'], self.dict[node_id]['range'][1], node_id])
        for node_id in sorted(node_list):
            sorted_list.append(node_id[2])
        return sorted_list

    def compute_decoder_mask(self):
        """

        Returns:
            None

        """
        addresses = []
        for x in self.get_object(["block", "register_with_bitfield", "register_without_bitfield"]):
            addresses.append(self.dict[str(x)]['addressable'])

        add_num = len(addresses)
        logger.info('Addresses are: {add_num}'
                    .format(add_num=add_num))
        baddr = np.zeros((add_num, 32), dtype=np.int)
        tree_dict = {}

        # building address array
        a = 0
        for add in sorted(addresses):
            bit_mask = 0x80000000
            for n in range(32):
                if add & bit_mask != 0:
                    baddr[a, 31 - n] = 1
                bit_mask = bit_mask >> 1
            a = a + 1
        self.logger.debug('baddr: {baddr}'.format(baddr=baddr))

        tree_dict["-1v0"] = baddr

        while True:
            done, tree_dict = dec_route_add(tree_dict)
            if done == 0:
                break

        for bit_path in tree_dict:
            if tree_dict[bit_path] != []:
                add_bits = tree_dict[bit_path][0]
                add = ""
                for n in reversed(range(32)):
                    add = add + str(add_bits[n])
                bit_list = bit_path.split("_")
                mask = 0
                for bit in bit_list:
                    x = int(re.sub(r'v.*', "", bit))
                    if x >= 0:
                        mask = mask | (1 << x)
                self.decode_dict[str(int(add, 2))] = mask

        self.logger.debug('Decode Dict:')
        for address in sorted(self.decode_dict.keys()):
            self.logger.debug('\taddr:')
            self.logger.debug('\t{address}'.format(address=address))
            self.logger.debug('\tmask:')
            self.logger.debug('\t{mask}'.format(mask=hex(self.decode_dict[address])))

    def get_max_id_len(self):
        """Return maximum addressable_id length

        Returns:
            (int): Length

        """
        length = 0
        for node_id in reverse_key_order(self.dict):
            tmp = self.dict[node_id]['addressable_id']
            tmp = re.sub(r"\|", "",  tmp)
            tmp = re.sub(r"/",  "",  tmp)
            tmp = re.sub(r"\*", "",  tmp)
            tmp = re.sub(r"<<", "_", tmp)
            tmp = re.sub(r">>", "",  tmp)
            if len(tmp) > length:
                length = len(tmp)
        return length

    def get_size(self):
        """

        Returns:
            (int): Size

        """
        add_max = 0
        for node_id in self.get_object(["all"]):
            node_dict = self.dict[node_id]
            add = node_dict['addressable']
            self.logger.debug('{add}'.format(add=add))
            if add is None:
                self.logger.debug('{complete_id}'.format(complete_id=node_dict['complete_id']))
                self.logger.debug('{type}'.format(type=node_dict['type']))
            # Why would we only add the size if > the atomic unit?
            # To get the size we always need address + size(?)
            #if int(node_dict['size']) > self.atom:
            #    add += int(node_dict['size']) * self.size_normalizer
            add += int(node_dict['size']) * self.size_normalizer
            if abs(add) > abs(add_max):
                add_max = add
        n = 0
        while True:
            if abs(2 ** n) >= abs(add_max):
                break
            else:
                n += 1
        return 2 ** n

    def fill_child(self):
        """OB fill child/parent fields

        Returns:
            None

        """
        for this_node in self.dict:
            if self.dict[this_node]['parent_node'] is not None:
                parent_key = self._key_table[str(self.dict[this_node]['parent_node'])]
                self.dict[this_node]['parent_key'] = str(parent_key)
                self.dict[str(parent_key)]['child_key'].append(int(this_node))

    def fill_absolute_offset(self):
        """OB fill absolute offset field walking from current node to root and accumulating offset

        Returns:
            None

        """
        # absolute_offset = 0
        for node_id in reverse_key_order(self.dict):
            if self.dict[node_id]['address'] is not None:
                absolute_offset = int(self.dict[node_id]['address'], 16)
                test_node = node_id
                while True:
                    parent_id = self.dict[test_node]['parent_key']
                    if parent_id is None:
                        break
                    else:
                        if self.dict[parent_id]['address'] is not None:
                            absolute_offset += int(self.dict[parent_id]['address'], 16)
                    test_node = parent_id
                self.dict[node_id]['absolute_offset'] = absolute_offset

    def fill_decoder_mask(self):
        """OB fill decoder mask field

        Returns:
            None

        """
        self.compute_decoder_mask()
        for node_id in reverse_key_order(self.dict):
            if self.dict[node_id]['addressable'] is not None:
                add = str(self.dict[node_id]['addressable'])
                add = str(int(add))
                self.dict[node_id]['decoder_mask'] = self.decode_dict[add]

    def fill_complete_id(self):
        """OB fill complete id field

        Returns:
            None

        """
        for node_id in reverse_key_order(self.dict):
            current_node = node_id
            complete_id = self.dict[current_node]['this_id']
            prev_id = ""
            while True:
                if self.dict[current_node]['parent_key'] is None:
                    break
                else:
                    complete_id = self.dict[current_node]['parent_id'] + "." + complete_id
                    if prev_id == "":
                        prev_id = self.dict[current_node]['parent_id']
                    else:
                        prev_id = self.dict[current_node]['parent_id'] + "." + prev_id
                current_node = str(self.dict[current_node]['parent_key'])
            self.dict[node_id]['complete_id'] = complete_id
            self.dict[node_id]['addressable_id'] = re.sub(r"^(\w*\.)", "", complete_id)
            self.dict[node_id]['prev_id'] = prev_id

    def propagate_reset_value(self):
        """OB propagate reset value to child nodes

        Returns:
            None

        """
        for node_id in self.get_object(["bitfield"]):
            parent_node_id = self.dict[node_id]['parent_key']
            if self.dict[node_id]['hw_rst'] is None and self.dict[parent_node_id]['hw_rst'] is not None:
                try:
                    rst_val = int(self.dict[parent_node_id]['hw_rst'], 16)
                    rst_val = rst_val & int(self.dict[node_id]['mask'], 16)
                    rst_val = rst_val >> int(self.dict[node_id]['range'][1])
                    self.dict[node_id]['hw_rst'] = string_io.hex_format(rst_val)
                except:
                    if self.dict[node_id]['range'][0] == -1:
                        rst_val = self.dict[parent_node_id]['hw_rst'] + "(" + str(self.dict[node_id]['range'][1]) + ")"
                    else:
                        rst_val = self.dict[parent_node_id]['hw_rst'] + "(" + str(self.dict[node_id]['range'][0]) + " downto " + str(self.dict[node_id]['range'][1]) + ")"
                    self.dict[node_id]['hw_rst'] = rst_val

    def get_reset_generics(self):
        """OB create generics resets dictionary

        Returns:
            None

        """
        reset_generics_dict = {}
        for node_id in self.get_object(["bitfield", "register_with_bitfield", "register_without_bitfield"]):
            if self.dict[node_id]['hw_rst'] is not None:
                try:
                    int(self.dict[node_id]['hw_rst'], 16)
                except:
                    # print self.dict[node_id]['hw_rst']
                    if not "(" in self.dict[node_id]['hw_rst'] and self.dict[node_id]['hw_rst'] != "no" and self.is_split_register(self.dict[node_id]) is False:
                        lo_idx = self.dict[node_id]['range'][1]
                        hi_idx = self.dict[node_id]['range'][0]
                        if hi_idx == -1:
                            reset_generics_dict[self.dict[node_id]['hw_rst']] = "std_logic"
                        else:
                            reset_generics_dict[self.dict[node_id]['hw_rst']] = "std_logic_vector(" + str(hi_idx - lo_idx) + " downto 0)"
        return reset_generics_dict

    def default_permission(self):
        """OB write default permission where it is not specified

        Returns:
             None

        """
        for node_id in reverse_key_order(self.dict):
            if self.dict[node_id]['permission'] is None:
                self.dict[node_id]['permission'] = 'rw'

    def default_reset(self):
        """OB write default reset where it is not specified

        Returns:
            None

        """
        for node_id in reverse_key_order(self.dict):
            if self.dict[node_id]['hw_rst'] is None:
                self.dict[node_id]['hw_rst'] = "0x0"

    def fill_type(self):
        """OB fill type field

        Returns:
            None

        """
        for node_id in reverse_key_order(self.dict):
            if int(self.dict[node_id]['size']) > self.atom:
                self.dict[node_id]['type'] = "block"
            elif self.dict[node_id]['child_key'] == []:
                if self.dict[node_id]['absolute_offset'] is not None:
                    self.dict[node_id]['type'] = "register_without_bitfield"
                elif self.dict[node_id]['mask'] is not None and int(self.dict[node_id]['size']) == self.atom:
                    self.dict[node_id]['type'] = "bitfield"
                    self.dict[self.dict[node_id]['parent_key']]['type'] = "register_with_bitfield"

    def fill_addressable(self):
        """OB fill addressable field

        An object is addressable if it is:

        * ``block``
        * ``register_with_bitfield``
        * ``register_without_bitfield``
        * ``bitfield``

        Returns:
            None

        """
        for node_id in reverse_key_order(self.dict):
            if self.dict[node_id]['type'] == "block":
                self.dict[node_id]['addressable'] = self.dict[node_id]['absolute_offset']
            elif self.dict[node_id]['type'] == "register_without_bitfield":
                self.dict[node_id]['addressable'] = self.dict[node_id]['absolute_offset']
            elif self.dict[node_id]['type'] == "bitfield":
                self.dict[node_id]['addressable'] = self.dict[self.dict[node_id]['parent_key']]['absolute_offset']
                self.dict[self.dict[node_id]['parent_key']]['addressable'] = self.dict[self.dict[node_id]['parent_key']]['absolute_offset']

    def get_nof_not_ignored_registers(self):
        """OB return number of registers

        Returns:
            (int):

        """
        return len(self.get_object(["register_without_bitfield", "register_with_bitfield"], include_ignored=False))

    def get_nof_not_ignored_blocks(self):
        """OB return number of blocks

        Returns:
            (int):

        """
        return len(self.get_object(["block"], include_ignored=False))

    def check_offset(self):
        """OB check for clashing addresses

        Returns:
            None

        """
        for x in self.get_object(["block", "register_with_bitfield", "register_without_bitfield"]):
            this_dict = self.dict[x]
            this_dict_size = int(this_dict['size']) * self.size_normalizer
            for y in self.get_object(["block", "register_with_bitfield", "register_without_bitfield"]):
                other_dict = self.dict[y]
                other_dict_size = int(other_dict['size']) * self.size_normalizer
                if this_dict['complete_id'] != other_dict['complete_id'] and "$s0_split$" not in this_dict['complete_id'] and "$s0_split$" not in other_dict['complete_id']:
                    if this_dict['addressable'] >= other_dict['addressable'] and this_dict['addressable'] < other_dict['addressable'] + other_dict_size:
                        # TODO Check hex is OK in the following formats.
                        self.logger.error('Error1: conflicting offsets:')
                        self.logger.error('\t{complete_id} {addressable}'
                                          .format(complete_id=this_dict['complete_id'],
                                                  addressable=hex(this_dict['addressable'])))
                        self.logger.error('\t{complete_id} {addressable}'
                                          .format(complete_id=other_dict['complete_id'],
                                                  addressable=hex(other_dict['addressable'])))
                        sys.exit(1)
                    if this_dict['addressable'] + this_dict_size - 1 >= other_dict['addressable'] and this_dict['addressable'] + this_dict_size - 1 < other_dict['addressable'] + other_dict_size:
                        self.logger.error('Error2: conflicting offsets:')
                        self.logger.error('\t{complete_id} at offset {addressable}'
                                          .format(complete_id=this_dict['complete_id'],
                                                  addressable=hex(this_dict['addressable'])))
                        self.logger.error('\t{complete_id} at offset {addressable}'
                                          .format(complete_id=other_dict['complete_id'],
                                                  addressable=hex(other_dict['addressable'])))
                        self.logger.error('Exiting...')
                        sys.exit(1)

    def check_address_requirement(self):
        """OB check that the size of the slave is smaller than absolute offset

        Returns:
            None

        """
        for x in self.get_object(["block"]):
            this_dict = self.dict[x]
            this_addr = this_dict['addressable']
            this_size = int(this_dict['size']) * self.size_normalizer
            if this_addr & (this_size - 1) != 0:
                self.logger.error('It should be (absolute_offset & (size-1)) = 0x0')
                self.logger.error('\t{complete_id} does not meet this requirement!'
                                  .format(complete_id=this_dict['complete_id']))
                self.logger.error('\t{complete_id} absolute offset is: {offset}'
                                  .format(complete_id=this_dict['complete_id'],
                                          offset=hex(this_addr)))
                self.logger.error('\t{complete_id} size is: {bytes}'
                                  .format(complete_id=this_dict['complete_id'],
                                          bytes=this_size))
                self.logger.error('Exiting...')
                sys.exit(1)

    def check_bitfield(self):
        """OB check for clashing bit-field

        Returns:
            None

        """
        for x in self.get_object(["register_with_bitfield"]):
            this_dict = self.dict[x]
            for m in this_dict['child_key']:
                for n in this_dict['child_key']:
                    if m != n:
                        mask_0 = int(self.dict[str(m)]['mask'], 16)
                        mask_1 = int(self.dict[str(n)]['mask'], 16)
                        if mask_0 & mask_1 != 0:
                            self.logger.error('conflicting bitfields!')
                            self.logger.error('\t{complete_id} conflicts with: {conflict_id}'
                                              .format(complete_id=self.dict[str(m)]['complete_id'],
                                                      conflict_id=self.dict[str(n)]['complete_id']))
                            self.logger.error('Exiting...')
                            sys.exit(1)

    def check_reserved_words(self):
        """OB check for reserved words occurrence

        Returns:
            None

        """
        for node_id in self.dict.keys():
            if string.lower(self.dict[node_id]['this_id']) in reserved_word.vhdl_reserved_words:
                self.logger.error('Keyword: "{id}" is used as node_id!'
                                  .format(id=self.dict[node_id]['this_id']))
                self.logger.error('Exiting...')
                sys.exit(1)

    def is_wide_register(self, node_dict):
        """

        Args:

            node_dict (dict):

        Returns:
            (???):

        """
        ret = False
        # if node_dict['range'] != None:
        #     if node_dict['range'][0] > self.data_bit_size - 1:
        #         ret = True
        if node_dict['mask'] != None:
            if int(node_dict['mask'], 16) > int(self.default_mask,16):
                ret = True
        return ret

    def is_split_register(self, node_dict):
        """

        Args:

            node_dict (dict):

        Returns:
            (???):

        """
        ret = False
        if node_dict['split'] != None:
            if int(node_dict['split']) >= 0:
                ret = True
        return ret

    def get_split_splice(self, node_dict):
        """

        Args:

            node_dict (dict):

        Returns:
            (???):

        """
        if node_dict['split'] == None:
            return -1
        else:
            return int(node_dict['split'])

