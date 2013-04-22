# Part of Release Buddy: Checkout Command
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

from buddylib import *

def buddy_checkout(options, project, branch):
  if project['url'].startswith("svn"):
    return svn_update(options, project['name'], project['url'])
  else:
    return git_update(options, project['name'], project['url'], branch)

def git_update(options, name, url, branch):
  info("Begin Git Checkout for " + name + ", using branch: " + branch)

  ChangeDir(options, options.Sources)
  if not os.path.exists(name):
    RUNIT(options, "git", "clone " + url + " " + name + " " + name)
  elif os.path.exists(name + os.sep + ".git"):
    os.chdir(name)
    RUNIT(options, "git", "reset --hard")
    RUNIT(options, "git", "clean -f -d -x")
    RUNIT(options, "git", "pull")
  else:
    warning(path + " exists and is not a Git clone!")

  ChangeDir(options, os.path.join(options.Sources, name))
  RUNIT(options, "git", "checkout " + branch)

  info("Checkout Complete")
  info(makeASubLine())

def svn_update(options, name, url):
  info("Begin SVN Checkout for " +  name)

  ChangeDir(options, options.Sources)
  if not os.path.exists(name):
    RUNIT(options, "svn", "checkout " + url + " " + name)
  elif os.path.exists(name + os.sep + ".svn"):
    RUNIT(options, "svn", "cleanup " + name)
    RUNIT(options, "svn", "relocate " + url + " " + name)
    RUNIT(options, "svn", "update " + name)
  else:
    warning(options, name + " exists and is not a SVN checkout!")

  info("Checkout Complete")
  info(makeASubLine())
