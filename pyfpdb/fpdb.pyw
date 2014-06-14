#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Copyright 2008-2013 Steffen Schaumburg
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as published by
#the Free Software Foundation, version 3 of the License.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU Affero General Public License
#along with this program. If not, see <http://www.gnu.org/licenses/>.
#In the "official" distribution you can find the license in agpl-3.0.txt.
import L10n
_ = L10n.init_translation()

import os
import sys
import re
import Queue

if os.name == 'nt':
    import win32api
    import win32con

print "Python " + sys.version[0:3] + '...'

import traceback
import Options
import string
cl_options = string.join(sys.argv[1:])
(options, argv) = Options.fpdb_options()

import logging

import pygtk
pygtk.require('2.0')
import gtk
## Horrible hack to Get Icons shown on the windows theme buttons
gtk.Settings.set_long_property(gtk.settings_get_default(), "gtk-button-images", gtk.TRUE, "main")
import pango

import interlocks

# these imports not required in this module, imported here to report version in About dialog
import matplotlib
matplotlib_version = matplotlib.__version__
import numpy
numpy_version = numpy.__version__
import sqlite3
sqlite3_version = sqlite3.version
sqlite_version = sqlite3.sqlite_version

import DetectInstalledSites
import GuiPrefs
import GuiLogView
import GuiDatabase
import GuiBulkImport
import GuiTourneyImport
import GuiImapFetcher
import GuiRingPlayerStats
import GuiTourneyPlayerStats
import GuiTourneyViewer
import GuiPositionalStats
import GuiAutoImport
import GuiGraphViewer
import GuiTourneyGraphViewer
import GuiSessionViewer
import GuiHandViewer
try:
    import GuiStove
except:
    print _("GuiStove not found. If you want to use it please install pypoker-eval.")
import SQL
import Database
import Configuration
import Exceptions
import Stats

Configuration.set_logfile("fpdb-log.txt")
log = logging.getLogger("fpdb")

try:
    import subprocess
    VERSION = subprocess.Popen(["git", "describe", "--tags", "--dirty"], stdout=subprocess.PIPE).communicate()[0]
    VERSION = VERSION[:-1]
except:
    VERSION = "0.40.4"


class fpdb:
    def tab_clicked(self, widget, tab_name):
        """called when a tab button is clicked to activate that tab"""
        self.display_tab(tab_name)

    def add_and_display_tab(self, new_page, new_tab_name):
        """adds a tab, namely creates the button and displays it and appends all the relevant arrays"""
        for name in self.nb_tab_names:  # todo: check this is valid
            if name == new_tab_name:
                self.display_tab(new_tab_name)
                return  # if tab already exists, just go to it

        used_before = False
        for i, name in enumerate(self.tab_names):
            if name == new_tab_name:
                used_before = True
                event_box = self.tabs[i]
                page = self.pages[i]
                break

        if not used_before:
            event_box = self.create_custom_tab(new_tab_name, self.nb)
            page = new_page
            self.pages.append(new_page)
            self.tabs.append(event_box)
            self.tab_names.append(new_tab_name)

        self.nb.append_page(page, event_box)
        self.nb_tab_names.append(new_tab_name)
        page.show()
        self.display_tab(new_tab_name)

    def display_tab(self, new_tab_name):
        """displays the indicated tab"""
        tab_no = -1
        for i, name in enumerate(self.nb_tab_names):
            if new_tab_name == name:
                tab_no = i
                break

        if tab_no < 0 or tab_no >= self.nb.get_n_pages():
            raise FpdbError("invalid tab_no " + str(tab_no))
        else:
            self.nb.set_current_page(tab_no)

    def switch_to_tab(self, accel_group, acceleratable, keyval, modifier):
        tab = keyval - ord('0')
        if (tab == 0): tab = 10
        tab = tab - 1
        if (tab < len(self.nb_tab_names)):
            self.display_tab(self.nb_tab_names[tab])

    def create_custom_tab(self, text, nb):
        #create a custom tab for notebook containing a
        #label and a button with STOCK_ICON
        eventBox = gtk.EventBox()
        tabBox = gtk.HBox(False, 2)
        tabLabel = gtk.Label(text)
        tabBox.pack_start(tabLabel, False)
        eventBox.add(tabBox)

        # NOTE: look at git annotate of this line to see when the revert of:
        #
        # force background state to fix problem where STATE_ACTIVE
        # tab labels are black in some gtk themes, and therefore unreadable
        # This behaviour is probably a bug in libwimp.dll or pygtk, but
        # need to force background to avoid issues with menu labels being
        # unreadable
        #
        # was removed. Removing to fix http://sourceforge.net/apps/mantisbt/fpdb/view.php?id=123

        tabButton = gtk.Button()
        tabButton.connect('clicked', self.remove_tab, (nb, text))
        #Add a picture on a button
        self.add_icon_to_button(tabButton)
        tabBox.pack_start(tabButton, False)

        # needed, otherwise even calling show_all on the notebook won't
        # make the hbox contents appear.
        tabBox.show_all()
        return eventBox

    def add_icon_to_button(self, button):
        iconBox = gtk.HBox(False, 0)
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_SMALL_TOOLBAR)
        gtk.Button.set_relief(button, gtk.RELIEF_NONE)
        settings = gtk.Widget.get_settings(button)
        (w, h) = gtk.icon_size_lookup_for_settings(settings, gtk.ICON_SIZE_SMALL_TOOLBAR)
        gtk.Widget.set_size_request(button, w + 4, h + 4)
        image.show()
        iconBox.pack_start(image, True, False, 0)
        button.add(iconBox)
        iconBox.show()

    # Remove a page from the notebook
    def remove_tab(self, button, data):
        (nb, text) = data
        page = -1
        #print "\n remove_tab: start", text
        for i, tab in enumerate(self.nb_tab_names):
            if text == tab:
                page = i
        #print "   page =", page
        if page >= 0 and page < self.nb.get_n_pages():
            #print "   removing page", page
            del self.nb_tab_names[page]
            nb.remove_page(page)
        # Need to refresh the widget --
        # This forces the widget to redraw itself.
        #nb.queue_draw_area(0,0,-1,-1) needed or not??

    def remove_current_tab(self, accel_group, acceleratable, keyval, modifier):
        self.remove_tab(None, (self.nb, self.nb_tab_names[self.nb.get_current_page()]))

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        self.quit(widget)

    def dia_about(self, widget, data=None):
        dia = gtk.AboutDialog()
        dia.set_name("Free Poker Database (FPDB)")
        dia.set_version(VERSION)
        dia.set_copyright("Copyright 2008-2013. See contributors.txt for details")   #do not translate copyright message
        dia.set_comments(_("You are free to change, and distribute original or changed versions of fpdb within the rules set out by the license"))
        dia.set_license(_("Please see the help screen for license information"))
        dia.set_website("http://fpdb.sourceforge.net/")

        dia.set_authors(['Steffen', 'Eratosthenes', 'Carl Gherardi',
            'Eric Blade', '_mt', 'sqlcoder', 'Bostik', 'gimick', 'Chaz',
            _('... and others.'), _("See contributors.txt")])
        dia.set_program_name("Free Poker Database (FPDB)")
        
        if (os.name=="posix"):
            os_text=str(os.uname())
        elif (os.name=="nt"):
            import platform
            os_text=("Windows" + " " + str(platform.win32_ver()))
        else:
            os_text="Unknown"
        
        import locale
        nums = [(_('Operating System'), os_text),
                ('Python',           sys.version[0:3]),
                ('GTK+',             '.'.join([str(x) for x in gtk.gtk_version])),
                ('PyGTK',            '.'.join([str(x) for x in gtk.pygtk_version])),
                ('matplotlib',       matplotlib_version),
                ('numpy',            numpy_version),
                ('sqlite',           sqlite_version),
                (_('fpdb version'),  VERSION),
                (_('database used'), self.settings['db-server']),
                (_('language'),      locale.getdefaultlocale()[0]),
                (_('character encoding'), locale.getdefaultlocale()[1])
               ]
        versions = gtk.TextBuffer()
        w = 20  # width used for module names and version numbers
        versions.set_text('\n'.join([x[0].rjust(w) + ': ' + x[1].ljust(w) for x in nums]))
        view = gtk.TextView(versions)
        view.set_editable(False)
        view.set_justification(gtk.JUSTIFY_CENTER)
        view.modify_font(pango.FontDescription('monospace 10'))
        view.show()
        dia.vbox.pack_end(view, True, True, 2)

        l = gtk.Label(_("Your config file is: ") + self.config.file)
        l.set_alignment(0.5, 0.5)
        l.show()
        dia.vbox.pack_end(l, True, True, 2)

        l = gtk.Label(_('Version Information:'))
        l.set_alignment(0.5, 0.5)
        l.show()
        dia.vbox.pack_end(l, True, True, 2)

        dia.run()
        dia.destroy()
        log.debug(_("Threads: "))
        for t in self.threads:
            log.debug("........." + str(t.__class__))

    def dia_advanced_preferences(self, widget, data=None):
        dia = gtk.Dialog(_("Advanced Preferences"),
                         self.window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                          gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))
        dia.set_deletable(False)
        dia.set_default_size(700, 500)

        #force reload of prefs from xml file - needed because HUD could
        #have changed file contents
        self.load_profile()
        prefs = GuiPrefs.GuiPrefs(self.config, self.window, dia.vbox, dia)
        response = dia.run()
        if response == gtk.RESPONSE_ACCEPT:
            # save updated config
            self.config.save()
            self.reload_config(dia)
        else:
            dia.destroy()

    def dia_maintain_dbs(self, widget, data=None):
        if len(self.tab_names) == 1:
            if self.obtain_global_lock("dia_maintain_dbs"):  # returns true if successful
                # only main tab has been opened, open dialog
                dia = gtk.Dialog(_("Maintain Databases"),
                                 self.window,
                                 gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                 (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                  gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))
                dia.set_default_size(700, 320)

                prefs = GuiDatabase.GuiDatabase(self.config, self.window, dia)
                response = dia.run()
                if response == gtk.RESPONSE_ACCEPT:
                    log.info(_('saving updated db data'))
                    # save updated config
                    self.config.save()
                    self.load_profile()
                    #for name in self.config.supported_databases:  # db_ip/db_user/db_pass/db_server
                    #    log.debug('fpdb: name,desc=' + name + ',' + self.config.supported_databases[name].db_desc)

                self.release_global_lock()

            dia.destroy()
        else:
            self.warning_box(_("Cannot open Database Maintenance window because other windows have been opened. Re-start fpdb to use this option."))

    def dia_database_stats(self, widget, data=None):
        self.warning_box(str=_("Number of Hands:") + " " + str(self.db.getHandCount()) +
                    "\n" + _("Number of Tourneys:") + " " + str(self.db.getTourneyCount()) +
                    "\n" + _("Number of TourneyTypes:") + " " + str(self.db.getTourneyTypeCount()),
                    diatitle=_("Database Statistics"))
    #end def dia_database_stats

    def dia_hud_preferences(self, widget, data=None):
        """Opens dialog to set parameters (game category, row count, column count) for HUD preferences"""
        #Note: No point in working on this until the new HUD configuration system is in place
        self.hud_preferences_rows = None
        self.hud_preferences_columns = None
        self.hud_preferences_game = None

        diaSelections = gtk.Dialog(_("HUD Preferences - choose category"),
                                 self.window,
                                 gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                 (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                                  gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))

        label = gtk.Label(_("Note that this does not load existing settings, but overwrites them (if you click save)."))
        diaSelections.vbox.add(label)
        label.show()

        label = gtk.Label(_("Please select the game category for which you want to configure HUD stats:"))
        diaSelections.vbox.add(label)
        label.show()

        comboGame = gtk.combo_box_new_text()
        comboGame.connect("changed", self.hud_preferences_combo_selection)
        diaSelections.vbox.add(comboGame)
        games = self.config.get_stat_sets()
        for game in games:
            comboGame.append_text(game)
        comboGame.set_active(0)
        comboGame.show()

        comboRows = gtk.combo_box_new_text()
        comboRows.connect("changed", self.hud_preferences_combo_selection)
        diaSelections.vbox.add(comboRows)
        for i in range(1, 8):
            comboRows.append_text(str(i) + " rows")
        comboRows.set_active(0)
        comboRows.show()

        comboColumns = gtk.combo_box_new_text()
        comboColumns.connect("changed", self.hud_preferences_combo_selection)
        diaSelections.vbox.add(comboColumns)
        for i in range(1, 8):
            comboColumns.append_text(str(i) + " columns")
        comboColumns.set_active(0)
        comboColumns.show()

        self.load_profile()
        response = diaSelections.run()
        diaSelections.destroy()

        if (response == gtk.RESPONSE_ACCEPT and
            self.hud_preferences_rows != None and
            self.hud_preferences_columns != None and
            self.hud_preferences_game != None):
            self.dia_hud_preferences_table()
    #end def dia_hud_preferences

    def hud_preferences_combo_selection(self, widget):
        #TODO: remove this and handle it directly in dia_hud_preferences
        result = widget.get_active_text()
        if result.endswith(" rows"):
            self.hud_preferences_rows = int(result[0])
        elif result.endswith(" columns"):
            self.hud_preferences_columns = int(result[0])
        else:
            self.hud_preferences_game = result
    #end def hud_preferences_combo_selection

    def dia_hud_preferences_table(self):
        """shows dialogue with Table of ComboBoxes to allow choosing of HUD stats"""
        #TODO: show explanation of what each stat means
        diaHudTable = gtk.Dialog(_("HUD Preferences - please choose your stats"),
                                 self.window,
                                 gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                 (gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT,
                                  gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))

        label = gtk.Label(_("Please choose the stats you wish to use in the below table."))
        diaHudTable.vbox.add(label)
        label.show()

        #label = gtk.Label(_("Note that you may not select any stat more than once or it will crash."))
        #diaHudTable.vbox.add(label)
        #label.show()

        #label = gtk.Label(_("It is not currently possible to select \"empty\" or anything else to that end."))
        #diaHudTable.vbox.add(label)
        #label.show()

        label = gtk.Label(_("To configure things like colouring you will still have to use the Advanced Preferences dialogue or manually edit your HUD_config.xml."))
        diaHudTable.vbox.add(label)
        label.show()

        self.hud_preferences_table_contents = []
        table = gtk.Table(rows=self.hud_preferences_rows + 1, columns=self.hud_preferences_columns + 1, homogeneous=True)

        statDict = Stats.get_valid_stats()

        for rowNumber in range(self.hud_preferences_rows + 1):
            newRow = []
            for columnNumber in range(self.hud_preferences_columns + 1):
                if rowNumber == 0:
                    if columnNumber == 0:
                        pass
                    else:
                        label = gtk.Label("column " + str(columnNumber))
                        table.attach(child=label, left_attach=columnNumber,
                                     right_attach=columnNumber + 1,
                                     top_attach=rowNumber,
                                     bottom_attach=rowNumber + 1)
                        label.show()
                elif columnNumber == 0:
                    label = gtk.Label("row " + str(rowNumber))
                    table.attach(child=label, left_attach=columnNumber,
                                 right_attach=columnNumber + 1,
                                 top_attach=rowNumber,
                                 bottom_attach=rowNumber + 1)
                    label.show()
                else:
                    comboBox = gtk.combo_box_new_text()

                    for stat in sorted(statDict.values()):
                        comboBox.append_text(stat)
                    comboBox.set_active(0)

                    newRow.append(comboBox)
                    table.attach(child=comboBox, left_attach=columnNumber,
                                 right_attach=columnNumber + 1,
                                 top_attach=rowNumber,
                                 bottom_attach=rowNumber + 1)

                    comboBox.show()
            if rowNumber != 0:
                self.hud_preferences_table_contents.append(newRow)
        diaHudTable.vbox.add(table)
        table.show()

        response = diaHudTable.run()
        diaHudTable.destroy()

        if response == gtk.RESPONSE_ACCEPT:
            self.storeNewHudStatConfig(statDict)
    #end def dia_hud_preferences_table

    def storeNewHudStatConfig(self, stat_dict):
        """stores selections made in dia_hud_preferences_table"""
        self.obtain_global_lock("dia_hud_preferences")
        statTable = []
        for row in self.hud_preferences_table_contents:
            newRow = []
            for column in row:
                new_field = column.get_active_text()
                for attr in stat_dict: #very inefficient, but who cares
                    if new_field == stat_dict[attr]:
                        newRow.append(attr)
                        break
            statTable.append(newRow)

        self.config.editStats(self.hud_preferences_game, statTable)
        self.config.save()  # TODO: make it not store in horrible formatting
        self.reload_config(None)
        self.release_global_lock()
    #end def storeNewHudStatConfig

    def dia_dump_db(self, widget, data=None):
        filename = "database-dump.sql"
        result = self.db.dumpDatabase()

        dumpFile = open(filename, 'w')
        dumpFile.write(result)
        dumpFile.close()
    #end def dia_database_stats

    def dia_recreate_tables(self, widget, data=None):
        """Dialogue that asks user to confirm that he wants to delete and recreate the tables"""
        if self.obtain_global_lock("fpdb.dia_recreate_tables"):  # returns true if successful
            dia_confirm = gtk.MessageDialog(parent=self.window, flags=gtk.DIALOG_DESTROY_WITH_PARENT, type=gtk.MESSAGE_WARNING,
                    buttons=(gtk.BUTTONS_YES_NO), message_format=_("Confirm deleting and recreating tables"))
            diastring = _("Please confirm that you want to (re-)create the tables.") \
                        + " " + (_("If there already are tables in the database %s on %s they will be deleted and you will have to re-import your histories.") % (self.db.database, self.db.host)) + "\n"\
                        + _("This may take a while.")
            dia_confirm.format_secondary_text(diastring)  # todo: make above string with bold for db, host and deleted
            # disable windowclose, do not want the the underlying processing interrupted mid-process
            dia_confirm.set_deletable(False)

            response = dia_confirm.run()
            dia_confirm.destroy()
            if response == gtk.RESPONSE_YES:
                self.db.recreate_tables()
                # find any guibulkimport/guiautoimport windows and clear cache:
                for t in self.threads:
                    if isinstance(t, GuiBulkImport.GuiBulkImport) or isinstance(t, GuiAutoImport.GuiAutoImport):
                        t.importer.database.resetCache()
                self.release_global_lock()
            elif response == gtk.RESPONSE_NO:
                self.release_global_lock()
                print _('User cancelled recreating tables')
        else:
            self.warning_box(_("Cannot open Database Maintenance window because other windows have been opened. Re-start fpdb to use this option."))

    #end def dia_recreate_tables

    def dia_recreate_hudcache(self, widget, data=None):
        if self.obtain_global_lock("dia_recreate_hudcache"):
            self.dia_confirm = gtk.MessageDialog(parent=self.window, flags=gtk.DIALOG_DESTROY_WITH_PARENT, type=gtk.MESSAGE_WARNING, buttons=(gtk.BUTTONS_YES_NO), message_format="Confirm recreating HUD cache")
            diastring = _("Please confirm that you want to re-create the HUD cache.")
            self.dia_confirm.format_secondary_text(diastring)
            # disable windowclose, do not want the the underlying processing interrupted mid-process
            self.dia_confirm.set_deletable(False)

            hb1 = gtk.HBox(True, 1)
            self.h_start_date = gtk.Entry(max=12)
            self.h_start_date.set_text(self.db.get_hero_hudcache_start())
            lbl = gtk.Label(_(" Hero's cache starts: "))
            btn = gtk.Button()
            btn.set_image(gtk.image_new_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_BUTTON))
            btn.connect('clicked', self.__calendar_dialog, self.h_start_date)

            hb1.pack_start(lbl, expand=True, padding=3)
            hb1.pack_start(self.h_start_date, expand=True, padding=2)
            hb1.pack_start(btn, expand=False, padding=3)
            self.dia_confirm.vbox.add(hb1)
            hb1.show_all()

            hb2 = gtk.HBox(True, 1)
            self.start_date = gtk.Entry(max=12)
            self.start_date.set_text(self.db.get_hero_hudcache_start())
            lbl = gtk.Label(_(" Villains' cache starts: "))
            btn = gtk.Button()
            btn.set_image(gtk.image_new_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_BUTTON))
            btn.connect('clicked', self.__calendar_dialog, self.start_date)

            hb2.pack_start(lbl, expand=True, padding=3)
            hb2.pack_start(self.start_date, expand=True, padding=2)
            hb2.pack_start(btn, expand=False, padding=3)
            self.dia_confirm.vbox.add(hb2)
            hb2.show_all()

            response = self.dia_confirm.run()
            if response == gtk.RESPONSE_YES:
                lbl = gtk.Label(_(" Rebuilding HUD Cache ... "))
                self.dia_confirm.vbox.add(lbl)
                lbl.show()
                while gtk.events_pending():
                    gtk.main_iteration_do(False)

                self.db.rebuild_cache(self.h_start_date.get_text(), self.start_date.get_text())
            elif response == gtk.RESPONSE_NO:
                print _('User cancelled rebuilding hud cache')

            self.dia_confirm.destroy()
            self.release_global_lock()
        else:
            self.warning_box(_("Cannot open Database Maintenance window because other windows have been opened. Re-start fpdb to use this option."))


    def dia_rebuild_indexes(self, widget, data=None):
        if self.obtain_global_lock("dia_rebuild_indexes"):
            self.dia_confirm = gtk.MessageDialog(parent=self.window,
                                                 flags=gtk.DIALOG_DESTROY_WITH_PARENT,
                                                 type=gtk.MESSAGE_WARNING,
                                                 buttons=(gtk.BUTTONS_YES_NO),
                                                 message_format=_("Confirm rebuilding database indexes"))
            diastring = _("Please confirm that you want to rebuild the database indexes.")
            self.dia_confirm.format_secondary_text(diastring)
            lbl = gtk.Label()
            self.dia_confirm.vbox.add(lbl)
            lbl.show()
            # disable windowclose, do not want the the underlying processing interrupted mid-process
            self.dia_confirm.set_deletable(False)

            response = self.dia_confirm.run()
            if response == gtk.RESPONSE_YES:
                
                lbl.set_text(_(" Rebuilding Indexes ... "))
                while gtk.events_pending():
                    gtk.main_iteration_do(False)
                self.db.rebuild_indexes()

                lbl.set_text(_(" Cleaning Database ... "))
                while gtk.events_pending():
                    gtk.main_iteration_do(False)
                self.db.vacuumDB()

                lbl.set_text(_(" Analyzing Database ... "))
                while gtk.events_pending():
                    gtk.main_iteration_do(False)
                self.db.analyzeDB()
            elif response == gtk.RESPONSE_NO:
                print _('User cancelled rebuilding db indexes')

            self.dia_confirm.destroy()
            self.release_global_lock()
        else:
            self.warning_box(_("Cannot open Database Maintenance window because other windows have been opened. Re-start fpdb to use this option."))

    def dia_logs(self, widget, data=None):
        """opens the log viewer window"""

        #lock_set = False
        #if self.obtain_global_lock("dia_logs"):
        #    lock_set = True

        # remove members from self.threads if close messages received
        self.process_close_messages()

        viewer = None
        for i, t in enumerate(self.threads):
            if str(t.__class__) == 'GuiLogView.GuiLogView':
                viewer = t
                break

        if viewer is None:
            #print "creating new log viewer"
            new_thread = GuiLogView.GuiLogView(self.config, self.window, self.closeq)
            self.threads.append(new_thread)
        else:
            #print "showing existing log viewer"
            viewer.get_dialog().present()

        #if lock_set:
        #    self.release_global_lock()

    def dia_site_preferences(self, widget, data=None):
        dia = gtk.Dialog(_("Site Preferences"), self.window,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))
        dia.set_deletable(False)
        dia.resize(750,550)
        label = gtk.Label(_("Please select which sites you play on and enter your usernames."))
        dia.vbox.pack_start(label, expand=False, padding=5)
        
        self.load_profile()
        site_names = self.config.site_ids
        available_site_names=[]
        for site_name in site_names:
            try:
                tmp = self.config.supported_sites[site_name].enabled
                available_site_names.append(site_name)
            except KeyError:
                pass
        
        column_headers=[_("Site"), _("Detect"), _("Screen Name"), _("Hand History Path"), "", _("Tournament Summary Path"), ""]  # todo _("HUD")
        #HUD column will contain a button that shows favseat and HUD locations. Make it possible to load screenshot to arrange HUD windowlets.

        table = gtk.Table(rows=len(available_site_names)+1, columns=len(column_headers), homogeneous=False)

        scrolling_frame = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        scrolling_frame.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolling_frame.show()
        scrolling_frame.add_with_viewport(table)
        dia.vbox.pack_end(scrolling_frame, expand=True, padding=0)
                
        for header_number in range (0, len(column_headers)):
            label = gtk.Label(column_headers[header_number])
            table.attach(label, header_number, header_number+1, 0, 1)
        
        check_buttons=[]
        screen_names=[]
        history_paths=[]
        summary_paths=[]
        detector = DetectInstalledSites.DetectInstalledSites()
              
        y_pos=1
        for site_number in range(0, len(available_site_names)):
            check_button = gtk.CheckButton(label=available_site_names[site_number])
            check_button.set_active(self.config.supported_sites[available_site_names[site_number]].enabled)
            table.attach(check_button, 0, 1, y_pos, y_pos+1)
            check_buttons.append(check_button)
            
            hero = gtk.Entry()
            hero.set_text(self.config.supported_sites[available_site_names[site_number]].screen_name)
            table.attach(hero, 2, 3, y_pos, y_pos+1)
            screen_names.append(hero)
            hero.connect("changed", self.autoenableSite, (check_buttons[site_number],))
            
            entry = gtk.Entry()
            entry.set_text(self.config.supported_sites[available_site_names[site_number]].HH_path)
            table.attach(entry, 3, 4, y_pos, y_pos+1)
            history_paths.append(entry)
            
            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_OPEN, gtk.ICON_SIZE_BUTTON)
            choose1 = gtk.Button()
            choose1.set_image(image)
            table.attach(choose1, 4, 5, y_pos, y_pos+1)
            choose1.connect("clicked", self.browseClicked, (dia, history_paths[site_number]))
            
            entry = gtk.Entry()
            entry.set_text(self.config.supported_sites[available_site_names[site_number]].TS_path)
            table.attach(entry, 5, 6, y_pos, y_pos+1)
            summary_paths.append(entry)

            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_OPEN, gtk.ICON_SIZE_BUTTON)
            choose2 = gtk.Button()
            choose2.set_image(image)
            table.attach(choose2, 6, 7, y_pos, y_pos+1)
            choose2.connect("clicked", self.browseClicked, (dia, summary_paths[site_number]))
            
            if available_site_names[site_number] in detector.supportedSites:
                button = gtk.Button(_("Detect"))
                table.attach(button, 1, 2, y_pos, y_pos+1)
                button.connect("clicked", self.detect_clicked, (detector, available_site_names[site_number], screen_names[site_number], history_paths[site_number], summary_paths[site_number]))
            y_pos+=1
        
        dia.show_all()
        response = dia.run()
        if (response == gtk.RESPONSE_ACCEPT):
            for site_number in range(0, len(available_site_names)):
                #print "site %s enabled=%s name=%s" % (available_site_names[site_number], check_buttons[site_number].get_active(), screen_names[site_number].get_text(), history_paths[site_number].get_text())
                self.config.edit_site(available_site_names[site_number], str(check_buttons[site_number].get_active()), screen_names[site_number].get_text(), history_paths[site_number].get_text(), summary_paths[site_number].get_text())
            
            self.config.save()
            self.reload_config(dia)
            
        dia.destroy()
        
    def autoenableSite(self, widget, data):
        #autoactivate site if something gets typed in the screename field
        checkbox=data[0]
        checkbox.set_active(True)
                
    def browseClicked(self, widget, data):
        """runs when user clicks one of the browse buttons for the TS folder"""

        parent=data[0]
        path=data[1]

        dia_chooser = gtk.FileChooserDialog(title=_("Please choose the path that you want to Auto Import"),
                action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))

        dia_chooser.set_filename(path.get_text())
        dia_chooser.set_show_hidden(True)
        dia_chooser.set_destroy_with_parent(True)
        dia_chooser.set_transient_for(parent)

        response = dia_chooser.run()
        if response == gtk.RESPONSE_OK:
            path.set_text(dia_chooser.get_filename())
        elif response == gtk.RESPONSE_CANCEL:
            #print 'Closed, no files selected'
            pass
        dia_chooser.destroy()
    
    def detect_clicked(self, widget, data):
        detector = data[0]
        site_name = data[1]
        entry_screen_name = data[2]
        entry_history_path = data[3]
        entry_summary_path = data[4]
        if detector.sitestatusdict[site_name]['detected']:
            entry_screen_name.set_text(detector.sitestatusdict[site_name]['heroname'])
            entry_history_path.set_text(detector.sitestatusdict[site_name]['hhpath'])
            if detector.sitestatusdict[site_name]['tspath']:
                entry_summary_path.set_text(detector.sitestatusdict[site_name]['tspath'])
    
    def reload_config(self, dia):
        if len(self.nb_tab_names) == 1:
            # only main tab open, reload profile
            self.load_profile()
            if dia: dia.destroy() # destroy prefs before raising warning, otherwise parent is dia rather than self.window
            self.warning_box(_("Configuration settings have been updated, Fpdb needs to be restarted now")+"\n\n"+_("Click OK to close Fpdb"))
            sys.exit()
        else:
            if dia: dia.destroy() # destroy prefs before raising warning, otherwise parent is dia rather than self.window
            self.warning_box(_("Updated preferences have not been loaded because windows are open.")+" "+_("Re-start fpdb to load them."))
    
    def addLogText(self, text):
        end_iter = self.logbuffer.get_end_iter()
        self.logbuffer.insert(end_iter, text)
        self.logview.scroll_to_mark(self.logbuffer.get_insert(), 0)

    def process_close_messages(self):
        # check for close messages
        try:
            while True:
                name = self.closeq.get(False)
                for i, t in enumerate(self.threads):
                    if str(t.__class__) == str(name):
                        # thread has ended so remove from list:
                        del self.threads[i]
                        break
        except Queue.Empty:
            # no close messages on queue, do nothing
            pass

    def __calendar_dialog(self, widget, entry):
# do not alter the modality of the parent
#        self.dia_confirm.set_modal(False)
        d = gtk.Window(gtk.WINDOW_TOPLEVEL)
        d.set_transient_for(self.dia_confirm)
        d.set_destroy_with_parent(True)
        d.set_modal(True)

        d.set_title(_('Pick a date'))

        vb = gtk.VBox()
        cal = gtk.Calendar()
        vb.pack_start(cal, expand=False, padding=0)

        btn = gtk.Button(_('Done'))
        btn.connect('clicked', self.__get_date, cal, entry, d)

        vb.pack_start(btn, expand=False, padding=4)

        d.add(vb)
        d.set_position(gtk.WIN_POS_MOUSE)
        d.show_all()

    def __get_dates(self):
        t1 = self.h_start_date.get_text()
        if t1 == '':
            t1 = '1970-01-01'
        t2 = self.start_date.get_text()
        if t2 == '':
            t2 = '1970-01-01'
        return (t1, t2)

    def __get_date(self, widget, calendar, entry, win):
        # year and day are correct, month is 0..11
        (year, month, day) = calendar.get_date()
        month += 1
        ds = '%04d-%02d-%02d' % (year, month, day)
        entry.set_text(ds)
        win.destroy()
        self.dia_confirm.set_modal(True)

    def get_menu(self, window):
        """returns the menu for this program"""
        fpdbmenu = """
            <ui>
              <menubar name="MenuBar">
                <menu action="configure">
                  <menuitem action="site_settings"/>
                  <menuitem action="hud_stats"/>
                  <menuitem action="preferences"/>
                  <separator/>
                  <menuitem action="Quit"/>
                </menu>
                <menu action="import">
                  <menuitem action="bulkimp"/>
                  <menuitem action="imapimport"/>
                </menu>
                <menu action="hud">
                  <menuitem action="autoimp"/>
                </menu>                
                <menu action="cash">
                  <menuitem action="graphs"/>
                  <menuitem action="ringplayerstats"/>
                  <menuitem action="handviewer"/>
                  <menuitem action="posnstats"/>
                  <menuitem action="sessionstats"/>
                  <menuitem action="stove"/>
                </menu>
                <menu action="tournament">
                  <menuitem action="tourneygraphs"/>
                  <menuitem action="tourneyplayerstats"/>
                  <menuitem action="tourneyviewer"/>
                </menu>
                <menu action="maintenance">
                  <menuitem action="databasestats"/>
                  <menuitem action="createtabs"/>
                  <menuitem action="rebuildhudcache"/>
                  <menuitem action="rebuildindexes"/>
                  <menuitem action="dumptofile"/>
                </menu>
                <menu action="help">
                  <menuitem action="Logs"/>
                  <menuitem action="Help Tab"/>
                  <separator/>
                  <menuitem action="About"/>
                </menu>
              </menubar>
            </ui>"""

        uimanager = gtk.UIManager()
        accel_group = uimanager.get_accel_group()
        actiongroup = gtk.ActionGroup('UIManagerExample')

        # Create actions
        actiongroup.add_actions([('configure', None, _('_Configure')),
                                 ('Quit', gtk.STOCK_QUIT, _('_Quit'), None, 'Quit the Program', self.quit),
                                 ('site_settings', None, _('_Site Settings'), None, 'Site Settings', self.dia_site_preferences),
                                 ('preferences', None, _('_Preferences'), _('<control>F'), 'Edit your preferences', self.dia_advanced_preferences),
                                 ('import', None, _('_Import')),
                                 ('bulkimp', None, _('_Bulk Import'), _('<control>B'), 'Bulk Import', self.tab_bulk_import),
                                 ('imapimport', None, _('_Import through eMail/IMAP'), _('<control>I'), 'Import through eMail/IMAP', self.tab_imap_import),
                                 ('cash', None, _('_Cash')),
                                 ('hud', None, _('_HUD')),
                                 ('tournament', None, _('_Tournament')),
                                 ('autoimp', None, _('_HUD and Auto Import'), _('<control>A'), 'HUD and Auto Import', self.tab_auto_import),
                                 ('hud_stats', None, _('_HUD Stats Settings'), _('<control>H'), 'HUD Stats Settings', self.dia_hud_preferences),
                                 ('graphs', None, _('_Graphs'), _('<control>G'), 'Graphs', self.tabGraphViewer),
                                 ('tourneygraphs', None, _('Tourney Graphs'), None, 'TourneyGraphs', self.tabTourneyGraphViewer),
                                 ('stove', None, _('Stove (preview)'), None, 'Stove', self.tabStove),
                                 ('ringplayerstats', None, _('Ring _Player Stats'), _('<control>P'), 'Ring Player Stats ', self.tab_ring_player_stats),
                                 ('tourneyplayerstats', None, _('_Tourney Stats'), _('<control>T'), 'Tourney Stats ', self.tab_tourney_player_stats),
                                 ('tourneyviewer', None, _('Tourney _Viewer'), None, 'Tourney Viewer)', self.tab_tourney_viewer_stats),
                                 ('posnstats', None, _('P_ositional Stats (tabulated view)'), _('<control>O'), 'Positional Stats (tabulated view)', self.tab_positional_stats),
                                 ('sessionstats', None, _('Session Stats'), _('<control>S'), 'Session Stats', self.tab_session_stats),
                                 ('handviewer', None, _('Hand _Viewer'), None, 'Hand Viewer', self.tab_hand_viewer),
                                 ('maintenance', None, _('_Maintenance')),
                                 ('maintaindbs', None, _('_Maintain Databases'), None, 'Maintain Databases', self.dia_maintain_dbs),
                                 ('createtabs', None, _('Create or Recreate _Tables'), None, 'Create or Recreate Tables ', self.dia_recreate_tables),
                                 ('rebuildhudcache', None, _('Rebuild HUD Cache'), None, 'Rebuild HUD Cache', self.dia_recreate_hudcache),
                                 ('rebuildindexes', None, _('Rebuild DB Indexes'), None, 'Rebuild DB Indexes', self.dia_rebuild_indexes),
                                 ('databasestats', None, _('_Statistics'), None, 'View Database Statistics', self.dia_database_stats),
                                 ('dumptofile', None, _('Dump Database to Textfile (takes ALOT of time)'), None, 'Dump Database to Textfile (takes ALOT of time)', self.dia_dump_db),
                                 ('help', None, _('_Help')),
                                 ('Logs', None, _('_Log Messages'), None, 'Log and Debug Messages', self.dia_logs),
                                 ('Help Tab', None, _('_Help Tab'), None, 'Help Tab', self.tab_main_help),
                                 ('About', None, _('A_bout, License, Copying'), None, 'About the program', self.dia_about),
                                ])
        actiongroup.get_action('Quit').set_property('short-label', _('_Quit'))

        # define keyboard shortcuts alt-1 through alt-0 for switching tabs
        for key in range(10):
            accel_group.connect_group(ord('%s' % key), gtk.gdk.MOD1_MASK, gtk.ACCEL_LOCKED, self.switch_to_tab)
        accel_group.connect_group(ord('w'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, self.remove_current_tab)

        uimanager.insert_action_group(actiongroup, 0)
        merge_id = uimanager.add_ui_from_string(fpdbmenu)

        # Create a MenuBar
        menubar = uimanager.get_widget('/MenuBar')
        window.add_accel_group(accel_group)
        return menubar
    #end def get_menu

    def load_profile(self, create_db=False):
        """Loads profile from the provided path name."""
        self.config = Configuration.Config(file=options.config, dbname=options.dbname)
        if self.config.file_error:
            self.warning_box(_("There is an error in your config file %s") % self.config.file
                              + ":\n" + str(self.config.file_error),
                              diatitle=_("CONFIG FILE ERROR"))
            sys.exit()

        log = logging.getLogger("fpdb")
        print (_("Logfile is %s") % os.path.join(self.config.dir_log, self.config.log_file))
        if self.config.example_copy or self.display_config_created_dialogue:
            self.info_box(_("Config file"),
                          _("Config file has been created at %s.") % self.config.file + " "
                           + _("Enter your screen_name and hand history path in the Site Preferences window (Main menu) before trying to import hands."))
            self.display_config_created_dialogue = False
        elif self.config.wrongConfigVersion:
            diaConfigVersionWarning = gtk.Dialog(title=_("Strong Warning - Local configuration out of date"),
                                             parent=None, flags=0, buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK))

            label = gtk.Label("\n"+_("Your local configuration file needs to be updated."))
            diaConfigVersionWarning.vbox.add(label)
            label.show()

            label = gtk.Label(_("This error is not necessarily fatal but it is strongly recommended that you update the configuration.")+"\n")
            diaConfigVersionWarning.vbox.add(label)
            label.show()

            label = gtk.Label(_("To create a new configuration, see fpdb.sourceforge.net/apps/mediawiki/fpdb/index.php?title=Reset_Configuration"))
            label.set_selectable(True)
            diaConfigVersionWarning.vbox.add(label)
            label.show()
            label = gtk.Label(_("A new configuration will destroy all personal settings (hud layout, site folders, screennames, favourite seats)")+"\n")
            diaConfigVersionWarning.vbox.add(label)
            label.show()

            label = gtk.Label(_("To keep existing personal settings, you must edit the local file."))
            diaConfigVersionWarning.vbox.add(label)
            label.show()

            label = gtk.Label(_("See the release note for information about the edits needed"))
            diaConfigVersionWarning.vbox.add(label)
            label.show()

            response = diaConfigVersionWarning.run()
            diaConfigVersionWarning.destroy()
            self.config.wrongConfigVersion = False
            
        self.settings = {}
        self.settings['global_lock'] = self.lock
        if (os.sep == "/"):
            self.settings['os'] = "linuxmac"
        else:
            self.settings['os'] = "windows"

        self.settings.update({'cl_options': cl_options})
        self.settings.update(self.config.get_db_parameters())
        self.settings.update(self.config.get_import_parameters())
        self.settings.update(self.config.get_default_paths())

        if self.db is not None and self.db.is_connected():
            self.db.disconnect()

        self.sql = SQL.Sql(db_server=self.settings['db-server'])
        err_msg = None
        try:
            self.db = Database.Database(self.config, sql=self.sql)
            if self.db.get_backend_name() == 'SQLite':
                # tell sqlite users where the db file is
                print (_("Connected to SQLite: %s") % self.db.db_path)
        except Exceptions.FpdbMySQLAccessDenied:
            err_msg = _("MySQL Server reports: Access denied. Are your permissions set correctly?")
        except Exceptions.FpdbMySQLNoDatabase:
            err_msg = _("MySQL client reports: 2002 or 2003 error. Unable to connect - ") \
                      + _("Please check that the MySQL service has been started")
        except Exceptions.FpdbPostgresqlAccessDenied:
            err_msg = _("PostgreSQL Server reports: Access denied. Are your permissions set correctly?")
        except Exceptions.FpdbPostgresqlNoDatabase:
            err_msg = _("PostgreSQL client reports: Unable to connect - ") \
                      + _("Please check that the PostgreSQL service has been started")
        if err_msg is not None:
            self.db = None
            self.warning_box(err_msg)
        if self.db is not None and not self.db.is_connected():
            self.db = None

        if self.db is not None and self.db.wrongDbVersion:
            diaDbVersionWarning = gtk.Dialog(title=_("Strong Warning - Invalid database version"),
                                             parent=None, flags=0, buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK))

            label = gtk.Label(_("An invalid DB version or missing tables have been detected."))
            diaDbVersionWarning.vbox.add(label)
            label.show()

            label = gtk.Label(_("This error is not necessarily fatal but it is strongly recommended that you recreate the tables by using the Database menu."))
            diaDbVersionWarning.vbox.add(label)
            label.show()

            label = gtk.Label(_("Not doing this will likely lead to misbehaviour including fpdb crashes, corrupt data etc."))
            diaDbVersionWarning.vbox.add(label)
            label.show()

            response = diaDbVersionWarning.run()
            diaDbVersionWarning.destroy()

        # TODO: This should probably be setup in GUI Init
        if self.status_bar is None:
            self.status_bar = gtk.Label("")
            self.main_vbox.pack_end(self.status_bar, False, True, 0)
            self.status_bar.show()

        if self.db is not None and self.db.is_connected():
            self.status_bar.set_text(_("Status: Connected to %s database named %s on host %s")
                                     % (self.db.get_backend_name(), self.db.database, self.db.host))
            # rollback to make sure any locks are cleared:
            self.db.rollback()

        #If the db-version is out of date, don't validate the config 
        # otherwise the end user gets bombarded with false messages
        # about every site not existing
        if hasattr(self.db, 'wrongDbVersion'):
            if not self.db.wrongDbVersion:
                self.validate_config()

    def obtain_global_lock(self, source):
        ret = self.lock.acquire(source=source)  # will return false if lock is already held
        if ret:
            print (_("Global lock taken by %s") % source)
            self.lockTakenBy=source
        else:
            print (_("Failed to get global lock, it is currently held by %s") % source)
        return ret
        # need to release it later:
        # self.lock.release()

    def quit(self, widget, data=None):
        # TODO: can we get some / all of the stuff done in this function to execute on any kind of abort?
        #FIXME  get two "quitting normally" messages, following the addition of the self.window.destroy() call
        #       ... because self.window.destroy() leads to self.destroy() which calls this!
        if not self.quitting:
            print _("Quitting normally")
            self.quitting = True
        # TODO: check if current settings differ from profile, if so offer to save or abort

        if self.db is not None:
            if self.db.backend == self.db.MYSQL_INNODB:
                try:
                    import _mysql_exceptions
                    if self.db is not None and self.db.is_connected():
                        self.db.disconnect()
                except _mysql_exceptions.OperationalError:  # oh, damn, we're already disconnected
                    pass
            else:
                if self.db is not None and self.db.is_connected():
                    self.db.disconnect()
        else:
            pass
        self.statusIcon.set_visible(False)

        self.window.destroy()  # explicitly destroy to allow child windows to close cleanly
        gtk.main_quit()

    def release_global_lock(self):
        self.lock.release()
        self.lockTakenBy = None
        print _("Global lock released.")

    def tab_auto_import(self, widget, data=None):
        """opens the auto import tab"""
        new_aimp_thread = GuiAutoImport.GuiAutoImport(self.settings, self.config, self.sql, self.window)
        self.threads.append(new_aimp_thread)
        aimp_tab = new_aimp_thread.get_vbox()
        self.add_and_display_tab(aimp_tab, _("HUD"))
        if options.autoimport:
            new_aimp_thread.startClicked(new_aimp_thread.startButton, "autostart")
            options.autoimport = False

    def tab_bulk_import(self, widget, data=None):
        """opens a tab for bulk importing"""
        new_import_thread = GuiBulkImport.GuiBulkImport(self.settings, self.config, self.sql, self.window)
        self.threads.append(new_import_thread)
        bulk_tab=new_import_thread.get_vbox()
        self.add_and_display_tab(bulk_tab, _("Bulk Import"))

    def tab_tourney_import(self, widget, data=None):
        """opens a tab for bulk importing tournament summaries"""
        new_import_thread = GuiTourneyImport.GuiTourneyImport(self.settings, self.config, self.sql, self.window)
        self.threads.append(new_import_thread)
        bulk_tab=new_import_thread.get_vbox()
        self.add_and_display_tab(bulk_tab, _("Tournament Results Import"))

    def tab_imap_import(self, widget, data=None):
        new_thread = GuiImapFetcher.GuiImapFetcher(self.config, self.db, self.sql, self.window)
        self.threads.append(new_thread)
        tab=new_thread.get_vbox()
        self.add_and_display_tab(tab, _("eMail Import"))
    #end def tab_import_imap_summaries

    def tab_ring_player_stats(self, widget, data=None):
        new_ps_thread = GuiRingPlayerStats.GuiRingPlayerStats(self.config, self.sql, self.window)
        self.threads.append(new_ps_thread)
        ps_tab=new_ps_thread.get_vbox()
        self.add_and_display_tab(ps_tab, _("Ring Player Stats"))

    def tab_tourney_player_stats(self, widget, data=None):
        new_ps_thread = GuiTourneyPlayerStats.GuiTourneyPlayerStats(self.config, self.db, self.sql, self.window)
        self.threads.append(new_ps_thread)
        ps_tab=new_ps_thread.get_vbox()
        self.add_and_display_tab(ps_tab, _("Tourney Stats"))

    def tab_tourney_viewer_stats(self, widget, data=None):
        new_thread = GuiTourneyViewer.GuiTourneyViewer(self.config, self.db, self.sql, self.window)
        self.threads.append(new_thread)
        tab=new_thread.get_vbox()
        self.add_and_display_tab(tab, _("Tourney Viewer"))

    def tab_positional_stats(self, widget, data=None):
        new_ps_thread = GuiPositionalStats.GuiPositionalStats(self.config, self.sql)
        self.threads.append(new_ps_thread)
        ps_tab=new_ps_thread.get_vbox()
        self.add_and_display_tab(ps_tab, _("Positional Stats"))

    def tab_session_stats(self, widget, data=None):
        new_ps_thread = GuiSessionViewer.GuiSessionViewer(self.config, self.sql, self.window, self)
        self.threads.append(new_ps_thread)
        ps_tab=new_ps_thread.get_vbox()
        self.add_and_display_tab(ps_tab, _("Session Stats"))

    def tab_hand_viewer(self, widget, data=None):
        new_ps_thread = GuiHandViewer.GuiHandViewer(self.config, self.sql, self.window)
        self.threads.append(new_ps_thread)
        ps_tab=new_ps_thread.get_vbox()
        self.add_and_display_tab(ps_tab, _("Hand Viewer"))

    def tab_main_help(self, widget, data=None):
        """Displays a tab with the main fpdb help screen"""
        mh_tab=gtk.Label(_("""Fpdb needs translators!
If you speak another language and have a few minutes or more to spare get in touch by emailing steffen@schaumburger.info

Welcome to Fpdb!
To be notified of new snapshots and releases go to https://lists.sourceforge.net/lists/listinfo/fpdb-announce and subscribe.
If you want to follow development more closely go to https://lists.sourceforge.net/lists/listinfo/fpdb-main and subscribe.

This program is currently in an alpha-state, so our database format is still sometimes changed.
You should therefore always keep your hand history files so that you can re-import after an update, if necessary.

For documentation please visit our website/wiki at http://fpdb.sourceforge.net/.
If you need help click on Contact - Get Help on our website.
Please note that default.conf is no longer needed nor used, all configuration now happens in HUD_config.xml.

This program is free/libre open source software licensed partially under the AGPL3, and partially under GPL2 or later.
The Windows installer package includes code licensed under the MIT license.
You can find the full license texts in agpl-3.0.txt, gpl-2.0.txt, gpl-3.0.txt and mit.txt in the fpdb installation directory."""))
        self.add_and_display_tab(mh_tab, _("Help"))

    def tabGraphViewer(self, widget, data=None):
        """opens a graph viewer tab"""
        new_gv_thread = GuiGraphViewer.GuiGraphViewer(self.sql, self.config, self.window)
        self.threads.append(new_gv_thread)
        gv_tab = new_gv_thread.get_vbox()
        self.add_and_display_tab(gv_tab, _("Graphs"))

    def tabTourneyGraphViewer(self, widget, data=None):
        """opens a graph viewer tab"""
        new_gv_thread = GuiTourneyGraphViewer.GuiTourneyGraphViewer(self.sql, self.config, self.window)
        self.threads.append(new_gv_thread)
        gv_tab = new_gv_thread.get_vbox()
        self.add_and_display_tab(gv_tab, _("Tourney Graphs"))

    def tabStove(self, widget, data=None):
        """opens a tab for poker stove"""
        thread = GuiStove.GuiStove(self.config, self.window)
        self.threads.append(thread)
        tab = thread.get_vbox()
        self.add_and_display_tab(tab, _("Stove"))

    def __init__(self):
        # no more than 1 process can this lock at a time:
        self.lock = interlocks.InterProcessLock(name="fpdb_global_lock")
        self.db = None
        self.status_bar = None
        self.quitting = False
        self.visible = False
        self.threads = []     # objects used by tabs - no need for threads, gtk handles it
        self.closeq = Queue.Queue(20)  # used to signal ending of a thread (only logviewer for now)

        if options.initialRun:
            self.display_config_created_dialogue = True
            self.display_site_preferences = True
        else:
            self.display_config_created_dialogue = False
            self.display_site_preferences = False
            
        # create window, move it to specific location on command line
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        if options.xloc is not None or options.yloc is not None:
            if options.xloc is None:
                options.xloc = 0
            if options.yloc is None:
                options.yloc = 0
            self.window.move(options.xloc, options.yloc)
        
        # connect to required events
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_title("Free Poker DB - v%s" % (VERSION, ))
        # set a default x/y size for the window
        self.window.set_border_width(1)
        defx, defy = 900, 720
        sx, sy = gtk.gdk.screen_width(), gtk.gdk.screen_height()
        if sx < defx:
            defx = sx
        if sy < defy:
            defy = sy
        self.window.set_default_size(defx, defy)
        self.window.set_resizable(True)

        # main area of window
        self.main_vbox = gtk.VBox(False, 1)
        self.main_vbox.set_border_width(1)
        self.window.add(self.main_vbox)
        self.main_vbox.show()

        # create our Main Menu Bar
        menubar = self.get_menu(self.window)
        self.main_vbox.pack_start(menubar, False, True, 0)
        menubar.show()
        
        # create a tab bar
        self.nb = gtk.Notebook()
        self.nb.set_show_tabs(True)
        self.nb.show()
        self.main_vbox.pack_start(self.nb, True, True, 0)
        self.tabs = []          # the event_boxes forming the actual tabs
        self.tab_names = []     # names of tabs used since program started, not removed if tab is closed
        self.pages = []         # the contents of the page, not removed if tab is closed
        self.nb_tab_names = []  # list of tab names currently displayed in notebook

        # create the first tab
        self.tab_main_help(None, None)
        
        # determine window visibility from command line options
        if options.minimized:
            self.window.iconify()
        if options.hidden:
            self.window.hide()

        if not options.hidden:
            self.window.show()
            self.visible = True     # Flip on
            
        self.load_profile(create_db=True)
        
        if options.initialRun and self.display_site_preferences:
            self.dia_site_preferences(None,None)
            self.display_site_preferences=False

        # setup error logging
        if not options.errorsToConsole:
            fileName = os.path.join(self.config.dir_log, 'fpdb-errors.txt')
            print((_("Note: error output is being diverted to %s.") % self.config.dir_log) + " " +
                  _("Any major error will be reported there _only_."))
            errorFile = open(fileName, 'w', 0)
            sys.stderr = errorFile

        # set up tray-icon and menu
        self.statusIcon = gtk.StatusIcon()
        cards = os.path.join(self.config.graphics_path, u'fpdb-cards.png')
        if os.path.exists(cards):
            self.statusIcon.set_from_file(cards)
            self.window.set_icon_from_file(cards)
        elif os.path.exists('/usr/share/pixmaps/fpdb-cards.png'):
            self.statusIcon.set_from_file('/usr/share/pixmaps/fpdb-cards.png')
            self.window.set_icon_from_file('/usr/share/pixmaps/fpdb-cards.png')
        else:
            self.statusIcon.set_from_stock(gtk.STOCK_HOME)
        self.statusIcon.set_tooltip("Free Poker Database")
        self.statusIcon.connect('activate', self.statusicon_activate)
        self.statusMenu = gtk.Menu()

        # set default menu options
        self.addImageToTrayMenu(gtk.STOCK_ABOUT, self.dia_about)
        self.addImageToTrayMenu(gtk.STOCK_QUIT, self.quit)

        self.statusIcon.connect('popup-menu', self.statusicon_menu, self.statusMenu)
        self.statusIcon.set_visible(True)

        self.window.connect('window-state-event', self.window_state_event_cb)
        sys.stderr.write(_("fpdb starting ..."))
        
        if options.autoimport:
            self.tab_auto_import(None)
            
    def addImageToTrayMenu(self, image, event=None):
        menuItem = gtk.ImageMenuItem(image)
        if event is not None:
            menuItem.connect('activate', event)
        self.statusMenu.append(menuItem)
        menuItem.show()
        return menuItem
        
    def addLabelToTrayMenu(self, label, event=None):
        menuItem = gtk.MenuItem(label)
        if event is not None:
            menuItem.connect('activate', event)
        self.statusMenu.append(menuItem)
        menuItem.show()
        return menuItem
    
    def removeFromTrayMenu(self, menuItem):
        menuItem.destroy()
        menuItem = None

    def __iconify(self):
        self.visible = False
        self.window.set_skip_taskbar_hint(True)
        self.window.set_skip_pager_hint(True)

    def __deiconify(self):
        self.visible = True
        self.window.set_skip_taskbar_hint(False)
        self.window.set_skip_pager_hint(False)

    def window_state_event_cb(self, window, event):
        # Deal with iconification first
        if event.changed_mask & gtk.gdk.WINDOW_STATE_ICONIFIED:
            if event.new_window_state & gtk.gdk.WINDOW_STATE_ICONIFIED:
                self.__iconify()
            else:
                self.__deiconify()
            if not event.new_window_state & gtk.gdk.WINDOW_STATE_WITHDRAWN:
                return True
        # And then the tray icon click
        if event.new_window_state & gtk.gdk.WINDOW_STATE_WITHDRAWN:
            self.__iconify()
        else:
            self.__deiconify()
        # Tell GTK not to propagate this signal any further
        return True

    def statusicon_menu(self, widget, button, time, data=None):
        # we don't need to pass data here, since we do keep track of most all
        # our variables .. the example code that i looked at for this
        # didn't use any long scope variables.. which might be an alright
        # idea too sometime
        if button == 3:
            if data:
                data.show_all()
                data.popup(None, None, None, 3, time)
        pass

    def statusicon_activate(self, widget, data=None):
        # Let's allow the tray icon to toggle window visibility, the way
        # most other apps work
        if self.visible:
            self.window.hide()
        else:
            self.window.present()

    def info_box(self, str1, str2):
        diapath = gtk.MessageDialog(parent=self.window, flags=gtk.DIALOG_DESTROY_WITH_PARENT, type=gtk.MESSAGE_INFO,
                                    buttons=(gtk.BUTTONS_OK), message_format=str1)
        diapath.format_secondary_text(str2)
        response = diapath.run()
        diapath.destroy()
        return response

    def warning_box(self, str, diatitle=_("FPDB WARNING")):
        diaWarning = gtk.Dialog(title=diatitle, parent=self.window,
                                flags=gtk.DIALOG_DESTROY_WITH_PARENT,
                                buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK))

        label = gtk.Label(str)
        diaWarning.vbox.add(label)
        label.show()

        response = diaWarning.run()
        diaWarning.destroy()
        return response

    def validate_config(self):
        # check if sites in config file are in DB
        for site in self.config.supported_sites:    # get site names from config file
            try:
                self.config.get_site_id(site)                     # and check against list from db
            except KeyError, exc:
                log.warning("site %s missing from db" % site)
                dia = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_WARNING, buttons=(gtk.BUTTONS_OK), message_format=_("Unknown Site"))
                diastring = _("Warning:") +" " + _("Unable to find site '%s'") % site
                dia.format_secondary_text(diastring)
                dia.run()
                dia.destroy()

    def main(self):
        gtk.main()
        return 0


if __name__ == "__main__":
    me = fpdb()
    me.main()
