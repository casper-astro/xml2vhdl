-- This file is part of XML2VHDL
-- Copyright (C) 2015
-- University of Oxford <http://www.ox.ac.uk/>
-- Department of Physics
-- 
-- This program is free software: you can redistribute it and/or modify  
-- it under the terms of the GNU General Public License as published by  
-- the Free Software Foundation, version 3.
--
-- This program is distributed in the hope that it will be useful, but 
-- WITHOUT ANY WARRANTY; without even the implied warranty of 
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
-- General Public License for more details.
--
-- You should have received a copy of the GNU General Public License 
-- along with this program. If not, see <http://www.gnu.org/licenses/>.

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library <BUS_LIBRARY>;
use <BUS_LIBRARY>.<BUS>_pkg.all;
library <SLAVE_LIBRARY>;
use <SLAVE_LIBRARY>.<BUS_PREFIX_><SLAVE_NAME>_pkg.all;
     
entity <BUS>_<SLAVE_NAME> is
<GENERICS_DEFINITION>
   port(
      <BUS_CLK> : in std_logic;
      <BUS_RST> : in std_logic;
      
      <BUS>_mosi : in <BUS_MOSI_TYPE>;
      <BUS>_miso : out <BUS_MISO_TYPE>;
<MEMORY_BLOCKS_PORT>
<REMOVE_IF_BLOCK_ONLY_START>
<REMOVE_IF_NO_FW_WRITE_START>
      <BUS_PREFIX_><SLAVE_NAME>_in_we : in t_<BUS_PREFIX_><SLAVE_NAME>_decoded;
      <BUS_PREFIX_><SLAVE_NAME>_in : in t_<BUS_PREFIX_><SLAVE_NAME>;
<REMOVE_IF_NO_FW_WRITE_END>
      <BUS_PREFIX_><SLAVE_NAME>_out_we : out t_<BUS_PREFIX_><SLAVE_NAME>_decoded;
      <BUS_PREFIX_><SLAVE_NAME>_out : out t_<BUS_PREFIX_><SLAVE_NAME>;
<REMOVE_IF_BLOCK_ONLY_END>
);
end entity;     

architecture <BUS>_<SLAVE_NAME>_a of <BUS>_<SLAVE_NAME> is 

   signal ipb_mosi : t_ipb_mosi;
   signal ipb_miso : t_ipb_miso;
   
   signal ipb_mosi_arr : t_ipb_<SLAVE_NAME>_mosi_arr;
   signal ipb_miso_arr : t_ipb_<SLAVE_NAME>_miso_arr;
   
<REMOVE_IF_BLOCK_ONLY_START>
   signal <BUS_PREFIX_><SLAVE_NAME>_int_we : t_<BUS_PREFIX_><SLAVE_NAME>_decoded;
   signal <BUS_PREFIX_><SLAVE_NAME>_int_re : t_<BUS_PREFIX_><SLAVE_NAME>_decoded;
   signal <BUS_PREFIX_><SLAVE_NAME>_int : t_<BUS_PREFIX_><SLAVE_NAME>;
<REMOVE_IF_BLOCK_ONLY_END>

begin
   --
   --
   --
   <BUS>_slave_logic_inst: entity <BUS_LIBRARY>.<BUS>_slave_logic
<SLAVE_GENERICS_MAP>
   port map (
      <BUS_CLK> => <BUS_CLK>,
      <BUS_RST> => <BUS_RST>,
      <BUS>_mosi => <BUS>_mosi,
      <BUS>_miso => <BUS>_miso,
      ipb_mosi => ipb_mosi,
      ipb_miso => ipb_miso
   );
   --
   -- blocks_muxdemux
   --
   <BUS>_<SLAVE_NAME>_muxdemux_inst: entity <SLAVE_LIBRARY>.<BUS>_<SLAVE_NAME>_muxdemux
   port map(
      <BUS_CLK> => <BUS_CLK>,
      <BUS_RST> => <BUS_RST>,
      ipb_mosi => ipb_mosi,
      ipb_miso => ipb_miso,
      ipb_mosi_arr => ipb_mosi_arr,
      ipb_miso_arr => ipb_miso_arr   
   );
<MEMORY_BLOCKS_INST>
<REMOVE_IF_BLOCK_ONLY_START>
   --
   -- Address decoder
   --
   <BUS_PREFIX_><SLAVE_NAME>_int_we <= <BUS_PREFIX_><SLAVE_NAME>_full_decoder(ipb_mosi_arr(0).addr,ipb_mosi_arr(0).wreq);
   <BUS_PREFIX_><SLAVE_NAME>_int_re <= <BUS_PREFIX_><SLAVE_NAME>_full_decoder(ipb_mosi_arr(0).addr,ipb_mosi_arr(0).rreq);
   --
   -- Register write process
   --
   process(<BUS_CLK>,<BUS_RST>)
   begin
      if rising_edge(<BUS_CLK>) then
         <BUS_PREFIX_><SLAVE_NAME>_out_we <= <BUS_PREFIX_><SLAVE_NAME>_int_we;
         --
         -- Write to registers from logic, put assignments here 
         -- if logic has lower priority than <BUS> bus master 
         --
         -- ...
         --
         -- hw_permission="w" or hw_permission="wen"
         -- hw_prio="bus"
         --
<HW_WRITE_REG_BUS_PRIO>
         --====================================================================
         --
         -- Write to registers from <BUS> side, think twice before modifying
         --
         <BUS_PREFIX_><SLAVE_NAME>_write_reg(ipb_mosi_arr(0).wdat,
                                      <BUS_PREFIX_><SLAVE_NAME>_int_we,
                                      <BUS_PREFIX_><SLAVE_NAME>_int);
         --
         --====================================================================
         --
         -- Write to registers from logic, put assignments here 
         -- if logic has higher priority than <BUS> bus master
         --
         -- ...
         --
         -- hw_permission="w" or hw_permission="wen"
         -- hw_prio="logic"
         --
<HW_WRITE_REG_LOGIC_PRIO>
      end if;
      if <BUS_RST> = '<BUS_RST_VAL>' then
         <BUS_PREFIX_><SLAVE_NAME>_reset(<BUS_PREFIX_><SLAVE_NAME>_int<RESET_GENERICS_MAP>);
      end if;
   end process;
   
   ipb_miso_arr(0).wack <= '1';
   ipb_miso_arr(0).rack <= '1';
   ipb_miso_arr(0).rdat <= <BUS_PREFIX_><SLAVE_NAME>_read_reg(<BUS_PREFIX_><SLAVE_NAME>_int_re,
                                                       <BUS_PREFIX_><SLAVE_NAME>_int);

   <BUS_PREFIX_><SLAVE_NAME>_out    <= <BUS_PREFIX_><SLAVE_NAME>_int; 
   
<REMOVE_IF_BLOCK_ONLY_END>
   
end architecture;

