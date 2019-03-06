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
library <DSN_LIBRARY>;
use <DSN_LIBRARY>.<BUS>_<TOP_LEVEL>_ic_pkg.all;
use <DSN_LIBRARY>.<BUS>_<TOP_LEVEL>_mmap_pkg.all;

entity <BUS>_<TOP_LEVEL>_example is
   port(
      <BUS_CLK> : in std_logic;
      <BUS_RST> : in std_logic;
      
      <BUS>_mosi      : in  t_<BUS>_mosi;       -- signals from master to interconnect
      <BUS>_miso      : out t_<BUS>_miso        -- signals from interconnect to master
   );
end entity;

-------------------------------------------------------------------------------
-- Architecture
-------------------------------------------------------------------------------
architecture struct of <BUS>_<TOP_LEVEL>_example is
   
   signal <BUS>_mosi_arr  : t_<BUS>_mosi_arr(0 to c_axi4lite_mmap_nof_slave-1);   -- signals from interconnect to slaves
   signal <BUS>_miso_arr  : t_<BUS>_miso_arr(0 to c_axi4lite_mmap_nof_slave-1);   -- signals from slaves to interconnect
   
begin
   
   <BUS>_<TOP_LEVEL>_ic_inst: entity work.<BUS>_<TOP_LEVEL>_ic
   port map (
      <BUS_CLK> => <BUS_CLK>,
      <BUS_RST> => <BUS_RST>,
      <BUS>_mosi => <BUS>_mosi,
      <BUS>_mosi_arr => <BUS>_mosi_arr,
      <BUS>_miso_arr => <BUS>_miso_arr,
      <BUS>_miso => <BUS>_miso
   );
<SLAVE_INST>

end architecture;
