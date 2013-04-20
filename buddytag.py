# Part of Release Buddy: tagging Commands

from buddylib import *
import re

#
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

def buddy_tag(options, project, branch, version):
  if project['url'].startswith("svn"):
    return svn_tag(options, project['name'], project['url'], branch)
  else:
    return git_tag(options, project['name'], project['url'], version)

def git_tag(options, name, url, version):
  info("Begin Git Tag for " + name + ", using version: " + version)

  ChangeDir(options, os.path.join(options.Sources, name))
  RUNIT(options, "git", "clean -f -d -x")
  RUNIT(options, "git", "tag -m'%s' v%s"%(version,version))
  RUNIT(options, "git", "push --tags")

  info("Tagging Complete")
  info(makeASubLine())

def svn_tag(options, name, url, branch):
  info("Begin SVN Tagging for " +  name)

  ChangeDir(options, os.path.join(options.Sources, name))
  tagurl = options.svntagurl
  rev = getSVNRevision()
  if rev is None:
    fail("Unable to determine revision for " + name)
  ChangeDir(options, os.path.join(options.Sources, name))
  RUNIT(options, "svn", "mkdir " + tagurl)
  RUNIT(options, "svn", "copy -m'v%s' "%branch + url + "@" + rev + " " + tagurl + "/" + name)

  info("Tagging Complete")
  info(makeASubLine())
