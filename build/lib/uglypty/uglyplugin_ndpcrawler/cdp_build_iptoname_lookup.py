import os
import yaml
from ttp import ttp

class IPtoName():
    def __init__(self):
        print("IPtoName")

    def run(self):
        # List of TTP templates
        ttp_templates = [
            '''Device ID: {{ device_id }}
          IP address: {{ ip }}
        Platform: {{ platform | ORPHRASE }},  Capabilities: {{ capabilities | ORPHRASE}}
        Interface: {{ local_port | ORPHRASE }},  Port ID (outgoing port): {{ remote_port | ORPHRASE}}''',
            '''System Name: {{ device_id }}
            IPv4 Address: {{ ip }}
        Platform: {{ platform | ORPHRASE }},  Capabilities: {{ capabilities | ORPHRASE}}
        Interface: {{ local_port | ORPHRASE }},  Port ID (outgoing port): {{ remote_port | ORPHRASE}}'''
        ]

        # Initialize lookup dictionary and failed list
        ip_device_lookup = {}
        failed_files = []

        def parse_file(filename, templates):
            with open(f"{folder_to_scan}/{filename}", 'r') as f:
                data = f.read()

            for template in templates:
                try:
                    parser = ttp(data=data, template=template)
                    parser.parse()
                    result = parser.result()
                    print(f"Parser result for file {filename} with template: {result}")  # Debugging line

                    if result and isinstance(result[0][0], list):
                        return result[0][0]
                    elif result and isinstance(result[0][0], dict):
                        return [result[0][0]]

                except Exception as e:
                    print(f"Parser exception for file {filename} with template: {e}")

            return None  # Return None if all templates fail

        # Traverse the directory for .txt files
        folder_to_scan = './cli_cdp_output'
        for filename in os.listdir(folder_to_scan):
            if filename.endswith('.txt'):
                parsed_data = parse_file(filename, ttp_templates)
                print(f"Parsed data for file {filename}: {parsed_data}")  # Debugging line

                if parsed_data:
                    for entry in parsed_data:
                        if 'ip' in entry and 'device_id' in entry:
                            ip_device_lookup[entry['ip']] = entry['device_id']
                else:
                    failed_files.append(filename)

        def deduplicate_dict(self, input_dict):
            deduped_dict = {}
            for key, value in input_dict.items():
                if "SEP" not in value:
                    if key not in deduped_dict:
                        deduped_dict[key] = value
                    else:
                        # Handle duplicates, for now, let's keep the last value
                        deduped_dict[key] = value
            return deduped_dict

        ip_device_lookup = deduplicate_dict(self, ip_device_lookup)

        # Write the lookup to a YAML file
        with open('./Output/ip_device_lookup.yaml', 'w') as f:
            yaml.dump(ip_device_lookup, f)

        # Write the failed files to failed.res
        with open('failed.res', 'w') as f:
            for file in failed_files:
                f.write(f"{file}\n")

if __name__ == "__main__":
    iptoname = IPtoName()
    iptoname.run()