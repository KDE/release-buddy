# Part of Release Buddy: version Commands

from buddylib import *

#
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

def buddy_version(options, project):
  ChangeDir(options, options.Tarballs)
  archives = getArchive(options, project, version)
  for archive in archives:
    with open(os.path.join(options.Tarballs, archive + ".sha256"), 'w') as f:
      digest = createChecksum(options, archive)
      f.write( digest )
      f.write( "\n" )

def buddy_versions(options, projects):
  ChangeDir(options, options.Tarballs)
  with open(os.path.join(options.Tarballs, "sha256sums.txt"), 'w') as f:
    for project in projects:
      archives = getArchive(options, project, version)
      for archive in archives:
        digest = createChecksum(options, archive)
        f.write( digest )
        f.write( "\n" )


def getVersion(options, archive):
  info("Creating checksum for %s"%archive)


def getSvnVersion():
  pass

def getGitVersion():
  pass