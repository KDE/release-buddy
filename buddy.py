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
from optparse import OptionParser, SUPPRESS_HELP
import ConfigParser

from buddylib import *
from buddycommands import buddy_doit

def main():

### Parse Command Line
  command_Desc = "command = the command to run: checkout, tag, pack, etc"
  cfgfile_Desc = "cfgfile = the configuration file with all the settings"
  usage = "usage %prog [options] command cfgfile" + "\n\n" + command_Desc + "\n" + cfgfile_Desc
  parser = OptionParser(usage, version="%prog, version " + BuddyVersion())
  parser.add_option("--top", action="store_false", help=SUPPRESS_HELP)
  parser.add_option("--sources", action="store_false", help=SUPPRESS_HELP)
  parser.add_option("--tarballs", action="store_false", help=SUPPRESS_HELP)
  parser.add_option("--collection", action="store_false", help=SUPPRESS_HELP)
  parser.add_option("-q", "--quiet", action="store_true", dest="Quiet",
                    default=False,
                    help="don't print any diagnostic or error messages")
  parser.add_option("-b", "--babble", action="store_true", dest="Verbose",
                    default=False,
                    help="print all messages")
  parser.add_option("-d", "--dry-run", action="store_true", dest="dryrun",
                    default=False,
                    help="don't execute; only show what would be done")
  parser.add_option("-k", "--keep-going", action="store_true", dest="keepgoing",
                    default=False,
                    help="keep processing even if an abnormal (but not fatal) condition is encountered")
  parser.add_option("--projects", dest="ProjectList",
                    help="a list of projects (comma-separated) on which to execute the command. By default, all the projects in the configfile will be used.")
  parser.add_option("--logFile", dest="LogFile",
                    help="the name of a file for logging the runtime information. "
                    "Specify a fullpath else the file will be written into the current working directory as \"command\".log")
  (options, args) = parser.parse_args()

### Sanity Check Command Line Arguments
  if len(args) != 2:
    parser.error("Must supply the command and cffile arguments")

  command = args[0]
  if not verifyCommand(command):
    print 'available commands are:', commandList()
    sys.exit(1)
  
  if options.Quiet and options.Verbose:
    parser.error("Cannot be quiet and verbose simultaneously")

  if not options.LogFile:
    options.LogFile = os.getcwd() + os.sep + command + '.log'

### Parse Configuration File
  cfParser = ConfigParser.ConfigParser()
  cfParser.optionxform = str

  cfgfile = args[1]
  if not os.path.exists(cfgfile):
    fail("The config file \"" + cfgfile + "\" does not exist")

  try:
    cfParser.read(cfgfile)
  except ConfigParser.MissingSectionHeader:
    fail(cfgfile + ": configFile is not properly formatted")

  BRANCH = readComponentVersion(cfParser, "Release")

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
    outlines = ''
    outlines = outlines + makeAHeadLine() + "\n"
    outlines = outlines + "BEGIN AT: " + dtStrUTC(startUTC) + "\n"
    outlines = outlines + makeAHeadLine() + "\n"
    Logger(options, outlines)

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
  for p in Ps:
    buddy_doit(command, options, p, BRANCH)

### Log End of Runs
  if command != "list":
    endUTC = nowUTC()
    outlines = ''
    outlines = outlines + makeAHeadLine() + "\n"
    outlines = outlines + "END AT: " + dtStrUTC(endUTC) + "\n"
    outlines = outlines + "TOTAL TIME: " + str(endUTC - startUTC) + "\n"
    outlines = outlines + makeAHeadLine() + "\n"
    Logger(options, outlines)

### We are Done
  sys.exit(0)

if __name__ == "__main__":
   main()
