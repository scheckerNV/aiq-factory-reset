#!/usr/bin/env python3
import yaml, sys, os, ipaddress

golden_path = sys.argv[1]
outdir = sys.argv[2]

with open(golden_path, "r") as f:
    g = yaml.safe_load(f)

mgmt = g["network_fabrics"]["management"]
subnet = ipaddress.ip_network(mgmt["subnet"], strict=False)
prefix = subnet.prefixlen
gateway = mgmt.get("gateway")
dns = mgmt.get("dns_servers", []) or []

os.makedirs(os.path.join(outdir, "host_vars"), exist_ok=True)
os.makedirs(os.path.join(outdir, "group_vars"), exist_ok=True)

inv = {"all": {"children": {"compute": {"hosts": {}}}}}

mtu = g.get("policies", {}).get("network", {}).get("ethernet", {}).get("mtu", 1500)

for node_name, node in (g.get("nodes") or {}).items():
    if not isinstance(node, dict):
        continue
    mg = node.get("networks", {}).get("management")
    if not mg:
        continue
    hostname = node.get("hostname", node_name)
    ip = mg["ip"]
    iface = mg.get("interface", "eth0")

    host_vars = {
        "nmstate_desired": {
            "interfaces": [
                {
                    "name": iface,
                    "type": "ethernet",
                    "state": "up",
                    "mtu": mtu,
                    "ipv4": {
                        "enabled": True,
                        "address": [{"ip": ip, "prefix-length": prefix}],
                        "gateway": gateway,
                        "dns": dns,
                    },
                }
            ]
        }
    }
    with open(os.path.join(outdir, "host_vars", f"{hostname}.yml"), "w") as hf:
        yaml.safe_dump(host_vars, hf, sort_keys=False)

    inv["all"]["children"]["compute"]["hosts"][hostname] = {"ansible_host": ip}

with open(os.path.join(outdir, "inventory.yml"), "w") as f:
    yaml.safe_dump(inv, f, sort_keys=False)

with open(os.path.join(outdir, "group_vars", "all.yml"), "w") as gf:
    yaml.safe_dump(
        {
            "cluster_name": g["metadata"]["cluster_name"],
            "dns_servers": dns,
            "mgmt_gateway": gateway,
            "nm_checkpoint_timeout": 120,
        },
        gf,
        sort_keys=False,
    )
