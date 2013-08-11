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

import collections
import os
import re
import stat
import tempfile

import puz.constants
import puz.error

class PackageError(puz.PuzError):
	pass

class PackageUseReadError(puz.PuzError):
	pass

class PackageUseWriteError(puz.PuzError):
	pass

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

		err = "Malformed ebuild line ({0})".format(line)

		if name is None:
			raise PackageError("{0} - no name".format(err))

		if version is None:
			raise PackageError("{0} - no version".format(err)

		if use_start and not use_end:
			raise PackageError("{0} - unmatched USE delimeter")

		return Package(name, version, use_flags)

class PackageUse:
	def __init__(self, use_file = puz.constants.DEFAULT_USE_FILE):
		self.use = collections.defaultdict(list)
		self.use_file = use_file

		try:
			with open(self.use_file, "r") as fh:
				for line in fh:
					new_entry = line.split(" ")

					if len(new_entry) < 2:
						continue

					pkg = new_entry.pop(0)
					flags = new_entry

					self.use[pkg] = flags
		except IOError as err:
			errmsg = "Could not read {0}: ".format(self.use_file)
			errmsg += "{1}".format(err.strerror)

			raise PackageUseReadError(errmsg)

	def __getitem__(self, index):
		return self.use[index]

	def __setitem__(self, index, val):
		self.use[index] = val

	def append(self, pkg, flags):
		for flag in flags:
			if flag in self.use[pkg]:
				continue

			self.use[pkg].append(flag)

	def file_entry(self, pkg):
		if self.use[pkg]:
			return pkg + " " + self.use[pkg].join(" ")

		return ""

	def commit(self):
		try:
			fh_os, fp = tempfile.mkstemp("_puz")

			with os.fdopen(fh_os, "w") as fh:
				for k in self.use.keys:
					pkg_entry = entry(k)
					fh.write(pkg_entry + "\n")

				os.rename(fp, self.use_file)
				
				# Permission mask 0664
				mask = stat.S_IRUSR
				mask |= stat.S_IWUSR
				mask |= stat.S_IRGRP
				mask |= stat.S_IROTH

				os.chmod(self.use_file, mask)

		except IOError as err:
			errmsg = "Unable to write to tempfile: "
			errmsg += "{0}".format(err.strerror)

			raise PackageUseWriteError(errmsg)
		except OSError as err:
			errmsg = "Unable to replace package.use: "
			errmsg += "{0}".format(err.strerror)

			raise PackageUseWriteError(errmsg) 

