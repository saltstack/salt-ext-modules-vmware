"""
  Data required for create and update of the resource(security rule, Nat rule, Network etc..) on VMC
"""

create_security_rules_mgw = {
    "sequence_number": 0,
    "source_groups": ["ANY"],
    "services": ["ANY"],
    "logged": False,
    "disabled": False,
    "destination_groups": ["ANY"],
    "scope": ["/infra/tier-1s/mgw"],
    "action": "ALLOW",
    "tag": "",
    "notes": "",
    "tags": None,
}


create_security_rules_cgw = {
    "sequence_number": 0,
    "source_groups": ["ANY"],
    "services": ["ANY"],
    "logged": False,
    "disabled": False,
    "destination_groups": ["ANY"],
    "scope": ["/infra/labels/cgw-all"],
    "action": "ALLOW",
    "tag": "",
    "notes": "",
    "tags": None,
}


update_security_rules = {
    "display_name": None,
    "sequence_number": None,
    "source_groups": None,
    "services": None,
    "logged": None,
    "disabled": None,
    "destination_groups": None,
    "scope": None,
    "action": None,
    "tag": None,
    "notes": None,
    "tags": None,
}
