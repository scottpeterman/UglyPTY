import copy

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QAbstractItemView
from uglypty.Library.models import Cred
from uglypty.Library.db import get_by_dbquery
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from uglypty.Library.creds_dlg import Ui_dlgCreds
import json
from uglypty.Library.util import cryptonomicon, encrypt


# Used to make table selection by row only
class ReadOnlyDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        print('createEditor event fired')
        return

class CredentialsManagerWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CredentialsManagerWidget, self).__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.formIsDirty = False
        self.setObjectName("TerminalsUI")
        self.resize(883, 299)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.twCreds = QtWidgets.QTableWidget(self)
        self.twCreds.setObjectName("twCreds")
        self.twCreds.setColumnCount(4)
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
        item = QtWidgets.QTableWidgetItem()
        self.twCreds.setHorizontalHeaderItem(3, item)
        self.verticalLayout.addWidget(self.twCreds)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menuCreds = QtWidgets.QMenu(self.menubar)
        self.menuCreds.setObjectName("menuCreds")
        self.menubar.addAction(self.menuCreds.menuAction())
        self.actionAdd = QtGui.QAction(self)
        self.actionAdd.setObjectName("actionAdd")
        self.actionAdd.triggered.connect(lambda: self.creds_add())
        self.menuCreds.addAction(self.actionAdd)
        self.verticalLayout.insertWidget(0, self.menubar)

        self.retranslateUi(self)

        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, MainWidget):
        _translate = QtCore.QCoreApplication.translate
        MainWidget.setWindowTitle(_translate("TerminalsUI", "Session Credentials"))
        item = self.twCreds.horizontalHeaderItem(0)
        item.setText(_translate("TerminalsUI", "id"))
        item = self.twCreds.horizontalHeaderItem(1)
        item.setText(_translate("TerminalsUI", "username"))
        item = self.twCreds.horizontalHeaderItem(2)
        item.setText(_translate("TerminalsUI", "password"))
        item = self.twCreds.horizontalHeaderItem(3)
        item.setText(_translate("TerminalsUI", "displayname"))
        self.menuCreds.setTitle(_translate("TerminalsUI", "Credentials"))
        self.actionAdd.setText(_translate("TerminalsUI", "Add"))


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
        stub_item = {'id': 'New', 'Username': '', 'Password': '', 'DisplayName': ''}
        dlg = QtWidgets.QDialog()
        dlg.setModal(True)
        ui = Ui_dlgCreds()
        ui.setupUi(dlg, stub_item, "ADD")
        # ui.mode = "ADD"
        dlg.show()
        result = dlg.exec()
        if result == 1:
            encrypted_password = encrypt(stub_item['Password'])
            stub_item['Password'] = encrypted_password.decode('utf-8')
            print(f"Item to add: {json.dumps(stub_item)}")
            try:
                # now save to DB
                engine = create_engine(f'sqlite:///settings.sqlite', echo=False)
                engine.connect()
                sqlite_session = Session(bind=engine)
                cur = sqlite_session.execute(text("select id from creds order by id desc"))
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
                    Password=stub_item['Password'],
                    DisplayName=stub_item['DisplayName']
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
        stub_item = {'id': 'New', 'Username': '', 'Password': ''}

        selected = self.twCreds.currentIndex()
        if selected.row() != -1:
            print(f"editing selected row {selected.row()}")
            edit_item = self.twCreds.item(selected.row(), 0)
            x = edit_item.refBinding
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
                    encrypted_password = encrypted_password.decode('utf-8')
                    # stub_item = {'id': x['id'], 'Username': x['Username'], 'Password': encrypted_password}
                    self.twCreds.item(selected.row(), 0).refBinding['Password'] = encrypted_password
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
                            sql_result[0].Password = encrypted_password
                            sql_result[0].DisplayName = edit_item.refBinding['DisplayName']
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
                    2: "Password",
                    3: "DisplayName"
                }
                for cred in sql_result:
                    # print(cred)
                    tcred = cred.toDict()
                    print(tcred)
                    for i in range(4):
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
    from qt_material import apply_stylesheet
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    cmw = CredentialsManagerWidget(MainWindow)
    cmw.setFixedWidth(800)
    MainWindow.setCentralWidget(cmw)
    MainWindow.show()
    sys.exit(app.exec())