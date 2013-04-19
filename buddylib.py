# Part of Release Buddy: General Purpose Functions

#
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

import datetime
import os
import subprocess
import shlex
import sys
import ConfigParser
from buddylogger import *
import re

def BuddyVersion():
  return "0.91"

COMMANDS= ['list','checkout','pack', 'pack_all', 'tag', 'checksum', 'checksums', 'upload', 'upload_all']
def verifyCommand(command):
  if command in COMMANDS:
    return True
  else:
    return False

def commandList():
  return ', '.join(COMMANDS)

def makeAHeadLine():
  return "=" * 60

def makeASubLine():
  return '-' * 60

def dtStrUTC(dt):
  return dt.strftime("%x %X UTC")

def nowUTC():
  return datetime.datetime.utcnow()

def printEndAll():
  return "Exiting due to errors\n"

def printContinuing():
  return "Continuing due to keep-going option\n"

def ChangeDir(options, d):
  try:
    os.chdir(d)
  except OSError:
    fail("Unable to navigate to the directory \"" + d + "\"")

def MakeDir(options, d, type):
  info("Create " + type + " directory : " + d)
  if options.dryrun:
    return
  if os.path.exists(d) and os.path.isdir(d):
    return

  try:
    os.makedirs(d)
  except OSError:
    fail("Unable to create " + type + " directory \"" + d + "\"")

def LoggerClear(options):
  if options.dryrun:
    return

  if os.path.exists(options.LogFile):
    try:
      os.remove(options.LogFile)
    except OSError:
      fail("logfile \"" + options.LogFile + "\" cannot be removed")

def RUNIT(options, cmd, args=None, shell=False):
  if args:
    cmd = cmd + " " + args

  if options.dryrun:
    info("Dry Run: " + cmd)
    if cmd.find("kde-checkout-list") != -1 and cmd.find("--dry-run") != -1:
       subprocess.call(shlex.split(cmd), shell=shell)
    return

  info("==> Start Run: " + str(shlex.split(cmd)))
  info("Working Dir: " + os.getcwd())
  startUTC = nowUTC()
  info("Start Time: " + dtStrUTC(startUTC))

  if options.Quiet:
    nf = open(os.devnull, 'w')
    stat = subprocess.call(shlex.split(cmd), stdout=nf, stderr=nf, shell=shell)
    nf.close()
  else:
    stat = subprocess.call(shlex.split(cmd), shell=shell)

  info("<== End Run: ")
  if stat:
    info("Failure condition encountered (stat=" + str(stat) + ")")
  else:
    info("Completed successfully")
  endUTC = nowUTC()
  info("End Time: " + dtStrUTC(endUTC))
  info("Elapsed Time: " + str(endUTC - startUTC))

  if stat:
    if options.keepgoing == False:
      info(printEndAll())
    else:
      stat = 0  #pretend nothing is wrong
      info(printContinuing())

  if stat:
    sys.exit(stat)

def readComponentVersionXYZ(cfparser, section, key, mini, maxi):

  try:
    xyz = cfparser.get(section, key)
  except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
    fail("ConfigFile is missing " +
          "section \"" + section + "\"" +
          " with a " +
          "\"" + key + "\" setting")

  try:
    ixyz = int(xyz)
  except ValueError:
    fail("Bad " + section + " " + key + " version (" + xyz + ") read from ConfigFile")

  if int(xyz) < mini or int(xyz) > maxi:
    fail(section + " " + key + " version (" + xyz + ") read from ConfigFile is out-of-range")

  return xyz

def readComponentVersion(cfparser, section):

  major = readComponentVersionXYZ(cfparser, section, "Major", 4, 10)
  minor = readComponentVersionXYZ(cfparser, section, "Minor", 0, 25)
  patch = readComponentVersionXYZ(cfparser, section, "Patch", 0, 99)
  return major + '.' + minor + '.' + patch

def getSVNRevision():
  proc=subprocess.Popen(["svn", "info"], stdout=subprocess.PIPE)
  rev = None
  while True:
    line = proc.stdout.readline()
    if line != '':
      if line.startswith("Revision:"):
        m = re.search('^Revision: ([0-9]*).*$', line)
        rev = m.group(1)
    else:
      break
  return rev

def getArchive(options, project, version):
  ChangeDir(options, options.Tarballs)

  archive = project['name'] + '-' + version + ".tar"
  if os.path.exists(archive + ".gz"):
    archive = archive + ".gz"
  elif os.path.exists(archive + ".bz2"):
    archive = archive + ".bz2"
  elif os.path.exists(archive + ".xz"):
    archive = archive + ".xz"
  else:
    fail("Unable to locate tarball for '%s-%s'"%(project['name'],version))
  return archive
