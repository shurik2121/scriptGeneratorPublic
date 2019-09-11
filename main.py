'''
# -*- coding: utf-8 -*-
# Created: Wed May 23 13:55:52 2018
# by: Alex Rudnik
# email: alex.rudnik@intel.com
'''
import sys
import os
import time
from os import listdir
from os import stat
from os import path
import os.path as path
from mimetypes import MimeTypes
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QColor
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QTreeWidgetItem, QCheckBox
from PyQt5.QtCore import QBasicTimer
from PyQt5.QtWidgets import QFileDialog, QApplication, QAction, QMainWindow, qApp
from libs.network_Thread import NetworkThread
from libs.powershell_Thread import powershellThread
import subprocess
import logging
from configparser import ConfigParser

# os.chdir(path.dirname(sys.argv[0]))
parser = ConfigParser()
parser.read('./ini/configuration.ini')
datepath = time.strftime("%d-%m-%Y")
LogPath = parser.get('locations', 'log_default_path')
if not os.path.exists(LogPath):
    os.makedirs('log')
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename=LogPath, level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger()

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class MyApp(QtWidgets.QWidget):

    def __init__(self):
        super(MyApp, self).__init__()
        self.load_css()
        ui = os.path.join(os.path.dirname(__file__), './ui/scriptGenerator2.ui')
        uic.loadUi(ui, self)
        # self.treeWidget.setAlternatingRowColors(True)
        self.treeWidget.setSortingEnabled(True)
        self.default_path = parser.get('locations', 'scripts_default_path')
        self.fgcListFilePath = parser.get('locations', 'fgcList_file_path')
        self.lastPath = self.default_path
        self.selectedScript = ()
        self.checkboxSelectedList = []
        self.setCheckboxDisabled = []
        '''After checking ping network those machines are offline- checkbox disabled  '''
        self.checkboxDisabledList = []
        '''After checking ping network those machines are online- checkbox enabled  '''
        self.checkboxEnabledList = []
        self.checkboxAllList = [self.FGC01, self.FGC02, self.FGC03, self.FGC04, self.FGC05, self.FGC06, self.FGC07,
                                self.FGC08,
                                self.FGC09, self.FGC10, self.FGC11, self.FGC12, self.FGC13, self.FGC14, self.FGC15,
                                self.FGC16,
                                self.FGC17, self.FGC18, self.FGC19, self.FGC20, self.FGC21, self.FGC22, self.FGC23,
                                self.FGC24,
                                self.FGC25, self.FGC26, self.FGC27, self.FGC28, self.FGC29, self.FGC30, self.FGC31,
                                self.FGC32,
                                self.FGC33, self.FGC34, self.FGC35, self.FGC36, self.FGC37, self.FGC38, self.FGCSPARE1,
                                self.FGCSPARE2,
                                self.FGCSPARE3, self.FGCSPARE4, self.Sync2, self.Sync1, self.Gateway, self.Output,
                                self.Outputspare,
                                self.Main, self.Nav, self.render01, self.render02, self.recon01, self.recon02,
                                self.recon03, self.recon04,
                                self.recon05, self.recon06, self.recon07, self.recon08, self.recon09, self.recon10,
                                self.recon11, self.recon12]
        for fgc in self.checkboxAllList:
            fgc.stateChanged.connect(self.clickEventCheckboxSelected)
        self.visuals()
        self.event_handler()
        self.eventPingFGCSystem()
        logger.info(">>> Deployer is started")

    def activate_checkbox_state(self):
        for fgc in self.checkboxAllList:
            fgc.stateChanged.connect(self.clickEventCheckboxSelected)

    def count_from_ini_collection(self):
        comp_list_to_add = str(len(parser.get('addcheckbox', 'checkbox_names').split(",")))
        return comp_list_to_add

    def event_handler(self):
        self.btnAddServer.setText('Add more ' + self.count_from_ini_collection() + ' servers')
        self.btnAddServer.clicked.connect(self.add_new_checkbox_server)
        self.initDefaultDirectory(self.default_path)
        self.btnRun.clicked.connect(self.click_event_main_logic)
        self.btnBrowse.clicked.connect(self.button_click_browse_directory)
        self.btnAll.clicked.connect(self.button_click_select_all)
        self.btnFGC.clicked.connect(self.click_event_selected_group)
        self.btnMgmt.clicked.connect(self.click_event_selected_group)
        self.btnRecon.clicked.connect(self.click_event_selected_group)
        self.btnClose.clicked.connect(self.click_event_close_app)
        self.btnInvert.clicked.connect(self.click_event_invert_checkbox_selection)
        self.btnNone.clicked.connect(self.click_event_none_selection)
        self.btnEdit.clicked.connect(self.click_event_edit_file)
        self.btnRefresh.clicked.connect(self.click_event_refresh_main_app)
        self.btnClear.clicked.connect(self.clear_new_server)
        self.treeWidget.itemDoubleClicked.connect(self.tree_widget_double_click)
        self.treeWidget.itemSelectionChanged.connect(self.event_tree_widget_selected_script)

    def visuals(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap('./img/alex.ico'), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.btnRun.setIcon(QtGui.QIcon('./img/play.png'))
        self.btnRun.setIconSize(QtCore.QSize(16, 16))
        self.btnEdit.setIcon(QtGui.QIcon('./img/edit.png'))
        self.btnEdit.setIconSize(QtCore.QSize(16, 16))
        self.btnBrowse.setIcon(QtGui.QIcon('./img/browse.png'))
        self.btnBrowse.setIconSize(QtCore.QSize(16, 16))
        self.btnClose.setIcon(QtGui.QIcon('./img/close.png'))
        self.btnClose.setIconSize(QtCore.QSize(16, 16))
        self.btnRefresh.setIcon(QtGui.QIcon('./img/refresh.png'))
        self.btnRefresh.setIconSize(QtCore.QSize(16, 16))
        self.btnInvert.setIcon(QtGui.QIcon('./img/invert.png'))
        self.btnInvert.setIconSize(QtCore.QSize(16, 16))
        self.btnNone.setIcon(QtGui.QIcon('./img/none.png'))
        self.btnNone.setIconSize(QtCore.QSize(16, 16))
        self.btnAll.setIcon(QtGui.QIcon('./img/all.png'))
        self.btnAll.setIconSize(QtCore.QSize(16, 16))
        self.btnFGC.setIcon(QtGui.QIcon('./img/plus.png'))
        self.btnFGC.setIconSize(QtCore.QSize(16, 16))
        self.btnMgmt.setIcon(QtGui.QIcon('./img/plus.png'))
        self.btnMgmt.setIconSize(QtCore.QSize(16, 16))
        self.btnRecon.setIcon(QtGui.QIcon('./img/plus.png'))
        self.btnRecon.setIconSize(QtCore.QSize(16, 16))

    def clear_new_server(self):
        """
            in my UI file is a horizontalLayout_24 exist in the main UI
            this allow me to reach this variable in the main code and apply changes and manipulation
            this function allow to clean the Layout from all the objects that have been created on
            right now there is no dynamic solution for horizontalLayout

        """
        count = self.horizontalLayout_24.count()
        for i in reversed(range(count)):
            self.horizontalLayout_24.itemAt(i).widget().setParent(None)

    def add_new_checkbox_server(self):
        """
            This function adding more servers to the application if needed.
            it's reading from ini file and checking the [addcheckbox] if names exist
            creating the servers as inaccessible unless it refresh all the servers

        """
        # TODO: when the button is clicked a dinamyc checkbox is added to the list of all server server01,
        #  server02 and etc....
        # TODO: i did a convert of UI --> PY and found how to create a checkbox = so now i have the tools to create
        #  dynamic checkbox
        i = 0
        self.new_server_to_add = parser.get('addcheckbox', 'checkbox_names').split(",")
        total_servers = len(self.new_server_to_add)
        if total_servers > 0:
            for newServer in self.new_server_to_add:
                i = i + 1
                if i <= 7:
                    '''create 7 servers in the row and break a line'''
                    self.checkboxTemplate = QtWidgets.QCheckBox(self.gbServers)
                    font = QtGui.QFont()
                    font.setPointSize(9)
                    self.checkboxTemplate.setFont(font)
                    self.checkboxTemplate.setObjectName(newServer)
                    self.checkboxTemplate.setText(newServer)
                    self.checkboxTemplate.setStyleSheet("color:red")
                    self.checkboxTemplate.setEnabled(True)
                    newHeight = self.geometry().height() + 21
                    self.checkboxTemplate.resize(self.geometry().width(), newHeight)
                    self.horizontalLayout_24.addWidget(self.checkboxTemplate)
                    self.gridLayout_2.addLayout(self.horizontalLayout_24, 11, 0, 1, 1)
                    self.checkboxAllList.append(self.checkboxTemplate)
                elif i <= 14:
                    '''continue creating servers in the new line up to 7 in line'''
                    self.horizontalLayout_26 = QtWidgets.QHBoxLayout()
                    self.horizontalLayout_26.setObjectName("horizontalLayout_26")
                    for newServer in self.new_server_to_add:
                        self.checkboxTemplate = QtWidgets.QCheckBox(self.gbServers)
                        font = QtGui.QFont()
                        font.setPointSize(9)
                        self.checkboxTemplate.setFont(font)
                        self.checkboxTemplate.setObjectName(newServer)
                        self.checkboxTemplate.setText(newServer)
                        self.checkboxTemplate.setStyleSheet("color:grey")
                        self.checkboxTemplate.setEnabled(True)
                        newHeight = self.geometry().height() + 21
                        self.checkboxTemplate.resize(self.geometry().width(), newHeight)
                        self.horizontalLayout_26.addWidget(self.checkboxTemplate)
                        self.gridLayout_2.addLayout(self.horizontalLayout_26, 15, 0, 1, 1)
                        self.checkboxAllList.append(self.checkboxTemplate)
                else:

                    print('You reached your limitation more than 15 servers ! ! !')
        else:
            pass
            '''button disabled at line 558'''

        self.add_dynamic_plus_button_to_add_new_servers()
        print('added all new servers, please see the configuration file')

    def add_dynamic_plus_button_to_add_new_servers(self):
        self.activate_checkbox_state()
        self.btnNewServers = QtWidgets.QPushButton(self.gbServers)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.btnNewServers.setFont(font)
        self.btnNewServers.setToolTipDuration(-1)
        self.btnNewServers.setText("")
        self.btnNewServers.setObjectName("btnNewServers")
        # self.buttonGroup.addButton(self.btnNewServers)
        self.horizontalLayout_24.addWidget(self.btnNewServers)
        self.btnNewServers.setToolTip("<html><head/><body><p>select all new Servers</p></body></html>")
        self.btnNewServers.setIcon(QtGui.QIcon('./img/plus.png'))
        self.btnNewServers.setIconSize(QtCore.QSize(16, 16))
        self.btnNewServers.clicked.connect(self.click_event_selected_group)

    def tree_widget_double_click(self, item, column_no):
        # print('double clicked')
        # print(column_no)
        suffix_list = parser.get('scripts', 'script_files').split(",")
        folder_file = item.text(0)
        if self.cut_script_suffix(folder_file) in suffix_list:
            self.event_tree_widget_selected_script()
            self.click_event_main_logic()
            print('selected file is script not a folder: ' + self.selectedScript)
        else:
            self.treeWidget.clear()
            self.initDefaultDirectory(self.lastPath + '\\' + folder_file)
            self.lastPath = self.lastPath + '\\' + folder_file

    def event_tree_widget_selected_script(self):
        getSelected = self.treeWidget.selectedItems()
        if getSelected:
            baseNode = getSelected[0]
            getChildNode = baseNode.text(0)
            self.selectedScript = self.default_path + "\\" + getChildNode

    def button_click_browse_directory(self):
        dname = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.treeWidget.clear()
        self.lastPath = dname.replace('/', '\\')
        self.initDefaultDirectory(dname)
        logger.debug(">>> browse button clicked")

    def initDefaultDirectory(self, defaultpath):
        ifFilter = parser.get('filter', 'browse_filter_files')
        # powershel = parser.get('scripts', 'powershell_script')
        # cmd = parser.get('scripts', 'commandLine_script')
        suffix_list = parser.get('scripts', 'script_files').split(",")
        dname = defaultpath
        if dname != '':
            dname = dname.replace('/', '\\')
        if path.isdir(dname):
            for element in listdir(dname):
                name = element
                if ifFilter == 'yes':
                    if self.cut_script_suffix(name) in suffix_list:
                        print(">>>>>>" + self.cut_script_suffix(name))
                        pathinfo = dname + "\\" + name
                        information = stat(pathinfo)
                        if path.isdir(pathinfo):
                            type = "File Folder"
                            size = ""
                        else:
                            mime = MimeTypes()
                            type = mime.guess_type(pathinfo)[0]
                            # size = str(information.st_size) + "bytes"
                            size = str("{0:.2f}".format(information.st_size / 1000000)) + "MB"
                        date = str(time.ctime(information.st_mtime))
                        # row = [name, date, type, size]
                        row = [name]
                        self.treeWidget.insertTopLevelItems(0, [QTreeWidgetItem(self.treeWidget, row)])
                    else:
                        pass
                else:  # show all folders and files
                    pathinfo = dname + "\\" + name
                    information = stat(pathinfo)
                    if path.isdir(pathinfo):
                        type = "File Folder"
                        size = ""
                    else:
                        mime = MimeTypes()
                        type = mime.guess_type(pathinfo)[0]
                        # size = str(information.st_size) + "bytes"
                        size = str("{0:.2f}".format(information.st_size / 1000000)) + "MB"
                    date = str(time.ctime(information.st_mtime))
                    # row = [name, date, type, size]
                    row = [name]
                    self.treeWidget.insertTopLevelItems(0, [QTreeWidgetItem(self.treeWidget, row)])
        logger.debug(">>> Default directory initialized")

    def click_event_edit_file(self):

        suffix_list = parser.get('scripts', 'script_files').split(",")
        edit_files = parser.get('scripts', 'editable_files').split(",")

        # TODO: some organization to this IF ELSE statement
        import subprocess as sp
        notepadPlusPlus = parser.get('applications', 'notepadplusplus')
        notepadPlusPlus86 = parser.get('applications', 'notepadplusplus86')
        notepad = parser.get('applications', 'notepad')

        if os.path.exists(notepadPlusPlus86):
            if (self.cut_script_suffix(self.selectedScript) in suffix_list) or (
                    self.cut_script_suffix(self.selectedScript) in edit_files):
                sp.Popen([notepadPlusPlus86, self.selectedScript])
                logger.info(">>> notepad++86 opened a file " + self.selectedScript)
            elif os.path.exists(notepadPlusPlus):
                if (self.cut_script_suffix(self.selectedScript) in suffix_list) or (
                        self.cut_script_suffix(self.selectedScript) in edit_files):
                    sp.Popen([notepadPlusPlus, self.selectedScript])
                    logger.info(">>> notepad++ opened a file " + self.selectedScript)
            else:
                QMessageBox.information(self, "information",
                                        "Hey you can not edit this one \n "
                                        "it could be a folder or check you "
                                        "configuration>>filter")
        else:
            if (self.cut_script_suffix(self.selectedScript) in suffix_list) or (
                    self.cut_script_suffix(self.selectedScript) in edit_files):
                sp.Popen([notepad, self.selectedScript])
                logger.info(">>> notepad opened a file " + self.selectedScript + " be aware notepad++ is missing")
            else:
                QMessageBox.information(self, "information",
                                        "Hey you can not edit this one \n "
                                        "it could be a folder or check you configuration>>filter")

    def load_css(self):
        cssFile = 'CSS/darkorange.stylesheet'
        with open(cssFile, 'r') as myfile:
            cssContent = myfile.read().replace('\n', '')
            app.setStyleSheet(cssContent)

    def clickEventCheckboxSelected(self, state):
        checkboxChecked = self.sender()
        print(checkboxChecked)
        if state == QtCore.Qt.Checked:
            self.checkboxSelectedList.append(checkboxChecked)
        else:
            self.checkboxSelectedList.remove(checkboxChecked)
            self.setCheckboxDisabled.append(checkboxChecked)
        return self.checkboxSelectedList

    def click_event_main_logic(self):


        # self.tmpDisableMachine = list(self.setCheckboxDisabled)
        # self.tmpCheckboxAllList = list(self.checkboxAllList)
        if os.path.isfile(self.fgcListFilePath + '\\' + parser.get('files', 'fgcList_file_name')):
            print(self.fgcListFilePath + '\\' + parser.get('files', 'fgcList_file_name'))
            totalSelectedFGC = len(self.checkboxSelectedList)
            if totalSelectedFGC != 0:
                '''WRITE FILE & CREATE'''
                f = open(self.fgcListFilePath + '\\' + parser.get('files', 'fgcList_file_name'), "w+")
                for i in range(totalSelectedFGC):
                    f.write(self.checkboxSelectedList[i].text() + '\n')
                f.close()
                logger.debug(">>> the " + "\\" + parser.get('files', 'fgcList_file_name') + "file is generated")
                self.sorting_file()
                self.execute_scripts()
                '''END: WRITE FILE & CREATE'''
            else:
                QMessageBox.warning(self, "warning", "Warning, scripts or servers are not selected  \n")
                logger.debug(">>> the" + "\\" + parser.get('files', 'fgcList_file_name') + "file is not generated")
        else:
            open(self.fgcListFilePath + "\\" + parser.get('files', 'fgcList_file_name'), "a")
            totalSelectedFGC = len(self.checkboxSelectedList)
            if totalSelectedFGC != 0:
                '''WRITE FILE & CREATE'''
                f = open(self.fgcListFilePath + "\\" + parser.get('files', 'fgcList_file_name'), "w+")
                for i in range(totalSelectedFGC):
                    f.write(self.checkboxSelectedList[i].text() + '\n')
                f.close()
                self.sorting_file()
                self.execute_scripts()
                '''END: WRITE FILE & CREATE'''
            else:
                QMessageBox.warning(self, "warning", "Warning, scripts or servers are not selected  \n")

    def execute_scripts(self):
        scriptSuffix = self.cut_script_suffix(self.selectedScript)
        if scriptSuffix == 'ps1':
            screenOutput = ''
            print("running PS1 installation : " + self.selectedScript)
            logger.info(">>> selected powershell file " + self.selectedScript)
            self.powershell_thread = powershellThread(self.selectedScript)
            self.powershell_thread.start()
            # self.powershell_thread.join()
            print(self.powershell_thread.stdout)
            print(self.powershell_thread.stderr)
            logger.info(">>> completed " + self.selectedScript)
        elif scriptSuffix == 'cmd' or scriptSuffix == 'bat':  # check if its dos file BAT ?
            print("running batch installation : " + self.selectedScript)
            logger.info(">>> selected cmd file " + self.selectedScript)
            output = subprocess.Popen(self.selectedScript, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            print("running bat files is completed")
            logger.info(">>> completed " + self.selectedScript)
        else:
            QMessageBox.warning(self, "Warning", "Error! Can not execute this file \n" + str(self.selectedScript))
            logger.info(">>> selected file are not cmd or powershell script")

    def sorting_file(self):
        totalSelectedFGC = len(self.checkboxSelectedList)
        inputFile = open(self.fgcListFilePath + "\\" + parser.get('files', 'fgcList_file_name'), 'r')
        lineList = inputFile.readlines()
        lineList.sort()
        f = open(self.fgcListFilePath + "\\" + parser.get('files', 'fgcList_file_name'), "w")
        for i in range(totalSelectedFGC):
            f.write(lineList[i])
        f.close()

    def cut_script_suffix(self, suffix):
        return suffix[-3:]

    def button_click_select_all(self):
        for fgc in self.checkboxEnabledList:
            fgc.setChecked(True)
        print('All selected')

    def click_event_selected_group(self):
        buttonSelected = str(self.sender().objectName())
        if buttonSelected == 'btnFGC':
            for fgc in self.checkboxAllList:
                if str(fgc.objectName()).startswith('FGC'):
                    if fgc.setTristate:
                        fgc.setChecked(True)
                        # print('this machine is selected:' + str(fgc.objectName()))
            print('all fgc selected')
        elif buttonSelected == 'btnMgmt':
            mgmtList = ['Sync2', 'Sync1', 'Gateway', 'Output', 'Outputspare', 'Main', 'Nav']
            for fgc in self.checkboxAllList:
                for mgmt in mgmtList:
                    if fgc.stateChanged:
                        if str(fgc.objectName()) == mgmt:
                            # print('this machine is selected:' + str(fgc.objectName()))
                            fgc.setChecked(True)
            print('all mgmt selected')
        elif buttonSelected == 'btnRecon':
            for fgc in self.checkboxAllList:
                if fgc.setEnabled:
                    if str(fgc.objectName()).startswith('re'):
                        fgc.setChecked(True)
            print('all 3rd rack selected')
        # those are extra servers were creating in configuration.ini
        elif buttonSelected == 'btnNewServers':
            totalAll = len(self.checkboxAllList) - 1
            totalNew = len(parser.get('addcheckbox', 'checkbox_names').split(","))
            print(totalAll)
            print(totalNew)
            for i in range(totalAll, totalAll - totalNew, -1):
                print(self.checkboxAllList[i].objectName())
                if self.checkboxAllList[i].setEnabled:
                    if self.checkboxAllList[i].stateChanged:
                        self.checkboxAllList[i].setChecked(True)
            # TODO: selection is working but if you Refreshing and checkbox are offline they still will be seleted,
            #  need to be fixed!
        else:
            print('nothing clicked')

    def click_event_refresh_main_app(self):
        for fgc in self.checkboxAllList:
            fgc.setChecked(False)
            fgc.setEnabled(True)
            fgc.setStyleSheet('color:#b1b1b1;font-weight:normal;')
        self.eventPingFGCSystem()
        print('refresh selected')

    def click_event_close_app(self):
        choice = QMessageBox.question(self, 'quit',
                                      "are you sure want to close?", QMessageBox.Yes | QMessageBox.No)
        if choice == 16384:  # 16384=yes | 65536=no
            logger.info(">>> Deployer is closed")
            sys.exit(0)
        else:
            pass

    def click_event_invert_checkbox_selection(self):

        # full temp list of checkbox selected.
        self.tmpCheckboxAllList = list(self.checkboxAllList)
        #
        self.tmpCheckboxSelectedList = list(self.checkboxSelectedList)

        for x in self.tmpCheckboxSelectedList:
            if x in self.tmpCheckboxAllList:
                self.tmpCheckboxAllList.remove(x)

        for z in self.tmpCheckboxSelectedList:
            z.setChecked(False)

        for y in self.tmpCheckboxAllList:
            y.setChecked(True)
        print('Invert selection')

    def click_event_none_selection(self):
        for fgc in self.checkboxAllList:
            fgc.setChecked(False)
        print('All unselected')

    def eventPingFGCSystem(self):
        self.network_thread = NetworkThread(self.checkboxAllList)
        self.network_thread.start()
        self.network_thread.connection.connect(self.get_connection_info)

    def get_connection_info(self, connection_list):
        if connection_list:
            print('Network >>ping>> completed')
            for connection in connection_list:
                if connection[1] == 'color:green;':
                    connection[0].setStyleSheet(connection[1])
                    self.checkboxEnabledList.append(connection[0])
                else:
                    connection[0].setStyleSheet(connection[1])
                    connection[0].setEnabled(False)
                    connection[0].setChecked(False)
                    self.checkboxDisabledList.append(connection[0])

            if not parser.get('addcheckbox', 'checkbox_names'):
                print('no extra server to create in configuration.ini')
                self.btnAddServer.setDisabled(True)
                self.btnClear.setDisabled(True)

            else:
                self.btnAddServer.setDisabled(False)
                self.btnClear.setDisabled(False)

            '''export a file to \scripts\ offline.txt'''
            if len(self.checkboxDisabledList) > 0:
                f = open(self.fgcListFilePath + '\\' + parser.get('files', 'fgclist_offline_file'), "w+")
                for i in range(len(self.checkboxDisabledList)):
                    f.write(self.checkboxDisabledList[i].text() + '\n')
                f.close()
                logger.debug(
                    ">>> the " + "\\" + parser.get('files', 'fgclist_offline_file') + "file is generated successfully")

                ''' sort the fgc_offline_list.txt'''
                f = open(self.fgcListFilePath + "\\" + parser.get('files', 'fgclist_offline_file'), 'r')
                lineList = f.readlines()
                lineList.sort()
                f = open(self.fgcListFilePath + "\\" + parser.get('files', 'fgclist_offline_file'), "w")
                for i in range(len(self.checkboxDisabledList)):
                    f.write(lineList[i])
                f.close()
                QMessageBox.information(self, "information",
                                        "It's a friendly notification.\nBe aware some of the servers are offline and"
                                        " not available.\nPlease check: \scripts\\offline.txt")
        else:
            print("shit")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
