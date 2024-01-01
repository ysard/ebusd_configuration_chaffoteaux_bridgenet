#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Ysard
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Proof of concept to find heating activation register on eBus boilers

TL;DR: We are searching for the register 1919 for the Mira C Green boiler
(see the doc to learn what it is).

This register seems to be sent only by an eBus thermostat.
The boiler doesn't broadcast its status.

People without "smart" thermostat (i.e ON/OFF thermostat with dry contact
connected to the TA1 pins of the boiler's motherboard) can't guess the register
without such a bruteforce script.

Dependencies:
    - colorama
      pip3 install --user (--break-system-packages) colorama
      Use --break-system-packages if you know what you are doing
      and not working inside a virtual env.

      Or remove string coloration feature.
"""
# Standard imports
import subprocess
import itertools as it
from time import sleep
# pylint: disable=redefined-builtin
from sys import exit

# Custom imports
from colorama import Fore


EBUSCTL_BIN_PATH = "~/ebusd/build/src/tools/"


def run_command_and_check_output(register, expected_value="020100"):
    """Execute the read command and check the output"""

    command = f"{EBUSCTL_BIN_PATH}ebusctl hex 3c200002{register}"
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=True
        )
        return result.stdout.strip() == expected_value
    # pylint: disable=invalid-name
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error output: {e.output}")
        return False


def run_write_command_and_check_output(register, expected_value="00", written_value="01"):
    """Execute the write command and check the output

    Ex:
        ebusctl hex 3c 2020 03 0120 01
    """

    command = f"~/ebusd/build/src/tools/ebusctl hex 3c202003{register}{written_value}"
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=True
        )
        return result.stdout.strip() == expected_value
    # pylint: disable=invalid-name
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error output: {e.output}")
        return False


def show_progress(register, index, total):
    """Display current register and global progression percentage"""

    print(f"0x{register}")
    progress_percentage = (index / total) * 100
    print(Fore.YELLOW + f"Progress: {progress_percentage:.2f}%" + Fore.RESET)


def read_bruteforce(not_wanted_registers=tuple(), wanted_registers=tuple(), boiler_active=False):
    """Search registers for which values are dependent on boiler status

    :param not_wanted_registers: Already known registers
    :param wanted_registers: Search only in this iterable of registers.
    :param boiler_active: Boolean that defines the boiler status.
        If True, registers with a value of 1 are searched.
        If False, registers with a value of 0 are searched.
    :type not_wanted_registers: <iterable>, <set> or <list> or <tuple>
    :type wanted_registers: <iterable>, <set> or <list> or <tuple>
    :type boiler_active: <boolean>
    """
    expected_value = "020101" if boiler_active else "020100"

    # Store the valid values of XX and YY
    valid_registers = set()

    byte1_end = 128
    byte2_end = 256

    # Force lowercase from user data
    not_wanted_registers, wanted_registers = [
        set(map(str.lower, user_data))
        for user_data in (not_wanted_registers, wanted_registers)
    ]

    total_combinations = byte1_end * byte2_end

    # Test all combinations of XX with YY
    for index, (xx, yy) in enumerate(it.product(range(byte1_end), range(byte2_end)), 1):
        current_register = f"{xx:02x}{yy:02x}"
        if current_register in not_wanted_registers:
            continue
        if wanted_registers and current_register not in wanted_registers:
            continue
        if run_command_and_check_output(current_register, expected_value=expected_value):
            valid_registers.add(current_register)

            show_progress(current_register, index, total_combinations)
        # Do not reduce too much, if you do not want unexpected reboot of the boiler
        # Due to nasty wiring on eBus ?
        sleep(0.200)

    print(sorted(valid_registers), "number:", len(valid_registers))

    return valid_registers


def write_process(registers):
    """Write and test written values in the given registers"""

    valid_registers = set()

    # Test if registers have the expected default value before doing anything nasty...
    print("Checking before the write process...")

    checked_registers = set()
    for index, register in enumerate(sorted(registers), 1):

        if run_command_and_check_output(register, expected_value="020100"):
            checked_registers.add(register)

            show_progress(register, index, len(registers))
        else:
            print("Fail pre-check:", register)

        sleep(0.200)

    # Write in registers
    print("Writing process...")

    for index, register in enumerate(sorted(checked_registers), 1):

        # Write in register
        if run_write_command_and_check_output(register, written_value="01"):
            valid_registers.add(register)

            show_progress(register, index, len(checked_registers))
        else:
            print("Fail write:", register)

        sleep(0.200)

    # Test the modifications
    print("Checking of the write process...")

    checked_registers = set()
    for index, register in enumerate(sorted(valid_registers), 1):

        if run_command_and_check_output(register, expected_value="020101"):
            checked_registers.add(register)

            show_progress(register, index, len(valid_registers))
        else:
            print("Fail check:", register)

        sleep(0.200)

    print(
        "Expected & checked registers:", sorted(checked_registers),
        "number:", len(checked_registers),
    )
    failed_registers = set(registers) - checked_registers
    print("Failed registers:", sorted(failed_registers), "number;", len(failed_registers))

    return checked_registers


def reset_values(registers, initial_value="00"):
    """Reset previous/default value (00) of the given registers"""

    print("Restoring previous values...")
    for index, register in enumerate(sorted(registers), 1):

        # Write in register
        if run_write_command_and_check_output(register, written_value=initial_value):
            show_progress(register, index, len(registers))

        sleep(0.200)


def write_bruteforce(registers):
    """Try to find activation candidates of the boiler among the given registers"""

    def chunk_this(iterable, length):
        """Split iterable in chunks of equal sizes"""

        iterator = iter(iterable)
        for _ in range(0, len(iterable), length):
            yield tuple(it.islice(iterator, length))

    def registers_test_loop(registers):
        """Recursive loop over chunks of registers to test the boiler reaction"""

        expected_length = len(registers) // 10 if len(registers) // 10 else 1
        for chunk in chunk_this(registers, expected_length):

            checked_registers = sorted(write_process(chunk))

            ret = input(
                Fore.LIGHTGREEN_EX + "Did the boiler start ? [Y/n] " + Fore.RESET
            ).lower()
            # Facultative ?? No ! Beware !
            # Mandatory for next tests !
            sleep(2)
            reset_values(checked_registers)

            if not ret in ("y", "o"):
                continue

            # Here, boiler is started thanks to at least 1 register in our chunk
            if not checked_registers:
                continue
            if len(checked_registers) == 1:
                print(Fore.LIGHTRED_EX + "Found candidate:", checked_registers)
                ret = input("Continue ? [Y/n] " + Fore.RESET).lower()
                if not ret in ("y", "o"):
                    return
                continue

            registers_test_loop(checked_registers)

    registers_test_loop(sorted(registers))


if __name__ == "__main__":

    # Set of registers with a value of 1 if the boiler is active.
    # 1919 is the searched register, it is in the set since I use an eBus thermostat...
    # Otherwise you should search registers with 0 value when the boiler is active
    # AND in standby mode.
    # (this register is invariable unless it is modified from an eBus device).
    # pylint: disable=line-too-long
    wanted_registers = {'1683', '1723', '0d23', '1f23', '1423', '1e23', '1321', '0886', '0b21', '1a83', '1283', '0021', '1785', '1f86', '0211', '1188', '0321', '0125', '1f84', '0524', '0f86', '0987', '1886', '1d83', '0784', '0884', '0f88', '1783', '1925', '1388', '1124', '0181', '0a23', '1182', '0587', '1086', '0064', '0583', '1981', '1c24', '0a25', '0287', '1a25', '1183', '1621', '0825', '0588', '0a81', '0ba0', '1f22', '1f21', '0683', '0d87', '1083', '0425', '0b86', '1788', '1a21', '1b82', '0467', '1982', '0545', '0c23', '07a0', '1488', '0686', '0286', '1e87', '1b86', '1923', '0b11', '0187', '0d25', '1588', '0981', '0e21', '1721', '1987', '0a82', '1687', '0f85', '0224', '0c81', '1481', '0c88', '1325', '0983', '1523', '0464', '1884', '1286', '0d81', '1887', '1684', '0887', '0324', '1b25', '0c21', '1d25', '0685', '1424', '0a88', '1323', '1787', '1c87', '1c25', '1285', '1688', '0824', '1786', '0222', '0881', '1782', '0988', '0a84', '0424', '0a86', '1983', '1d23', '1486', '0985', '0001', '0783', '0282', '1585', '0982', '1a84', '1f87', '1ba0', '00a4', '1e83', '0f82', '1082', '0923', '1187', '1b81', '1624', '1287', '0823', '0184', '1386', '0c87', '1c81', '1e21', '0281', '1288', '0288', '0b24', '1024', '0e85', '1282', '0688', '1686', '0d21', '0785', '0724', '0924', '1e86', '0285', '0782', '0883', '1a81', '0191', '1e25', '1e81', '1a88', '0045', '0b87', '0d88', '1d82', '1383', '0586', '0781', '1581', '1d88', '1487', '1f85', '0d86', '0183', '0223', '1f82', '1a86', '0c85', '1888', '1582', '0c84', '0625', '1d85', '1882', '0a85', '1d86', '1984', '0e87', '1a24', '1421', '1986', '0069', '1387', '0f81', '1da0', '1825', '0023', '1a85', '0a87', '0020', '1623', '1c85', '1025', '1084', '1088', '0284', '1d87', '1584', '0c25', '1821', '1121', '1c82', '1e84', '1b24', '0421', '1583', '1a23', '1485', '0925', '1425', '1b21', '0984', '0725', '0b81', '0d83', '0423', '0a83', '1883', '1625', '0681', '0f25', '0c86', '0225', '0687', '0185', '1885', '0787', '1a82', '1384', '1681', '1184', '0986', '0682', '1420', '1482', '0a19', '0a24', '1081', '1385', '1e82', '0f87', '11a0', '0d84', '0e11', '1123', '1381', '0624', '1125', '0025', '0f84', '0b88', '1221', '1320', '1b87', '1021', '0921', '1d24', '1725', '0d85', '0024', '0b23', '0088', '0f21', '1524', '0c83', '0121', '1f83', '1b83', '1367', '0d24', '1b84', '1781', '1c21', '1919', '0f24', '0111', '1382', '1525', '1682', '0623', '1284', '1223', '0e24', '1e22', '1f25', '1988', '1085', '0c82', '0882', '0b85', '0888', '0f23', '0123', '1185', '0581', '0d82', '1e88', '0525', '0786', '1f81', '1a87', '1484', '14a0', '1224', '1b23', '0323', '1921', '1b85', '0b25', '0e81', '1220', '0325', '0721', '0188', '0584', '1225', '0e86', '1e85', '0e82', '1824', '0820', '1483', '1520', '0523', '0e83', '1685', '1324', '1186', '1b88', '0221', '0621', '0821', '0a21', '0e25', '0585', '0c24', '1281', '1d81', '1d22', '1087', '0f83', '1c22', '0041', '1767', '1823', '0283', '1f24', '1c86', '1c88', '1c83', '1e24', '1521', '1d84', '0767', '1467', '1724', '1e45', '0684', '0b83', '1c23', '0723', '0521', '1924', '1d21', '0e88', '0788', '1881', '1586', '0b82', '1181', '0582', '0186', '1587', '1784', '0124', '0e23', '1c84', '1f88', '0e84', '0885', '1023', '0b84', '1985'}

    # Already known registers except 0191, 1919
    # pylint: disable=line-too-long
    not_wanted_registers = {"0291", "0391", "0491", "0591", "0691", "0791", "0081", "0082", "0083", "0084", "0085", "0086", "0087", "6197", "6297", "6397", "6497", "6597", "6697", "6797", "6071", "6072", "6073", "6074", "6075", "6076", "6077", "6171", "6172", "6173", "6174", "6175", "6176", "6177", "6271", "6272", "6273", "6274", "6275", "6276", "6277", "6371", "6372", "6373", "6374", "6375", "6376", "6377", "6471", "6472", "6473", "6474", "6475", "6476", "6477", "6571", "6572", "6573", "6574", "6575", "6576", "6577", "6671", "6672", "6673", "6674", "6675", "6676", "6677", "6771", "6772", "6773", "6774", "6775", "6776", "6777", "6971", "6972", "6973", "6974", "6975", "6976", "6977", "6a71", "6a72", "6a73", "6a74", "6a75", "6a76", "6a77", "6b71", "6b72", "6b73", "6b74", "6b75", "6b76", "6b77", "6c71", "6c72", "6c73", "6c74", "6c75", "6c76", "6c77", "c04b", "c079", "c07a", "c07b", "c07c", "c07d", "c07e", "c07f", "c279", "c27a", "c27b", "c27c", "c27d", "c27e", "c27f", "c679", "c67a", "c67b", "c67c", "c67d", "c67e", "c67f", "c979", "c97a", "c97b", "c97c", "c97d", "c97e", "c97f", "6810", "6910", "602b", "4013", "c028", "6126", "6147", "d746", "da46", "dc46", "de46", "0b20", "0f20", "0120", "0220", "0520", "d140", "50d9", "42d8", "7647", "7426", "7118", "7218", "7318", "7418", "7518", "7618", "7718", "0c19", "4bd1", "6047", "6d26", "6f10", "7526", "c528", "6226", "6426", "6bc0", "2b70", "6997", "6a97", "6b97", "6c97", "6d97", "6e97", "6f97", "7997", "7a97", "7b97", "7c97", "7d97", "7e97", "7f97", "0119", "0219", "0319", "0419", "0519", "0619", "0719", "0990", "0a90", "0b90", "0c90", "0d90", "0e90", "0f90"}


    # Among these registers search the registers that have a value of 0
    # if the boiler is on standby.
    potential_registers = read_bruteforce(
        wanted_registers=wanted_registers,
        not_wanted_registers=not_wanted_registers,
        boiler_active=False,
    )
    ret = input(
        Fore.LIGHTGREEN_EX
        + "Continue with the write bruteforce of the registers found ?\n"
        "If Yes, the boiler and the heating must be waiting a heating request\n"
        "(0120 register should be active for Mira C green) [Y/n] "
        + Fore.RESET
    ).lower()

    if not ret in ("y", "o"):
        exit()

    write_bruteforce(potential_registers)
