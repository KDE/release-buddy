# Part of Release Buddy: General Purpose Functions

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

import datetime
import os
import subprocess
import sys
import ConfigParser

def BuddyVersion():
  return "0.91"

def fail(message):
  sys.stdout.write("Failure: " + message + "\n")
  sys.exit(1)

def warning(options, message):
  if not options.Quiet:
    sys.stdout.write("Warning: " + message + "\n")

COMMANDS= ['checkout','pack']
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

def ChangeDir(options,d):
  if options.dryrun:
    return

  try:
    os.chdir(d)
  except OSError:
    fail("Unable to navigate to the directory \"" + d + "\"")

def MakeDir(options,d,type):
  Logger(options,"Create " + type + " directory : " + d + "\n")
  if options.dryrun:
    return

  try:
    os.mkdir(d)
  except OSError:
    fail("Unable to create " + type + " directory \"" + d + "\"")

def Logger(options,lines):
  if not options.Quiet:
    sys.stdout.write(lines)

  if options.dryrun:
    return

  try:
    of = open(options.LogFile, 'a')
  except IOError:
    fail("logfile \"" + options.LogFile + "\" cannot be opened for writing")

  of.write(lines)
  of.close()

def LoggerClear(options):
  if options.dryrun:
    return

  if os.path.exists(options.LogFile):
    try:
      os.remove(options.LogFile)
    except OSError:
      fail("logfile \"" + options.LogFile + "\" cannot be removed")

def RUNIT(options, cmd, args):
  if args:
    cmd = cmd + " " + args

  if options.dryrun:
    sys.stdout.write("Dry Run: " + cmd + "\n")
    if cmd.find("kde-checkout-list") != -1 and cmd.find("--dry-run") != -1:
       subprocess.call(cmd.split(' '))
    return

  outlines = ''
  outlines = outlines + "==> Start Run: " + cmd + "\n"
  outlines = outlines + "Working Dir: " + os.getcwd() + "\n"
  startUTC = nowUTC()
  outlines = outlines + "Start Time: " + dtStrUTC(startUTC) + "\n"
  Logger(options, outlines)

  if options.Quiet:
    nf = open(os.devnull, 'w')
    stat = subprocess.call(cmd.split(' '), stdout=nf, stderr=nf)
    nf.close()
  else:
    stat = subprocess.call(cmd.split(' '))

  outlines = ''
  outlines = outlines + "<== End Run: "
  if stat:
    outlines = outlines + "Failure condition encountered (stat=" + str(stat) + ")\n"
  else:
    outlines = outlines + "Completed successfully\n"
  endUTC = nowUTC()
  outlines = outlines + "End Time: " + dtStrUTC(endUTC) + "\n"
  outlines = outlines + "Elapsed Time: " + str(endUTC - startUTC) + "\n"

  if stat:
    if options.keepgoing == False:
      outlines = outlines + printEndAll()
    else:
      stat = 0  #pretend nothing is wrong
      outlines = outlines + printContinuing()

  Logger(options, outlines)

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
