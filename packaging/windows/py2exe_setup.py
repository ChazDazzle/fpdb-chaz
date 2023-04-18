#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""setup.py

Py2exe script for fpdb.
"""
#    Copyright 2009-2011,  Ray E. Barker
#    
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#    
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

########################################################################

#TODO:   
#        think about an installer

#HOW TO USE this script:
#
#- edit the fpdbver variable in this script  (this value will be used to create the distribution folder name)
#- cd to the folder where this script is stored, usually ...packaging/windows
#- Run the script with python "py2exe_setup.py py2exe"
#- You will frequently get messages about missing .dll files.just assume other
#  person will have them? we have copyright issues including some dll's
#- If it works, you'll have a new dir  fpdb-version  which should
#  contain dir: gfx and two bat files: run_fpdb.bat and install_fpdb.bat and fpdb dir content

#  See walkthrough in packaging directory for versions used
#  Very useful guide here : http://www.no-ack.org/2010/09/complete-guide-to-py2exe-for-pygtk.html

# steffeN: Doesnt seem necessary to gettext-ify this, but feel free to if you disagree
# Gimick: restructure to allow script to run from packaging/windows directory, and not to write to source fpdb

fpdbver = '0.40.5'

import os
import sys

# get out now if parameter not passed
try: 
    sys.argv[1] <> ""
except: 
    print "A parameter is required, quitting now"
    quit()

if sys.argv[1] <> "py2exe":
    print "Parameter 1 is not valid, quitting now"
    quit()

from distutils.core import setup
import py2exe
import glob
import fnmatch
import matplotlib
import shutil
import cdecimal

def isSystemDLL(pathname):
        #dwmapi appears to be vista-specific file, not XP 
        if os.path.basename(pathname).lower() in ("dwmapi.dll"):
                return 0
        return origIsSystemDLL(pathname)

def test_and_remove(top):
    #print "Attempting to delete:", top
    if os.path.exists(top):
        if os.path.isdir(top):
            remove_tree(top)
        else:
            print "Unexpected file '"+top+"' found. Exiting."
            exit()
    else:
        "oops folder not found"
        
def remove_tree(top):
    # Delete everything reachable from the directory named in 'top',
    # assuming there are no symbolic links.
    # CAUTION:  This is dangerous!  For example, if top == '/', it
    # could delete all your disk files.
    # sc: Nicked this from somewhere, added the if statement to try 
    #     make it a bit safer
    if (top in ('build','dist') or top.startswith('dist')) and os.path.basename(os.getcwd()) == 'windows':
        print "removing directory '"+top+"' ..."
        for root, dirs, files in os.walk(top, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(top)

def copy_tree(source,destination):
    source = source.replace('\\', '\\\\')
    destination = destination.replace('\\', '\\\\')
    print "*** Copying " + source + " to " + destination + " ***"
    shutil.copytree( source, destination )

def copy_file(source,destination):
    source = source.replace('\\', '\\\\')
    destination = destination.replace('\\', '\\\\')
    print "*** Copying " + source + " to " + destination + " ***"
    shutil.copy( source, destination )


distdir = r'fpdb-' + fpdbver
rootdir = r'../../' #cwd is normally /packaging/windows
cardsdir = rootdir+'cards'
packagedir = rootdir+'packaging/windows/'
gfxdir = rootdir+'gfx/'
sys.path.append(rootdir)  # allows fpdb modules to be found in the setup() below
tofpdb_file_list = fnmatch.filter(os.listdir(rootdir), '*ToFpdb.py')
summary_file_list = fnmatch.filter(os.listdir(rootdir), '*Summary.py')
#convert to module list by removing extensions in this list comprehension
tofpdb_module_list = [os.path.splitext(filename)[0] for filename in tofpdb_file_list]
summary_module_list = [os.path.splitext(filename)[0] for filename in summary_file_list]
fpdb_aux_module_list = ['Hello','Aux_Hud','Aux_Classic_Hud','Mucked']

print "\n" + r"Output will be created in "+'dist'

print "*** Cleaning working folders ***"
test_and_remove('dist')
test_and_remove('build')
test_and_remove('dist')

print "compiling fpdb_folder_check.exe"

returncode=os.system("gcc  fpdb_folder_check.c -o fpdb_folder_check.exe")
if returncode <> 0:
    quit()

print "*** Building now in dist folder ***"

origIsSystemDLL = py2exe.build_exe.isSystemDLL
py2exe.build_exe.isSystemDLL = isSystemDLL

setup(
    name        = 'fpdb',
    description = 'Free Poker DataBase',

    windows = [   {'script': rootdir+'fpdb.pyw', 'uac_info': "requireAdministrator", "icon_resources": [(1, gfxdir+"fpdb_large_icon.ico")]},
                  {'script': rootdir+'HUD_main.pyw', 'uac_info': "requireAdministrator", }
              ],

    console = [   {'script': rootdir+'Stove.py', },
                  {'script': rootdir+'Configuration.py', },
                  {'script': rootdir+'fpdb_prerun.py', }
              ],

    options = {'py2exe': {
                      'packages'    : ['win32process', 'encodings', 'matplotlib', 'BeautifulSoup', 'xlrd'],
                                                            
                      'includes'    : ['PyQt5.sip', 'gio', 'gtk.cairo', 'pango', 'pangocairo'
				      ,'atk', 'gobject'] + tofpdb_module_list + summary_module_list + fpdb_aux_module_list,
                                      
                      'excludes'    : ['_tkagg', '_agg2', 'cocoaagg', 'fltkagg'],
                      
                      'dll_excludes': ['libglade-2.0-0.dll', 'libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll'
                                      , 'msvcr90.dll', 'MSVCP90.dll', 'MSVCR90.dll','msvcr90.dll'],  # these are vis c / c++ runtimes, and must not be redistributed
                  }
              },

    # files in 2nd value in tuple are moved to dir named in 1st value
    # this code will not walk a tree
    # Note: cwd for 1st value is packaging/windows/dist (this is confusing BTW)
    # Note: only include files here which are to be put into the package fpdb folder or subfolders

    data_files = [('', glob.glob(rootdir+'*.txt'))
                 ,('', [rootdir+'HUD_config.xml.example',rootdir+'logging.conf'])
                 ,('', ['C:\Python27\Lib\site-packages\PyQt5\libEGL.dll'])
                 ,('platforms', [
                'C:\Python27\Lib\site-packages\PyQt5\plugins\platforms\qwindows.dll'
                ])
                 ] + matplotlib.get_py2exe_datafiles()
)

print "*** py2exe build phase complete ***"

# copy zone info, fpdb translation folders and cards folders
copy_tree (r'C:\Python27\Lib\site-packages\pytz\zoneinfo', os.path.join(r'dist', 'zoneinfo'))
copy_tree (rootdir+r'locale', os.path.join(r'dist', 'locale'))
#copy_tree (cardsdir, os.path.join(r'dist', 'cards'))#enable this line when Bostik's svg cards goes live

# create distribution folder and populate with gfx + bat
copy_tree (gfxdir, os.path.join('dist', 'gfx'))
copy_file (packagedir+'run_fpdb.bat', 'dist')
copy_file (packagedir+'install_fpdb.bat', 'dist')

print "*** Copying dist folder to fpdb folder ***"
os.rename( 'dist', 'dist' )

copy_file (packagedir+'fpdb_folder_check.exe', 'dist')

gtk_dir = "C:/Python27/Lib/site-packages/gtk-2.0/runtime/"
while not os.path.exists(gtk_dir):
    print "Enter directory name for GTK (e.g. c:/gtk) : ",     # the comma means no newline
    gtk_dir = sys.stdin.readline().rstrip()

print "*** copying GTK runtime from ", gtk_dir
copy_file(os.path.join(gtk_dir, 'bin', 'libgdk-win32-2.0-0.dll'), 'dist' )
copy_file(os.path.join(gtk_dir, 'bin', 'libgobject-2.0-0.dll'), 'dist')
copy_file(os.path.join(gtk_dir, 'bin', 'libcroco-0.6-3.dll'), 'dist')
copy_file(os.path.join(gtk_dir, 'bin', 'librsvg-2-2.dll'), 'dist')
copy_file(os.path.join(gtk_dir, 'bin', 'libxml2-2.dll'), 'dist')
copy_file(os.path.join(gtk_dir, 'bin', 'gdk-pixbuf-query-loaders.exe'), 'dist')
copy_tree(os.path.join(gtk_dir, 'etc'), os.path.join('dist', 'etc'))
copy_tree(os.path.join(gtk_dir, 'lib'), os.path.join('dist', 'lib'))
copy_tree(os.path.join(gtk_dir, 'share'), os.path.join('dist', 'share'))

print "*** Activating MS-Windows GTK theme ***"
gtkrc = open(os.path.join('dist', 'etc', 'gtk-2.0', 'gtkrc'), 'w')
print >>gtkrc, 'gtk-theme-name = "MS-Windows"'
print >>gtkrc, 'gtk-tooltip-timeout = 1750'
gtkrc.close()

print "*** deleting temporary build folder ***"
test_and_remove('build')

print "*** deleting folders to shrink package size ***"
test_and_remove(os.path.join('dist', 'lib', 'glib-2.0'))
test_and_remove(os.path.join('dist', 'lib', 'gtk-2.0','include'))
test_and_remove(os.path.join('dist', 'lib', 'pkgconfig'))
test_and_remove(os.path.join('dist', 'share', 'aclocal'))
test_and_remove(os.path.join('dist', 'share', 'doc'))
test_and_remove(os.path.join('dist', 'share', 'glib-2.0'))
test_and_remove(os.path.join('dist', 'share', 'gtk-2.0'))
test_and_remove(os.path.join('dist', 'share', 'gtk-doc'))
test_and_remove(os.path.join('dist', 'share', 'locale'))
test_and_remove(os.path.join('dist', 'share', 'man'))
test_and_remove(os.path.join('dist', 'share', 'dtds'))
test_and_remove(os.path.join('dist', 'share', 'icon-naming-utils'))
test_and_remove(os.path.join('dist', 'share', 'icons', 'Tango'))
test_and_remove(os.path.join('dist', 'share', 'xml'))

print "***++++++++++++++++++++++++++++++++++++++++++++++"
print "All done!"
print "The distribution folder "+'dist'+" is in the fpdb dir"
print "***++++++++++++++++++++++++++++++++++++++++++++++"
