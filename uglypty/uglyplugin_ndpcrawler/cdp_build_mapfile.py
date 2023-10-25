import os
import json
import re
from ttp import ttp
from collections import defaultdict


class NetworkDiscovery:
    BASE_PATH = "./cli_cdp_output/"

    ttp_templates = [
        '''
Device ID: {{ device_id }}
  IP address: {{ ip | default("undefined")}}
Platform: {{ platform | ORPHRASE }},  Capabilities: {{ capabilities | ORPHRASE}}
Interface: {{ local_port | ORPHRASE }},  Port ID (outgoing port): {{ remote_port | ORPHRASE}}
        ''',
        '''
Device ID:{{ device_id  | split(".") | item(0) | split("(") | item(0)}}
    IPv4 Address: {{ ip }}
Device ID:{{ device_id | split(".") | item(0) | split("(") | item(0) }}
Platform: {{ platform | ORPHRASE }},  Capabilities: {{ capabilities | ORPHRASE}}
Interface: {{ local_port | ORPHRASE }},  Port ID (outgoing port): {{ remote_port | ORPHRASE}}
        ''',
        '''
  Local Port   : {{ local_port | ORPHRASE }}
  SysName      : {{ device_id | ORPHRASE | replace(" ","") }}    
  System Descr : {{ platform | ORPHRASE | default("unknown") }}   
  PortDescr    :   {{ remote_port | ORPHRASE | replace(" ","") | default("SWPORT") }}    
  System Capabilities Supported  : {{ capabilities | ORPHRASE  | default("unknown") | replace(" ","_") }}
     Address : {{ ip }}
'''
    ]
    def __init__(self, exclude_string):
        self.exclude_string = exclude_string
        self.BASE_PATH = "./cli_cdp_output/"

    def is_excluded(self, device):
        excluded = False
        for exstring in self.exclude_string.split(","):
            if exstring in device.get("device_id", "unknown"):
                excluded = True
                print(f"Hit Exclusion Rule: {device.get('device_id')}")
        return excluded
    def filter_filename(self, filename):
        return re.sub(r'\(.*?\)', '', filename)

    def parse_data(self, data):
        for template in self.ttp_templates:
            try:
                parser = ttp(data=data, template=template)
                parser.parse()
                result = parser.result()

                if result and all(entry != {} for entry in result[0][0]):
                    for entry in result[0][0]:
                        # entry_device_id = entry.get("device_id", "unknown")

                        if 'device_id' in entry:
                            device_id = entry['device_id']
                            cleaned_device_id = self.filter_filename(device_id)
                            entry['device_id'] = cleaned_device_id

                    if len(result[0][0]) == 0:
                        continue
                    if isinstance(result[0][0], list):
                        return result[0][0]
                    elif isinstance(result[0][0], dict):
                        return [result[0][0]]
            except Exception as e:
                print(f"Parser exception with template: {e}")

        return None

    def discover_network(self):
        network_map = defaultdict(list)
        # Get the absolute path of the directory where the Python script resides
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Navigate two levels up
        self.APP_PATH = os.path.dirname(os.path.dirname(script_dir))
        print(os.path.join(self.APP_PATH,self.BASE_PATH))
        folder_to_clean = os.path.join(self.APP_PATH,self.BASE_PATH)
        for file_name in os.listdir(folder_to_clean):
            device_name = self.filter_filename(file_name.split(".")[0])
            file_path = os.path.join(folder_to_clean, file_name)
            with open(file_path) as fh:
                content = fh.read()

            parsed_data = self.parse_data(content)
            cleaned_data = []
            if parsed_data is not None:
                for neighbor in parsed_data:

                    if self.is_excluded(neighbor):
                        continue
                    else:
                        keys = list(neighbor.keys())
                        if 'device_id' in keys and 'local_port' in keys and 'remote_port' in keys:
                            cleaned_data.append(neighbor)

                if cleaned_data:
                    try:
                        network_map[device_name].extend(cleaned_data)
                    except Exception as e:
                        print(e)

        with open(self.APP_PATH + "./Output/network_map.json", "w") as fh:
            fh.write(json.dumps(network_map, indent=2))

        return network_map

    def run(self):
        return self.discover_network()


if __name__ == '__main__':
    nd = NetworkDiscovery(exclude_string="SEP")
    network_map = nd.run()
    print(json.dumps(network_map, indent=4))
