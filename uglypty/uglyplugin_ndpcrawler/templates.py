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
'''
]
class template_builder():
    def __init__(self):
        self.ttp_templates = ttp_templates

