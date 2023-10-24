import os

from cryptography.fernet import Fernet
from uglypty.uglyplugin_ndpcrawler.make_crawl import file_builder

def cryptonomicon(to_decrypt, key_path="./crypto.key"):
    from cryptography.fernet import Fernet

    try:
        # load crypto key - and sanity check
        fhc = open(key_path, "r")
        key = fhc.read()
        key = key.strip()
        cryptonizer = Fernet(key)

        to_decrypt = bytes(to_decrypt, 'utf-8')
        result = cryptonizer.decrypt(to_decrypt)

        return result.decode("utf-8")
    except Exception as e:
        print("error processing crypto key file")
        raise e

def encrypt(to_encrypt):
    from cryptography.fernet import Fernet
    try:
        # load crypto key - and sanity check
        fhc = open("crypto.key", "r")
        key = fhc.read()
        key = key.strip()
        cryptonizer = Fernet(key)
        to_encrypt = bytes(str(to_encrypt), 'utf-8')
        result = cryptonizer.encrypt(to_encrypt)
        return result
    except Exception as e:
        print("error processing crypto key file")

def generate_key():

    # Check if the file exists
    if os.path.isfile('crypto.key'):
        # Ask the user for confirmation
        confirm = input(
            'The file "crypto.key" already exists, do you want to overwrite it? This will invalidate your currently encrypted passwords. (y/n): ')

        # Check the user's response
        if confirm.lower() != 'y':
            print('Operation cancelled.')
            exit()

    # Generate a key
    key = Fernet.generate_key()

    # Save the key to the file
    with open('crypto.key', 'wb') as file:
        file.write(key)

    print('Key saved to "crypto.key".')

def create_db():
    import sqlite3

    conn = sqlite3.connect('settings.sqlite')
    c = conn.cursor()

    c.execute('''
              CREATE TABLE "creds" (
    	"id" INTEGER NOT NULL  ,
    	"username" TEXT NULL  ,
    	"password" TEXT NULL
    , "displayname"	TEXT)
              ''')
    c.execute('''CREATE TABLE installed_plugins (
    id INTEGER PRIMARY KEY,
    name TEXT,
    package_name TEXT,
    description TEXT,
    import_name TEXT,
    status TEXT
);
''')

    conn.commit()
    print("settings.sqlite created")

def create_catalog():
    base_catalog = '''plugins:
  - name: "Ugly Ace Editor"
    package_name: "ugly_ace_editor"
    description: "An Ace based editor with some unique features."
    import_name: "uglyplugin_ace.ugly_ace.QtAceWidget"
    version: "0.1.0"
    source_type: "wheel"
    wheel_url: "https://github.com/scottpeterman/UglyPTY-Plugins/raw/main/wheels/uglyplugin_ace-0.1.0-py3-none-any.whl"

  - name: "Ugly Windows Terminal"
    package_name: "ugly_terminal"
    description: "A Windows Terminal with cmd, powershell and wsl support"
    import_name: "uglyplugin_terminal.qtwincon.TerminalsUI"
    version: "0.1.0"
    source_type: "wheel"
    wheel_url: "https://github.com/scottpeterman/UglyPTY-Plugins/raw/main/wheels/uglyplugin_terminal-0.1.0-py3-none-any.whl"

  - name: "Ugly Parsing Widget"
    package_name: "uglyplugin_parsers"
    description: "A widget for parsing text-based data with various modes like TTP, Jinja2, and JMesPath."
    import_name: "uglyplugin_parsers.ugly_parsers.UglyParsingWidget"
    version: "0.1.0"
    source_type: "wheel"
    wheel_url: "https://github.com/scottpeterman/UglyPTY-Plugins/raw/main/wheels/uglyplugin_parsers-0.1.0-py3-none-any.whl"

  - name: "UglyPTY Serial Widget"
    package_name: "uglyplugin_serial"
    description: "A widget for Serial Terminal support"
    import_name: "uglyplugin_serial.qtserialcon_widget.SerialWidgetWrapper"
    version: "0.1.0"
    source_type: "wheel"
    wheel_url: "https://github.com/scottpeterman/UglyPTY-Plugins/raw/main/wheels/uglyplugin_serial-0.1.0-py3-none-any.whl"

  - name: "UglyPTY Netmiko Collector Widget"
    package_name: "uglyplugin_collector"
    description: "A widget for cli output collection ve Netmiko"
    import_name: "uglyplugin_collector.collect_gui_netmiko.CollectorForm"
    version: "0.1.0"
    source_type: "wheel"
    wheel_url: "https://github.com/scottpeterman/UglyPTY-Plugins/raw/main/wheels/uglyplugin_collector-0.1.0-py3-none-any.whl"

  - name: "UglyPTY Click Dynamic Front End"
    package_name: "uglyplugin_collector"
    description: "A widget for cli scripts written using click to run in a window with a dynamic form"
    import_name: "uglyplugin_click.uglyclick.ClickCommandWidget"
    version: "0.1.0"
    source_type: "wheel"
    wheel_url: "https://github.com/scottpeterman/UglyPTY-Plugins/raw/main/wheels/uglyplugin_click-0.1.0-py3-none-any.whl"

  - name: "Netbox to UglyPTY Session Export"
    package_name: "uglyplugin_nbtosession"
    description: "A widget for downloading devices from Netbox DCIM, organized by site"
    import_name: "uglyplugin_nbtosession.nbtosession.App"
    version: "0.1.0"
    source_type: "wheel"
    wheel_url: "https://github.com/scottpeterman/UglyPTY-Plugins/raw/main/wheels/uglyplugin_nbtosession-0.1.0-py3-none-any.whl"

  - name: "UglyPTY small TFTP server"
    package_name: "uglyplugin_tftp"
    description: "A widget for a quick and easy local tftp server"
    import_name: "uglyplugin_tftp.server.TftpServerApp"
    version: "0.1.0"
    source_type: "wheel"
    wheel_url: "https://github.com/scottpeterman/UglyPTY-Plugins/raw/main/wheels/uglyplugin_tftp-0.1.0-py3-none-any.whl"

  - name: "UglyPTY Yaml Browser"
    package_name: "uglyplugin_yamlbrowser"
    description: "A companion widget for the Netmiko CLI Collector"
    import_name: "uglyplugin_yamlbrowser.YAMLSearch.YAMLViewer"
    version: "0.1.0"
    source_type: "wheel"
    wheel_url: "https://github.com/scottpeterman/UglyPTY-Plugins/raw/main/wheels/uglyplugin_yamlbrowser-0.1.0-py3-none-any.whl"
'''
    with open("./catalog.yaml", "w") as fh:
        fh.write(base_catalog)

    print(f"Created base plugin catalog.yaml")

def create_crawl():
    fb = file_builder()
    with open('crawl.py', 'w') as fhc:
        fhc.write(fb.get_crawl())
