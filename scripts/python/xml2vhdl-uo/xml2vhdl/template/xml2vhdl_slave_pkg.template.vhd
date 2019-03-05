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

library <BUS_LIBRARY>;
use <BUS_LIBRARY>.<BUS>_pkg.all;

package <BUS_PREFIX_><SLAVE_NAME>_pkg is 

   --##########################################################################
   --
   -- Register Records
   --
   --##########################################################################
<RECORDS>
   --##########################################################################
   --
   -- Register Decoded Records
   --
   --##########################################################################
<RECORDS_DECODED>
   --##########################################################################
   --
   -- Register Descriptors
   --
   --##########################################################################
   type t_access_type is (r,w,rw);
   type t_reset_type is (async_reset,no_reset);
   
   type t_reg_descr is record
      offset: std_logic_vector(31 downto 0);
      bit_hi: natural;
      bit_lo: natural;
      rst_val: std_logic_vector(<DATA_BUS_BIT_SIZE-1> downto 0);
      reset_type: t_reset_type;
      decoder_mask: std_logic_vector(31 downto 0);
      access_type: t_access_type;
   end record;
   
<DESCRIPTOR_RECORDS>
   
<DESCRIPTOR_RECORDS_INIT>
   --##########################################################################
   --
   -- Constants
   --
   --##########################################################################
   constant c_nof_register_blocks: integer := <NOF_REGISTER_BLOCKS>;
   constant c_nof_memory_blocks: integer := <NOF_MEMORY_BLOCKS>;
   constant c_total_nof_blocks: integer := c_nof_memory_blocks+c_nof_register_blocks;
   
   type t_ipb_<SLAVE_NAME>_mosi_arr is array (0 to c_total_nof_blocks-1) of t_ipb_mosi;
   type t_ipb_<SLAVE_NAME>_miso_arr is array (0 to c_total_nof_blocks-1) of t_ipb_miso;
   
<IPB_MAPPING_RECORD>

<IPB_MAPPING_RECORD_INIT>

   --##########################################################################
   --
   -- Functions
   --
   --##########################################################################
   function <BUS_PREFIX_><SLAVE_NAME>_decoder(descr: t_reg_descr; addr: std_logic_vector) return boolean;
   
   function <BUS_PREFIX_><SLAVE_NAME>_full_decoder(addr: std_logic_vector; en: std_logic) return t_<BUS_PREFIX_><SLAVE_NAME>_decoded;
   
<REMOVE_IF_BLOCK_ONLY_START>
   procedure <BUS_PREFIX_><SLAVE_NAME>_reset(signal <SLAVE_NAME>: inout t_<BUS_PREFIX_><SLAVE_NAME><RESET_GENERICS_PROCEDURE>);
   procedure <BUS_PREFIX_><SLAVE_NAME>_default_decoded(signal <SLAVE_NAME>: inout t_<BUS_PREFIX_><SLAVE_NAME>_decoded);
   procedure <BUS_PREFIX_><SLAVE_NAME>_write_reg(data: std_logic_vector; 
                                          signal <SLAVE_NAME>_decoded: in t_<BUS_PREFIX_><SLAVE_NAME>_decoded;
                                          signal <SLAVE_NAME>: inout t_<BUS_PREFIX_><SLAVE_NAME>);
   
   function <BUS_PREFIX_><SLAVE_NAME>_read_reg(signal <SLAVE_NAME>_decoded: in t_<BUS_PREFIX_><SLAVE_NAME>_decoded;
                                        signal <SLAVE_NAME>: t_<BUS_PREFIX_><SLAVE_NAME>) return std_logic_vector;
<REMOVE_IF_BLOCK_ONLY_END>
   
   function <BUS_PREFIX_><SLAVE_NAME>_demux(addr: std_logic_vector) return std_logic_vector;

end package;

package body <BUS_PREFIX_><SLAVE_NAME>_pkg is
   
   function <BUS_PREFIX_><SLAVE_NAME>_decoder(descr: t_reg_descr; addr: std_logic_vector) return boolean is
      variable ret: boolean:=true;
      variable bus_addr_i: std_logic_vector(addr'length-1 downto 0) := addr;
      variable mask_i: std_logic_vector(descr.decoder_mask'length-1 downto 0) := descr.decoder_mask;
      variable reg_addr_i: std_logic_vector(descr.offset'length-1 downto 0) := descr.offset;
   begin
      for n in 0 to bus_addr_i'length-1 loop
         if mask_i(n) = '1' and bus_addr_i(n) /= reg_addr_i(n) then
            ret := false;
         end if;
      end loop;
      return ret;
   end function;
   
   function <BUS_PREFIX_><SLAVE_NAME>_full_decoder(addr: std_logic_vector; en: std_logic) return t_<BUS_PREFIX_><SLAVE_NAME>_decoded is
      variable <SLAVE_NAME>_decoded: t_<BUS_PREFIX_><SLAVE_NAME>_decoded;
   begin
   
<FULL_DECODER_ASSIGN>
      
      return <SLAVE_NAME>_decoded;
   end function;
     
<REMOVE_IF_BLOCK_ONLY_START>
   procedure <BUS_PREFIX_><SLAVE_NAME>_reset(signal <SLAVE_NAME>: inout t_<BUS_PREFIX_><SLAVE_NAME><RESET_GENERICS_PROCEDURE>) is
   begin
      
<RESET_ASSIGN>

   end procedure;
   
   procedure <BUS_PREFIX_><SLAVE_NAME>_default_decoded(signal <SLAVE_NAME>: inout t_<BUS_PREFIX_><SLAVE_NAME>_decoded) is
   begin
      
<DEFAULT_DECODED>

   end procedure;

   procedure <BUS_PREFIX_><SLAVE_NAME>_write_reg(data: std_logic_vector; 
                                          signal <SLAVE_NAME>_decoded: in t_<BUS_PREFIX_><SLAVE_NAME>_decoded;
                                          signal <SLAVE_NAME>: inout t_<BUS_PREFIX_><SLAVE_NAME>) is
   begin
      
<WRITE_ASSIGN>

   end procedure;
   
   function <BUS_PREFIX_><SLAVE_NAME>_read_reg(signal <SLAVE_NAME>_decoded: in t_<BUS_PREFIX_><SLAVE_NAME>_decoded;
                                        signal <SLAVE_NAME>: t_<BUS_PREFIX_><SLAVE_NAME>) return std_logic_vector is
      variable ret: std_logic_vector(<DATA_BUS_BIT_SIZE-1> downto 0);
   begin
      ret := (others=>'0');
      
<READ_ASSIGN>

      return ret;
   end function;
<REMOVE_IF_BLOCK_ONLY_END>
   
   function <BUS_PREFIX_><SLAVE_NAME>_demux(addr: std_logic_vector) return std_logic_vector is
      variable ret: std_logic_vector(c_total_nof_blocks-1 downto 0);
   begin
      ret := (others=>'0');
      if c_total_nof_blocks = 1 then
         ret := (others=>'1');
      else

<MUX_ASSIGN>
  
      end if;
      return ret;
   end function;

end package body;

