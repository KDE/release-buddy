# Part of Release Buddy: uloading Commands

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

from ftplib import FTP
from buddylib import *

def buddy_upload_all(options, projects, version):
  ftp = _connect(options)
  for project in projects:
    archives = getArchive(options, project, version)
    for archive in archives:
      upload(options, ftp, archive, version)
  upload(options, ftp, "sha256sums.txt", version)
  _close(ftp)

def buddy_upload(options, project, version):
  ftp = _connect(options)
  archives = getArchive(options, project, version)
  for archive in archives:
    upload(options, ftp, archive, version)
    upload(options, ftp, archive + ".sha256", version)
  _close(ftp)

def _connect(options):
  if not options.dryrun:
    ftp = FTP('upload.kde.org')   # connect to host, default port
    ftp.login()
    ftp.cwd('/incoming')
  else:
    ftp = None
  return ftp

def _close(ftp):
  if ftp is not None:
    ftp.quit()

def upload(options, ftp, archive, version):
  info("Uploading %s"%archive)
  if not options.dryrun:
    if not os.path.exists( archive ):
		fail("Unable to locate file: %s"%archive)
    ftp.storbinary("STOR " + archive, open(archive, "rb"), 1024)
  debug("Uploading... done")
