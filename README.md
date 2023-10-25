# UglyPTY

UglyPTY is an extensible graphical terminal emulator built with Python and PyQt6. It provides a user-friendly interface for managing and establishing SSH connections, with some great productivity of features. This is the base product of many Network Engineering automation tools currently in development. A plugin based system for adding features to the application is included in this release, along with some basic plugin examples. The best network automation tools are in python ... UglyPTY now has many built in tools from Desktop TFTP & SFTP Servers built in for code upgrades, to highly concurrent data collection automation.

## Why?

The whole point of the UglyPTY project is not to solve every problem, but to provide a platform based on the tool network engineers use most - an SSH Terminal. Developers like text editors with add-on capabilites, this is just the equivilent for CLI focused engineers. Nothing in these plugins is supper special, I just wanted to provide enough example plugins that others could create there own tools. Both the usable .whl files, as well as original source code are included in the repo. And hopefully you enjoy using the base SSH application if thats all you need. You don't have to load any plugins to use UglyPTY, but remember, these are all beta tools, be careful ;)

### Python needed a native SSH GUI Terminal
This application does NOT wrap a backend web server like Webssh. It DOES use xterm.js for terminal emulation.

> **Note**: This is a VERY beta release with a lot of functionality.

## Features

- **Session Manager** Leverage the sessions you use in your Terminal environment in your automation scripts (examples included).
  - Create, edit, or delete sessions with specific settings.
  - Supports password and key based authentication.
  - You can have as many device tree (i.e. session) files to organize as you like. Files are basic YAML.
- **Credentials Manager** Safely manage your user credentials.
  - Passwords are encrypted.
  - Fetch all credentials or a specific credential by ID from a SQLite database (`settings.sqlite`).
- **Builtin TFTP and SFTP servers** 
  - For device firmware upgrades, config backups etc. 
  - When your in the field and you need to upgrade that box now.
- **TCP Port scanner lite** 
  - For quick tests of ACL's, check for unwanted network device services like telnet or http
- **IP Subnet Calculator**
  - For the obvious
- **LDAP Test Tool**
  - For authentication tests
  - Includes search
  - Full O,OU tree view (Container objects only), just to help you find your way around the tree
- **Netbox Exporter** 
  - To quickly populate your sessions.yaml file with data from Netbox
- **Diff Tool**
  - To quickly compare configuration or output differences
- **Grep GUI**
  - A friendly grep tool for all the data you collect
- **Netmiko Concurrent CLI Collector**
  - Quickly issue show commands against 100's of network devices. I've hit over 1000 in less than 10 minutes. 
  - The data will be saved in both raw text (see the grep tool), and a structured yaml file with additional device meta data for processing later
  - Great for audits, or just searching for ckt id's
- **YAML Browser** 
  - All those structured yaml files with collected data? This will search, browse and view them for you
- **Themed Views**
  - Multiple theme modes - light, dark, light-dark, and dark-light.
- **Network Maps!**
  - Based on CDP, but soon for LLDP as well. Tool crawls the network via cdp and then maps it to a graphml file.
  - Uses N2G (Need to Graph), from the creator of TTP! 
  - Filters to support setting bounds on the crawling. (an issue if you have point-to-point WAN ckts)

## Built-in Tools

<div align="center">
  <img src="https://github.com/scottpeterman/UglyPTY/raw/main/screen_shots/toolbox.png" alt="UglyPTY Dark" width="400px">
  <hr><img src="https://github.com/scottpeterman/UglyPTY/raw/main/screen_shots/cdp_map.png" alt="UglyPTY Light Splash" width="400px">
  
</div>

## Installation

1. Tested with Python 3.9.13 for Windows in venv, and Ubuntu 22.04 with Python 3.10. Other versions might work.
2. Use PyPi unless you want to contribute.
3. Use `pip` with an activated venv:

    ```bash
    pip install uglypty
    ```

To start the application, navigate to the activated virtual directory, local keys, your session database, and log files will be here:

    python or pythonw -m uglypty
    python -m uglypty  --plugins-enabled

## UglyPTY Plugins
Some plugins have been moved to the main application under "Tools". To use a plugin, download its `.whl` file and save it in a `./wheels` directory where your UglyPTY application is installed. You will have to create this folder. Here is a list of just some of the plugins:

    1. Ace Code Editor:  uglyplugin_ace-0.1.0-py3-none-any.whl
    2. Dynamic Front End for Click based scripts: uglyplugin_click-0.1.0-py3-none-any.whl
    7. CMD, Powershell and WSL2 Tabbed terminals: uglyplugin_terminal-0.1.0-py3-none-any.whl

## Download More Plugins

You can find more about UglyPTY's wheel based plugins from [github](https://github.com/scottpeterman/UglyPTY-Plugins).
You can download more `.whl` plugins from [wheels](https://github.com/scottpeterman/UglyPTY-Plugins/tree/main/wheels).

### `catalog.yaml` Explained

Only 2 example plugins are pre-entered in the pluging catalog. The `catalog.yaml` file contains metadata for all available plugins. UglyPTY's Plugin Manager reads this file, so if you download additional plugins, you will have to edit this file to get them installed and registered with the application. Each plugin has its entry defined by the following keys:

- `name`: The human-readable name of the plugin.
- `package_name`: The name used to register the plugin as a Python package. This is the name you would use if you were to install the plugin using pip.
- `description`: A brief description of what the plugin does.
- `import_name`: The Python import statement that would be used to load the plugin's main class or function.
- `version`: The version number of the plugin.
- `source_type`: The type of installation source, currently only supports "wheel".
- `wheel_url`: The path to the `.whl` file for the plugin, relative to the `./wheels` directory.

Example entry:

```yaml
- name: "Ugly Ace Editor"
  package_name: "ugly_ace_editor"
  description: "An Ace based editor with some unique features."
  import_name: "uglyplugin_ace.ugly_ace.QtAceWidget"
  version: "0.1.0"
  source_type: "wheel"
  wheel_url: "./wheels/uglyplugin_ace-0.1.0-py3-none-any.whl"
```

## A Note about Xterm.js
- Xterm.js is a front-end component written in TypeScript that lets applications bring fully-featured terminals to their users in the browser. It's used by popular projects such as VS Code, Hyper and Theia.
- In PyQt6, xterm.js is implemented in QT's WebEngine, and chromium based widget. There is of course overhead associated with this approach. If you are interested in how something like UglyPTY could be implemented more natively using a graphics approach, take a look at the early development being done on "UglierPTY" here: https://github.com/scottpeterman/UglierPTY

## Features

- **Terminal apps just work**: Xterm.js works with most terminal apps such as `bash`, `vim`, and `tmux`, including support for curses-based apps and mouse events.
- **Performant**: Xterm.js is *really* fast, it even includes a GPU-accelerated renderer.
- **Rich Unicode support**: Supports CJK, emojis, and IMEs.
- **Self-contained**: Requires zero dependencies to work.
- **Accessible**: Screen reader and minimum contrast ratio support can be turned on.



## A special thanks to those whose efforts this tool is built on (shoulders of giants and all that)
- Qt   https://www.qt.io/
- PyQt6    https://www.riverbankcomputing.com/software/pyqt/   Yes I could have used PySide6, and maybe will add that. I've used PyQt to fix my own problems for years, and I just love it!
- Netmiko  Kirk - you are awesome! (Network Engineers - his classes are awesome as well)
- Paramiko  Most don't know just how much automation has been enabled by this project (Ansible, looking at you over the years)
- TTP  Very few outside the network automation space know of this, but it transformed the ability to automate legacy network equipment, much of which still wont do a simple "show blah | json". I have literally worked with it since ver 0.0.1 - this guy is amazing: https://github.com/dmulyalin/ttp


## Screenshots

Here are some snapshots of UglyPTY in action:

<div align="center">
  <img src="https://github.com/scottpeterman/UglyPTY/raw/main/screen_shots/uglydark.PNG" alt="UglyPTY Dark" width="400px">
  <hr><img src="https://github.com/scottpeterman/UglyPTY/raw/main/screen_shots/uglylight.png" alt="UglyPTY Light Splash" width="400px">
  <hr><img src="https://github.com/scottpeterman/UglyPTY/raw/main/screen_shots/darklight.png" alt="UglyPTY darklight" width="400px">
  <hr><img src="https://github.com/scottpeterman/UglyPTY/raw/main/screen_shots/lightdark.png" alt="UglyPTY Lightdark" width="400px">
</div>

---

## Here are some snapshots of UglyPTY-Plugins in action:

<div align="center">
  <img src="https://github.com/scottpeterman/UglyPTY-Plugins/raw/main/screen_shots/UglyConsole.png" alt="UglyPTY Console" width="400px">
  <hr><img src="https://github.com/scottpeterman/UglyPTY/raw/main/screen_shots/collector_yaml.png" alt="UglyPTY CLI Collector" width="400px">
  <hr><img src="https://github.com/scottpeterman/UglyPTY-Plugins/raw/main/screen_shots/UglyParser.png" alt="UglyPTY parsers" width="400px">
  <hr><img src="https://github.com/scottpeterman/UglyPTY-Plugins/raw/main/screen_shots/serial.png" alt="UglyPTY Serial" width="400px">
   <hr><img src="https://github.com/scottpeterman/UglyPTY/raw/main/screen_shots/cdp_map.png" alt="UglyPTY Map" width="400px">
  
</div>

---

**Enjoy using UglyPTY!**


## Package Distribution

```python
# Create a source distribution and a wheel
python setup.py sdist bdist_wheel

# Set up a new virtual environment
python -m venv test_env

# Activate the virtual environment
source test_env/bin/activate  # On Linux/Mac
test_env\Scripts\activate     # On Windows

# Install the wheel
pip install dist/uglypty-0.1-py3-none-any.whl

# Test your script
python or pythonw -m uglypty

# Use `twine` to upload your package to PyPI: 
twine upload dist/* 

 