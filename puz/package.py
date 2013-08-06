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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import re
import regex

from puz.error import PuzError

class PackageError(PuzError):

	def __init__(self, message):
		self.message = message

class Package:

	def __init__(self, name, version, use_flags):
		self.name = name
		self.version = version
		self.name_ver = name + "-" + version

		self.current_use = use_flags
		self.all_use = []

		for flag in self.current_use:
			match = re.search("([0-9A-Za-z\-]+)", flag)

			if not match:
				continue

			flag_raw = match.group(0)
			if flag_raw[0] == "-":
				flag_raw = flag_raw[1:-1]

			a.append(flag_raw)

	def is_valid_flag(self, flag):
		return flag in self.all_use

	@staticmethod
	def parse_emerge_output(line):
		name_regex_str = "[0-9A-Za-z+_\.\-]+/"
		name_regex_str += "[0-9A-Za-z+_\.]+(-[[:alpha:]][0-9A-Za-z+_\.]*)*"

		name_regex = re.compile(name_regex_str)

		name = None
		version = None
		use_flags = []

		use_start = False
		use_end = False

		for v in line.split(" "):
			match = name_regex.search(v)

			if match:
				name = match.group(0)
				version = v[(name.length + 1):-1]
				continue

			match = re.search("^USE=")

			if match:
				use_start = True
				use_flags.append(v[(v.index('"') + 1):-1])
				continue

			if use_start and not use_end:
				if v[-1] == '"':
					use_flags.append(v[0:-2])
					use_end = true
				else
					use_flags.append(v)

			raise PackageError("Cannot match package element")

		err = "Malformed ebuild line ({0})".format(line)

		if name is None:
			raise PackageError("{0} - no name".format(err))

		if version is None:
			raise PackageError("{0} - no version".format(err)

		if use_start and not use_end:
			raise PackageError("{0} - unmatched USE delimeter")

		return Package(name, version, use_flags)

