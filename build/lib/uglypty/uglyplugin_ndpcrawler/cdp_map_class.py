import json
from N2G import yed_diagram

class NetworkDiagramGenerator:

    def __init__(self, json_file_path, domain_name):
        self.json_file_path = json_file_path
        self.domain_name = domain_name
        self.diagram = yed_diagram()
        self.network_map = self._load_network_map()

    def _load_network_map(self):
        with open(self.json_file_path, 'r') as f:
            return json.load(f)

    @staticmethod
    def _clean_device_id(device_id, domain):
        return device_id.replace(domain, "")



    def generate(self):
        for device, connections in self.network_map.items():
            cleaned_device = self._clean_device_id(device, self.domain_name)
            platform = connections[0].get('platform', '')
            ip = connections[0].get('ip', 'Unknown')
            self.diagram.add_node(cleaned_device, top_label=ip, bottom_label=platform)

            for conn in connections:
                try:
                    neighbor = conn['device_id']
                    cleaned_neighbor = self._clean_device_id(neighbor, self.domain_name)
                    neighbor_platform = conn.get('platform', '')
                    neighbor_ip = conn.get('ip', '')

                    if cleaned_neighbor not in [self._clean_device_id(dev, self.domain_name) for dev in
                                                self.network_map.keys()]:
                        self.diagram.add_node(cleaned_neighbor, top_label=neighbor_ip, bottom_label=neighbor_platform)

                    local_port = conn.get('local_port', 'Unknown')
                    remote_port = conn.get('remote_port', 'Unknown')
                    self.diagram.add_link(cleaned_device, cleaned_neighbor, label='', src_label=local_port,
                                          trgt_label=remote_port)
                except Exception as e:
                    print(f"Error processing connection: {e}")
    def layout_and_save(self, layout_algo="kk", output_folder="./Output/", filename="Network_graph.graphml"):
        self.diagram.layout(algo=layout_algo)
        self.diagram.dump_file(filename=filename, folder=output_folder)


if __name__ == "__main__":
    generator = NetworkDiagramGenerator('./Output/network_map.json', ".company.com")
    generator.generate()
    generator.layout_and_save(layout_algo="rt") # kk, rt
