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
import subprocess
import sys

import puz.constants
import puz.error
import puz.package

class NoMatchError(puz.PuzError):
	pass

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

def _select_use_flags(pu, pkg):
	if not pkg.current_use:
		return

	done = False

	print("")
	print("Select USE flags for {0}".format(pkg.name_ver))
	print("USE=\"{0}\"".format(" ".join(pkg.current_use)))
	print("")

	print("Current package.use entry for {0}".format(pkg.name))
	if pu[pkg.name]:
		print(pu.file_entry(pkg.name))
	else:
		print("<none>")

	print("Current package.use entry for {0}".format(pkg.name_ver))
	if pu[pkg.name_ver]:
		print(pu.file_entry(pkg.name_ver))
	else:
		print("<none>")

	print("")

	# Main USE flag selection loop


def _is_nomatch_line(line):
	pattern = "emerge: there are no ebuilds to satisfy"
	return re.match(pattern, line) is not None


def _is_ebuild_line(line):
	pattern = "\[ebuild[[:blank:]]+[NSUDrRFfIBb]*[[:blank:]]+[~*#]*\]"
	return re.match(pattern, line) is not None


def _get_ebuild_lines(emerge_output):
	ebuild_lines = []

	for line in emerge_output.split("\n"):
		if _is_nomatch_line(line):
			errmsg = "ERROR: No matching ebuilds!\n"
			errmsg += "Output from emerge:\n")
			errmsg += emerge_output

			raise NoMatchError(errmsg)

		if _is_ebuild_line(line):
			ebuild_lines.append(line)

	return ebuild_lines


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

	try:
		pu = puz.package.PackageUse()
	except puz.package.PackageUseReadError as err:
		sys.exit("ERROR: Unable to read package.use file! Are you root?")

	emerge_flags = "-pv"
	if not opts["with_deps"]:
		emerge_flags += "O"

	emerge_target = opts["atom"]

	try:
		emerge_output = subprocess.check_output(
			["emerge", emerge_flags, emerge_target],
			stderr=subprocess.STDOUT
	except subprocess.CalledProcessError as err:
		sys.exit("ERROR: Failed to run 'emerge {0} {1}'".format(
			emerge_flags,
			emerge_target)

	if opts["show_emerge"]:
		print("Output from emerge:")
		print(emerge_output)

	try:
		ebuild_lines = _get_ebuild_lines(emerge_output)
	except NoMatchError as err:
		sys.exit(err.strerr)

	for ebuild in ebuild_lines:
		pkg = puz.package.Package.parse_emerge_output(ebuild)
		_select_use_flags(pu, pkg)

	try:
		pu.commit()
	except puz.package.PackageUseWriteError as err:
		sys.exit("ERROR: Unable to write package.use file! Are you root?")

	print("Done!")
	sys.exit(0)

