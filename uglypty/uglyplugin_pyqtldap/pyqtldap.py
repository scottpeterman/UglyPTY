# https://www.labsrc.com/setting-up-openldap-sssd-w-sudo-on-ubuntu-22-04/
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QTabWidget, QTextEdit, \
    QPushButton, QLabel, QCheckBox, QTextBrowser
from ldap3 import Server, Connection, ALL, SUBTREE

class LdapTestClient(QWidget):
    def __init__(self):
        super(LdapTestClient, self).__init__()

        self.setWindowTitle('LDAP Test Client')

        # Main Layout
        layout = QVBoxLayout()

        # LDAP Server Properties
        form_layout = QFormLayout()
        self.ip_edit = QLineEdit()
        self.ip_edit.setText("ldap server ip")
        self.ssl_checkbox = QCheckBox('Use SSL')
        self.ssl_checkbox.setChecked(True)
        form_layout.addRow('Use SSL:', self.ssl_checkbox)
        self.port_edit = QLineEdit()
        self.port_edit.setText("389")
        self.base_context_edit = QLineEdit()
        self.base_context_edit.setPlaceholderText("DC=company,DC=com")
        form_layout.addRow('IP:', self.ip_edit)
        form_layout.addRow('Port:', self.port_edit)
        form_layout.addRow('Base Context:', self.base_context_edit)
        layout.addLayout(form_layout)

        # Tabs: Login and Browse LDAP
        tab_widget = QTabWidget()

        # Login Tab
        login_tab = QWidget()
        login_layout = QVBoxLayout()
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText(f"CN=commonname,OU=some_ou,OU=parent_ou,DC=company,DC=com")

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("commonnames password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        login_button = QPushButton('Login')
        self.login_output = QTextEdit()
        self.login_output.setMinimumWidth(500)
        login_layout.addWidget(QLabel('FDN:'))
        login_layout.addWidget(self.username_edit)
        login_layout.addWidget(QLabel('Password:'))
        login_layout.addWidget(self.password_edit)
        login_layout.addWidget(login_button)
        login_layout.addWidget(self.login_output)
        login_tab.setLayout(login_layout)
        login_button.clicked.connect(self.ldap_login)
                # Browse Tab
        self.browse_tab = QWidget()
        self.browse_layout = QVBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setText("(&(objectclass=person)(sAMAccountName=some_user))")


        search_button = QPushButton('Search')
        search_button.clicked.connect(self.ldap_search)
        self.ssl_checkbox.stateChanged.connect(self.toggle_ssl)

        self.search_output = QTextEdit()
        self.browse_layout.addWidget(QLabel('Search:'))
        self.browse_layout.addWidget(self.search_edit)
        self.browse_layout.addWidget(search_button)
        self.browse_layout.addWidget(self.search_output)
        self.browse_tab.setLayout(self.browse_layout)

        # tree tab

        tree_tab = QWidget()
        tree_layout = QVBoxLayout()

        # "Fetch Tree" Button
        fetch_tree_button = QPushButton('Fetch Tree')
        fetch_tree_button.clicked.connect(self.fetch_tree)

        # Text Browser to display LDAP tree
        self.tree_display = QTextBrowser()

        tree_layout.addWidget(fetch_tree_button)
        tree_layout.addWidget(self.tree_display)
        tree_tab.setLayout(tree_layout)

        # Add tabs
        tab_widget.addTab(login_tab, 'Login')
        tab_widget.addTab(self.browse_tab, 'Search LDAP')
        tab_widget.addTab(tree_tab, 'LDAP Tree')
        layout.addWidget(tab_widget)

        # Complete Main window
        self.setLayout(layout)

    def fetch_tree(self):
        try:
            username = self.username_edit.text()

            fdn = f"{username}"
            password = self.password_edit.text()
            conn = self.get_ldap_connection(fdn, password)
            if conn.bind():
                base_dn = self.base_context_edit.text()
                search_filter = '(|(objectClass=organizationalUnit)(objectClass=organization))'
                attributes = ['o', 'ou']

                conn.search(base_dn, search_filter, SUBTREE, attributes=attributes)
                tree_text = self.print_tree(conn.entries, base_dn)
                self.tree_display.setPlainText(tree_text)
            else:
                self.tree_display.setPlainText('Failed to bind to server.')
        except Exception as e:
            print(e)
            self.tree_display.setPlainText(str(e))

    def print_tree(self, entries, parent, level=0, visited=None):
        if visited is None:
            visited = set()

        result_text = ""
        for entry in entries:
            dn = entry.entry_dn
            if dn.endswith(parent) and dn not in visited:
                visited.add(dn)
                ou_or_o = entry['o'][0] if 'o' in entry and entry['o'] else entry['ou'][0] if 'ou' in entry and entry[
                    'ou'] else "Unknown"
                entry_text = '  ' * level + f"{ou_or_o} ({dn})\n"
                result_text += entry_text
                result_text += self.print_tree(entries, dn, level + 1, visited)
        return result_text



    def toggle_ssl(self, state):
        if state == 2:  # Checked
            self.port_edit.setText("636")
        else:
            self.port_edit.setText("389")

    def get_ldap_connection(self, user, password):
        server_ip = self.ip_edit.text()
        port = int(self.port_edit.text())
        use_ssl = bool(self.ssl_checkbox.isChecked())

        server = Server(f"{server_ip}:{port}", use_ssl=use_ssl, get_info=ALL)
        conn = Connection(server, user=user, password=password)
        return conn
    def ldap_login(self):
        # server_ip = self.ip_edit.text()
        # port = self.port_edit.text()
        username = self.username_edit.text()

        fqdn = f"{username}"
        password = self.password_edit.text()
        try:

            conn = self.get_ldap_connection(user=fqdn, password=password)
            if conn.bind():
                if "SIMPLE" in conn.authentication:
                    self.login_output.setPlainText('Login Successful')
                else:
                    self.login_output.setPlainText('Login Failed')

            else:
                self.login_output.setPlainText('Login Failed')
        except Exception as e:
            print(e)
            self.login_output.setPlainText(str(e))


    def ldap_search(self):
        server_ip = self.ip_edit.text()
        port = self.port_edit.text()
        base_context = self.base_context_edit.text()
        search_filter = self.search_edit.text()

        try:
            # server = Server(f'ldap://{server_ip}:{port}', get_info=ALL)
            username = self.username_edit.text()

            fdn = f"{username}"
            password = self.password_edit.text()
            conn = self.get_ldap_connection(fdn, password)

            if conn.bind():
                if "SIMPLE" not in conn.authentication:
                    self.login_output.setPlainText('Login Failed')
                    return

                conn.search(search_base=base_context,
                            search_filter=search_filter,
                            search_scope=SUBTREE)

                entries = conn.entries

                if entries:
                    output = '\n'.join(str(entry) for entry in entries)
                else:
                    output = 'No entries found.'

                self.search_output.setPlainText(output)
            else:
                self.search_output.setPlainText('Failed to bind to server.')
        except Exception as e:
            print(e)
            self.search_output.setPlainText(str(e))


if __name__ == '__main__':
    app = QApplication([])
    app.setStyle("fusion")
    window = LdapTestClient()
    window.show()
    app.exec()
