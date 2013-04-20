# Part of Release Buddy: Package Command
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

import re
import shutil
import multiprocessing
import string
import os
from buddylib import *


def buddy_pack_all(options, projects, version):
  prepare_documentation_tools(options)
  for project in projects:
    package(options, project['name'], version)

def buddy_pack(options, project, version):
  prepare_documentation_tools(options)
  return package(options, project['name'], version)

def package(options, name, version):
  if name == 'kde-l10n':
    return package_l10n(options, name, version)

  info("Packaging %s-%s"%(name, version))
  #TODO: Set versions (see readme from sysadmin/release-tools)

  make_dokumentation(options, name)

  packExecutable = options.packExecutable
  archive = name + '-' + version + ".tar." + packExecutable 
  source = name
  destination = os.path.join(options.Tarballs, archive)

  ChangeDir(options, options.Sources)

  RUNIT(options, options.packCommand.format(source=source, destination=destination), None)

  info(makeASubLine())

def package_l10n(options, name, version):
  info("Packaging languages for version: %s"%(version))
  packExecutable = options.packExecutable
  ChangeDir(options, os.path.join(options.Sources, name))
  with open('subdirs', 'r') as f:
    for lang in f:
      lang = lang.strip()
      if not fileContains( os.path.join( options.buddyDir, 'language_list'), lang):
        info("Skipping {lang}, it does not meet the release criteria".format(lang=lang))
        continue

      RUNIT(options, "bash scripts/autogen.sh " + lang, None)
      archive = name + "-" + lang + '-' + version + ".tar." + packExecutable 
      destination = os.path.join(options.Tarballs, name, archive)

      ChangeDir(options, os.path.join(options.Sources, name))
      MakeDir(options, os.path.join(options.Tarballs, name), "Sources")
      RUNIT(options, options.packCommand.format(source=lang, destination=destination), None)

  info(makeASubLine())

def make_dokumentation(options, name):
  source = options.Sources
  packageDir = os.path.join(options.Sources, name)
  threads = multiprocessing.cpu_count() + 1
  kdocToolsDir = os.path.join(options.Top, "kdocToolsDir")
  command = options.makeDocumentationCommand.format(source=source, packageDir = packageDir, threads = threads, kdocToolsDir = kdocToolsDir)
  ChangeDir(options, os.path.join(options.Sources, name))
  RUNIT(options, command, None)

def prepare_documentation_tools(options):
  # Locate include dirs
  searchPaths = options.qtSearchPath
  fileNames = ["QCoreApplication", "QDebug", "QDir", "QFile", "QIODevice", "QList", "QPair", "QRegExp", "QStringList", "QTextStream"]
  includePaths = []
  for fileName in fileNames:
    path = findDir(fileName, searchPaths)
    if path not in includePaths:
      includePaths.append( path )

  # locate docbook locations
  searchPaths = options.docbookSearchPaths
  fileName = "catalog.xml"
  content = "XML Catalog data for DocBook XML V4.2"
  docbookLocation = findDir(fileName, searchPaths, content)

  fileName = "VERSION.xsl"
  content = "XSL Stylesheets"
  docbookXslLocation = findDir(fileName, searchPaths, content)

  # Copy kdocToolsDir
  kdocToolsDir = os.path.join(options.Top, "kdocToolsDir")
  if not os.path.exists(os.path.join( options.Sources, "kdelibs", "kdoctools" ) ):
    fail("kdelibs must be in the sources directory (%s)"%options.Sources)
  RUNIT(options, "rm -rf {kdocToolsDir}".format(kdocToolsDir=kdocToolsDir), None)
  RUNIT(options, "cp -R {kdoctools} {kdocToolsDir}".format(kdoctools = os.path.join(options.Sources, "kdelibs", "kdoctools"), kdocToolsDir = kdocToolsDir), None)
  RUNIT(options, "cp {buddyDir}/Makefile.docu {sources}".format(sources=options.Sources, buddyDir=options.buddyDir), None)

  # Create the helper
  cppFlags = " -I" + " -I".join( includePaths )
  ldFlags = " -lQtCore"
  ChangeDir(options, kdocToolsDir)
  RUNIT(options, options.compileDocbookHelperCommand.format(cppFlags=cppFlags, kdocToolsDir=".", ldFlags=ldFlags), None)

  # Prepare the cmake files
  replaceInFile(options, "@DOCBOOKXML_CURRENTDTD_DIR@", "{docbookLocation}".format(docbookLocation=docbookLocation), "{kdocToolsDir}/customization/dtd/kdex.dtd.cmake".format(kdocToolsDir=kdocToolsDir), '{kdocToolsDir}/customization/dtd/kdex.dtd'.format(docbookLocation=docbookLocation, kdocToolsDir=kdocToolsDir))
  replaceInFile(options, "@DOCBOOKXSL_DIR@", "{docbookXslLocation}".format(docbookXslLocation=docbookXslLocation), "{kdocToolsDir}/customization/kde-include-common.xsl.cmake".format(kdocToolsDir=kdocToolsDir), '{kdocToolsDir}/customization/kde-include-common.xsl'.format(docbookXslLocation=docbookXslLocation, kdocToolsDir=kdocToolsDir))
  replaceInFile(options, "@DOCBOOKXSL_DIR@", "{docbookXslLocation}".format(docbookXslLocation=docbookXslLocation), "{kdocToolsDir}/customization/kde-include-man.xsl.cmake".format(kdocToolsDir=kdocToolsDir), '{kdocToolsDir}/customization/kde-include-man.xsl'.format(docbookXslLocation=docbookXslLocation, kdocToolsDir=kdocToolsDir))

  # Run the helper
  RUNIT(options, "{kdocToolsDir}/docbookl10nhelper {docbookXslLocation} {kdocToolsDir}/customization/xsl/ {kdocToolsDir}/customization/xsl/".format(docbookXslLocation=docbookXslLocation, kdocToolsDir=kdocToolsDir), None)

def findDir(filename, search_path, content = None):
  file_found = 0
  paths = string.split(search_path, os.path.pathsep)
  for path in paths:
    if os.path.exists(os.path.join(path, filename)):
      if content is None or fileContains(os.path.join(path, filename), content):
        file_found = 1
        break
  if file_found:
    return os.path.abspath(path)
  else:
    return None

def fileContains(fileName, content):
  for line in open(fileName):
    if content in line:
      return True
  return False

def replaceInFile(options, searchString, replaceString, srcFileName, destFileName):
  debug("Replacing %s in %s with %s to %s"%(searchString, srcFileName, replaceString, destFileName) )
  srcFile = open(srcFileName, 'r')
  destFile = open(destFileName, 'w')
  
  for line in srcFile:
    if searchString in line:
      line = string.replace(line, searchString, replaceString)
    if not options.dryrun:
      destFile.write(line)
  srcFile.close()
  destFile.close()