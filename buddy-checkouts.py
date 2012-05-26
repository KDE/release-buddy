#!/usr/bin/env python

# Part of Release Buddy: Updates the checkout for a KDE component.

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

def main():

### Parse Command Line
  cfgfile_Desc = "cfgfile = the configuration file with all the settings"
  usage = "usage %prog [options] cfgfile" + "\n\n" + cfgfile_Desc
  parser = OptionParser(usage, version="%prog, version " + BuddyVersion())
  parser.add_option("--top", action="store_false", help=SUPPRESS_HELP)
  parser.add_option("--project", action="store_false", help=SUPPRESS_HELP)
  parser.add_option("-q", "--quiet", action="store_true", dest="Quiet",
                    default=False,
                    help="don't print any diagnostic or error messages")
  parser.add_option("-b", "--babble", action="store_true", dest="Verbose",
                    default=False,
                    help="print all messages")
  parser.add_option("-d", "--dry-run", action="store_true", dest="dryrun",
                    default=False,
                    help="don't execute the checkouts; only show what would be done")
  parser.add_option("-k", "--keep-going", action="store_true", dest="keepgoing",
                    default=False,
                    help="keep processing even if an abnormal (but not fatal) condition is encountered")
  parser.add_option("--logFile", dest="LogFile",
                    default="checkout.log",
                    help="the name of a file for logging the runtime information. "
                    "Specify a fullpath else the file will be written into the current working directory")
  (options, args) = parser.parse_args()

### Sanity Check Command Line Arguments
  if len(args) != 1:
    parser.error("Must supply the cffile argument")

  if options.Quiet and options.Verbose:
    parser.error("Cannot be quiet and verbose simultaneously")

### Parse Configuration File
  cfParser = ConfigParser.ConfigParser()
  cfParser.optionxform = str

  cfgfile = args[0]
  if not os.path.exists(cfgfile):
    fail("The config file \"" + cfgfile + "\" does not exist")

  try:
    cfParser.read(cfgfile)
  except ConfigParser.MissingSectionHeader:
    fail(cfgfile + ": configFile is not properly formatted")

  BRANCH = readComponentVersion(cfParser, "Release")

### Create the top-level checkout directory, if necessary
  try:
    options.Top = cfParser.get("General","TOP")
  except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
    fail("ConfigFile is missing a section called \"General\" with a \"TOP\" setting")

  if not os.path.exists(options.Top):
    MakeDir(options,options.Top,"top-level")

  try:
    options.Project = cfParser.get("General","Project")
  except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
    fail("ConfigFile is missing a section called \"General\" with a \"Project\" setting")

  options.Top = options.Top + os.sep + options.Project + '-' + BRANCH
  if not os.path.exists(options.Top):
    MakeDir(options,options.Top,"project")
  
  options.Top = options.Top + os.sep + "sources"
  if not os.path.exists(options.Top):
    MakeDir(options,options.Top,"checkout")

### Log Start of Runs
  if not options.LogFile.startswith(os.sep):
    options.LogFile = os.getcwd() + os.sep + options.LogFile

  LoggerClear(options)
  startUTC = nowUTC()
  outlines = ''
  outlines = outlines + makeAHeadLine() + "\n"
  outlines = outlines + "BEGIN AT: " + dtStrUTC(startUTC) + "\n"
  outlines = outlines + makeAHeadLine() + "\n"
  Logger(options, outlines)

### Checkout!
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

  for p in AllPs:
    if p['url'].startswith("svn"):
      svn_update(options,p['url'],p['name'])
    else:
      git_update(options,p['url'],p['name'])

### Log End of Runs
  endUTC = nowUTC()
  outlines = ''
  outlines = outlines + makeAHeadLine() + "\n"
  outlines = outlines + "END AT: " + dtStrUTC(endUTC) + "\n"
  outlines = outlines + "TOTAL TIME: " + str(endUTC - startUTC) + "\n"
  outlines = outlines + makeAHeadLine() + "\n"
  Logger(options, outlines)

### We are Done
  sys.exit(0)

##### END OF MAIN #####

def git_update(options,url,project):
  outlines = ''
  outlines = outlines + "Begin Git Checkout for " + project + "\n"
  Logger(options, outlines)

  ChangeDir(options,options.Top)
  if not os.path.exists(project):
    RUNIT(options,"git", "clone " + url + " " + project)
  elif os.path.exists(project + os.sep + ".git"):
    os.chdir(project)
    RUNIT(options,"git", "reset --hard")
    RUNIT(options,"git", "clean -f -d -x")
    RUNIT(options,"git", "pull")
  else:
    warning(path + " exists and is not a Git clone!")

  outlines = ''
  outlines = outlines + "Checkout Complete\n"
  outlines = outlines + makeASubLine() + "\n"
  Logger(options, outlines)

def svn_update(options,url,project):
  outlines = ''
  outlines = outlines + "Begin SVN Checkout for " +  project + "\n"
  Logger(options, outlines)

  ChangeDir(options,options.Top)
  if not os.path.exists(project):
    RUNIT(options, "svn", "checkout " + url)
  elif os.path.exists(project + os.sep + ".svn"):
    RUNIT(options, "svn", "cleanup " + project)
    RUNIT(options, "svn", "update " + project)
  else:
    warning(options, module + " exists and is not a SVN checkout!")

  outlines = ''
  outlines = outlines + "Checkout Complete\n"
  outlines = outlines + makeASubLine() + "\n"
  Logger(options, outlines)

if __name__ == "__main__":
   main()
