# Copyright (c) 2013 Matthew Rheaume
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

import argparse
import sys

import puz.constants

def _print_select_usage():
	print("""

	USAGE
		<options> <use-flags>

	OPTIONS
		/?
			Show this help screen.

		/v
			Include version in USE flag entry.

		/a
			Append the following flags to the current entry in package.use.

		/s
			Make no changes and skip this package.

	EXAMPLES
		All examples use x11-base/xorg-server-1.12.2 as the package whose USE
		flags are being selected. Current entry in package.use is
		'x11-base/xorg-server ipv6 nptl xorg'.

		Add 'udev' and 'doc' to the current USE flags for x11-base/xorg-server:
			> /a udev doc
		Entry:
			x11-base/xorg-server ipv6 nptl xorg udev doc

		Add 'udev' and '-static-libs' to current USE flags for
		x11-base/xorg-server-1.12.2:
			> /v /a udev -static-libs
		Entries:
			x11-base/xorg-server ipv6 nptl xorg
			x11-base/xorg-server-1.12.2 udev -static-libs

		Clear current entry for x11-base/xorg-server and create a new entry
		with 'udev' and 'doc':
			> udev doc
		Entry:
			x11-base/xorg-server udev doc

		Clear current entry for x11-base/xorg-server-1.12.2 and create new
		entry with 'udev' and 'doc':
			> /v udev doc
		Entry:
			x11-base/xorg-server ipv6 nptl xorg
			x11-base/xorg-server-1.12.2 udev doc

	""")

def _user_confirm():
	res = ""

	while True:
		print("Is this correct? (y/n) ", end="")

		res = sys.stdin.readline()
		res = res.strip().lower()

		if res in ["yes", "y", "no", "n"]:
			break

	return res == "yes" or res == "y"

def _parse_options():
	parser = argparse.ArgumentParser(
		description="Interactively choose atom specific USE flags.")

	parser.add_argument("-s", "--show-emerge",
		action="store_true",
		help="show full output from portage")

	parser.add_argument("-w", "--with-deps",
		action="store_true",
		help="choose USE flags for the atom as well as each dependency")

	parser.add_argument("-v", "--version",
		action="version",
		version=puz.constants.VERSION_STR)

	parser.add_argument("atom", nargs="+")

	return parser.parse_args()

def start():
	opts = _parse_options()

	print(opts)
	sys.exit(0)
