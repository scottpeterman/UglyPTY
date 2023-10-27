from concurrent.futures import ThreadPoolExecutor
import socket
import os
from PyQt6.QtCore import QThread, pyqtSignal


class PortScannerThread(QThread):
    textReady = pyqtSignal(str)  # Signal emitted when there is new text to show on the UI
    scanComplete = pyqtSignal(list)  # Signal emitted when scanning is complete

    def __init__(self, ip_list, port_list, thread_num, show_refused, wait_time, stop_after_count):
        super(PortScannerThread, self).__init__()
        self.ip_list = ip_list
        self.port_list = port_list
        self.thread_num = thread_num
        self.show_refused = show_refused
        self.wait_time = wait_time
        self.stop_after_count = stop_after_count
        self.open_results = []

    def run(self):
        found_count = 0  # Keep track of how many open ports are found

        with ThreadPoolExecutor(max_workers=self.thread_num) as executor:
            # Create a flat list of (ip, port) combinations
            tasks = [(ip, port) for ip in self.ip_list for port in self.port_list]

            # Use executor.map() to map ping_port function across all (ip, port) combinations
            results = list(executor.map(lambda p: self.ping_port(*p), tasks))

            # Filter out None results (you can adapt ping_port to return some status)
            self.open_results = [r for r in results if r is not None]

        self.scanComplete.emit(self.open_results)  # Emit signal to indicate that scanning is complete

    def ping_port(self, ip, port):
        self.textReady.emit(f"scanning... {ip}:{port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.wait_time)
        status = sock.connect_ex((ip, port))
        if status == 0:
            self.textReady.emit(f'{ip}:{port} OPEN')
            return (ip, port)  # Return the open port information
        elif status not in [35, 64, 65] and self.show_refused:
            self.textReady.emit(f'{ip}:{port} ERRNO {status}, {os.strerror(status)}')
            return None
