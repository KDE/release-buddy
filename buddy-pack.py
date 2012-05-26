#!/usr/bin/env python

# Part of Release Buddy: Uses CPack to create source release packages.

# Requires CPack from Kitware

#TODO
#*support EXTRA_IGNORES

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
import re
import shutil
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
                    help="don't execute the packaging; only show what would be done")
  parser.add_option("-k", "--keep-going", action="store_true", dest="keepgoing",
                    default=False,
                    help="keep processing even if an abnormal (but not fatal) condition "
                    "is encountered")
  parser.add_option("--logFile", dest="LogFile",
                    default="pack.log",
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

### Create the top-level package directory, if necessary
  try:
    options.Top = cfParser.get("General","TOP")
  except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
    fail("ConfigFile is missing a section called \"General\" with a \"TOP\" setting")

  try:
    options.Project = cfParser.get("General","Project")
  except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
    fail("ConfigFile is missing a section called \"General\" with a \"Project\" setting")

  options.Top = options.Top + os.sep + options.Project + '-' + BRANCH
  if not os.path.exists(options.Top):
    fail("The top-level project directory \"" + options.Top + "\" does not exist")
  sourceDir = options.Top + os.sep + "sources"
  if not os.path.exists(sourceDir):
    fail("The source directory \"" + sourceDir + "\" does not exist")

  options.Top = options.Top + os.sep + "tarballs"
  if not os.path.exists(options.Top):
    MakeDir(options,options.Top,"packaging")

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

### Package!

  PPrefix = "Project:"
  Projs = {'name':'', 'desc':''}
  AllPs = []
  
  for section in cfParser.sections():
    if section.startswith(PPrefix):
      Projs['name'] = section

      Projs['desc'] = cfParser.get(section,'Desc')
      if not Projs['desc']:
        Projs['desc'] = "No description available"

      AllPs.append({'name' : Projs['name'].replace(PPrefix,''),
                    'desc' : Projs['desc']})

  ChangeDir(options,options.Top)
  for p in AllPs:
    package(options, sourceDir, p['name'], p['desc'], BRANCH)

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

def package(options, srcpath, project, desc, version):

  desc = re.sub('^"','',desc)
  desc = re.sub('"$','',desc)
  desc = desc.replace('"', '\\\"')

  #TODO read the option EXTRA_IGNORES

  #write the CPack configfile for this project
  cpackcfg = options.Top + os.sep + "CPackConfig.cmake"
  if not options.dryrun:
    writeCPackConfig(cpackcfg, project, desc, version, srcpath)

  #generate the CPack command line
  args = createCPackCommand(options)

  #run the CPack command
  RUNIT(options, "cpack", args)

  #CPack doesn't have an LZMA generator, so we must bunzip2 then run xz ourselves.
  archive = project + '-' + version + ".tar"
  RUNIT(options, "bunzip2", archive + ".bz2")
  RUNIT(options, "xz", archive)

  #remove the CPack configfile
  if not options.dryrun:
    os.remove(cpackcfg)

  #remove CPack temporary files
  shutil.rmtree("_CPack_Packages", True)

def writeCPackConfig(f, project, desc, version, srcpath):
  
  try:
    of = open(f, "w")
  except IOError:
    fail("Unable to write CPackConfig.cmake, \"" + f + "\"")

  of.write("set(CPACK_GENERATOR \"TBZ2\")\n")
  of.write("set(CPACK_SOURCE_GENERATOR \"TBZ2\")\n")
  of.write("set(CPACK_PACKAGE_VENDOR \"The KDE Community\")\n")

  n = version.split('.')[0]
  of.write("set(CPACK_PACKAGE_VERSION_MAJOR " + n + ")\n")
  n = version.split('.')[1]
  of.write("set(CPACK_PACKAGE_VERSION_MINOR " + n + ")\n")
  n = version.split('.')[2]
  of.write("set(CPACK_PACKAGE_VERSION_PATCH " + n + ")\n")

  of.write("set(CPACK_PACKAGE_VERSION "
            "\"${CPACK_PACKAGE_VERSION_MAJOR}."
            "${CPACK_PACKAGE_VERSION_MINOR}."
            "${CPACK_PACKAGE_VERSION_PATCH}\")\n")

  of.write("set(CPACK_IGNORE_FILES \"/\\\\.git/\" \"/\\\\.gitignore\" \"/\\\\.svn/\"")
  of.write(" ${EXTRA_IGNORES})\n")

  of.write("set(CPACK_PACKAGE_NAME \"" + project + "\")\n")
  of.write("set(CPACK_PACKAGE_DESCRIPTION \"" + desc + "\")\n")

  of.write("set(CPACK_INSTALLED_DIRECTORIES \"")
  of.write(srcpath + os.sep + project)
  of.write(";.\")\n")

  of.write("set(CPACK_PACKAGE_FILE_NAME \"${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}\")\n")

  of.close()

def createCPackCommand(options):

  args = "-G TBZ2"
  if options.Verbose:
    args = args + " --verbose"
  return args

if __name__ == "__main__":
  main()
