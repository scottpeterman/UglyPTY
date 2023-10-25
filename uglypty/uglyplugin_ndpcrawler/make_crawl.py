import sys


crawl_file = '''
import json
import re
import subprocess
import platform
import shutil
import os
import click
from uglypty.uglyplugin_ndpcrawler.cdp_crawler import CDPDiscover
from uglypty.uglyplugin_ndpcrawler.cdp_build_iptoname_lookup import IPtoName
from uglypty.uglyplugin_ndpcrawler.cdp_build_mapfile import NetworkDiscovery
from uglypty.uglyplugin_ndpcrawler.cdp_map_class import NetworkDiagramGenerator
from uglypty.uglyplugin_ndpcrawler.templates import ttp_templates

def open_folder(folder_path):
    # Convert to absolute path if it's relative
    folder_path = os.path.abspath(folder_path)
    
    if platform.system() == 'Windows':
        os.startfile(folder_path)
    elif platform.system() == 'Linux':
        subprocess.run(['xdg-open', folder_path])
    else:
        print(f'Platform {platform.system()} not supported')

def backup_files(collection_name):
    # Define the source and destination directories
    source_dir = './cli_cdp_output'
    dest_dir = f'./collections/{collection_name}'

    # Create the destination directory if it doesn't exist
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Copy each file from the source directory to the destination directory
    for file_name in os.listdir(source_dir):
        source_file = os.path.join(source_dir, file_name)
        dest_file = os.path.join(dest_dir, file_name)
        shutil.copy2(source_file, dest_file)  # copy2 will also copy metadata
    shutil.copy2("./Output/network_map.json", f"./Output/{collection_name}_network_map.json")

def abbreviate_interface_name(interface_name):
    interface_mapping = {
        'Ethernet': 'Et',
        'GigabitEthernet': 'Gi',
        'TenGigabitEthernet': 'Te',  # Updated mapping for TenGigabitEthernet
        'FastEthernet': 'Fa',  # Added mapping for FastEthernet
        'GigabitEt': 'Gi'
    }
    # Use regular expression to split alphabetic and numeric parts
    parts = re.split(r'(\d+)', interface_name)
    abbreviated_parts = []

    for part in parts:
        if part.isnumeric():
            # Keep numeric parts as-is
            abbreviated_parts.append(part)
        else:
            # Check if the alphabetic part matches any full name in the mapping
            for full_name, abbreviation in interface_mapping.items():
                if full_name in part:
                    part = part.replace(full_name, abbreviation)
                    break
            abbreviated_parts.append(part)

    return ''.join(abbreviated_parts)

def handle_edge_cases(map_data):
    for device, device_data in map_data.items():
        for entry in device_data:
            if entry['remote_port'].startswith('GigabitEt'):
                entry['remote_port'] = entry['remote_port'].replace('GigabitEt', 'Gi')
            if entry['local_port'].startswith('GigabitEt'):
                entry['local_port'] = entry['local_port'].replace('GigabitEt', 'Gi')

            if entry['remote_port'].startswith('TenGigabitEt'):
                entry['remote_port'] = entry['remote_port'].replace('TenGigabitEt', 'Te')
            if entry['local_port'].startswith('TenGigabitEt'):
                entry['local_port'] = entry['local_port'].replace('TenGigabitEt', 'Te')
    return map_data

def shorten_intf_names(map_data, output_file):
    processed_data = {}
    for device, device_data in map_data.items():
        processed_entries = []
        for entry in device_data:
            entry['local_port'] = abbreviate_interface_name(entry['local_port'])
            entry['remote_port'] = abbreviate_interface_name(entry['remote_port'])
            processed_entries.append(entry)
        processed_data[device] = processed_entries

    final_map = handle_edge_cases(processed_data)
    with open(output_file, "w") as ofh:
        ofh.write(json.dumps(final_map, indent=2))

@click.command()
@click.option('--seed_ip', required=True, help='Seed IP address')
@click.option('--device_id',  required=True, help='Device ID')
@click.option('--username',  required=True, help='Username')
@click.option('--password',  required=True, help='Password')
@click.option('--domain_name', default="home.com", help='Domain name to strip')
@click.option('--exclude_string', default="SEP", help='comma delimited exclude string (i.e. SEP,VMWare')
@click.option('--layout_algo', default="rt", help='Map Algorythm - recommended rt,kk')
@click.option('--map_name', default="Network_map.graphml", help='.graphml file to save')
@click.option('--collection_name', default="default", help='collection folder to backup retrieved cli info - i.e. site_name')
@click.option('--vendor', default="cisco", help='cisco, aruba')
def main(seed_ip, device_id, username, password, domain_name, exclude_string, layout_algo, map_name, collection_name, vendor):
    folders_to_check = ["./Output", "./collections", "./cli_cdp_output"]

    # Loop through the list and create folders if they don't exist
    for folder in folders_to_check:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created folder: {folder}")
        else:
            print(f"Folder {folder} already exists.")

    seed_device_stub = {
        'local_port': 'N/A',
        'remote_port': 'N/A',
        'platform': 'N/A',
        'capabilities': 'N/A',
        'ip': str(seed_ip).strip(),
        'device_id': str(device_id).strip()
    }

    discoverer = CDPDiscover(seed_ip, seed_device_stub, username, password, domain_name=domain_name, exclude=exclude_string, vendor=vendor)
    with open("failed_neighbors.json", "w") as fh:
        fh.write(json.dumps(discoverer.failed_neighbors, indent=2))
    discoverer.discover()
    if len(discoverer.visited) < 2:
        print(f"\n\nseed device failure, nothing else can be discovered!")
        return
    # Step 2
    parser = IPtoName()
    parser.run()

    # Step 3

    nd = NetworkDiscovery(exclude_string=exclude_string)
    network_map = nd.run()

    # 3.5
    shorten_intf_names(network_map, './Output/network_map.json')
    # Step 4
    generator = NetworkDiagramGenerator('./Output/network_map.json', domain_name)
    generator.generate()
    generator.layout_and_save(layout_algo=layout_algo, filename=map_name)
    # shorten_intf_names(network_map, f'./Output/{map_name}')

    backup_files(collection_name)
    open_folder("./Output")

    print("Crawl Process Complete!")
    print("Maps created in ./Output")
    print("also see ./collections")



if __name__ == "__main__":
    main()

'''
class file_builder():
    def __init__(self):
        self.crawl_file = crawl_file
    
    def get_crawl(self):
        return self.crawl_file