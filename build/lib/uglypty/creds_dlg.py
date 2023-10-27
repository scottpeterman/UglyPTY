from PyQt6 import QtCore, QtWidgets
from uglypty.Library.util import cryptonomicon


class Ui_dlgCreds(QtWidgets.QDialog):
    def setupUi(self, dlgCreds, data, mode):
        self.me = dlgCreds
        self.mode = mode
        self.data = data
        dlgCreds.setObjectName("dlgCreds")
        dlgCreds.resize(417, 155)
        self.verticalLayout = QtWidgets.QVBoxLayout(dlgCreds)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_0 = QtWidgets.QLabel(dlgCreds)
        self.label_0.setObjectName("label_0")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_0)
        self.leDisplayName = QtWidgets.QLineEdit(dlgCreds)
        self.leDisplayName.setObjectName("leDisplayName")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.leDisplayName)

        self.label = QtWidgets.QLabel(dlgCreds)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label)
        self.leID = QtWidgets.QLineEdit(dlgCreds)
        self.leID.setObjectName("leID")
        self.leID.setReadOnly(True)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.leID)
        self.label_2 = QtWidgets.QLabel(dlgCreds)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_2)
        self.leUsername = QtWidgets.QLineEdit(dlgCreds)
        self.leUsername.setObjectName("leUsername")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.leUsername)
        self.label_3 = QtWidgets.QLabel(dlgCreds)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_3)
        self.lePassword = QtWidgets.QLineEdit(dlgCreds)
        self.lePassword.setObjectName("lePassword")
        self.lePassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.lePassword)
        self.label_4 = QtWidgets.QLabel(dlgCreds)
        self.label_4.setText("")
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_4)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.lblMode = QtWidgets.QLabel(dlgCreds)
        self.lblMode.setObjectName("lblMode")
        self.horizontalLayout.addWidget(self.lblMode)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.formLayout.setLayout(4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.horizontalLayout)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(dlgCreds)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(dlgCreds)
        self.buttonBox.accepted.connect(dlgCreds.accept) # type: ignore
        self.buttonBox.rejected.connect(dlgCreds.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(dlgCreds)

    def retranslateUi(self, dlgCreds):
        _translate = QtCore.QCoreApplication.translate
        dlgCreds.setWindowTitle(_translate("dlgCreds", "Automation Credentials"))
        self.label_0.setText(_translate("dlgCreds", "Display Name: "))
        self.label.setText(_translate("dlgCreds", "id"))
        self.label_2.setText(_translate("dlgCreds", "Username: "))
        self.label_3.setText(_translate("dlgCreds", "Password:"))
        self.lblMode.setText(_translate("dlgCreds", "Edit"))

        self.buttonBox.accepted.connect(self.okSaveChanges) # type: ignore
        self.buttonBox.rejected.connect(dlgCreds.reject) # type: ignore

        if self.mode == "EDIT":
            self.leID.setText(str(self.data['id']))
            self.leUsername.setText(str(self.data['Username']))
            self.leDisplayName.setText(str(self.data['DisplayName']))
            try:
                unencrypted_payload = cryptonomicon(self.data['Password'])

                self.lePassword.setText(unencrypted_payload)
            except Exception as e:
                self.notify("Decryption Error", "Unable to decrypt pw, possibly due to crypto.key change\nenter a new password")


            self.lblMode.setText(_translate("dlgCreds", "               Save?"))

        if self.mode == "ADD":
            self.lblMode.setText(_translate("dlgCreds", "               Save New Creds?"))

    def notify(self, message, info):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
        msg.setText(info)
        msg.setWindowTitle(message)
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        retval = msg.exec()

    def okSaveChanges(self):
        print("Saving form to data passed in")
        self.data['Username'] = str(self.leUsername.text())
        self.data['Password'] = str(self.lePassword.text())
        # add displayname
        self.data['DisplayName'] = str(self.leDisplayName.text())
        self.me.accept()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    sample_data = {'id': 4, 'Username': 'cisco', 'Password': 'gAAAAABkuEzZI7vL5itNNojW_6ifhdWx-RjRRsWGInj_7gqYuwWw5R1GjDJ7KuMuEI2ZUNlP30Vp4lRcP1VMAVT5Dab-e7FDAg==', 'DisplayName': "testing dlg"}
    dlgCreds = QtWidgets.QDialog()
    ui = Ui_dlgCreds()
    ui.setupUi(dlgCreds, sample_data, "EDIT")
    dlgCreds.show()
    sys.exit(app.exec())
