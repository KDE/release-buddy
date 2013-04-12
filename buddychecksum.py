# Part of Release Buddy: checksum Commands

import hashlib
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

def buddy_checksum(options, project, version):
  ChangeDir(options, options.Tarballs)
  archive = getArchive(options, project, version)
  with open(os.path.join(options.Tarballs, archive + ".sha256"), 'w') as f:
    digest = createChecksum(options, archive)
    f.write( digest )
    f.write( "\n" )

def buddy_checksums(options, projects, version):
  ChangeDir(options, options.Tarballs)
  with open(os.path.join(options.Tarballs, "sha256sums.txt"), 'w') as f:
    for project in projects:
      archive = getArchive(options, project, version)
      digest = createChecksum(options, archive)
      f.write( digest )
      f.write( "\n" )


def createChecksum(options, archive):
  info("Creating checksum for %s"%archive)
  crypt = hashlib.sha256()

  debug("Calculating...")
  with open( os.path.join(options.Tarballs, archive) ) as f:
    while True:
      block = f.read(256)
      if block == '':
        break
      crypt.update(block)
  digest = crypt.hexdigest()
  info("checksum: %s"%digest)
  return "%s %s"%(digest, archive)
