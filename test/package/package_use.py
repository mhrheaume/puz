# Copyright (C) 2013 Matthew Rheaume
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

import os
import textwrap
import tempfile
import unittest

from puz.package import PackageUse

TEST_ENTRIES = textwrap.dedent("""\
	x11-wm/xmonad doc hscolour
	dev-libs/libxml2 ipv6 -python
	sys-devel/gcc-4.5.4 cxx
""")

class PackageUseTests(unittest.TestCase):
	def test_init(self):
		fh_os, fp = tempfile.mkstemp()

		with os.fdopen(fh_os, "w") as fh:
			fh.write(TEST_ENTRIES)

		pu = PackageUse(fp)

		self.assertCountEqual(pu["x11-wm/xmonad"], ["doc", "hscolour"])
		self.assertCountEqual(pu["dev-libs/libxml2"], ["ipv6", "-python"])
		self.assertCountEqual(pu["sys-devel/gcc-4.5.4"], ["cxx"])

		os.remove(fp)


	def test_use_manipulation(self):
		fh_os, fp = tempfile.mkstemp()
		os.close(fh_os)

		pu = PackageUse(fp)

		flags = [
			["gdbm", "ncurses", "threads"],
			["sqlite", "tk", "xml"],
			["examples", "hardened"]
		]

		pu["dev-lang/python-3.2.5"] = flags[0]
		pu["dev-lang/python"] = flags[1]

		self.assertCountEqual(pu["dev-lang/python-3.2.5"], flags[0])
		self.assertCountEqual(pu["dev-lang/python"], flags[1])

		pu.append("dev-lang/python", flags[2])
		self.assertCountEqual(pu["dev-lang/python"], flags[1] + flags[2])

		pu.append("dev-lang/python", flags[1])
		self.assertCountEqual(pu["dev-lang/python"], flags[1] + flags[2])

		os.remove(fp)


	def test_commit(self):
		fh_os, fp = tempfile.mkstemp()

		with os.fdopen(fh_os, "w") as fh:
			fh.write(TEST_ENTRIES)

		pu = PackageUse(fp)

		pu["x11-wm/xmonad-0.9.2"] = ["profile", "hscolour"]
		pu["dev-libs/libxml2"] = ["ipv6"]
		pu["sys-devel/gcc"] = ["cxx", "fortran"]

		final_entries = [
			"x11-wm/xmonad doc hscolour",
			"dev-libs/libxml2 ipv6",
			"sys-devel/gcc-4.5.4 cxx -fortran",
			"x11-wm/xmonad-0.9.2 profile hscolour",
			"sys-devel/gcc cxx fortran"
		]

		pu.commit()

		# Check that each of the entries in the file contain one of the
		# final entries

		with open(fp, "r") as fh:
			for line in fh:
				self.assertIn(line.rstrip("\n"), final_entries)

		os.remove(fp)

if __name__ == "__main__":
	unittest.main()
