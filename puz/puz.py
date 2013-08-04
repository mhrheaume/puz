if __name__ == "__main__" and __package__ is None:
	__package__ = "puz"

from puz import *

import argparse
import sys

def _print_usage():
	print("""

	NAME
		puz - Easily choose package specific USE flags

	SYNOPSIS
		puz [-wsvh] <package>

	DESCRIPTION
		Choose package specific USE flags for a given package and optionally all
		of it's dependencies. This program will run emerge to determine available
		USE flags, will list current USE flags for the package, and  then give the
		option to choose USE flags for the package. Will loop through package if
		--with-deps is selected.

		This script will modify /etc/portage/package.use, therefore must be run
		as a user who can read/write to /etc/portage/package.use, or can write
		to /etc/portage if package.use does not exist.

	OPTIONS
		-w, --with-deps
			Loop through dependencies and choose USE flags for each one.

		-s, --show-emerge-output
			Display full output from emerge.

		-v, --version
			Display version and exit.

		-h, --help
			Display help page and exit.

	EXAMPLES
		Choose USE flags for sys-kernel/gentoo-sources.
			$ puz sys-kernel/gentoo-sources

		Choose USE flags for x11-base/xorg-drivers and all of it's
		dependencies.
			$ muz --with-deps xorg-drivers

	""")

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

def _print_version():
	print("puz {0} (C) 2013 Matthew Rheaume".format(puz.VERSION))

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
	opts = None

	parser = argparse.ArgumentParser(usage="", add_help=False)
	parser.add_argument("-s", "--show-emerge-output", action="store_true")
	parser.add_argument("-w", "--with-deps", action="store_true")
	parser.add_argument("-v", "--version", action="store_true")
	parser.add_argument("-h", "--help", action="store_true")

	try:
		opts = parser.parse_args()
	except SystemExit:
		_print_usage()
		return None

	if opts.version:
		_print_version()
		return None

	if opts.help:
		_print_usage()
		return None

	return opts

def start():
	opts = _parse_options()

	if opts is None:
		sys.exit(1)

	print(opts)
	sys.exit(0)

if __name__ == "__main__":
	start()
