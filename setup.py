#!/usr/bin/env python3
#
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

from distutils.core import setup

setup(name="puz",
	version="1.0",
	description="An interactive way to choose Gentoo USE flags",
	author="Matthew Rheaume",
	author_email="mhrheaume@gmail.com",
	url="http://www.github.com/mhrheaume/puz",
	packages=["puz"],
	scripts=["bin/puz.py"])
