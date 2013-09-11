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
import re
import subprocess
import sys

import puz.constants
import puz.error
import puz.package

class NoMatchError(puz.error.PuzError):
	pass


def _user_confirm():
	res = ""

	while True:
		print("Is this correct? (y/n)")
		print("> ", end="")

		res = input()
		res = res.strip().lower()

		if res in ["yes", "y", "no", "n"]:
			break

	return res == "yes" or res == "y"


def _parse_use_argv(argv, pkg):
	parser = argparse.ArgumentParser(
		prefix_chars="+",
		prog="",
		add_help=False)

	parser.add_argument("+v", "++version",
		action="store_true",
		help="include version in USE flag entry")

	parser.add_argument("+s", "++skip",
		action="store_true",
		help="make no changes and skip this package")

	parser.add_argument("+a", "++append",
		action="store_true",
		help="append the following flags to the current entry")

	parser.add_argument("+h", "++help",
		action="store_true",
		help="show this help message")

	parser.add_argument("flag", nargs="*")

	opts = parser.parse_args(argv)

	if opts.help:
		parser.print_help()
		sys.exit(0)

	for flag in opts.flag:
		if not pkg.is_valid_flag(flag):
			print("ERROR: {0} is not a valid USE flag".format(flag))
			parser.print_help()
			sys.exit(0)

	return opts


def _select_use_flags(pu, pkg):
	if not pkg.current_use:
		return

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
	while True:
		print("Enter USE flags (+h for help): ")
		print("> ", end="")

		name = pkg.name
		new_use = []

		try:
			opts = _parse_use_argv(input().split(" "), pkg)
		except SystemExit as err:
			print("")
			continue

		if opts.skip:
			return

		if opts.version:
			name = pkg.name_ver

		new_use = opts.flag
		old_use = pu[name]

		if opts.append:
			pu.extend(name, new_use)
		else:
			pu[name] = new_use

		print("")
		print("Entry to write:")
		print(pu.file_entry(name))
		print("")

		if not _user_confirm():
			pu[name] = old_use
			continue

		break


def _is_nomatch_line(line):
	pattern = r"emerge: there are no ebuilds to satisfy"
	return re.match(pattern, line) is not None


def _is_ebuild_line(line):
	pattern = r"\[ebuild[ \t]+[NSUDrRFfIBb]*[ \t]+[~*#]*\]"
	return re.match(pattern, line) is not None


def _get_ebuild_lines(emerge_output):
	ebuild_lines = []

	for line in emerge_output.split("\n"):
		if _is_nomatch_line(line):
			errmsg = "ERROR: No matching ebuilds!\n"
			errmsg += "Output from emerge:\n"
			errmsg += emerge_output

			raise NoMatchError(errmsg)

		if _is_ebuild_line(line):
			ebuild_lines.append(line)

	return ebuild_lines


def _parse_argv():
	parser = argparse.ArgumentParser(
		description="Interactively choose package specific USE flags.")

	parser.add_argument("-v", "--version",
		action="version",
		version=puz.constants.VERSION_STR)

	parser.add_argument("-s", "--show-emerge",
		action="store_true",
		help="show full output from emerge")

	parser.add_argument("package",
		help="the package to be operated on")

	return parser.parse_args()


def start():
	opts = _parse_argv()

	try:
		pu = puz.package.PackageUse()
	except puz.package.PackageUseReadError as err:
		sys.exit("ERROR: Unable to read package.use file!")

	emerge_flags = "-pvO"
	emerge_target = opts.package

	try:
		emerge_output = subprocess.check_output(
			["emerge", emerge_flags, emerge_target],
			stderr=subprocess.STDOUT)
		emerge_output_str = emerge_output.decode("utf-8")
	except subprocess.CalledProcessError as err:
		sys.exit("ERROR: Failed to run 'emerge {0} {1}'".format(
			emerge_flags,
			emerge_target))

	if opts.show_emerge:
		print("Output from emerge:")
		print(emerge_output_str)

	try:
		ebuild_lines = _get_ebuild_lines(emerge_output_str)
	except NoMatchError as err:
		sys.exit(err.strerr)

	for ebuild in ebuild_lines:
		pkg = puz.package.Package.parse_emerge_output(ebuild)
		_select_use_flags(pu, pkg)

	try:
		output_file = pu.commit()
	except puz.package.PackageUseWriteError as err:
		sys.exit("ERROR: Unable to write to file!")

	print("Done! New package.use file is {0}".format(output_file))
	sys.exit(0)

