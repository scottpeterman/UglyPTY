import os
import re

import netmiko
from netmiko import ConnectHandler
from queue import Queue
from ttp import ttp
import json
from uglypty.uglyplugin_ndpcrawler.templates import template_builder
ttp_templates = template_builder().ttp_templates

class CDPDiscover:
    def __init__(self, seed_device, seed_device_stub, username, password, domain_name, exclude, vendor="cisco"):
        self.seed_device = seed_device
        self.seed_device_stub = seed_device_stub
        self.exclude = exclude
        self.visited = set()
        self.queue = Queue()
        self.ttp_templates = ttp_templates
        self.failed_neighbors = []
        self.username = username
        self.password = password
        self.domain_name = domain_name
        self.vendor = vendor
    def is_excluded(self, device):
        excluded = False
        for exstring in self.exclude.split(","):
            if str(exstring).strip() in device.get("device_id", "unknown"):
                # if "SEP" in device.get("device_id", "unknown"):
                #     print("No Phones")
                excluded = True
                print(f"Hit Exclusion Rule: {device.get('device_id')}")
        return excluded

    def get_neighbors(self, device, cmd):

        if self.exclude in device.get("device_id", "unknown"):
            return []
        username = str(self.username).strip()
        password = str(self.password).strip()
        if "aruba" in self.vendor:
            device_type = "hp_procurve"
        else:
            device_type = "cisco_xe"
        netmiko_device = {
            'device_type': device_type,
            'ip': device.get('ip', 'unknown'),
            'username': username,
            'password': password,
        }

        command = cmd
        neighbors = []
        output_dir = 'cli_cdp_output'
        hostname = "unknown"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        try:
            with ConnectHandler(**netmiko_device) as ssh:

                output = ssh.send_command(command)
                hostname = device.get("device_id", device.get("ip"))
                import ipaddress
                try:
                    ip = ipaddress.ip_address(hostname)
                    print(f"Hostname is an IP address: {ip}")
                    self.failed_neighbors.append(device)

                except:
                    hostname = hostname.split(".")[0]

                print(f"Connected to: {hostname}")
                with open(f"{output_dir}/{hostname}.txt", "w") as f:
                    f.write(output)

                for template in self.ttp_templates:
                    parser = ttp(data=output, template=template)
                    parser.parse()
                    result = parser.result()

                    if isinstance(result[0][0], list):
                        parsed_neighbors = result[0][0]
                    elif isinstance(result[0][0], dict):
                        parsed_neighbors = [result[0][0]]

                    for entry in parsed_neighbors:
                        device_id = entry.get('device_id')
                        if device_id:
                            if not self.is_excluded(device):
                                neighbors.append(entry)
        except netmiko.NetMikoAuthenticationException as ae:
            print(f"Netmiko Auth Failure: {device.get('device_id','name parsing failed')}")
        except netmiko.NetMikoTimeoutException as se:
            print(f"Netmiko Timeout Error, unable to connect: {device.get('device_id','name parsing failed')}:{device.get('ip','ip_unknown')}")
        except Exception as e:
            print(f"An error occurred while fetching neighbors for {hostname}:{device.get('ip', 'ip_unknown')}")
            print(e)
            import socket
            try:
                dns_name = socket.gethostbyaddr(device.get("ip","ip_unknown"))
                device['dns_name'] = dns_name
            except:
                print(f"DNS Lookup failed")
            self.failed_neighbors.append(device)

        return neighbors

    def remove_txt_files(self, folder_path="./cli_cdp_output"):
        # Validate if folder exists
        if not os.path.exists(folder_path):
            print(f"Error: The folder '{folder_path}' doesn't exist.")
            return

        # Iterate over each file in the folder
        for filename in os.listdir(folder_path):
            if filename.endswith('.txt'):
                # Construct full file path
                file_path = os.path.join(folder_path, filename)
                try:
                    # Remove the .txt file
                    os.remove(file_path)
                    print(f"Successfully removed: {file_path}")
                except Exception as e:
                    print(f"Error occurred while deleting {file_path}: {e}")
    def discover(self):
        self.remove_txt_files()
        self.queue.put(self.seed_device_stub)
        while not self.queue.empty():
            current_device_dict = self.queue.get()
            current_device_id = current_device_dict.get('device_id', None)

            if current_device_id is None:
                print(f"Failed to parse device ID: {current_device_dict}")
                self.failed_neighbors.append(current_device_dict)
                continue

            if current_device_id not in self.visited:
                self.visited.add(current_device_id)
                if "aruba" in self.vendor:
                    cmd = "show lldp info remote-device detail"
                else:
                    cmd = 'show cdp neighbors detail'

                neighbors = self.get_neighbors(current_device_dict, cmd)
                for neighbor_dict in neighbors:
                    try:
                        neighbor_device_id = self.strip_domain(neighbor_dict['device_id'])
                        if neighbor_device_id not in self.visited and not self.is_excluded(neighbor_dict):
                            self.queue.put(neighbor_dict)
                    except Exception as e:
                        print(f"Neighbor discovery issue: {neighbor_dict} : {e}")
                        self.failed_neighbors.append(neighbor_dict)
        print(f"Discovery complete. Visited devices: {self.visited}")


    def strip_domain(self, device_id):
        hostname = device_id.split(self.domain_name)[0]
        # hostname = hostname.split("(")[0]
        hostname = re.sub(r'\(.*?\)', '', hostname)

        return hostname


if __name__ == "__main__":
    seed_device_ip = '10.200.124.10'
    seed_device_stub = {
        'local_port': 'N/A',
        'remote_port': 'N/A',
        'platform': 'N/A',
        'capabilities': 'N/A',
        'ip': seed_device_ip,
        'device_id': 'us-0445-swl-01'
    }
    # excluded_types = ['SEP']
    discoverer = CDPDiscover(seed_device_ip, seed_device_stub, "el-speterman", "T0lkien@2023", ".columbia.csc", exclude="nothing", vendor="aruba")
    with open("failed_neighbors.json", "w") as fh:
        fh.write(json.dumps(discoverer.failed_neighbors, indent=2))
    discoverer.discover()
