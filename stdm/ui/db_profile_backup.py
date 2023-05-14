"""
/***************************************************************************
Name                 : DBProfileBackupDialog
Description          : Dialog for doing profile and database backup
Date                 : 01/10/2022
copyright            : (C) 2016 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os
import sys
import shutil
import json
import winreg
from zipfile import ZipFile

import subprocess
from subprocess import Popen

from qgis.PyQt import uic

from qgis.PyQt.QtWidgets import (
        QDialog,
        QMessageBox,
        QFileDialog,
        QLineEdit,
        QTreeWidgetItem
)

from qgis.PyQt.QtCore import (
        Qt,
        QDir,
        QDateTime,
        QCoreApplication
)

from qgis.gui import QgsGui

from stdm.ui.gui_utils import GuiUtils
from stdm.data.config import DatabaseConfig
from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.data.connection import DatabaseConnection
from stdm.data.configuration.profile import Profile
from stdm.security.user import User
from stdm.composer.document_template import DocumentTemplate

from stdm.utils.util import (
    PLUGIN_DIR,
    documentTemplates,
    user_non_profile_views
)

class StreamHandler:
    def log(self, msg: str):
        raise NotImplementedError

class StdOutHandler(StreamHandler):
    def log(self, msg: str):
        print(msg)

class FileHandler(StreamHandler):
    def __init__(self, msg: str):
        dtime = QDateTime.currentDataTime().toString('ddMMyyyy_HH.mm')
        filename ='/.stdm/logs/template_converter_{}.log'.format(dtime)
        self.log_file = '{}{}'.format(QDir.home().path(),  filename)

    def log(self, msg: str):
        with open(self.log_file, 'a') as lf:
            lf.write(msg)
            lf.write('\n')

class MessageLogger:
    def __init__(self, handler:StreamHandler=StdOutHandler):
        self.stream_handler =  handler()

    def log_error(self, msg: str):
        log_msg = 'ERROR: {}'.format(msg)
        self.stream_handler.log(log_msg)

    def log_info(self, msg: str):
        log_msg = 'INFO: {}'.format(msg)
        self.stream_handler.log(log_msg)

WIDGET, BASE = uic.loadUiType(
        GuiUtils.get_ui_file_path('ui_db_profile_backup.ui'))

class DBProfileBackupDialog(WIDGET, BASE):
    def __init__(self, iface):
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface

        self.tbBackupFolder.clicked.connect(self.backup_folder_clicked)
        self.btnBackup.clicked.connect(self.do_backup)
        self.btnClose.clicked.connect(self.close_dialog)

        self.db_config = DatabaseConfig()

        self.db_conn = self.db_config.read()  # DatabaseConnection
        self.txtDBName.setText(self.db_conn.Database)
        self.txtAdmin.setText('postgres')
        self.lblStatus.setText('')

        self.config_templates = []

        self.stdm_config = StdmConfiguration.instance()
        self.twProfiles.setColumnCount(1)
        self.load_profiles_tree()
        pg_base_folder = self.get_pg_base_folder()

        self.msg_logger = MessageLogger(StdOutHandler)

    def load_profiles_tree(self):
        profiles = self.stdm_config.profiles
        for profile in profiles.values():
            profile_item = QTreeWidgetItem()
            profile_item.setText(0, profile.key)
            profile_item.setIcon(0, GuiUtils.get_icon("folder.png"))

            entity_node = QTreeWidgetItem()
            entity_node.setText(0, "Entities")
            profile_item.addChild(entity_node)

            entity_items =  self._profile_entities(profile)
            entity_node.addChildren(entity_items)

            template_node = QTreeWidgetItem()
            template_node.setText(0, "Templates")
            profile_item.addChild(template_node)
            
            templates = self._profile_templates(profile)
            template_node.addChildren(templates)

            self.twProfiles.insertTopLevelItem(0, profile_item)


    def _profile_entities(self, profile: Profile) ->list[QTreeWidgetItem]:
        entity_items = []
        for entity in profile.entities.values():
            if not entity.user_editable:
                continue
            entity_item = QTreeWidgetItem()
            entity_item.setText(0, entity.short_name)
            entity_item.setIcon(0, GuiUtils.get_icon("Table02.png"))
            entity_items.append(entity_item)
        return entity_items

    def _profile_templates(self, profile: Profile) ->list[QTreeWidgetItem]:
        template_items = []
        templates = documentTemplates()
        profile_tables = profile.table_names()
        for name, filepath in templates.items():
            doc_temp = DocumentTemplate.build_from_path(name, filepath)
            if doc_temp.data_source is None:
                continue
            if doc_temp.data_source.referenced_table_name in profile_tables or \
                 doc_temp.data_source.name() in user_non_profile_views():
                template_item = QTreeWidgetItem()
                template_item.setText(0, doc_temp.name)
                template_item.setIcon(0, GuiUtils.get_icon("record02.png"))
                template_items.append(template_item)
                self.config_templates.append(filepath)
        return template_items

    def backup_folder_clicked(self):
        self._set_selected_directory(self.edtBackupFolder, 
                self.tr('Configuration file and DB backup folder')
            )

    def _set_selected_directory(self, txt_box: QLineEdit, title: str):
        def_path = txt_box.text()
        sel_doc_path = QFileDialog.getExistingDirectory(self, title, def_path)

        if sel_doc_path:
            normalized_path = f"{QDir.fromNativeSeparators(sel_doc_path)}/{self.db_conn.Database}"
            txt_box.clear()
            txt_box.setText(normalized_path)

    def do_backup(self):
        if self.edtAdminPassword.text() == '':
            msg = self.tr('Please enter password for user `postgres`')
            self.show_message(msg, QMessageBox.Critical)
            return False

        if self.edtBackupFolder.text() == '':
            msg = self.tr('Please select a backup folder')
            self.show_message(msg, QMessageBox.Critical)
            return False

        db_con = DatabaseConnection(self.db_conn.Host, self.db_conn.Port,
                self.db_conn.Database)

        user = User('postgres', self.edtAdminPassword.text())
        db_con.User = user

        validity, msg = db_con.validateConnection()

        if validity == False:
            error_type = self.tr('Authentication Failed!')
            error_msg = '{}: `{}`'.format(error_type, msg)
            QMessageBox.critical(self, self.tr('BackupDialog', error_type),
                    error_msg)

            self.msg_logger.log_error(error_msg)
            return False

        db_name = self.db_conn.Database
        db_backup_filename = self._make_backup_filename(db_name)

        self.lblStatus.setText('Backup started, please wait...')
        QCoreApplication.processEvents()

        path_sep = "/"
        backup_folder = f"{self.edtBackupFolder.text()}"
        db_backup_filepath =f"{backup_folder}{path_sep}{db_backup_filename}"

        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        if not self.backup_database(self.db_conn, 'postgres',
                self.edtAdminPassword.text(), db_backup_filepath):
                return

        stdm_folder = ".stdm"
        config_file ='configuration.stc'
        home_folder = QDir.home().path()
        config_filepath = f"{home_folder}{path_sep}{stdm_folder}{path_sep}{config_file}"
        config_backup_filepath = f"{backup_folder}{path_sep}{config_file}"

        self.backup_config_file(config_filepath, config_backup_filepath)

        self.backup_templates(self.config_templates, backup_folder)
        
        template_file_names = self._get_template_file_names(self.config_templates)

        log_dtime = self._dtime()
        json_ext = ".json"
        log_filename = f"backuplog_{log_dtime}{json_ext}"
        log_filepath = f"{backup_folder}{path_sep}{log_filename}"

        backup_log = self._make_log(self.stdm_config.profiles.keys(), db_name,
                db_backup_filename, template_file_names, log_dtime, self.cbCompress.isChecked())

        self.create_backup_log(backup_log, log_filepath)

        if self.cbCompress.isChecked():
            compressed_files = []
            compressed_files.append(db_backup_filepath)
            compressed_files.append(config_backup_filepath)
            compressed_files.append(log_filepath)
            backed_templates = self._backed_template_files(template_file_names, backup_folder)
            compressed_files += backed_templates

            if self.compress_backup(db_name, backup_folder, compressed_files):
                self._remove_compressed_files(compressed_files)
        
        self.lblStatus.setText('Backup completed.')
        
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(self.tr('Backup completed successfully.'))
        msg_box.setInformativeText(self.tr('Do you want to open the backup folder?'))
        msg_box.setStandardButtons(QMessageBox.Save | QMessageBox.Close)
        msg_box.setDefaultButton(QMessageBox.Close)
        save_btn = msg_box.button(QMessageBox.Save)
        save_btn.setText('Open Backup Folder')
        close_btn = msg_box.button(QMessageBox.Close)

        msg_box.exec_()
        if msg_box.clickedButton() == save_btn:
            self.open_backup_folder()
        if msg_box.clickedButton() == close_btn:
            self.close_dialog()

    def open_backup_folder(self):
        backup_folder = self.edtBackupFolder.text()

        # windows
        if sys.platform.startswith('win32'):
            os.startfile(backup_folder)

        # *nix systems
        if sys.platform.startswith('linux'):
            subprocess.Popen(['xdg-open', backup_folder])

        # macOS
        if sys.platform.startswith('darwin'):
            subprocess.Popen(['open', backup_folder])

    def close_dialog(self):
        self.done(0)

    def _make_backup_filename(self, database_name) -> str:
        date_str = QDateTime.currentDateTime().toString('ddMMyyyyHHmm')
        backup_file = '{}{}{}{}'.format(database_name, '_', date_str,'.backup')
        return backup_file

    def backup_database(self, db_conn: DatabaseConnection, user: str,
                         password: str, backup_filepath: str) -> bool:

        backup_util = self.get_pg_base_folder()+"\\bin\\pg_dump.exe"
        if backup_util == "":
            return False

        script_file = "/scripts/dbbackup.bat"
        script_filepath = f"{PLUGIN_DIR}{script_file}"
        backup_folder = f"{self.edtBackupFolder.text()}"

        startup_info = subprocess.STARTUPINFO()
        startup_info.dwFlags |=subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen([script_filepath, db_conn.Database, 
            db_conn.Host, str(db_conn.Port), user, password, backup_folder, backup_util,
            backup_filepath], startupinfo=startup_info)

        stdout, stderr = process.communicate()
        process.wait()

        result_code = process.returncode

        return True if result_code == 0 else False


    def backup_config_file(self, config_filepath:str, backup_filepath: str):
        shutil.copyfile(config_filepath, backup_filepath)

    def backup_templates(self, template_files:list[str], backup_folder: str):
        path_sep = "/"
        for template_filepath in template_files:
            filename = os.path.basename(template_filepath)
            backup_filepath = f"{backup_folder}{path_sep}{filename}"
            shutil.copyfile(template_filepath, backup_filepath)

    def _get_template_file_names(self, templates: list[str]):
        template_file_names = []
        for template_filepath in templates:
            template_file_names.append(os.path.basename(template_filepath))
        return template_file_names

    def _backed_template_files(self, template_file_names: str, backup_folder: str) -> list[str]:
        temp_files = []
        path_sep = "/"
        for template_name in template_file_names:
            filename = f"{backup_folder}{path_sep}{template_name}"
            temp_files.append(filename)
        return temp_files


    def compress_backup(self, compressed_filename:str, backup_folder: str, files:list[str]) -> bool:
        """
        param: files
        type: list
        """
        path_sep = "/"
        name_sep = "_"
        file_ext = ".zip"
        
        dtime =QDateTime.currentDateTime().toString('ddMMyyyyHHmm')
        zip_filepath = f"{backup_folder}{path_sep}{compressed_filename}{name_sep}{dtime}{file_ext}"

        try:
            self.write_zip_file(files, zip_filepath)
        except BadZipfile:
            self.log_error('Failed to compress backup!')
            return False
        return True

    def _remove_compressed_files(self, files):
        for file in files:
            if os.path.isfile(file):
                os.remove(file)

    def _dtime(self):
        return QDateTime.currentDateTime().toString('dd-MM-yyyy HH.mm')

    def _make_log(self, profiles: list, db_name: str, db_backup_filename: str,
            template_file_names: list[str], log_dtime: str, is_compressed: bool) -> dict:

        backup_log = {'configuration':{'filename':'configuration.stc',
                                       'profiles':list(profiles),
                                       'templates': template_file_names,
               'database':{'name':db_name,
                           'backup_file':db_backup_filename},
               'created_on':log_dtime,
               'compressed':is_compressed
              }}

        return backup_log

    def create_backup_log(self, log: dict, log_file: str):
        with open(log_file, 'w') as lf:
            json.dump(log, lf, indent=4)

    def write_zip_file(self, file_list: list, zip_file: str):
        with ZipFile(zip_file, 'w') as zf:
            for file in file_list:
                basename = os.path.basename(file)
                zf.write(file, arcname=basename)

    def show_message(self, msg: str, icon_type):
        msg_box = QMessageBox()
        msg_box.setText(msg)
        msg_box.setIcon(icon_type)
        msg_box.exec_()

    def get_pg_base_folder(self):
        """
        PostgrSQL base folder
        """
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\PostgreSQL\\Installations\\")
        pg_base_value = ""
        for i in range(winreg.QueryInfoKey(reg_key)[0]):
            try:
                subkey_name = winreg.EnumKey(reg_key, i)
                subkey = winreg.OpenKey(reg_key, subkey_name)

                for j in range(winreg.QueryInfoKey(subkey)[1]):
                    name, value,_ = winreg.EnumValue(subkey, j)
                    if name == "Base Directory":
                        pg_base_value = value
                        break
                if not pg_base_value == "":
                    break
                winreg.CloseKey(subkey)
            except OSError:
                pass
        winreg.CloseKey(reg_key)

        return pg_base_value





