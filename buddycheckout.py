# Part of Release Buddy: Checkout Command

from buddylib import *

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

def buddy_checkout(options, project, branch):
  if project['url'].startswith("svn"):
    return svn_update(options, project['name'], project['url'])
  else:
    return git_update(options, project['name'], project['url'])

def git_update(options, name, url):
  outlines = ''
  outlines = outlines + "Begin Git Checkout for " + name + "\n"
  Logger(options, outlines)

  ChangeDir(options, options.Sources)
  if not os.path.exists(name):
    RUNIT(options, "git", "clone " + url + " " + name)
  elif os.path.exists(name + os.sep + ".git"):
    os.chdir(name)
    RUNIT(options, "git", "reset --hard")
    RUNIT(options, "git", "clean -f -d -x")
    RUNIT(options, "git", "pull")
  else:
    warning(path + " exists and is not a Git clone!")

  outlines = ''
  outlines = outlines + "Checkout Complete\n"
  outlines = outlines + makeASubLine() + "\n"
  Logger(options, outlines)

def svn_update(options, name, url):
  outlines = ''
  outlines = outlines + "Begin SVN Checkout for " +  name + "\n"
  Logger(options, outlines)

  ChangeDir(options, options.Sources)
  if not os.path.exists(name):
    RUNIT(options, "svn", "checkout " + url)
  elif os.path.exists(name + os.sep + ".svn"):
    RUNIT(options, "svn", "cleanup " + name)
    RUNIT(options, "svn", "update " + name)
  else:
    warning(options, module + " exists and is not a SVN checkout!")

  outlines = ''
  outlines = outlines + "Checkout Complete\n"
  outlines = outlines + makeASubLine() + "\n"
  Logger(options, outlines)
