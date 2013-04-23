# Part of Release Buddy: Commands

from buddylist import *
from buddycheckout import *
from buddypack import *
from buddytag import *
from buddychecksum import *
from buddyupload import *
from buddyversion import *

# Copyright (c) 2012 Allen Winter <winter@kde.org>
# Copyright (c) 2013 Torgny Nyblom <nyblom@kde.org>
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

def buddy_doit(command, options, project, branch, version):

  options.Sources = options.Top + os.sep + "sources"
  options.Tarballs = options.Top + os.sep + "tarballs"

  if command == "list":
    return buddy_list(options, project, branch)
  
  elif command == "checkout":
    if not os.path.exists(options.Sources):
      MakeDir(options, options.Sources, command)
    return buddy_checkout(options, project, branch)

  elif command == "pack" or command == "pack_all":
    if not os.path.exists(options.Tarballs):
      MakeDir(options, options.Tarballs, command)
    if command == "pack":
      return buddy_pack(options, project, version)
    else:
      return buddy_pack_all(options, project, version)

  elif command == "tag":
    return buddy_tag(options, project, branch, version)

  elif command == "checksum":
    return buddy_checksum(options, project, version)

  elif command == "checksums":
    return buddy_checksums(options, project, version)

  elif command == "upload":
  	  return buddy_upload(options, project, version)
  elif command == "upload_all":
  	  return buddy_upload_all(options, project, version)

  elif command == "version":
      return buddy_version(options, project)
  elif command == "versions":
      return buddy_versions(options, project)

  else:
    fail("There is no such command \"" + command + "\" available.")

