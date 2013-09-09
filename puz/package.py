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

import collections
import os
import re
import stat
import time

import puz.constants
import puz.error

class PackageError(puz.error.PuzError):
	pass

class PackageUseReadError(puz.error.PuzError):
	pass

class PackageUseWriteError(puz.error.PuzError):
	pass

class Package:
	def __init__(self, name, version, use_flags):
		self.name = name
		self.version = version
		self.name_ver = name + "-" + version

		self.current_use = use_flags
		self.all_use = []

		for flag in self.current_use:
			match = re.search(r"([0-9A-Za-z\-]+)", flag)

			if not match:
				continue

			flag_raw = match.group(0)
			if flag_raw[0] == "-":
				flag_raw = flag_raw[1:]

			self.all_use.append(flag_raw)


	def is_valid_flag(self, flag):
		return flag in self.all_use


	@staticmethod
	def parse_emerge_output(line):
		name_regex_str = r"[0-9A-Za-z+_\.\-]+/"
		name_regex_str += r"[0-9A-Za-z+_\.]+(-[A-Za-z][0-9A-Za-z+_\.]*)*"

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
				version = v[(len(name) + 1):]
				continue

			match = re.search(r"^USE=", v)

			if match:
				use_start = True
				use_flags.append(v[(v.index('"') + 1):])
				continue

			if use_start and not use_end:
				if v[-1] == '"':
					use_flags.append(v[0:-1])
					use_end = True
				else:
					use_flags.append(v)

		err = "Malformed ebuild line ({0})".format(line)

		if name is None:
			raise PackageError("{0} - no name".format(err))

		if version is None:
			raise PackageError("{0} - no version".format(err))

		if use_start and not use_end:
			raise PackageError("{0} - unmatched USE delimeter")

		return Package(name, version, use_flags)


class PackageUse:
	def __init__(self, use_file = puz.constants.DEFAULT_USE_FILE):
		self.use = collections.defaultdict(list)

		try:
			with open(use_file, "r") as fh:
				for line in fh:
					new_entry = line.strip().split(" ")

					if len(new_entry) < 2:
						continue

					pkg = new_entry.pop(0)
					flags = new_entry

					self.use[pkg] = flags
		except IOError as err:
			errmsg = "Could not read {0}: ".format(use_file)
			errmsg += "{1}".format(err.strerror)

			raise PackageUseReadError(errmsg)


	def __getitem__(self, index):
		return self.use[index]


	def __setitem__(self, index, val):
		self.use[index] = val


	def append(self, pkg, flag):
		if flag in self.use[pkg]:
			return

		if flag[0] == "-" and flag[1:] in self.use[pkg]:
			# Replace "-flag" with "flag"
			self.use[pkg].remove(flag[1:])
			self.use[pkg].append(flag)
			return

		if flag[0] != "-" and ("-" + flag) in self.use[pkg]:
			self.use[pkg].remove("-" + flag)
			self.use[pkg].append(flag)
			return

		self.use[pkg].append(flag)


	def extend(self, pkg, flags):
		for flag in flags:
			self.append(pkg, flag)


	def file_entry(self, pkg):
		if self.use[pkg]:
			return pkg + " " + " ".join(self.use[pkg])

		return ""


	def commit(self):
		try:
			fp = "puz_" + time.strftime("%Y-%m-%d-%H%M")

			with open(fp, "w") as fh:
				for k in self.use.keys():
					pkg_entry = self.file_entry(k)
					if pkg_entry:
						fh.write(pkg_entry + "\n")

				# Permission mask 0664
				mask = stat.S_IRUSR
				mask |= stat.S_IWUSR
				mask |= stat.S_IRGRP
				mask |= stat.S_IROTH

				os.chmod(fp, mask)

		except IOError as err:
			errmsg = "Unable to write to tempfile: "
			errmsg += "{0}".format(err.strerror)

			raise PackageUseWriteError(errmsg)

