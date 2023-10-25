readme_html = '''<!DOCTYPE html>
<html>
<head>
    <title>UglyPTY</title>
    <style>
  body {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
  }

  .container {
    text-align: center;
  }

  h1 {
    color: #FF9800;

  }

  p {
    color: #607D8B;
    text-align: left;
  }

  ul {
    color: #4CAF50;
    text-align: left;
    list-style-position: inside;
    padding-left: 0;
  }

  li {
    color: #2196F3;
  }
</style>

</head>
<body>
    <h1>UglyPTY</h1>
    <p>UglyPTY is an extensible graphical terminal emulator built with Python and PyQt6. It provides a user-friendly interface for managing and establishing SSH connections, with some great productivity features. This is the base product of many Network Engineering automation tools currently in development. A plugin-based system for adding features to the application is included in this release, along with some basic plugin examples. The best network automation tools are in Python. UglyPTY now has many built-in tools from Desktop TFTP & SFTP Servers built-in for code upgrades to highly concurrent data collection automation.</p>

    <h2>Why?</h2>
    <p>The whole point of the UglyPTY project is not to solve every problem but to provide a platform based on the tool network engineers use most - an SSH Terminal. Developers like text editors with add-on capabilities; this is just the equivalent for CLI-focused engineers. Nothing in these plugins is super special; I just wanted to provide enough example plugins that others could create their tools. Both the usable .whl files, as well as the original source code, are included in the repo. And hopefully, you enjoy using the base SSH application if that's all you need. You don't have to load any plugins to use UglyPTY, but remember, these are all beta tools, be careful ;)</p>

    <h3>Python needed a native SSH GUI Terminal</h3>
    <p>This application does NOT wrap a backend web server like Webssh. It DOES use xterm.js for terminal emulation.</p>
    <p><em>Note: This is a VERY beta release with a lot of functionality.</em></p>

    <h2>Features</h2>
    <ul>
        <li>
            <h3>Session Manager</h3>
            <p>Leverage the sessions you use in your Terminal environment in your automation scripts (examples included).</p>
            <ul>
                <li>Create, edit, or delete sessions with specific settings.</li>
                <li>Supports password and key-based authentication.</li>
                <li>You can have as many device tree (i.e., session) files to organize as you like. Files are basic YAML.</li>
            </ul>
        </li>
        <li>
            <h3>Credentials Manager</h3>
            <p>Safely manage your user credentials.</p>
            <ul>
                <li>Multiple credential profiles</li>
                <li>Passwords are encrypted.</li>
                
            </ul>
        </li>
         <li>
            <h3>Limited Netbox Integration</h3>
            <p>Pull Netbox DCIM cmdb devices, and create a Session.yaml file you can use int the UI</p>
            <p>Requires netbox API token</p>
        </li>
        <li>
            <h3>Builtin TFTP and SFTP servers</h3>
            <p>For device firmware upgrades, config backups, etc.</p>
            <p>When you're in the field and you need to upgrade that box now.</p>
        </li>
        <li>
            <h3>Netmiko based CLI collector</h3>
            <p>Capture any single CLI command and build a repo for it (i.e. configs, version, cdp etc)</p>
            <p>Data becomes searchable via the YAML browser, or Gui Grep tools</p>
        </li>
           <li>
            <h3>Dynamic CDP Map Generator</h3>
            <p>Pick a seed device, it will crawl the cdp neighbors and generate a YED Diagram you can further customize</p>
            <p>Limited LLDP support for Aruba</p>
        </li>
        <li>
            <h3>Other Features...</h3>
            <p>Serial Console support - auto detects available ports</p>
            <p>LDAP Test tool</p>
            <p>Lite TCP port scanner with threading control</p>
            <p>IP Subnet calculator (IPv4 and IPv6)</p>
            <p>TTP, Jinja2, JMesPath Test tool. Quickly test your templates and parsing logic</p>
        </li>
        <!-- More feature sections go here -->
    </ul>

    <!-- Additional sections go here -->

    <h2>Installation</h2>
    <ol>
        <li>Tested with Python 3.9.13 for Windows in venv, and Ubuntu 22.04 with Python 3.10. Other versions might work.</li>
        <li>Use PyPi unless you want to contribute.</li>
        <li>Use <code>pip</code> with an activated venv:</li>
    </ol>
    <pre><code>pip install uglypty</code></pre>
    <p>To start the application, navigate to the activated virtual directory, local keys, your session database, and log files will be here:</p>
    <pre><code>python or pythonw -m uglypty</code></pre>
    <pre><code>python -m uglypty  --plugins-enabled</code></pre>

    <!-- Installation details go here -->

    <h2>UglyPTY Plugins</h2>
    <p>Some plugins have been moved to the main application under "Tools". To use a plugin, download its <code>.whl</code> file and save it in a <code>./wheels</code> directory where your UglyPTY application is installed. You will have to create this folder. Here is a list of just some of the plugins:</p>
    <ol>
        <li>Ace Code Editor: uglyplugin_ace-0.1.0-py3-none-any.whl</li>
        <li>Dynamic Front End for Click-based scripts: uglyplugin_click-0.1.0-py3-none-any.whl</li>
        <li>CMD, Powershell and WSL2 Tabbed terminals: uglyplugin_terminal-0.1.0-py3-none-any.whl</li>
    </ol>

    <!-- Plugins and their details go here -->

    <h2>Download More Plugins</h2>
    <p>You can find more about UglyPTY's wheel-based plugins from <a href="https://github.com/scottpeterman/UglyPTY-Plugins">GitHub</a>. You can download more <code>.whl</code> plugins from <a href="https://github.com/scottpeterman/UglyPTY-Plugins/tree/main/wheels">wheels</a>.</p>

    <h3><code>catalog.yaml</code> Explained</h3>
    <p>Only 2 example plugins are pre-entered in the plugin catalog. The <code>catalog.yaml</code> file contains metadata for all available plugins. UglyPTY's Plugin Manager reads this file, so if you download additional plugins, you will have to edit this file to get them installed and registered with the application. Each plugin has its entry defined by the following keys:</p>
    <ul>
        <li><strong>name:</strong> The human-readable name of the plugin.</li>
        <li><strong>package_name:</strong> The name used to register the plugin as a Python package. This is the name you would use if you were to install the plugin using pip.</li>
        <li><strong>description:</strong> A brief description of what the plugin does.</li>
        <li><strong>import_name:</strong> The Python import statement that would be used to load the plugin's main class or function.</li>
        <li><strong>version:</strong> The version number of the plugin.</li>
        <li><strong>source_type:</strong> The type of installation source, currently only supports "wheel".</li>
        <li><strong>wheel_url:</strong> The path to the <code>.whl</code> file for the plugin, relative to the <code>./wheels</code> directory.</li>
    </ul>
    <p>Example entry:</p>
    <pre><code>- name: "Ugly Ace Editor"
  package_name: "ugly_ace_editor"
  description: "An Ace-based editor with some unique features."
  import_name: "uglyplugin_ace.ugly_ace.QtAceWidget"
  version
'''