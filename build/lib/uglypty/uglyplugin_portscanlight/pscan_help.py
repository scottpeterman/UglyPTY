help_content = '''<p>Usage: <code>portscan [192.168.1.0/24] [-p 22,80-200 [-t 100 [-w 1 [-e]]]]</code></p>

<pre>
$ portscan -w 0.2
No IP string found, using local address
Local IP found to be 192.168.1.175, scanning entire block
Threads will wait for ping response for 0.2 seconds
192.168.1.1:80 OPEN
192.168.1.1:443 OPEN
192.168.1.167:443 OPEN
192.168.1.167:80 OPEN
Pinged 1024 ports
</pre>

<p>
By default the command checks for your <em>Local Area Network</em> IP first, and then initiate a block wise search. specify IP if you want to search any other IP blocks. <em>Note: This is not available before 0.2.1, please update or specify IP if you're using 0.2.0 and older</em>
</p>

<p>
Use <code>-w [float]</code> to change timeout settings from default of <code>3</code> seconds: for LAN, this can be as low as <code>0.1</code>. <code>1</code> is usually good enough for continental level connection.
</p>

<p>
To show more ports that have denied/refused connection, use <code>-e</code>, this will show you all ports that are not timed out.
</p>

<pre>
$ portscan 174.109.64.0/24 -w 0.5 -e
Threads will wait for ping response for 0.5 seconds
174.109.64.3:443 ERRNO 61, Connection refused
174.109.64.3:23 ERRNO 61, Connection refused
174.109.64.3:80 ERRNO 61, Connection refused
174.109.64.3:22 ERRNO 61, Connection refused
174.109.64.88:80 ERRNO 61, Connection refused
174.109.64.88:23 ERRNO 61, Connection refused
174.109.64.88:443 ERRNO 61, Connection refused
174.109.64.88:22 ERRNO 61, Connection refused
174.109.64.125:443 OPEN
Pinged 1024 ports
</pre>

<h3>Arguments</h3>

<p>
<code>ip</code>: default and optional <em>(since 0.2.1, required before 0.2.1)</em> argument, can parse single IP, list of IP, IP blocks:
</p>

<pre>
192.168.1.0 # single IP
192.168.1.0/24 # A 24 block, from 192.168.1.0 to 192.168.1.255
[192.168.1.0/24,8.8.8.8] # The aforementioned 24 block and 8.8.8.8.
</pre>

<p>Options:</p>

<p>
<code>-p, --port</code>: port range, default <code>22,23,80</code>, use <code>,</code> as a delimiter without space, support port range (e.g. <code>22-100,5000</code>).<br>
<code>-t, --threadnum</code>: thread numbers, default 500, as of now, thread number have a hard cap of 2048. More thread will increase performance on large scale scans.<br>
<code>-e, --show_refused</code>: show connection errors other than timeouts, e.g. connection refused, permission denied with errno number as they happen.<br>
<code>-w, --wait</code>: Wait time for socket to respond. If scanning LAN or relatively fast internet connection, this can be set to <code>1</code> or even <code>0.1</code> for faster (local) scanning, but this runs a risk of missing the open ports. Default to <code>3</code> seconds<br>
<code>-s, --stop_after</code>: Number of open ports to be discovered after which scan would be gracefully stopped. Default is None for not stopping. Note that it will continue to finish what's left in the queue, so the number of open ports returned might be greater than the value passed in.
</p>

<h3>Python API</h3>

<p>
One can also use this portscan inside existing python scripts.
</p>

<p>
Consider following example for finding out adb port for Android device in LAN with static IP:
</p>

<pre>
from portscan import PortScan
ip = '192.168.1.42'
port_range = '5555,37000-44000'
scanner = PortScan(ip, port_range, thread_num=500, show_refused=False, wait_time=1, stop_after_count=True)
open_port_discovered = scanner.run()  # &lt;----- actual scan
# run returns a list of (ip, open_port) tuples
adb_port = int(open_port_discovered[0][1])

# Usecase specific part
from adb_shell.adb_device import AdbDeviceTcp, AdbDeviceUsb
device1 = AdbDeviceTcp(ip, adb_port, default_transport_timeout_s=9)
device1.connect(rsa_keys=[python_rsa_signer], auth_timeout_s=0.1)  # adb connect
# shell exec
notifications_dump = device1.shell('dumpsys notification').encode().decode('ascii','ignore')
device1.close()

print(notifications_dump)
</pre>

<h3>Acknowledgement</h3>
<a href="https://github.com/Aperocky/PortScan">Aperocky/PortScan</a>
'''