#!/usr/bin/env python3
#
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
import unittest
import sys

RUN_TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(RUN_TESTS_DIR))

if __name__ == "__main__":
	testsuite = unittest.TestLoader().discover(".")
	unittest.TextTestRunner(verbosity=1).run(testsuite)
