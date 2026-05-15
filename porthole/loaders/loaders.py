#!/usr/bin/env python3

"""
    Porthole loader functions
    The main interface the user will interact with

    Copyright (C) 2003 - 2008 Fredrik Arnerup, Brian Dolbec,
    Daniel G. Taylor, Wm. F. Wheeler, Tommy Iorns

    Fixed for Python 3 - March 2020 Michael Greene

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

    Note!!!!!  as of 6 July 2020 porthole depends on gentookit, using Query
    to get installed files.

"""

import os
import threading
import datetime
import logging
from gettext import gettext as _
from porthole.backends import portagelib as portage_lib
from porthole.config import Config
from gentoolkit.query import Query
from gentoolkit.package import Package
import webbrowser

logger = logging.getLogger(__name__)
logger.debug("LOADERS: id initialized to %d", datetime.datetime.now().microsecond)

# File types dictionary used for logic & loading
Textfile_type = {"changelog": "/ChangeLog", "best_ebuild": ".ebuild", "version_ebuild": ".ebuild"}


def get_textfile(path):
    logger.debug("LOADERS: get_textfile(): loading from: ", path)
    f = open(path)
    data = f.read();
    f.close()
    return data


def decode_text(data=None, mode=None):
    if data == None:
        return ''
    if isinstance(data, str):
        return data
    text = ''
    try:
        logger.debug("LOADERS: decode_text(); trying utf_8 encoding")
        text = data.decode('utf_8', 'replace')
    except:
        try:
            logger.debug("LOADERS: decode_text(); trying iso-8859-1 encoding")
            text = data.decode('iso-8859-1', 'replace')
        except:
            logger.debug("LOADERS: decode_text(); Failure = unknown encoding")
            text = _("This %s has an encoding method unknown to porthole.\n"
                     "Please report this to bugs.gentoo.org and porthole's bugtracker"
                     ) % Textfile_type[mode][1:]
    return text


def load_textfile(view, package, mode, version=None):
    """ Load and display a text file associated with a package """
    if package:
        logger.debug("LOADERS; load_textfile(): for '%s'", package.full_name)
        if mode == "version_ebuild":
            logger.debug("LOADERS; load_textfile(): version_ebuild = ", version)
        elif mode != "changelog":
            installed = package.get_installed()
            versions = package.get_versions()
            nonmasked = package.get_versions(include_masked=False)
            if package.depricated or mode == "installed_ebuild":
                ebuild_path = portage_lib.get_vdb
            if mode == "best_ebuild":
                best = portage_lib.best(installed + nonmasked)
                if best == "":  # all versions are masked and the package is not installed
                    ebuild = package.get_latest_ebuild(True)  # get latest masked version
                else:
                    ebuild = best
                # debug.dprint("LOADERS; load_textfile(): best_ebuild '%s'" % ebuild)
                package_file = ('/' + package.full_name + '/' + ebuild.split('/')[1]) + Textfile_type[mode]
            else:
                logger.debug("LOADERS: load_textfile(); version = ", version)
                package_file = ('/' + package.full_name + '/' + package.full_name.split('/')[1] + '-' + version +
                                Textfile_type[mode])
            # debug.dprint("LOADERS: load_textfile(): package file '%s'" % package_file)
        else:
            package_file = "/" + package.full_name + Textfile_type[mode]
            logger.debug("LOADERS: load_textfile(): package_file = ", package_file)
        try:
            logger.debug("loaders:load_textfile(); try opening & reading the file")
            if mode == "changelog":
                try:
                    f = open(portage_lib.settings.portdir + package_file)
                except:
                    # need to add multiple overlay support
                    f = open(portage_lib.settings.portdir_overlay + package_file)
            # ~ elif portage_lib.is_overlay(ebuild):
            # ~ debug.dprint("LOADERS: load_textfile(); loading from an overlay")
            # ~ f = open(portage_lib.settings.portdir_overlay + package_file)
            elif mode == "version_ebuild":
                # debug.dprint("LOADERS: load_textfile(): version_ebiuld, getting path for: " + ebuild)
                path = portage_lib.get_path(version)
                logger.debug("LOADERS: load_textfile(): loading from: ", path)
                f = open(path)
            else:
                logger.debug("LOADERS: load_textfile(): loading from the portage tree")
                f = open(portage_lib.settings.portdir + package_file)
            data = f.read();
            f.close()

            if data != None:
                view.set_text(decode_text(data, mode))
            else:
                view.set_text(_("%s is Empty") % Textfile_type[mode][1:])
        except:
            logger.debug("LOADERS: Error opening %s for %s", Textfile_type[mode][1:], package.full_name)
            view.set_text(_("%s Not Available") % Textfile_type[mode][1:])
    else:
        logger.debug("LOADERS: No package sent to load_textfile()!")
        view.set_text(_("%s Not Available") % Textfile_type[mode][1:])


# called from notebook to get installed tab content
def load_installed_files(window, view, package=None, ebuild=None):
    """Obtain and display list of installed files for a package, if installed.

    So here is the big change - we will use gentoolkit - model on equery code

    1. make sure the package is installed, try with ebuild and fallback to
    package to verify the ebuild/package is on the system. If for some crazy
    reason ebuild/package are !True return the formal blurb.
    2. If the Query calls turn up nothing bail with Not installed
    3. Get the content and put it in the window - we be done

    """
    matches = []
    found = 0
    filelist = []

    if ebuild:
        logger.debug("LOADERS: load_installed_files(); ebuild check")
        matches = Query(ebuild).smart_find(in_installed=True,
                                           in_porttree=False,
                                           in_overlay=False,
                                           include_masked=False,
                                           show_progress=False,
                                           no_matches_fatal=False)
        found = len(matches)

    if package and not found:
        logger.debug("LOADERS: load_installed_files(); package check")
        matches = Query(package.full_name).smart_find(in_installed=True,
                                                      in_porttree=False,
                                                      in_overlay=False,
                                                      include_masked=False,
                                                      show_progress=False,
                                                      no_matches_fatal=False)
        found = len(matches)

    if not found:
        logger.debug("LOADERS: No package sent to load_installed_files!")
        view.set_text(_("No data currently available.\nThe package may not be installed"))
        return

    pkg = Package(matches[0].cpv)
    files = pkg.environment('CONTENTS').splitlines()

    for x in files:
        element = x.split()
        filelist.append(element[1])

    filelist.sort()

    d = {"installed_count": len(filelist), "ebuild": matches[0].cpv}
    view.set_text((_("%(installed_count)i installed files for: %(ebuild)s \n\n") % d)
                  + "\n".join(filelist))

    return


def load_web_page(name):
    """Try to load a web page in the default browser"""
    logger.debug("LOADERS: load_web_page(); starting browser thread")
    browser = web_page(name)
    browser.start()
    return


def load_help_page(name):
    """Load a locale-specific help page with the default browser."""
    logger.debug("LOADERS: load_help_page: %s", name)
    lc = Config.Prefs.globals.LANG
    if not lc: lc = "en"
    helpdir = os.path.join(Config.Prefs.DATA_PATH, 'help')
    if os.access(os.path.join(helpdir, lc, name), os.R_OK):
        pagename = "file://" + os.path.join(helpdir, lc, name)
    elif os.access(os.path.join(helpdir, lc.split('_')[0], name), os.R_OK):
        pagename = "file://" + os.path.join(helpdir, lc.split('_')[0], name)
    elif os.access(os.path.join(helpdir, "en", name), os.R_OK):
        pagename = "file://" + os.path.join(helpdir, "en", name)
    else:
        logger.debug(" * LOADERS: failed to find help file '%s' with LANG='%s'!",
                     name, Config.Prefs.globals.LANG)
        return False
    load_web_page(pagename)


class web_page(threading.Thread):
    """Try to load a web page in the default browser"""

    def __init__(self, name):
        logger.debug("LOADERS: web_page.__init__()")
        threading.Thread.__init__(self)
        self.name = name
        self.setDaemon(1)  # quit even if this thread is still running

    def run(self):
        logger.debug("LOADERS: web_page.run()")
        if self.name == '' or self.name == None:
            return
        if Config.Prefs.globals.use_custom_browser:
            command = Config.Prefs.globals.custom_browser_command
            try:
                browser = webbrowser.get(command)
            except:  # probably python-2.4 and failed to get a registered browser or
                if '%s' not in command:  # '%s' probably wasn't in, so add it to get a generic browser
                    command += ' %s'
                browser = webbrowser.get(command)
            try:
                browser.open(self.name)
            except:
                logger.debug("LOADERS: failed to open '%s' with browser command '%s'", self.name, command)
        logger.debug("LOADERS: Browser call_completed for: %s", self.name)
