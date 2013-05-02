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
  MakeDir(options, options.Workdir, "Workdir")

  prepare_documentation_tools(options)
  for project in projects:
    if project['prePackCommand']:
      info("Project {name} has a custom pre pack command.".format(name=project['name']))
      cwd = os.path.join(options.Sources, project['name'])
      ChangeDir(options, cwd)
      RUNIT(options, project['prePackCommand'].format(cwd=cwd, name = project['name'], version = version))

    package(options, project['name'], version)

def buddy_pack(options, project, version):
  MakeDir(options, options.Workdir, "Workdir")

  if project['prePackCommand']:
    info("Project {name} has a custom pre pack command.".format(name=project['name']))
    cwd = os.path.join(options.Sources, project['name'])
    ChangeDir(options, cwd)
    RUNIT(options, project['prePackCommand'].format(cwd=cwd, name = project['name'], version = version))

  prepare_documentation_tools(options)
  package(options, project['name'], version)

def package(options, name, version):
  if os.path.exists( os.path.join( options.Workdir, name) ) and not options.Resume:
    info("Removing old workdir")
    shutil.rmtree(os.path.join( options.Workdir, name))

  if name == 'kde-l10n':
    package_l10n(options, name, version)
    return

  info("Packaging %s-%s"%(name, version))

  packExecutable = options.packExecutable
  archive = name + '-' + version + ".tar." + packExecutable 
  source = name
  destination = os.path.join(options.Tarballs, archive)

  if options.Resume and os.path.exists(destination):
    info("Resume specified and tarball exists, skipping.")
    return

  # Copy the unaltered sources to a working directory where we can play how ever we like
  info("Copying sources to the workdir")
  MakeDir(options, options.Workdir, "Workdir")
  shutil.copytree( os.path.join( options.Sources, name), os.path.join( options.Workdir, name), ignore=shutil.ignore_patterns('.git', '.svn') )

  ChangeDir(options, options.Workdir)
  make_dokumentation(options, name)

  ChangeDir(options, options.Workdir)
  RUNIT(options, options.prePackCommand.format(source = source, destination = source + "-" + version))
  RUNIT(options, options.packCommand.format(source=source + "-" + version, destination=destination))
  RUNIT(options, options.postPackCommand.format(destination = source + "-" + version))

  info(makeASubLine())

def package_l10n(options, name, version):
  info("Packaging languages for version: %s"%(version))
  packExecutable = options.packExecutable

  # Copy the unaltered sources to a working directory where we can play how ever we like
  info("Copying sources to the workdir")
  shutil.copytree( os.path.join( options.Sources, name), os.path.join( options.Workdir, name), ignore=shutil.ignore_patterns('.git', '.svn') )
  ChangeDir(options, os.path.join( options.Workdir, name) )

  make_dokumentation(options, name)

  with open('subdirs', 'r') as f:
    for lang in f:
      lang = lang.strip()

      info(lang + "...")
      ChangeDir(options, os.path.join( options.Workdir, name) )
      if not os.path.isdir(lang):
        info(lang + "... not present (%s)"%os.getcwd())
        continue

      archive = name + "-" + lang + '-' + version + ".tar." + packExecutable 
      destination = os.path.join(options.Tarballs, name, archive)

      if options.Resume and os.path.exists(destination):
        info("Resume specified and tarball exists, skipping.")
        continue

      ChangeDir(options, os.path.join( options.Workdir, name, lang) )

      removeWithWildcard(options, "internal")
      removeWithWildcard(options, "docmessages") 
      removeWithWildcard(options, "webmessages")
      removeWithWildcard(options, "messages/*/desktop_*")
      removeWithWildcard(options, "messages/others")
      removeWithWildcard(options, "messages/index.lokalize")
      removeWithWildcard(options, "docs/others")
      removeWithWildcard(options, "messages/kdenonbeta")
      removeWithWildcard(options, "docs/kdenonbeta")
      removeWithWildcard(options, "messages/extragear-*")
      removeWithWildcard(options, "messages/www")
      removeWithWildcard(options, "messages/playground-*")
      removeWithWildcard(options, "messages/no-auto-merge")
      removeWithWildcard(options, "docs/extragear-*")
      removeWithWildcard(options, "docs/playground-*")
      removeWithWildcard(options, "messages/kdekiosk")
      removeWithWildcard(options, "docs/kdekiosk")
      removeWithWildcard(options, "messages/play*") 
      removeWithWildcard(options, "messages/kdereview")
      removeWithWildcard(options, "*/koffice")
      removeWithWildcard(options, "*/calligra")
      removeWithWildcard(options, "messages/kdevelop")
      removeWithWildcard(options, "docs/kdevelop")
      removeWithWildcard(options, "messages/kdevplatform")
      removeWithWildcard(options, "docs/kdevplatform")
      removeWithWildcard(options, "docs/kdewebdev/quanta*")
      removeWithWildcard(options, "messages/kdewebdev/quanta*")
      removeWithWildcard(options, "no-auto-merge")
      removeWithWildcard(options, "*/no-auto-merge")

      #ChangeDir(options, os.path.join(options.Sources, name))
      #removeWithWildcard(options, "templates")

      if not fileContains( os.path.join( options.buddyDir, 'language_list'), lang):
        info("Skipping {lang}, it does not meet the release criteria".format(lang=lang))
        continue

      if os.path.exists( "pack-with-variants" ):
        info("Bundling language variants to be packed together")
        with open( "pack-with-variants", 'r') as f:
          for sublang in f:
            sublang = sublang.strip()
            if not fileContains( os.path.join( options.buddyDir, 'language_list'), sublang):
              info("Skipping {lang}, it does not meet the release criteria".format(lang=sublang))
              continue
            info("Moving {sublang} into {lang}".format(sublang=sublang, lang=lang))
            shutil.move(os.path.join(options.Workdir, name, sublang),os.path.join(options.Workdir, name, lang))
        removeWithWildcard(options, "pack-with-variants")

      ChangeDir(options, os.path.join(options.Workdir, name))
      RUNIT(options, "bash scripts/autogen.sh " + lang)

      packageDirName = name + "-" + lang + "-" + version

      MakeDir(options, os.path.join(options.Tarballs, name), "Sources")
      ChangeDir(options, os.path.join(options.Workdir, name))
      RUNIT(options, options.prePackCommand.format(source = lang, destination = packageDirName))
      RUNIT(options, options.packCommand.format(source = packageDirName, destination = destination))
      RUNIT(options, options.postPackCommand.format(destination = packageDirName))

      info(lang + "... done")

  info(makeASubLine())

def make_dokumentation(options, name):
  source = options.Workdir
  packageDir = os.path.join(options.Workdir, name)
  threads = multiprocessing.cpu_count() + 1
  kdocToolsDir = os.path.join(options.Top, "kdocToolsDir")
  command = options.makeDocumentationCommand.format(source=source, packageDir = packageDir, threads = threads, kdocToolsDir = kdocToolsDir)
  ChangeDir(options, os.path.join(options.Workdir, name))
  RUNIT(options, command)

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
  RUNIT(options, "rm -rf {kdocToolsDir}".format(kdocToolsDir=kdocToolsDir))
  RUNIT(options, "cp -R {kdoctools} {kdocToolsDir}".format(kdoctools = os.path.join(options.Sources, "kdelibs", "kdoctools"), kdocToolsDir = kdocToolsDir))
  RUNIT(options, "cp {buddyDir}/Makefile.docu {sources}".format(sources=options.Workdir, buddyDir=options.buddyDir))

  # Create the helper
  cppFlags = " -I" + " -I".join( includePaths )
  ldFlags = " -lQtCore"
  ChangeDir(options, kdocToolsDir)
  RUNIT(options, options.compileDocbookHelperCommand.format(cppFlags=cppFlags, kdocToolsDir=".", ldFlags=ldFlags))

  # Prepare the cmake files
  replaceInFile(options, "@DOCBOOKXML_CURRENTDTD_DIR@", "{docbookLocation}".format(docbookLocation=docbookLocation), "{kdocToolsDir}/customization/dtd/kdex.dtd.cmake".format(kdocToolsDir=kdocToolsDir), '{kdocToolsDir}/customization/dtd/kdex.dtd'.format(docbookLocation=docbookLocation, kdocToolsDir=kdocToolsDir))
  replaceInFile(options, "@DOCBOOKXSL_DIR@", "{docbookXslLocation}".format(docbookXslLocation=docbookXslLocation), "{kdocToolsDir}/customization/kde-include-common.xsl.cmake".format(kdocToolsDir=kdocToolsDir), '{kdocToolsDir}/customization/kde-include-common.xsl'.format(docbookXslLocation=docbookXslLocation, kdocToolsDir=kdocToolsDir))
  replaceInFile(options, "@DOCBOOKXSL_DIR@", "{docbookXslLocation}".format(docbookXslLocation=docbookXslLocation), "{kdocToolsDir}/customization/kde-include-man.xsl.cmake".format(kdocToolsDir=kdocToolsDir), '{kdocToolsDir}/customization/kde-include-man.xsl'.format(docbookXslLocation=docbookXslLocation, kdocToolsDir=kdocToolsDir))

  # Run the helper
  RUNIT(options, "{kdocToolsDir}/docbookl10nhelper {docbookXslLocation} {kdocToolsDir}/customization/xsl/ {kdocToolsDir}/customization/xsl/".format(docbookXslLocation=docbookXslLocation, kdocToolsDir=kdocToolsDir))

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