# -*- coding: utf8 -*-
"""

*****************************
``helper/bus_definitions.py``
*****************************

`GNU General Public License v3`_ © 2015-2019 University of Oxford & contributors

.. _GNU General Public License v3: _static/LICENSE

``bus_definitions.py`` is a helper module provided to define bus definitions for generated ``AXI4-Lite``
connections.

"""
class BusDefinition:
    def __init__(self, configuration=0):
        if configuration == 0:
            self.name = "axi4lite"
            self.clock = "axi4lite_aclk"
            self.reset = "axi4lite_aresetn"
            self.reset_val = "0"
            self.mosi_type = "t_axi4lite_mosi"
            self.miso_type = "t_axi4lite_miso"
            self.data_bit_size = 32
            self.data_byte_size = self.data_bit_size / 8
            self.slave_generics = []
            self.size_indicate_bytes = 0
            self.add_prefix = True
            self.atom = self.get_atom()
            self.bus_prefix = self.get_bus_prefix()

        if configuration == 1:
            self.name = "wb"
            self.clock = "wb_clk"
            self.reset = "wb_rst"
            self.reset_val = "1"
            self.mosi_type = "wb_m2s_type"
            self.miso_type = "wb_s2m_type"
            self.data_bit_size = 16
            self.data_byte_size = self.data_bit_size / 8
            self.slave_generics = [{'name': "WB_MAP", 'type': "WB_SLAVE_C"}]
            self.size_indicate_bytes = 1
            self.add_prefix = False
            self.atom = self.get_atom()
            self.bus_prefix = self.get_bus_prefix()

        if configuration == 2:
            self.name = "wb"
            self.clock = "wb_clk"
            self.reset = "wb_rst"
            self.reset_val = "1"
            self.mosi_type = "wb_m2s_type"
            self.miso_type = "wb_s2m_type"
            self.data_bit_size = 32
            self.data_byte_size = self.data_bit_size / 8
            self.slave_generics = [{'name': "WB_MAP", 'type': "WB_SLAVE_C"}]
            self.size_indicate_bytes = 1
            self.add_prefix = False
            self.atom = self.get_atom()
            self.bus_prefix = self.get_bus_prefix()

    def get_atom(self):
        if self.size_indicate_bytes == 0:
            atom = 1
        else:
            atom = self.data_byte_size
        return atom

    def get_bus_prefix(self):
        if self.add_prefix:
            prefix = self.name + "_"
        else:
            prefix = ""
        return prefix
