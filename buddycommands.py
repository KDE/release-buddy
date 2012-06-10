# Part of Release Buddy: Commands

from buddycheckout import *
from buddypack import *

#
# Copyright (c) 2012 Allen Winter <winter@kde.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

def buddy_doit(command, options, project, branch):

  options.Sources = options.Top + os.sep + "sources"
  options.Tarballs = options.Top + os.sep + "tarballs"
  
  if command == "checkout":
    if not os.path.exists(options.Sources):
      MakeDir(options, options.Sources, command)
    return buddy_checkout(options, project, branch)
  
  elif command == "pack":
    if not os.path.exists(options.Tarballs):
      MakeDir(options, options.Tarballs, command)
    return buddy_pack(options, project, branch)
  
  elif command == "createtag":
    fail("Sorry, the createtag command is not implemented yet.")
  elif command == "pushtag":
    fail("Sorry, the pushtag command is not implemented yet.")
  else:
    fail("There is no such command \"" + command + "\" available.")

