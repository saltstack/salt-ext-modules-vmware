import json
import saltext.vmware.utils.misc as misc

firewall_rule_old = {
  "sshClient": {
    "enabled": False,
    "allowed_hosts": {
      "all_ip": True,
      "ip_address": [],
      "ip_network": []
    }
  },
  "sshServer": {
    "enabled": True,
    "allowed_hosts": {
      "all_ip": False,
      "ip_address": [
        "192.168.110.90",
        "192.168.110.91"
      ],
      "ip_network": []
    }
  }
}
  
firewall_rule_new = {
  "sshClient": {
    "enabled": True,
    "allowed_hosts": {
      "all_ip": False,
      "ip_address": [
        "3.3.3.3"
      ],
      "ip_network": [
        "1.1.1.1/24",
        "2.2.2.2/24"
      ]
    }
  },
  "sshServer": {
    "enabled": True,
    "allowed_hosts": {
      "all_ip": False,
      "ip_address": [
        "192.168.110.90"
      ],
      "ip_network": []
    }
  }
}

storage_policy_new = {
  "Performance - Thick": {
    "constraints": {
      "VSAN": {
        "replicaPreference": "RAID-5/6 (Erasure Coding) - Capacity",
        "hostFailuresToTolerate": 2,
        "checksumDisabled": True,
        "stripeWidth": 1,
        "proportionalCapacity": 70,
        "cacheReservation": 0
      }
    }
  },
  "Management Storage policy - Thin": {
    "constraints": {
      "vSAN VMC Small sub-profile": {
        "hostFailuresToTolerate": 2,
        "replicaPreference": "RAID-1 (Mirroring) - Performance",
        "proportionalCapacity": 1
      }
    }
  }
}

storage_policy_old = {
  "Performance - Thick": {
    "constraints": {
      "VSAN": {
        "hostFailuresToTolerate": 1,
        "replicaPreference": "RAID-1 (Mirroring) - Performance",
        "checksumDisabled": False,
        "stripeWidth": 1,
        "forceProvisioning": False,
        "iopsLimit": 0,
        "cacheReservation": 0,
        "proportionalCapacity": 0,
        "ad5a249d-cbc2-43af-9366-694d7664fa52": "ad5a249d-cbc2-43af-9366-694d7664fa52"
      },
      "vSANDirect rules": {
        "vSANDirectType": "vSANDirect",
        "ad5a249d-cbc2-43af-9366-694d7664fa52": "ad5a249d-cbc2-43af-9366-694d7664fa52"
      }
    }
  },
  "Management Storage policy - Thin": {
    "constraints": {
      "vSAN VMC Small sub-profile": {
        "hostFailuresToTolerate": 1,
        "replicaPreference": "RAID-1 (Mirroring) - Performance",
        "proportionalCapacity": 0
      }
    }
  }
}



diff = misc.drift_report(firewall_rule_old, firewall_rule_new, diff_level=0)
print(json.dumps(diff, indent=2))
