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
"""
Interactive script to search the mapping of the error codes sent on eBus
with the codes displayed on the boiler.
"""
# Standard imports
import subprocess
from time import sleep
from pathlib import Path

# Custom imports
import argparse
from colorama import Fore


EBUSCTL_BIN_PATH = "~/ebusd/build/src/tools/ebusctl"
LOG_FILE = "errors_dump.log"
# Update this set with the expected codes from the user manual of your boiler.
# See :meth:`compare_with_expected_errors` function.
EXPECTED_ERRORS = {
    # Primary circuit
    "101", "103", "104", "105", "106", "107", "108", "110", "112", "114", "116", "118", "1P1", "1P2", "1P3",
    # Sanitary circuit
    "201", "203", "205", "209",
    # Internal motherboard
    "301", "302", "303", "304", "305", "306", "307", "3P9",
    # External motherboard (ambient probe)
    "411", "412", "413",
    # Ignition
    "501", "502", "504", "5P1", "5P2", "5P3",
    # Air inlet / smoke outlet
    "610", "612",
    # MCD (not enabled/compatible on Mira C Green)
    #"701", "702", "703", "711", "712", "713", "722", "723", "750"
}


def run_write_command_and_check_output(
    error_code: str, cmd="2004", expected_value="done broadcast", written_value="02", simulate=False
) -> bool:
    """Execute the write command and check the output

    Ex:
        ebusctl hex fe 2004 04 ec 02

    :param error_code: Error code value (1 byte in hex format)
    :key cmd: Command used to read a register on the boiler. (Default: 2004).
    :key expected_value: Expected value from ebusctl program in case of success.
    :key written_value: Value used to trigger the error. (Default: 02, i.e. Not for a zone error).
        See :meth:`generate_errors`.
    :key simulate: If True, just print the ebusctl command without sending it
        on the bus. (Default: False).
    :type error_code: <str>
    :type cmd: <str>
    :type expected_value: <str>
    :type written_value: <str>
    :type simulate: <bool>
    :return: The status of the command ; False in case of error
    """
    packet_length = "{0:02x}".format((len(error_code) + len(written_value)) // 2)

    if cmd == "2034":
        # Just want to send fe203400
        packet_length = ""

    command = f"{EBUSCTL_BIN_PATH} hex fe{cmd}{packet_length}{error_code}{written_value}"

    if simulate:
        print(command)
        return True

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


def send_bus_reset() -> bool:
    """Send bus reset command fe203400

    :return: The status of the command ; False in case of error.
    """
    return run_write_command_and_check_output("", cmd="2034", written_value="00")


def dump_results(error_code, reported_code, *args):
    """Dump the given hex code & human readable code in the log file

    :param error_code: hex representation of the ebus code
    :param reported_code: numeric representation of the code showed on the boiler
    :type error_code: <str>
    :type reported_code: <str>
    """
    with open(LOG_FILE, "a", encoding="utf8") as f_d:
        f_d.write(f"{error_code},{reported_code}," + ",".join(args) + "\n")


def load_results():
    """Get hex codes and human readable codes from the log file

    .. note:: Already known codes and codes that trigger a bus reset
        ARE loaded, and thus not tested if passed to :meth:`generate_errors`.

    :return: List of tuples that contain the 2 codes (hex, code seen on the boiler).
    :rtype: <list <tuple <str, str>>>
    """
    if not Path(LOG_FILE).exists():
        print("Log file doesn't exist.")
        return

    with open(LOG_FILE, "r", encoding="utf8") as f_d:
        # RESET status is imported but not the others
        error_codes = [
            splitted[:2]
            for line in f_d.readlines()
            if not frozenset(("SKIPPED", "ERROR")) & set(splitted := line.split(","))
        ]
    return error_codes


def sort_results():
    """Sort the log file content according to the hex error code

    .. note:: Also remove duplicates
    .. warning:: File is modified in place
    .. todo:: Once a code is found, also remove previous attempts (skipped, error)
    """
    logfile = Path(LOG_FILE)

    if not logfile.exists():
        return

    # Sort & remove duplicates
    results = sorted(set(logfile.read_text(encoding="utf8").split()))

    logfile.write_text("\n".join(results), encoding="utf8")


def generate_errors(error_codes=tuple(), start=0, end=255, zone_commands=False):
    """Broadcast errors & waits for the user to enter the code displayed on the boiler

    Codes are usually stored on 1 byte. There are 256 possible codes.
    start & end arguments can be set to reduce the search space.

    Results are stored in the log file.

    User can skip the current code or quit at any time.
    Each error code is reset before the next test.
    If the reset is not effective, a bus reset can be triggered.

    :key error_codes: Accept a list of known codes, that will NOT be tested.
        See :meth:`load_results`.
    :key start: 1st byte value searched. Should be >= 0
    :key end: last byte value searched. Should be <= 255
    :key zone_commands: Zone commands have a special 2nd byte after the error
        code which contains the zone flag (id of the zone).
        The reset of these errors is made with this byte without the zone flag.

        The LSB (called zone_enable) seems to be always set for this kind of
        commands (when enabling AND disabling zone errors).

    :type error_codes: <list <tuple <str>, <str>>>
    :type start: <int>
    :type end: <int>
    :type zone_commands: <bool>
    :raise: AssertionError if start or end arguments are out of the scope
    """
    assert start >= 0 and end <= 255

    # Add zone_enable flag to values if required
    trigger_value = "03" if zone_commands else "02"
    reset_value = "01" if zone_commands else "00"

    # Get only hex codes
    error_codes = set(list(zip(*error_codes))[0]) if error_codes else set()

    for error_code in range(start, end + 1):
        error_code = f"{error_code:02x}"

        # Skip if code is already known or if it causes bus reset
        if error_code in error_codes:
            continue

        print(Fore.LIGHTRED_EX + f"Tested code: {error_code}" + Fore.RESET)
        if not run_write_command_and_check_output(
            error_code, written_value=trigger_value
        ):
            print("ERROR")
            dump_results(error_code, "ERROR")
            continue

        ret = input("Displayed code ? (Press Enter to skip) [<code>/s/q] ").lower()

        # Skipped by default
        if ret in ("s", "") or len(ret) != 3:
            # Nothing showed ("---"), skip to the next code
            # PS: those errors can't be reset unless a reset command is sent
            dump_results(error_code, "SKIPPED")
            print("skipped...")
            continue
        if ret == "q":
            break

        reported_code = ret.upper()

        # Try to reset the error
        # 2 packets to be sure
        run_write_command_and_check_output(error_code, written_value=reset_value)
        sleep(1)
        run_write_command_and_check_output(error_code, written_value=reset_value)

        ret = input(
            "Error code gone ? [Y/n]\n"
            "Note: If this doesn't work, it doesn't prevent other errors from being tested. "
        ).lower()

        if ret in ("n",):
            ret = input("Do you want to initiate a bus reset ? [Y/n] ").lower()
            if ret in ("n",):
                continue

            print("Resetting...")
            send_bus_reset()
            # Keep the returned code, add 3rd column to indicate that the user
            # asked a bus reset
            dump_results(error_code, reported_code, "RESET")

            _ = input("Reset done ? [Y/n] ").lower()
            continue

        dump_results(error_code, reported_code)


def compare_with_expected_errors(error_codes):
    """Displayed missing & extra codes with respect to the expected codes

    .. note:: Only use human readable codes / codes as seen on the boiler.
        See the global variable EXPECTED_ERRORS and update it with the expected
        codes from the user manual of your boiler.

    :param error_codes: Accept a list of known codes.
        See :meth:`load_results`.
    """
    # Get only human readable codes
    reported_code = set(list(zip(*error_codes))[1]) if error_codes else set()

    missing_codes = sorted(EXPECTED_ERRORS - reported_code)
    print("Missing codes:\n", missing_codes)

    excess_codes = sorted(reported_code - EXPECTED_ERRORS)
    print("Excess codes:\n", excess_codes)


def to_csv_template(error_codes):
    """Convert the mapping to a string ready to be inserted in the ebusd
    `_templates.csv` config file.

    Ex:
        "0=101;2:1P1"

    :param error_codes: Accept a list of known codes.
        See :meth:`load_results`.
    :return: The template string.
    :rtype: <str>
    """
    if not error_codes:
        raise ValueError("Empty error_codes")

    template_str = ";".join(
        [f"{k}={v}" for k, v in {int(k, 16): v for k, v in error_codes}.items()]
    )

    print("CSV template string:\n", template_str)
    return template_str


def args_to_param(args):
    """Return argparse namespace as a dict {variable name: value}"""
    return {k: v for k, v in vars(args).items() if k not in ("func", "verbose")}


def find_errors(start, end, *args, **kwargs):
    """Broadcast errors & waits for the user to enter the code displayed on the boiler.
    Results are stored in the log file defined in LOG_FILE.

    User can skip the current code or quit at any time.
    Each error code is reset before the next test.
    If the reset is not effective, a bus reset can be triggered.
    """
    # One of the 2 following functions...
    # The important thing is that error codes must be reset
    # with compatible commands that raised them.
    # i.e always use one or the other.
    # generate_errors(load_results(), start=start, end=end)
    generate_errors(load_results(), start=start, end=end, zone_commands=True)

    # Reorder results file
    sort_results()


def analysis():
    """Display missing & extra codes vs the expected ones defined in EXPECTED_ERRORS ;
    Output mapped errors for ebusd config file : _templates.csv.
    """
    # Reorder results file
    sort_results()

    # Display missing & extra codes vs the expected ones defined in EXPECTED_ERRORS
    compare_with_expected_errors(load_results())

    # Output mapped errors for ebusd config file : _templates.csv
    to_csv_template(load_results())


def main():
    """Entry point and argument parser"""

    def get_formatter_class(prog):
        """Limit help width"""
        return argparse.HelpFormatter(prog, max_help_position=80, width=80)

    parser = argparse.ArgumentParser(formatter_class=get_formatter_class)

    # Subparsers
    subparsers = parser.add_subparsers(title="subcommands")

    parser_bf = subparsers.add_parser(
        "find_errors",
        help=find_errors.__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser_bf.add_argument(
        "-s",
        "--start",
        help="Start value for code search (0 <= val <= 255)",
        type=int,
        default=0,
    )
    parser_bf.add_argument(
        "-e",
        "--end",
        help="End value for code search (0 <= val <= 255)",
        type=int,
        default=128,
    )
    parser_bf.set_defaults(func=find_errors)

    parser_analysis = subparsers.add_parser(
        "analysis",
        help=analysis.__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser_analysis.set_defaults(func=analysis)

    # Get program args and launch associated command
    args = parser.parse_args()
    if "func" not in dir(args):
        # Nor argument
        parser.print_usage()
        raise SystemExit(1)

    args.func(**args_to_param(args))


if __name__ == "__main__":
    main()
