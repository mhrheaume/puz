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

import textwrap
import unittest

from puz.package import Package, PackageError

EMERGE_OUTPUT = textwrap.dedent("""\
	[ebuild   R   ~] x11-wm/xmonad-0.9.2  USE="-doc -hscolour -profile" 0kB
	[ebuild   R    ] dev-libs/libxml2-2.8.0-r2:2  USE="ipv6 (-python)" 0kB
	[ebuild   R    ] sys-devel/gcc-4.5.4  USE="cxx {-test} -fortran" 843kB
""")

class PackageTests(unittest.TestCase):
	def test_emerge_parsing(self):
		expect_name = [
			"x11-wm/xmonad",
			"dev-libs/libxml2",
			"sys-devel/gcc",
		]

		expect_version = [
			"0.9.2",
			"2.8.0-r2:2",
			"4.5.4",
		]

		expect_name_ver = [
			"x11-wm/xmonad-0.9.2",
			"dev-libs/libxml2-2.8.0-r2:2",
			"sys-devel/gcc-4.5.4",
		]

		expect_current_use = [
			["-doc", "-hscolour", "-profile"],
			["ipv6", "(-python)"],
			["cxx", "{-test}", "-fortran"],
		]

		expect_all_use = [
			["doc", "hscolour", "profile"],
			["ipv6", "python"],
			["cxx", "test", "fortran"],
		]

		for i, v in enumerate(EMERGE_OUTPUT.strip().split("\n")):
			try:
				pkg = Package.parse_emerge_output(v)
			except PackageError:
				raise Exception("Error processing {0} ({1})".format(v, i))

			self.assertEqual(pkg.name, expect_name[i])
			self.assertEqual(pkg.version, expect_version[i])
			self.assertEqual(pkg.name_ver, expect_name_ver[i])

			self.assertCountEqual(pkg.current_use, expect_current_use[i])
			self.assertCountEqual(pkg.all_use, expect_all_use[i])

if __name__ == "__main__":
	unittest.main()
