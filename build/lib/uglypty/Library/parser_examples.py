p_examples = {
    "TTP": {
        'teSource': """interface Loopback0
 description Router-id-loopback
 ip address 192.168.0.113/24
!
interface Vlan778
 description CPE_Acces_Vlan
 ip address 10.28.0.200/24
 ip vrf DATA
!""",
        'teTemplate': """interface {{ interface }}
 ip address {{ ip }}/{{ mask }}
 description {{ description }}
 ip vrf {{ vrf }}"""
    },
    "Jinja2": {
        'teSource': """---
isis:
  instancetag: qa-test
  net: 49.0001.1720.1600.1001.00
  level: level-1
  authtype: md5
  key: cisco
  interfaces:
  - name: port-channel313
""",
        'teTemplate': """feature isis
!
router isis {{isis.instancetag}}
  net {{isis.net}}
  is-type {{isis.level}}
  log-adjacency-changes
  authentication-type {{isis.authtype}} {{isis.level}}
  authentication key-chain {{isis.key}} {{isis.level}}
  address-family ipv4 unicast
    bfd
  address-family ipv6 unicast
    bfd
!
{% for interface in isis.interfaces -%}
interface {{interface.name}}
  ip router isis {{isis.instancetag}}
  ipv6 router isis {{isis.instancetag}}
{% endfor -%}
!
"""
    },
    "JMesPath": {
        'teSource': """[
    {
        "ntp_associations_detail": [
            {
                "peer": "10.240.72.125",
                "reach": "377",
                "root_delay": "1541.1377",
                "root_disp": "34088.13",
                "stratum": "2",
                "sync_dist": "55841.0566",
                "type": "candidate"
            },
            {
                "peer": "2605:1c00:50f3:70:10:240:72:125",
                "reach": "377",
                "root_delay": "1541.1377",
                "root_disp": "22109.99",
                "stratum": "2",
                "sync_dist": "55537.1848",
                "type": "candidate"
            },
            {
                "peer": "172.30.105.134",
                "reach": "377",
                "root_delay": "0.0000",
                "root_disp": "991.82",
                "stratum": "1",
                "sync_dist": "31185.3384",
                "type": "our_master"
            }
        ]
    }
]
""",
        'teTemplate': """[0].ntp_associations_detail[?peer == '172.30.105.134']"""
    }

}