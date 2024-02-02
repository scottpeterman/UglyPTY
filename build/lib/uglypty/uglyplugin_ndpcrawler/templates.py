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
''', '''
  Local Port   : {{ local_port | ORPHRASE }}
  SysName      : {{ device_id | ORPHRASE | replace(" ","") }}    
  System Descr : {{ platform | ORPHRASE | default("unknown") }}   
  PortDescr    :   {{ remote_port | ORPHRASE | replace(" ","") | default("SWPORT") }}    
  System Capabilities Supported  : {{ capabilities | ORPHRASE  | default("unknown") | replace(" ","_") }}
     Address : {{ ip }}'''
]
class template_builder():
    def __init__(self):
        self.ttp_templates = ttp_templates

