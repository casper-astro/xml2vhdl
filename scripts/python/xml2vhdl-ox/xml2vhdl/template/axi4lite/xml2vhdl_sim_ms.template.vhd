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

library axi4lite;
use axi4lite.axi4lite_pkg.all;

entity axi4lite_<SLAVE_NAME>_sim_ms is
   port(
      <BUS_CLK> : in std_logic; 
      <BUS_RST> : in std_logic; 
      
      axi4lite_mosi : out t_axi4lite_mosi;
      axi4lite_miso : in t_axi4lite_miso
   );
end entity;

architecture sim of axi4lite_<SLAVE_NAME>_sim_ms is

begin

   process
      --
      -- initialization procedure 
      --
      procedure init is 
      begin
         axi4lite_mosi.arvalid <= '0';
         axi4lite_mosi.araddr <= (others=>'0');
         axi4lite_mosi.rready <= '0';
         axi4lite_mosi.awvalid <= '0';
         axi4lite_mosi.awaddr <= (others=>'0');
         axi4lite_mosi.wdata <= (others=>'0');
         axi4lite_mosi.wvalid <= '0';
         axi4lite_mosi.bready <= '1';
         axi4lite_mosi.wstrb <= (others=>'1');
         wait until <BUS_RST> = not('<BUS_RST_VAL>') and rising_edge(<BUS_CLK>);
         wait until rising_edge(<BUS_CLK>);
         wait until rising_edge(<BUS_CLK>);
         wait until rising_edge(<BUS_CLK>);
      end procedure;
      --
      -- read procedure 
      --
      procedure rd32(add: in std_logic_vector(31 downto 0); dat: inout std_logic_vector(31 downto 0)) is
      begin
         axi4lite_mosi.arvalid <= '1';
         axi4lite_mosi.araddr <= add;
         wait until rising_edge(<BUS_CLK>) and axi4lite_miso.arready = '1';
         axi4lite_mosi.arvalid <= '0';
         axi4lite_mosi.rready <= '1';
         wait until rising_edge(<BUS_CLK>) and axi4lite_miso.rvalid = '1';
         axi4lite_mosi.rready <= '0';
         dat := axi4lite_miso.rdata;
         wait until rising_edge(<BUS_CLK>);
      end procedure;
      --
      -- write procedure 
      --
      procedure wr32(add: in std_logic_vector(31 downto 0); dat: in std_logic_vector(31 downto 0)) is
         variable done: std_logic_vector(2 downto 0):="000";
      begin
         axi4lite_mosi.awvalid <= '1';
         axi4lite_mosi.awaddr <= add;
         axi4lite_mosi.wdata <= dat;
         axi4lite_mosi.wvalid <= '1';
         axi4lite_mosi.wstrb <= (others=>'1');
         wait_loop: loop 
            if axi4lite_miso.awready = '1' then
               done(0) := '1';
               axi4lite_mosi.awvalid <= '0';
            end if;
            if axi4lite_miso.wready = '1' then
               done(1) := '1';
               axi4lite_mosi.wvalid <= '0';
            end if; 
            if axi4lite_miso.bvalid = '1' then
               done(2) := '1';
            end if; 
            wait until rising_edge(<BUS_CLK>);
            if done = "111" then
               exit wait_loop;
            end if;
         end loop;
      end procedure;

      variable rdata: std_logic_vector(31 downto 0);
      
   begin
      init;
      
      wr32(<TB_ADD>,X"0000_0000");
      -- Here data has been written to your slave
      -- at requested address
      rd32(<TB_ADD>,rdata);
      -- Here the variable rdata contains read data 
      -- from your slave at requested address 

   end process;

end architecture;
