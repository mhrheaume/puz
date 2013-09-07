# puz

A simple tool for choosing package specific USE flags for a given package, and
optionally all of it's dependencies. This program will run emerge to determine
available USE flags, will list current USE flags for the package, and then give
the option to choose USE flags for the package. Will loop through package
dependencies if --with-deps is selected.

This script will read /etc/portage/package.use, therefore must be run as a
user who can read to /etc/portage/package.use. Once finished, the script
will write to a file in the current working directory with the new
package.use file.

## Usage

    puz [-wsvh] <package>

#### -w, --with-deps

Loop through dependencies and choose USE flags for each one.

#### -s, --show-emerge-output

Display full output from emerge.

#### -v, --version

Display version and exit.

#### -h, --help

Display help page and exit.

## Examples

Choose USE flags for sys-kernel/gentoo-sources
    
    puz sys-kernel/gentoo-sources

Choose USE flags for x11-base/xorg-server and all of it's dependencies.
    
    puz --with-deps xorg-server
