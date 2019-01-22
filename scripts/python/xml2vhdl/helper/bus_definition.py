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
