# from Library.settings_json import usettings
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QAbstractItemView
from uglypty.Library.models import Cred
from uglypty.Library.db import get_by_dbquery
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from creds_dlg import Ui_dlgCreds
import json
from uglypty.Library.util import encrypt


# used to make table selection by row only
class ReadOnlyDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        print('createEditor event fired')
        return

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.formIsDirty = False
        MainWindow.setObjectName("TerminalsUI")
        MainWindow.resize(883, 299)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.twCreds = QtWidgets.QTableWidget(self.centralwidget)
        self.twCreds.setObjectName("twCreds")
        self.twCreds.setColumnCount(3)
        self.twCreds.setRowCount(0)
        # enable context menu's
        self.twCreds.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.twCreds.customContextMenuRequested['QPoint'].connect(self.tw_right_click)
        self.twCreds.horizontalHeader().setDefaultSectionSize(180)
        item = QtWidgets.QTableWidgetItem()
        self.twCreds.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.twCreds.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.twCreds.setHorizontalHeaderItem(2, item)
        self.verticalLayout.addWidget(self.twCreds)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 883, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuCreds")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionExit.triggered.connect(lambda: sys.exit())
        self.actionAdd = QtGui.QAction(MainWindow)
        self.actionAdd.setObjectName("actionAdd")
        self.actionAdd.triggered.connect(lambda: self.creds_add())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionAdd)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("TerminalsUI", "Device Credentials"))
        item = self.twCreds.horizontalHeaderItem(0)
        item.setText(_translate("TerminalsUI", "id"))
        item = self.twCreds.horizontalHeaderItem(1)
        item.setText(_translate("TerminalsUI", "username"))
        item = self.twCreds.horizontalHeaderItem(2)
        item.setText(_translate("TerminalsUI", "password"))
        self.menuFile.setTitle(_translate("TerminalsUI", "File"))
        self.actionExit.setText(_translate("TerminalsUI", "Exit"))
        self.actionAdd.setText(_translate("TerminalsUI", "Add Record"))

        # make whole table read only
        delegateTw = ReadOnlyDelegate(self.twCreds)
        self.twCreds.setItemDelegate(delegateTw)

        # select by row only
        self.twCreds.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.twCreds.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.load_db_creds()


    def tw_right_click(self):
        selected = self.twCreds.currentIndex()
        engine = create_engine(f'sqlite:///settings.sqlite', echo=False)
        engine.connect()
        sqlite_session = Session(bind=engine)
        # print(f"Selected Row: {selected.row()}!")
        if selected.row() != -1:
            # refBinding created when item created. col 0 is container
            try:
                print(f"selected: {self.twCreds.item(selected.row(),0).refBinding['Username']}")
            except:
                self.notify("data error", f"error reading refbinding")
                return
            top_menu = QtWidgets.QMenu()
            menu = top_menu.addMenu("Menu")
            _edit = menu.addAction("&Edit ...")
            _delete = menu.addAction("&Delete ...")
            action = menu.exec(QtGui.QCursor.pos())
            if action == _edit:
                self.creds_edit()

            if action == _delete:
                self.creds_delete()

    def confirm(self, message, info):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Icon.Information)
        msgBox.setText(info)
        msgBox.setWindowTitle(message)
        msgBox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Cancel)
        returnValue = msgBox.exec()
        return returnValue

    def creds_delete(self):
        selected = self.twCreds.currentIndex()
        if selected.row() != -1:
            delete_item = self.twCreds.item(selected.row(), 0)
            # print(f"deleting selected user: {delete_item.refBinding['Username']} ID: {delete_item.refBinding['id']}")
            try:
                # now save to DB
                engine = create_engine(f'sqlite:///settings.sqlite', echo=False)
                engine.connect()
                sqlite_session = Session(bind=engine)
                sql = f"select * from creds where id = {delete_item.refBinding['id']}"
                sql_result = get_by_dbquery(Cred, sqlite_session, sql)

                if len(sql_result) == 0:
                    self.notify("DB Error", f"Error processing database: No Device Records")
                else:
                    response = self.confirm("Delete?", f"Delete creds: {self.twCreds.item(selected.row(), 1).text()}")
                    if response == QtWidgets.QMessageBox.StandardButton.Ok:
                        print(
                            f"deleting selected user: {delete_item.refBinding['Username']} ID: {delete_item.refBinding['id']}")
                        sqlite_session.delete(sql_result[0])
                        sqlite_session.commit()
                        self.twCreds.setRowCount(0)
                        self.load_db_creds()


            except Exception as e:
                print(e)
                self.notify("Database Error", f"Error deleting creds: {e}")

    def creds_add(self):
        stub_item = {'id': 'New', 'Username': '', 'Password': ''}
        dlg = QtWidgets.QDialog()
        dlg.setModal(True)
        ui = Ui_dlgCreds()
        ui.setupUi(dlg, stub_item, "ADD")
        # ui.mode = "ADD"
        dlg.show()
        result = dlg.exec()
        if result == 1:
            encrypted_password = encrypt(stub_item)
            stub_item['Password'] = encrypted_password.decode('utf-8')
            print(f"Item to add: {json.dumps(stub_item)}")
            try:
                # now save to DB
                engine = create_engine(f'sqlite:///settings.sqlite', echo=False)
                engine.connect()
                sqlite_session = Session(bind=engine)
                cur = engine.execute("select id from creds order by id desc")
                first_record = cur.first()
                if first_record is None:
                    # empty table, start with 1
                    last_id = 0
                else:
                    last_id = first_record[0]
                # last_id = cur.first()[0]
                new_record = Cred(
                    id=last_id + 1,
                    Username=stub_item['Username'],
                    Password=stub_item['Password']
                )
                sqlite_session.add(new_record)
                sqlite_session.commit()
                sqlite_session.close()
                self.twCreds.setRowCount(0)
                self.load_db_creds()
            except Exception as e:
                print(e)
                self.notify("Database Error", f"Error processing creds: {e}")


    def creds_edit(self):
        selected = self.twCreds.currentIndex()
        if selected.row() != -1:
            print(f"editing selected row {selected.row()}")
            edit_item = self.twCreds.item(selected.row(), 0)
            try:
                print(edit_item.refBinding)
                dlg = QtWidgets.QDialog()
                dlg.setModal(True)
                ui = Ui_dlgCreds()
                ui.setupUi(dlg, edit_item.refBinding,"EDIT")
                dlg.show()
                result = dlg.exec()
                if result == 1:
                    self.formIsDirty = True
                    encrypted_password = encrypt(edit_item.refBinding['Password'])
                    edit_item.refBinding['Password'] = encrypted_password.decode('utf-8')
                    # verify item refBinding in col 0 of selected row is updated
                    print(f"Data to save: {self.twCreds.item(selected.row(), 0).refBinding}")

                    try:
                        # now save to DB
                        engine = create_engine(f'sqlite:///settings.sqlite', echo=False)
                        engine.connect()
                        sqlite_session = Session(bind=engine)
                        sql = f"select * from creds where id = {edit_item.refBinding['id']}"
                        sql_result = get_by_dbquery(Cred, sqlite_session, sql)
                        current_row = 0
                        if len(sql_result) == 0:
                            self.notify("DB Error", f"Error processing database: No Device Records")
                        else:
                            print(sql_result[0])
                            sql_result[0].Username = edit_item.refBinding['Username']
                            sql_result[0].Password = edit_item.refBinding['Password']
                            sqlite_session.commit()
                        sqlite_session.close()
                        # reload table for data refresh
                        self.twCreds.setRowCount(0)
                        self.load_db_creds()
                    except Exception as e:
                        print(e)
                        self.notify("Database Error", f"Error processing creds: {e}")


            except Exception as e:
                self.notify("edit error", "Error opening row, no refBinding data")


    def notify(self, message, info):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
        msg.setText(info)
        msg.setWindowTitle(message)
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        retval = msg.exec()

    def load_db_creds(self):
        engine = create_engine(f'sqlite:///settings.sqlite', echo=False)
        engine.connect()
        sqlite_session = Session(bind=engine)
        try:
            sql = "select * from creds"
            sql_result = get_by_dbquery(Cred, sqlite_session, sql)
            current_row = 0
            if len(sql_result) == 0:
                self.notify("New DB", f"No Credentials Records, start by adding new creds")
            else:
                self.twCreds.setRowCount(len(sql_result))
                cred_list = []
                map_cmdb = {
                    0: "id",
                    1: "Username",
                    2: "Password"
                }
                for cred in sql_result:
                    # print(cred)
                    tcred = cred.toDict()
                    print(tcred)
                    for i in range(3):
                        newitem = QtWidgets.QTableWidgetItem(str(tcred[map_cmdb[i]]))
                        newitem.refBinding = tcred
                        newitem.refKey = tcred['id']
                        newitem.refRow = current_row
                        self.twCreds.setItem(current_row, i, newitem)

                    current_row += 1

            sqlite_session.close()

        except Exception as e:
            self.notify("Database Error", f"Error loading Creds table: {e}")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
