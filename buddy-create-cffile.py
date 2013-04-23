#!/usr/bin/env python

# Part of Release Buddy: Use kde-checkout-list to create a Buddy configfile

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

import sys
import subprocess
from optparse import OptionParser

from buddylib import *

def main():

### Parse Command Line
  cfgfile_Desc = "cfgfile = the name of the Buddy configuration file to create"
  usage = "usage %prog [options] cfgfile" + "\n\n" + cfgfile_Desc
  parser = OptionParser(usage, version="%prog, version " + BuddyVersion())
  (options, args) = parser.parse_args()

### Sanity Check Command Line Arguments
  initLogging(options)
  if len(args) != 1:
    parser.error("Must supply the cffile argument")

  cfgfile = args[0]
  
  if os.path.exists(cfgfile):
    fail("Sorry, the specified output configfile \"" + cfgfile + "\" already exists.\nThis program will not overwrite an existing file.\nIf you really want to overwrite the file you must remove it by-hand first.")

  try:
    cf = open(cfgfile,"w")
  except IOError:
    fail("Cannot open the specified output configfile \"" + cfgfile + "\" for writing.")

  KDE_CHECKOUT = "kde-checkout-list.pl"
  cmd = KDE_CHECKOUT + " --component=kde --desc"
  try:
    proc = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE)
  except OSError:
    fail("Cannot find " + KDE_CHECKOUT + ". Maybe it isn't in your PATH?")

  cf.write("#Buddy Configuration File -- Autogenerated by " + os.path.basename(sys.argv[0]) + "\n")

  cf.write(
'''
#Instructions:
# 1. Change the TOP setting in the [General] section to where you want all
#    the Buddy managed files to be stored. This is where the clean checkouts,
#    dirty fixups, tarballs and other Buddy files will be stored.
#    So make sure you have a lot of diskspace available for TOP.
#
# 2. Set a Collection name in the [General] section.
#
# 3. Set the Major, Minor, Patch, etc settings in the [Release] section
#    according to the release you want to make.
#
# 4. You can adjust the Git or SVN settings in the [DEFAULT] section if desired
#
# NOTE: this configuration file should be re-used for all releases in the
#       lifespan of the major release. i.e. you should re-use this for
#       KDE 4.8.80 all the way through to KDE 4.9.4. Only the settings in
#       the [Release] section should need to be modified.
'''
)
  cf.write(
'''
#default values that can be used like variables
[DEFAULT]
Major=x
Minor=y
Patch=z ;patch levels: 80=>beta1, 90=>beta2, 95=>rc1, 97=>rc2
Git=git@git.kde.org                           ;read-write url
SVN=svn+ssh://svn.kde.org/home/kde/trunk/KDE  ;read-write url
Branch=KDE/%(Major)s.%(Minor)s
Git=git@git.kde.org                           ;read-write url
SVNROOT=svn+ssh://svn.kde.org/home/kde        ;read-write url
SVN=%(SVNROOT)s/branches
SVNTAG=%(SVNROOT)s/tags/KDE/%(Major)s.%(Minor)s.%(Patch)s
# This is executed using the shell=True parameter to popen so review before executing the packing
PrePackCommand=

[General]
Collection=kde  ;kde for example

##################################################################
## Below here is a list of all the projects for this collection ##
##################################################################

## Start SVN projects list
[Project:kde-l10n]
Url=%(SVN)s/stable/l10n-kde4
Desc=KDE Translations

[Project:kde-wallpapers]
Url=%(SVN)s/%(Branch)s/kde-wallpapers
Desc=wallpaper images

[Project:kdeadmin]
Url=%(SVN)s/%(Branch)s/kdeadmin
Desc=programs that usually only a system administrator might need

[Project:kdeartwork]
Url=%(SVN)s/%(Branch)s/kdeartwork
Desc=additional themes, widgets, screensavers, sounds, wallpapers, etc for KDE

[Project:kde-base-artwork]
Url=%(SVN)s/%(Branch)s/kde-base-artwork
Desc=additional themes, widgets, screensavers, sounds, wallpapers, etc for the KDE base system

[Project:kdenetwork]
Url=%(SVN)s/%(Branch)s/kdenetwork
Desc=network applications

[Project:kdewebdev]
Url=%(SVN)s/%(Branch)s/kdewebdev
Desc=applications for the Web developer

[Project:oxygen-icons]
Url=%(SVN)/%(Branch)s/oxygen-icons
Desc=The Oxygen Icon Collection

## Start Git projects list
'''
)

  for line in proc.stdout:
    name = line.split(' ')[0].split('/')[-1]
    if name == "superbuild":
      continue
    url = line.split(' ')[1]
    cf.write("[Project:" + name + "]\n")
    url = url.replace("git://anongit.kde.org/", "%(Git)s:")
    cf.write("Url=" + url + "\n")
    cf.write("Desc=" + " ".join(line.split(' ')[2:]).replace('h1. ','') + "\n")

### We are Done
  cf.close()
  sys.exit(0)

##### END OF MAIN #####

if __name__ == "__main__":
   main()
