#!/usr/bin/env python

# Release Buddy: Command Shell

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

import os
import sys
import argparse
import ConfigParser

from buddylib import *
from buddycommands import buddy_doit

def main():

### Parse Command Line
  command_Desc = "command = the command to run: checkout, tag, pack, etc"
  cfgfile_Desc = "cfgfile = the configuration file with all the settings"
  parser = argparse.ArgumentParser(version=BuddyVersion())
  parser.add_argument("--top", action="store_false")
  parser.add_argument("--sources", action="store_false")
  parser.add_argument("--tarballs", action="store_false")
  parser.add_argument("--collection", action="store_false")
  parser.add_argument("-q", "--quiet", action="store_true", dest="Quiet",
                    default=False,
                    help="don't print any diagnostic or error messages")
  parser.add_argument("-b", "--babble", action="store_true", dest="Verbose",
                    default=False,
                    help="print all messages")
  parser.add_argument("-d", "--dry-run", action="store_true", dest="dryrun",
                    default=False,
                    help="don't execute; only show what would be done")
  parser.add_argument("-k", "--keep-going", action="store_true", dest="keepgoing",
                    default=False,
                    help="keep processing even if an abnormal (but not fatal) condition is encountered")
  parser.add_argument("--projects", dest="ProjectList",
                    help="a list of projects (comma-separated) on which to execute the command. By default, all the projects in the configfile will be used.")
  parser.add_argument("--logFile", dest="LogFile",
                    help="the name of a file for logging the runtime information. "
                    "Specify a fullpath else the file will be written into the current working directory as \"command\".log")
  parser.add_argument('command')
  parser.add_argument('cfgfile')
  options = parser.parse_args()

  initLogging(options)

  command = options.command
  if not verifyCommand(command):
    fail('available commands are:', commandList())

  if options.Quiet and options.Verbose:
    parser.error("Cannot be quiet and verbose simultaneously")

  if not options.LogFile:
    options.LogFile = os.getcwd() + os.sep + command + '.log'

### Parse Configuration File
  cfParser = ConfigParser.SafeConfigParser()
  cfParser.optionxform = str

  cfgfile = options.cfgfile
  if not os.path.exists(cfgfile):
    fail("The config file \"" + cfgfile + "\" does not exist")

  try:
    cfParser.read(cfgfile)
  except ConfigParser.MissingSectionHeader:
    fail(cfgfile + ": configFile is not properly formatted")

  BRANCH = cfParser.get("DEFAULT", "Branch")
  VERSION = readComponentVersion(cfParser, "DEFAULT")
  options.svntagurl = cfParser.get("DEFAULT", "SVNTAG")

### Create the top-level collection directory, if necessary
  try:
    options.Top = cfParser.get("General","TOP")
  except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
    fail("ConfigFile is missing a section called \"General\" with a \"TOP\" setting")

  if not os.path.exists(options.Top):
    MakeDir(options, options.Top, "top-level")

  try:
    options.Collection = cfParser.get("General","Collection")
  except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
    fail("ConfigFile is missing a section called \"General\" with a \"Collection\" setting")

  options.Top = options.Top + os.sep + options.Collection + '-' + BRANCH
  if not os.path.exists(options.Top):
    MakeDir(options, options.Top, "collection")

### Log Start of Runs
  if command != "list":
    LoggerClear(options)
    startUTC = nowUTC()
    info(makeAHeadLine())
    info("BEGIN AT: " + dtStrUTC(startUTC))
    info(makeAHeadLine())

### Generate the List of Projects
  PPrefix = "Project:"
  Projs = {'name':'', 'desc':'', 'url':''}
  AllPs = []
  
  for section in cfParser.sections():
    if section.startswith(PPrefix):
      Projs['name'] = section

      Projs['desc'] = cfParser.get(section,'Desc')
      if not Projs['desc']:
        Projs['desc'] = "No description available"

      Projs['url'] = cfParser.get(section,'Url');
      if not Projs['url']:
        fail("ConfigFile is missing a \"Url\" setting for project \"" + section + "\"")

      AllPs.append({'name' : Projs['name'].replace(PPrefix,''),
                    'desc' : Projs['desc'],
                    'url'  : Projs['url']})

### Check projects specified on the command line
  Ps = []
  if options.ProjectList:
    for p in options.ProjectList.split(','):
      found = False
      for a in AllPs:
        if a['name'] == p:
          Ps.append(a)
          found = True
          break
      if not found:
        fail("Specified project \"" + p + "\" is not in this collection")
  else:
    Ps = AllPs
    
### DoIt!
  if command == "checksums":
    buddy_doit(command, options, Ps, BRANCH, VERSION)
  for p in Ps:
    buddy_doit(command, options, p, BRANCH, VERSION)

### Log End of Runs
  if command != "list":
    endUTC = nowUTC()
    info(makeAHeadLine())
    info("END AT: " + dtStrUTC(endUTC))
    info("TOTAL TIME: " + str(endUTC - startUTC))
    info(makeAHeadLine())

### We are Done
  sys.exit(0)

if __name__ == "__main__":
   main()
