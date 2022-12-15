import json
import pytest
import saltext.vmware.utils.drift as drift

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

firewall_rule_drift = {
    "sshServer": {
    "old": {
      "allowed_hosts": {
        "ip_address": [
          "192.168.110.90",
          "192.168.110.91"
        ]
      }
    },
    "new": {
      "allowed_hosts": {
        "ip_address": [
          "192.168.110.90"
        ]
      }
    }
  },
  "sshClient": {
    "old": {
      "enabled": False,
      "allowed_hosts": {
        "ip_address": [],
        "all_ip": True,
        "ip_network": []
      }
    },
    "new": {
      "enabled": True,
      "allowed_hosts": {
        "ip_address": [
          "3.3.3.3"
        ],
        "all_ip": False,
        "ip_network": [
          "1.1.1.1/24",
          "2.2.2.2/24"
        ]
      }
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

storage_policy_drift = {
    "Management Storage policy - Thin": {
    "old": {
      "constraints": {
        "vSAN VMC Small sub-profile": {
          "hostFailuresToTolerate": 1,
          "proportionalCapacity": 0
        }
      }
    },
    "new": {
      "constraints": {
        "vSAN VMC Small sub-profile": {
          "hostFailuresToTolerate": 2,
          "proportionalCapacity": 1
        }
      }
    }
  },
  "Performance - Thick": {
    "old": {
      "constraints": {
        "VSAN": {
          "hostFailuresToTolerate": 1,
          "checksumDisabled": False,
          "proportionalCapacity": 0,
          "replicaPreference": "RAID-1 (Mirroring) - Performance"
        }
      }
    },
    "new": {
      "constraints": {
        "VSAN": {
          "hostFailuresToTolerate": 2,
          "checksumDisabled": True,
          "proportionalCapacity": 70,
          "replicaPreference": "RAID-5/6 (Erasure Coding) - Capacity"
        }
      }
    }
  }
}

storage_policy_new2 = {
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
  }
}

storage_policy_old2 = {}

storage_policy_drift2 = {
  "Performance - Thick": {
    "old": {},
    "new": {
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
    }
  }
}

@pytest.fixture(
  params=(
    [firewall_rule_old, firewall_rule_new, firewall_rule_drift], 
    [storage_policy_old, storage_policy_new, storage_policy_drift], 
    [storage_policy_old2, storage_policy_new2, storage_policy_drift2]
    )
)
def mocked_drift_report_configs(request):
  yield request.param[0], request.param[1], request.param[2]

def test_druft_report(mocked_drift_report_configs):
  _old, _new, _drift = mocked_drift_report_configs
  diff = drift.drift_report(_old, _new, diff_level=0)

  assert diff == _drift
