import ipaddress
import sys
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pathlib import Path
import yaml
import traceback
import time
from typing import List, Dict
import pandas as pd
import pandasql
import socket
from netmiko import ConnectHandler, NetMikoAuthenticationException, NetMikoTimeoutException
from uglypty.Library.util import cryptonomicon
import sqlite3
from pprint import pprint as pp

# Set output directory paths
output_dir = Path("./Capture")
failed_output_dir = Path("./Capture")
failed_connections_dir = Path("./Capture")

# Ensure that the output directories exist
output_dir.mkdir(parents=True, exist_ok=True)
failed_output_dir.mkdir(parents=True, exist_ok=True)
failed_connections_dir.mkdir(parents=True, exist_ok=True)

# Command to run on the devices
# cmds_to_run = ["terminal len 0", "show run", "exit"]
response_prompt = "sw02#"  # Example prompt indicating the completion of response
timeout_seconds = 180
# query_default = """SELECT * FROM df WHERE display_name like '%wan%' or display_name like '%core%' or display_name like '%-sw-%' or display_name like '%edge%'"""
query_default = """SELECT * FROM df WHERE display_name like '%rtr-%'"""

max_job_size = "10"
# command_to_run = "show run"

from concurrent.futures import ThreadPoolExecutor

def ssh_to_device_with_timeout(device):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(ssh_to_device, device)
        try:
            return future.result(timeout=timeout_seconds)  # Waits for at most 'timeout' seconds
        except TimeoutError:
            print(f"Timeout for device {device['display_name']}")
            return {"device": device, "status": "failure", "output": "Command timed out."}


def get_creds(credsid, db_path, key_path):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM creds WHERE id = ?", (credsid,))
    record = cursor.fetchone()
    encrypted_password = record[1]
    username = record[0]
    conn.close()

    # Decrypt the password
    decrypted_password = cryptonomicon(encrypted_password, key_path)
    # print(f"Credentials for user {credsid}: {username}, {decrypted_password}")

    return username, decrypted_password
def ssh_to_device(device_source):
    # print(f"ssh_to_device: {device_source}")
    command_to_run = device_source['command']
    print(f"command_to_run: {command_to_run}")
    hostname = device_source['display_name']
    ip = device_source['host']
    result = {'device': device_source, 'status': 'unknown', 'output': ''}


    # sys.exit()
    if not is_valid_ipv4(ip):
        print(f"Invalid IPv4 address: {ip}. Skipping.")
        result['status'] = 'skipped'
        result['output'] = f"Invalid IPv4 address: {ip}"
        return result  # Skipped due to invalid IP

    if not is_port_open(ip, 22):
        print(f"Port 22 is closed for {hostname} ({ip}). Marking as failure.")
        result['status'] = 'failure'
        result['output'] = f"Port 22 is closed for {hostname} ({ip})"
        return result  # Failure due to closed port

    try:
        # Retrieve creds
        # username, password = get_creds(device_source['credsid'], db_path, key_path)
        print(f"Connecting: {hostname}:{ip}")
        netmiko_device = {
            'device_type': device_source['device_type'],
            'ip':   ip,
            'username': device_source['username'],
            'password': device_source['password'],
        }

        try:
            connection = ConnectHandler(**netmiko_device)
        except NetMikoAuthenticationException as e:
            print(f"Failed to authenticate: {e}")

            # with failed_output_dir.joinpath(f"{hostname}_failed_auth.txt").open("w") as output_file:
            #     output_file.write(f"Hostname: {hostname}\nFolder: {device_source['folder_name']}\nIP: {ip}")
            result['status'] = 'failure'
            result['output'] = f"Failure: {e}"
            return result  # Failed connection or command execution

        except NetMikoTimeoutException as e:
            print(f"SSH connection timed out: {e}")
            result['status'] = 'failure'
            result['output'] = f"Failure: {e}"
            return result  # Failed connection or command execution
        except Exception as e:
            traceback.print_exc()
            print(f"Error connecting to {ip}: {e}")
            result['status'] = 'failure'
            result['output'] = f"Failure: {e}"
            return result  # Failed connection or command execution

        try:
            output = connection.send_command(command_to_run, read_timeout=30)
        except Exception as e:
            traceback.print_exc()
            print(f"Error connecting to {ip}: {e}")
            result['status'] = 'failure'
            result['output'] = f"Failure: {e}"
            return result  # Failed connection or command execution


        result['output'] = output
        result['status'] = 'success'
        print(f"ssh_to_device is returning: {result['status']}")

        # connection.disconnect()

        return result  # Successful connection and command execution

    except Exception as e:
        print(f"Failure: {e}")
        result['status'] = 'failure'
        result['output'] = f"Failure: {e}"
        return result  # Failed connection or command execution

class LiteralStr(str):
    pass

# Define a custom representer for that class
def literal_str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

def save_result_to_file(destination_dir: str, filename: str, result: dict):
    if result is not None:
        destination_text_dir = destination_dir + "/text_output"

        destination_dir = Path(destination_dir)
        destination_dir.mkdir(parents=True, exist_ok=True)

        destination_text_dir = Path(destination_text_dir)
        destination_text_dir.mkdir(parents=True, exist_ok=True)
        # pp(result)
        output_str = result['output']
        print("-- output begin --\n" + output_str + "\n-- output end --")
        output_result = {'device': {'command': result['device']['command'],
                    'credsid': result['device']['credsid'],
                    'device_type': result['device']['device_type'],
                    'display_name': result['device']['display_name'],
                    'folder_name': result['device']['folder_name'],
                    'host': result['device']['host'],
                    'timestamp': result['device']['timestamp'],
                    'username': result['device']['username']},
                    'output': LiteralStr(output_str),
                    'status': result['status']
                     }

        try:
            with open(destination_text_dir.joinpath(f"{filename}.txt"), 'w') as file:
                file.write(result['output'])
            with open(destination_dir.joinpath(f"{filename}.yaml"), 'w') as file:
                yaml.add_representer(LiteralStr, literal_str_representer, Dumper=yaml.SafeDumper)
                yaml.safe_dump(output_result, file)
                print(f"Yaml Saved: {file}")
        except Exception as e:
            print(f"Error saving results: {e}")
            print(e.args[0])

def flatten_data(data):
    flattened_data = []
    for record in data:
        folder_name = record['folder_name']
        for session in record['sessions']:
            flattened_record = session.copy()
            flattened_record['folder_name'] = folder_name
            flattened_data.append(flattened_record)
    return pd.DataFrame(flattened_data)


def fetch_devices(yaml_file: str, query=None) -> List[Dict]:
    with open(yaml_file) as file:
        yaml_data = yaml.safe_load(file)

    df = flatten_data(yaml_data)
    if query is not None:
        df = pandasql.sqldf(query, locals())

    return df.to_dict('records')


def is_valid_ipv4(ip: str) -> bool:
    try:
        ipaddress.IPv4Address(ip)
        return True
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
        return False


def is_port_open(ip: str, port: int, timeout: int = 2) -> bool:
    try:
        sock = socket.create_connection((ip, port), timeout=timeout)
        sock.close()
        return True
    except (socket.timeout, ConnectionRefusedError):
        return False
    except Exception as e:
        print(f"Error checking port {port} on {ip}: {e}")
        return False

