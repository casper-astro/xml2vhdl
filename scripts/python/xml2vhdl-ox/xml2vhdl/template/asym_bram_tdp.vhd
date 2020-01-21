--<h---------------------------------------------------------------------------
--
-- Copyright (C) 2015
-- University of Oxford <http://www.ox.ac.uk/>
-- Department of Physics
--
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <http://www.gnu.org/licenses/>.
--
-----------------------------------------------------------------------------h>
-- Asymmetric true dual port RAM

library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use ieee.std_logic_arith.all;

entity asym_bram_tdp is
    generic (
        WIDTHA      : integer := 4;
        ADDRWIDTHA  : integer := 10;
        WIDTHB      : integer := 16;
        ADDRWIDTHB  : integer := 8;
        READLATA    : integer range 1 to 2 := 1;
        READLATB    : integer range 1 to 2 := 1;
        INIT        : bit_vector := X""
    );
    port (
        clkA   : in  std_logic;
        clkB   : in  std_logic;
        enA    : in  std_logic;
        enB    : in  std_logic;
        weA    : in  std_logic;
        weB    : in  std_logic;
        addrA  : in  std_logic_vector(ADDRWIDTHA-1 downto 0);
        addrB  : in  std_logic_vector(ADDRWIDTHB-1 downto 0);
        diA    : in  std_logic_vector(WIDTHA-1 downto 0);
        diB    : in  std_logic_vector(WIDTHB-1 downto 0);
        doA    : out std_logic_vector(WIDTHA-1 downto 0);
        doB    : out std_logic_vector(WIDTHB-1 downto 0)
    );
end asym_bram_tdp;

architecture behavioral of asym_bram_tdp is

    function max(L, R: INTEGER) return INTEGER is
    begin
        if L > R then
            return L;
        else
            return R;
        end if;
    end;

    function min(L, R: INTEGER) return INTEGER is
    begin
        if L < R then
            return L;
        else
            return R;
        end if;
    end;

    function log2 (val: INTEGER) return natural is
        variable res : natural;
    begin
        for i in 0 to 31 loop
            if (val <= (2**i)) then
                res := i;
                exit;
            end if;
        end loop;
        return res;
    end function log2;

    constant minWIDTH : integer := min(WIDTHA,WIDTHB);
    constant maxWIDTH : integer := max(WIDTHA,WIDTHB);
    constant SIZEA    : integer := 2**WIDTHA;
    constant SIZEB    : integer := 2**WIDTHB;
    constant maxSIZE  : integer := max(SIZEA,SIZEB);
    constant RATIO    : integer := maxWIDTH / minWIDTH;

    -- An asymmetric RAM is modeled in a similar way as a symmetric RAM, with an
    -- array of array object. Its aspect ratio corresponds to the port with the
    -- lower data width (larger depth)
    type ramType is array (0 to maxSIZE-1) of std_logic_vector(minWIDTH-1 downto 0);

  -- function get_init_word(init: bit_vector; word_index: integer; word_w: integer) return std_logic_vector is
  --   variable lo_idx: integer := word_w*word_index;
  --   variable hi_idx: integer := word_w*(word_index+1)-1;
  --   variable init_i: bit_vector(init'length-1 downto 0) := init;
  -- begin
  --   return To_StdLogicVector(init_i(hi_idx downto lo_idx));
  -- end function;
  --
  -- function get_init return ramType is
  --   variable idx: integer := 0;
  --   variable ret: ramType :=(others => (others => '0'));
  --   variable init_length : integer := init'right - init'left + 1;
  -- begin
  --   if init'length > 0 then
  --      loop0: for n in 0 to maxSIZE-1 loop
  --         if n*minWIDTH-1 > init'length-1 and init_length > 0 then
  --            exit loop0;
  --         else
  --            ret(n) := get_init_word(INIT, n, minWIDTH);
  --         end if;
  --      end loop;
  --   end if;
  --   return ret;
  -- end function;

    shared variable my_ram : ramType := (others => (others => '0'));

    signal readA : std_logic_vector(WIDTHA-1 downto 0):= (others => '0');
    signal readB : std_logic_vector(WIDTHB-1 downto 0):= (others => '0');
    signal regA  : std_logic_vector(WIDTHA-1 downto 0):= (others => '0');
    signal regB  : std_logic_vector(WIDTHB-1 downto 0):= (others => '0');

    attribute ram_style: string;
    attribute ram_style of my_ram: variable is "block";

begin

  g_a_wider: if WIDTHA >= WIDTHB generate
      process(clkA)
      begin
        if rising_edge(clkA) then
            for i in 0 to RATIO-1 loop
              if enA = '1' then
                  if RATIO = 1 then
                    readA((i+1)*minWIDTH-1 downto i*minWIDTH)
        	        <= my_ram(conv_integer(addrA));
                  else
                    readA((i+1)*minWIDTH-1 downto i*minWIDTH)
        	        <= my_ram(conv_integer(addrA & conv_std_logic_vector(i,log2(RATIO))));
                  end if;
              end if;
          end loop;
          regA <= readA;
        end if;
      end process;

      process(clkB)
      begin
        if rising_edge(clkB) then
          if enB = '1' then
            readB <= my_ram(conv_integer(addrB));
          end if;
          regB <= readB;
        end if;
      end process;

      process (clkA)
      begin
        if rising_edge(clkA) then
        for i in 0 to RATIO-1 loop
          if enA = '1' then
              if weA = '1' then
                if RATIO = 1 then
                  my_ram(conv_integer(addrA))
                := diA((i+1)*minWIDTH-1 downto i*minWIDTH);
                else
                  my_ram(conv_integer(addrA & conv_std_logic_vector(i,log2(RATIO))))
                := diA((i+1)*minWIDTH-1 downto i*minWIDTH);
                end if;
              end if;
          end if;
          end loop;
        end if;
      end process;

      process (clkB)
      begin
        if rising_edge(clkB) then
          if enB = '1' then
            if weB = '1' then
              my_ram(conv_integer(addrB)) := diB;
            end if;
          end if;
        end if;
      end process;
  end generate;

  g_b_wider: if WIDTHA < WIDTHB generate
      process(clkA)
      begin
        if rising_edge(clkA) then
          if enA = '1' then
            readA <= my_ram(conv_integer(addrA));
          end if;
          regA <= readA;
        end if;
      end process;

      process(clkB)
      begin
        if rising_edge(clkB) then
            for i in 0 to RATIO-1 loop
              if enB = '1' then
                  if RATIO = 1 then
                    readB((i+1)*minWIDTH-1 downto i*minWIDTH)
                  <= my_ram(conv_integer(addrB));
                  else
                    readB((i+1)*minWIDTH-1 downto i*minWIDTH)
                  <= my_ram(conv_integer(addrB & conv_std_logic_vector(i,log2(RATIO))));
                  end if;
              end if;
          end loop;
          regB <= readB;
        end if;
      end process;

      process (clkA)
      begin
        if rising_edge(clkA) then
          if enA = '1' then
            if weA = '1' then
              my_ram(conv_integer(addrA)) := diA;
            end if;
          end if;
        end if;
      end process;

      process (clkB)
      begin
        if rising_edge(clkB) then
        for i in 0 to RATIO-1 loop
          if enB = '1' then
              if weB = '1' then
                if RATIO = 1 then
                  my_ram(conv_integer(addrB))
    	          := diB((i+1)*minWIDTH-1 downto i*minWIDTH);
                else
                  my_ram(conv_integer(addrB & conv_std_logic_vector(i,log2(RATIO))))
    	          := diB((i+1)*minWIDTH-1 downto i*minWIDTH);
                end if;
              end if;
          end if;
          end loop;
        end if;
      end process;
  end generate;

  READLATA_1_gen: if READLATA = 1 generate
    doA <= readA;
  end generate;
  READLATA_2_gen: if READLATA = 2 generate
    doA <= regA;
  end generate;
  READLATB_1_gen: if READLATB = 1 generate
    doB <= readB;
  end generate;
  READLATB_2_gen: if READLATB = 2 generate
    doB <= regB;
  end generate;

end behavioral;
