# SPDX-FileCopyrightText: Copyright (c) 2024-2025,
# NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Cluster-wide DCGM Expert Tools

Provides DCGM analysis and monitoring tools that work across BCM-managed clusters
via SSH. Supports auto-discovery of compute nodes and flexible node targeting.

Designed to work with any BCM cluster (DGX, GB300, H100, etc.) from a headnode.
"""

import asyncio
import json
import logging
import re
import shlex
import socket
from concurrent.futures import ThreadPoolExecutor
from os import getenv
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from urllib.parse import urlparse
from urllib.parse import urlunparse

import requests
from pydantic import Field

from aiq.builder.builder import Builder
from aiq.builder.function_info import FunctionInfo
from aiq.cli.register_workflow import register_function
from aiq.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)

# Configuration from environment
DEFAULT_CLUSTER_HOST = getenv("CLUSTER_HOST", "localhost")
DEFAULT_CLUSTER_USER = getenv("CLUSTER_USER", "hpcuser1")
DEFAULT_SSH_TIMEOUT = int(getenv("SSH_TIMEOUT", "30"))
DEFAULT_DCGM_TIMEOUT = int(getenv("DCGM_TIMEOUT", "60"))
PROM_URL = getenv("PROM_URL", "http://localhost:9090")
GRAFANA_URL = getenv("GRAFANA_URL", "http://localhost:3000")


class ClusterNode:
    """Represents a compute node in the cluster"""

    def __init__(self, hostname: str, ip: str, category: str = "", status: str = ""):
        self.hostname = hostname
        self.ip = ip
        self.category = category
        self.status = status

    def __str__(self):
        return f"{self.hostname}({self.ip})"

    def __repr__(self):
        return f"ClusterNode(hostname='{self.hostname}', ip='{self.ip}', category='{self.category}')"


def parse_kv(text: Optional[str]) -> Dict[str, str]:
    """Parse key=value parameters from input text"""
    out: Dict[str, str] = {}
    if not text:
        return out
    s = str(text).strip().strip("`")

    # Try JSON first
    if s.startswith("{") and s.endswith("}"):
        try:
            obj = json.loads(s)
            if isinstance(obj, dict):
                if "text" in obj and isinstance(obj["text"], str):
                    return parse_kv(obj["text"])
                return {str(k).strip().lower(): str(v).strip() for k, v in obj.items()}
        except Exception:
            pass

    # Fallback: split on whitespace and commas into key=value
    for tok in re.split(r"[\s,]+", s):
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k.strip().lower()] = v.strip().strip(",")
    return out


def sanitize(s: Optional[str], fallback: str = "OK") -> str:
    """Sanitize output text"""
    if not s:
        return fallback
    s2 = s.strip()
    return s2 if s2 else fallback


async def run_local_cmd(cmd: str, timeout: int = 30) -> Tuple[str, str, int]:
    """Run a local command and return (stdout, stderr, returncode)"""
    try:
        proc = await asyncio.create_subprocess_shell(cmd,
                                                     stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return (stdout.decode("utf-8", errors="replace"), stderr.decode("utf-8", errors="replace"), proc.returncode)
    except asyncio.TimeoutError:
        return ("", f"Command timed out after {timeout}s", 124)
    except Exception as e:
        return ("", f"Command failed: {str(e)}", 1)


async def run_ssh_cmd(node: ClusterNode, cmd: str, user: str, timeout: int = 30) -> Tuple[str, str, int]:
    """Run a command on a remote node via SSH"""
    ssh_cmd = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        "-o",
        f"ConnectTimeout={min(10, timeout)}",
        f"{user}@{node.ip}",
        cmd
    ]

    try:
        proc = await asyncio.create_subprocess_exec(*ssh_cmd,
                                                    stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return (stdout.decode("utf-8", errors="replace"), stderr.decode("utf-8", errors="replace"), proc.returncode)
    except asyncio.TimeoutError:
        return ("", f"SSH command timed out after {timeout}s", 124)
    except Exception as e:
        return ("", f"SSH failed: {str(e)}", 1)


async def discover_cluster_nodes(cluster_host: str = "localhost", cluster_user: str = "hpcuser1") -> List[ClusterNode]:
    """Discover compute nodes from BCM cluster management"""
    nodes: List[ClusterNode] = []

    try:
        # Get device list from BCM
        cmd = 'cmsh -c "device list -f hostname,ip,category,status"'
        stdout, stderr, returncode = await run_local_cmd(cmd, timeout=30)

        if returncode != 0:
            logger.error("Failed to discover cluster nodes via BCM: %s", stderr)
            return nodes

        # Parse BCM device list output
        for line in stdout.splitlines():
            line = line.strip()
            if not line or line.startswith("Device") or "---" in line:
                continue

            # Parse line format: hostname ip category status
            parts = line.split()
            if len(parts) >= 2:
                hostname = parts[0]
                ip = parts[1]
                category = parts[2] if len(parts) > 2 else ""
                status = " ".join(parts[3:]) if len(parts) > 3 else ""

                # Skip non-compute nodes (headnodes, switches, etc.)
                if any(skip in hostname.lower() for skip in ['headnode', 'switch', 'sw-', 'nvsw']):
                    continue

                # Only include nodes with valid IPs
                if re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
                    nodes.append(ClusterNode(hostname, ip, category, status))

    except Exception as e:
        logger.error("Error discovering cluster nodes: %s", str(e))

    logger.info("Discovered %d compute nodes", len(nodes))
    return nodes


def parse_node_spec(spec: str, all_nodes: List[ClusterNode]) -> List[ClusterNode]:
    """Parse node specification and return matching nodes

    Supports:
    - "all" - all discovered nodes
    - "10.1.1.1,10.1.1.2" - specific IPs
    - "10.1.1.1-5" - IP range
    - "node01,node02" - hostnames
    - "r1-p1-gb300-n01-18" - hostname range patterns
    """
    if not spec or spec.lower() == "all":
        return all_nodes

    target_nodes: Set[ClusterNode] = set()

    for part in spec.split(","):
        part = part.strip()

        # IP range: 10.1.1.1-5
        ip_range_match = re.match(r'^(\d+\.\d+\.\d+\.)(\d+)-(\d+)$', part)
        if ip_range_match:
            base_ip, start_num, end_num = ip_range_match.groups()
            for i in range(int(start_num), int(end_num) + 1):
                target_ip = f"{base_ip}{i}"
                for node in all_nodes:
                    if node.ip == target_ip:
                        target_nodes.add(node)
                        break
            continue

        # Hostname range: r1-p1-gb300-n01-18
        hostname_range_match = re.match(r'^(.+-)(\d+)-(\d+)$', part)
        if hostname_range_match:
            base_name, start_num, end_num = hostname_range_match.groups()
            start_len = len(start_num)
            for i in range(int(start_num), int(end_num) + 1):
                target_hostname = f"{base_name}{i:0{start_len}d}"
                for node in all_nodes:
                    if node.hostname == target_hostname:
                        target_nodes.add(node)
                        break
            continue

        # Single IP or hostname
        for node in all_nodes:
            if node.ip == part or node.hostname == part:
                target_nodes.add(node)
                break

    return list(target_nodes)


async def execute_on_cluster(nodes: List[ClusterNode],
                             cmd: str,
                             user: str,
                             timeout: int = 60,
                             max_concurrent: int = 10) -> Dict[str, Dict[str, Any]]:
    """Execute command on multiple nodes concurrently"""
    results: Dict[str, Dict[str, Any]] = {}

    # Limit concurrency to avoid overwhelming SSH connections
    semaphore = asyncio.Semaphore(max_concurrent)

    async def execute_on_node(node: ClusterNode) -> None:
        async with semaphore:
            try:
                stdout, stderr, returncode = await run_ssh_cmd(node, cmd, user, timeout)
                results[node.ip] = {
                    "node": str(node),
                    "hostname": node.hostname,
                    "ip": node.ip,
                    "success": returncode == 0,
                    "stdout": stdout.strip(),
                    "stderr": stderr.strip(),
                    "returncode": returncode
                }
            except Exception as e:
                results[node.ip] = {
                    "node": str(node),
                    "hostname": node.hostname,
                    "ip": node.ip,
                    "success": False,
                    "stdout": "",
                    "stderr": f"Execution error: {str(e)}",
                    "returncode": -1
                }

    # Execute on all nodes concurrently
    tasks = [execute_on_node(node) for node in nodes]
    await asyncio.gather(*tasks)

    return results


# ========================
# Cluster DCGM Tools
# ========================


class ClusterGPUStatusConfig(FunctionBaseConfig, name="cluster_gpu_status"):
    cluster_host: str = Field(default=DEFAULT_CLUSTER_HOST, description="Cluster head hostname/IP")
    cluster_user: str = Field(default=DEFAULT_CLUSTER_USER, description="SSH username for cluster access")
    ssh_timeout: int = Field(default=DEFAULT_SSH_TIMEOUT, description="SSH timeout in seconds")


@register_function(config_type=ClusterGPUStatusConfig)
async def cluster_gpu_status(config: ClusterGPUStatusConfig, builder: Builder):

    async def _cluster_gpu_status(text: str) -> str:
        """Get GPU status across cluster nodes"""
        opts = parse_kv(text)
        node_spec = opts.get("nodes", "all")
        output = opts.get("output", "text")

        # Discover cluster nodes
        all_nodes = await discover_cluster_nodes(config.cluster_host, config.cluster_user)
        if not all_nodes:
            return "❌ No cluster nodes discovered. Check BCM connectivity and node configuration."

        # Parse target nodes
        target_nodes = parse_node_spec(node_spec, all_nodes)
        if not target_nodes:
            return f"❌ No nodes matched specification: {node_spec}"

        logger.info("Checking GPU status on %d nodes: %s", len(target_nodes), [n.hostname for n in target_nodes])

        # Execute DCGM discovery and nvidia-smi on all nodes
        dcgm_cmd = ('if command -v dcgmi >/dev/null 2>&1; then '
                    'echo "=== DCGM DISCOVERY ==="; dcgmi discovery -l 2>/dev/null; '
                    'echo "=== GPU STATUS ==="; '
                    'nvidia-smi --query-gpu=index,name,temperature.gpu,power.draw,utilization.gpu,utilization.memory '
                    '--format=csv,noheader,nounits 2>/dev/null; '
                    'else echo "DCGM not available"; fi')

        results = await execute_on_cluster(target_nodes, dcgm_cmd, config.cluster_user, timeout=config.ssh_timeout + 30)

        if output == "json":
            return sanitize(json.dumps(results, indent=2))

        # Build text summary
        summary_lines = [f"🖥️ Cluster GPU Status ({len(target_nodes)} nodes)"]
        summary_lines.append("=" * 50)

        total_gpus = 0
        healthy_nodes = 0
        total_nodes = len(target_nodes)

        for node_ip in sorted(results.keys()):
            result = results[node_ip]
            hostname = result["hostname"]

            if not result["success"]:
                summary_lines.append(f"❌ {hostname} ({node_ip}): {result['stderr']}")
                continue

            stdout = result["stdout"]
            if "DCGM not available" in stdout:
                summary_lines.append(f"⚠️ {hostname} ({node_ip}): DCGM not installed")
                continue

            # Parse GPU count and basic info
            gpu_count = len(
                [line for line in stdout.split("\n") if line.strip() and "GPU ID" in line and "Name:" in line])

            if gpu_count == 0:
                # Try to count from nvidia-smi output
                gpu_lines = [
                    line for line in stdout.split("\n") if line.strip() and "," in line and not line.startswith("===")
                ]
                gpu_count = len(gpu_lines)

            total_gpus += gpu_count
            healthy_nodes += 1

            # Show basic GPU metrics if available
            temp_info = ""
            if "GPU STATUS" in stdout:
                gpu_lines = [
                    line for line in stdout.split("=== GPU STATUS ===")[1].split("\n") if line.strip() and "," in line
                ]  # Show all GPUs
                if gpu_lines:
                    temps = []
                    for line in gpu_lines:
                        parts = line.split(",")
                        if len(parts) >= 3:
                            try:
                                temp = float(parts[2].strip())
                                temps.append(temp)
                            except:
                                pass
                    if temps:
                        temp_info = f" (temps: {[f'{t:.0f}°C' for t in temps]})"

            summary_lines.append(f"✅ {hostname} ({node_ip}): {gpu_count} GPUs{temp_info}")

        # Overall summary
        summary_lines.append("=" * 50)
        summary_lines.append(f"📊 Summary: {healthy_nodes}/{total_nodes} nodes healthy, {total_gpus} total GPUs")

        if healthy_nodes < total_nodes:
            failed_nodes = total_nodes - healthy_nodes
            summary_lines.append(f"⚠️ {failed_nodes} nodes need attention")

        return sanitize("\n".join(summary_lines))

    yield FunctionInfo.from_fn(
        _cluster_gpu_status,
        description=
        "Check GPU status across cluster compute nodes. Optional: nodes=all|IP1,IP2|IP1-5|hostname1,hostname2")


class ClusterGPUEnableHealthConfig(FunctionBaseConfig, name="cluster_gpu_enable_health"):
    cluster_host: str = Field(default=DEFAULT_CLUSTER_HOST, description="Cluster head hostname/IP")
    cluster_user: str = Field(default=DEFAULT_CLUSTER_USER, description="SSH username for cluster access")
    ssh_timeout: int = Field(default=DEFAULT_SSH_TIMEOUT, description="SSH timeout in seconds")


@register_function(config_type=ClusterGPUEnableHealthConfig)
async def cluster_gpu_enable_health(config: ClusterGPUEnableHealthConfig, builder: Builder):

    async def _cluster_gpu_enable_health(text: str) -> str:
        """Enable DCGM health monitoring across cluster nodes"""
        opts = parse_kv(text)
        node_spec = opts.get("nodes", "all")
        systems = opts.get("systems", "all")

        # Map system names to DCGM flags
        system_map = {
            "all": "a", "pcie": "p", "memory": "m", "inforom": "i", "thermal": "t", "nvlink": "n", "power": "t"
        }
        flags = system_map.get(systems.lower(), "a")

        # Discover and parse nodes
        all_nodes = await discover_cluster_nodes(config.cluster_host, config.cluster_user)
        target_nodes = parse_node_spec(node_spec, all_nodes)

        if not target_nodes:
            return f"❌ No nodes matched specification: {node_spec}"

        logger.info("Enabling DCGM health on %d nodes with systems=%s", len(target_nodes), systems)

        # Enable health monitoring command
        health_cmd = (f'if command -v dcgmi >/dev/null 2>&1; then '
                      f'dcgmi health -g 0 -s {flags} 2>/dev/null && '
                      f'echo "Enabled DCGM health monitoring: {systems}"; '
                      f'else echo "DCGM not available"; fi')

        results = await execute_on_cluster(target_nodes,
                                           health_cmd,
                                           config.cluster_user,
                                           timeout=config.ssh_timeout + 15)

        # Summarize results
        summary_lines = [f"🏥 DCGM Health Monitoring Enable ({systems} systems)"]
        summary_lines.append("=" * 50)

        success_count = 0
        for node_ip in sorted(results.keys()):
            result = results[node_ip]
            hostname = result["hostname"]

            if result["success"] and "Enabled DCGM health" in result["stdout"]:
                summary_lines.append(f"✅ {hostname} ({node_ip}): Health monitoring enabled")
                success_count += 1
            elif "DCGM not available" in result["stdout"]:
                summary_lines.append(f"⚠️ {hostname} ({node_ip}): DCGM not installed")
            else:
                error_msg = result["stderr"] or result["stdout"] or "Unknown error"
                summary_lines.append(f"❌ {hostname} ({node_ip}): {error_msg}")

        summary_lines.append("=" * 50)
        summary_lines.append(f"📊 Health monitoring enabled on {success_count}/{len(target_nodes)} nodes")
        summary_lines.append("💡 Wait ~60 seconds before checking health status for data collection")

        return sanitize("\n".join(summary_lines))

    yield FunctionInfo.from_fn(
        _cluster_gpu_enable_health,
        description=
        "Enable DCGM health monitoring across cluster. Optional: nodes=all|spec, systems=all|pcie|memory|thermal|nvlink"
    )


class ClusterGPUHealthCheckConfig(FunctionBaseConfig, name="cluster_gpu_health_check"):
    cluster_host: str = Field(default=DEFAULT_CLUSTER_HOST, description="Cluster head hostname/IP")
    cluster_user: str = Field(default=DEFAULT_CLUSTER_USER, description="SSH username for cluster access")
    ssh_timeout: int = Field(default=DEFAULT_SSH_TIMEOUT, description="SSH timeout in seconds")


@register_function(config_type=ClusterGPUHealthCheckConfig)
async def cluster_gpu_health_check(config: ClusterGPUHealthCheckConfig, builder: Builder):

    async def _cluster_gpu_health_check(text: str) -> str:
        """Check DCGM health status across cluster nodes"""
        opts = parse_kv(text)
        node_spec = opts.get("nodes", "all")
        output = opts.get("output", "text")

        # Discover and parse nodes
        all_nodes = await discover_cluster_nodes(config.cluster_host, config.cluster_user)
        target_nodes = parse_node_spec(node_spec, all_nodes)

        if not target_nodes:
            return f"❌ No nodes matched specification: {node_spec}"

        logger.info("Checking DCGM health on %d nodes", len(target_nodes))

        # Health check command
        health_cmd = ('if command -v dcgmi >/dev/null 2>&1; then '
                      'dcgmi health -g 0 -c 2>/dev/null; '
                      'else echo "DCGM not available"; fi')

        results = await execute_on_cluster(target_nodes,
                                           health_cmd,
                                           config.cluster_user,
                                           timeout=config.ssh_timeout + 20)

        if output == "json":
            return sanitize(json.dumps(results, indent=2))

        # Parse health results and create summary
        summary_lines = [f"🏥 Cluster GPU Health Status ({len(target_nodes)} nodes)"]
        summary_lines.append("=" * 50)

        total_gpus = 0
        healthy_gpus = 0
        warning_gpus = 0
        critical_gpus = 0
        nodes_with_issues = []

        for node_ip in sorted(results.keys()):
            result = results[node_ip]
            hostname = result["hostname"]

            if not result["success"] or "DCGM not available" in result["stdout"]:
                summary_lines.append(f"⚠️ {hostname} ({node_ip}): DCGM unavailable")
                continue

            stdout = result["stdout"]

            # Parse DCGM health output
            node_gpus = 0
            node_healthy = 0
            node_warning = 0
            node_critical = 0
            issues = []

            current_gpu = None
            for line in stdout.splitlines():
                # Look for GPU health status
                gpu_match = re.search(r'GPU ID:\s*(\d+).*?(OK|Warning|Error)', line)
                if gpu_match:
                    gpu_id, status = gpu_match.groups()
                    current_gpu = gpu_id
                    node_gpus += 1

                    if status == "OK":
                        node_healthy += 1
                    elif status == "Warning":
                        node_warning += 1
                    else:  # Error
                        node_critical += 1

                # Look for specific issues
                elif current_gpu and " - " in line:
                    issue = line.replace("|", "").strip()
                    if issue:
                        issues.append(f"GPU{current_gpu}: {issue}")

            total_gpus += node_gpus
            healthy_gpus += node_healthy
            warning_gpus += node_warning
            critical_gpus += node_critical

            # Node status summary
            if node_critical > 0:
                status_icon = "🔴"
                nodes_with_issues.append(hostname)
            elif node_warning > 0:
                status_icon = "🟡"
                nodes_with_issues.append(hostname)
            elif node_healthy > 0:
                status_icon = "🟢"
            else:
                status_icon = "⚪"  # No health data yet

            summary_lines.append(
                f"{status_icon} {hostname} ({node_ip}): "
                f"{node_gpus} GPUs ({node_healthy} OK, {node_warning} Warning, {node_critical} Critical)")

            # Show critical issues
            if issues and len(issues) <= 3:  # Show up to 3 issues per node
                for issue in issues:
                    summary_lines.append(f"    ⚠️ {issue}")
            elif issues:
                summary_lines.append(f"    ⚠️ {len(issues)} issues detected")

        # Overall cluster summary
        summary_lines.append("=" * 50)
        summary_lines.append(f"📊 Cluster Health: {total_gpus} total GPUs")
        summary_lines.append(f"   🟢 Healthy: {healthy_gpus}")
        summary_lines.append(f"   🟡 Warning: {warning_gpus}")
        summary_lines.append(f"   🔴 Critical: {critical_gpus}")

        if nodes_with_issues:
            summary_lines.append(f"⚠️ Nodes needing attention: {', '.join(nodes_with_issues)}")

        if total_gpus == 0:
            summary_lines.append("💡 No health data found. Enable health monitoring first, then wait ~60s")

        return sanitize("\n".join(summary_lines))

    yield FunctionInfo.from_fn(
        _cluster_gpu_health_check,
        description="Check DCGM health status across cluster nodes. Optional: nodes=all|spec, output=text|json")


class ClusterGPUDiagnosticsConfig(FunctionBaseConfig, name="cluster_gpu_diagnostics"):
    cluster_host: str = Field(default=DEFAULT_CLUSTER_HOST, description="Cluster head hostname/IP")
    cluster_user: str = Field(default=DEFAULT_CLUSTER_USER, description="SSH username for cluster access")
    ssh_timeout: int = Field(default=DEFAULT_SSH_TIMEOUT, description="SSH timeout in seconds")
    dcgm_timeout: int = Field(default=DEFAULT_DCGM_TIMEOUT, description="DCGM diagnostics timeout in seconds")


@register_function(config_type=ClusterGPUDiagnosticsConfig)
async def cluster_gpu_diagnostics(config: ClusterGPUDiagnosticsConfig, builder: Builder):

    async def _cluster_gpu_diagnostics(text: str) -> str:
        """Run DCGM diagnostics across cluster nodes"""
        opts = parse_kv(text)
        node_spec = opts.get("nodes", "all")
        level = opts.get("level", "r2").lower()
        output = opts.get("output", "text")

        # Discover and parse nodes
        all_nodes = await discover_cluster_nodes(config.cluster_host, config.cluster_user)
        target_nodes = parse_node_spec(node_spec, all_nodes)

        if not target_nodes:
            return f"❌ No nodes matched specification: {node_spec}"

        logger.info("Running DCGM diagnostics level %s on %d nodes", level, len(target_nodes))

        # Build diagnostics command
        if level == "nvbandwidth":
            diag_cmd = ('if command -v dcgmi >/dev/null 2>&1; then '
                        'echo "Running NVBandwidth test..."; '
                        'dcgmi diag -r nvbandwidth -p nvbandwidth.is_allowed=true 2>/dev/null; '
                        'else echo "DCGM not available"; fi')
            timeout = config.dcgm_timeout + 60  # NVBandwidth takes longer
        else:
            diag_cmd = (f'if command -v dcgmi >/dev/null 2>&1; then '
                        f'echo "Running DCGM diagnostics level {level}..."; '
                        f'dcgmi diag -g 0 -r {level} 2>/dev/null; '
                        f'else echo "DCGM not available"; fi')
            timeout = config.dcgm_timeout

        results = await execute_on_cluster(target_nodes, diag_cmd, config.cluster_user, timeout)

        if output == "json":
            return sanitize(json.dumps(results, indent=2))

        # Process diagnostics results
        summary_lines = [f"🔬 Cluster DCGM Diagnostics (Level: {level})"]
        summary_lines.append("=" * 60)

        passed_nodes = 0
        failed_nodes = 0

        for node_ip in sorted(results.keys()):
            result = results[node_ip]
            hostname = result["hostname"]

            if not result["success"] or "DCGM not available" in result["stdout"]:
                summary_lines.append(f"⚠️ {hostname} ({node_ip}): DCGM unavailable")
                continue

            stdout = result["stdout"]

            # Parse diagnostic results - look for PASS/FAIL patterns
            if "PASS" in stdout and "FAIL" not in stdout:
                summary_lines.append(f"✅ {hostname} ({node_ip}): All tests PASSED")
                passed_nodes += 1
            elif "FAIL" in stdout:
                summary_lines.append(f"❌ {hostname} ({node_ip}): Some tests FAILED")
                failed_nodes += 1

                # Extract failure details (first few lines)
                fail_lines = [line for line in stdout.splitlines() if "FAIL" in line][:3]
                for fail_line in fail_lines:
                    summary_lines.append(f"    🔴 {fail_line.strip()}")
            else:
                # Check for other completion indicators
                if "completed" in stdout.lower() or "finished" in stdout.lower():
                    summary_lines.append(f"✅ {hostname} ({node_ip}): Diagnostics completed")
                    passed_nodes += 1
                else:
                    summary_lines.append(f"⚠️ {hostname} ({node_ip}): Diagnostics status unclear")

            # Add truncated output for context (limit to avoid overwhelming output)
            if len(stdout) > 500:
                preview = stdout[:400] + "\n... [truncated] ..."
            else:
                preview = stdout
            summary_lines.append(f"    📋 Output: {preview.replace(chr(10), ' ')[:200]}")

        # Overall summary
        summary_lines.append("=" * 60)
        summary_lines.append(f"📊 Diagnostics Summary: {passed_nodes} passed, {failed_nodes} failed")

        if failed_nodes > 0:
            summary_lines.append("⚠️ Check failed nodes for hardware issues")
            summary_lines.append("💡 Consider running higher diagnostic levels (r3, r4) for detailed analysis")

        return sanitize("\n".join(summary_lines))

    yield FunctionInfo.from_fn(
        _cluster_gpu_diagnostics,
        description=
        "Run DCGM diagnostics across cluster. Optional: nodes=all|spec, level=r1|r2|r3|r4|nvbandwidth, output=text|json"
    )


class ClusterDeployMonitoringConfig(FunctionBaseConfig, name="cluster_deploy_monitoring"):
    cluster_host: str = Field(default=DEFAULT_CLUSTER_HOST, description="Cluster head hostname/IP")
    cluster_user: str = Field(default=DEFAULT_CLUSTER_USER, description="SSH username for cluster access")
    ssh_timeout: int = Field(default=DEFAULT_SSH_TIMEOUT, description="SSH timeout in seconds")


@register_function(config_type=ClusterDeployMonitoringConfig)
async def cluster_deploy_monitoring(config: ClusterDeployMonitoringConfig, builder: Builder):

    async def _cluster_deploy_monitoring(text: str) -> str:
        """Deploy dcgm-exporter monitoring across cluster nodes"""
        opts = parse_kv(text)
        node_spec = opts.get("nodes", "all")
        force = opts.get("force", "false").lower() in ("true", "1", "yes")

        # Discover and parse nodes
        all_nodes = await discover_cluster_nodes(config.cluster_host, config.cluster_user)
        target_nodes = parse_node_spec(node_spec, all_nodes)

        if not target_nodes:
            return f"❌ No nodes matched specification: {node_spec}"

        logger.info("Deploying monitoring to %d nodes (force=%s)", len(target_nodes), force)

        # Build deployment command
        deploy_cmd = ('if command -v docker >/dev/null 2>&1; then '
                      f'{"docker rm -f dcgm-exporter 2>/dev/null; " if force else ""}'
                      'if ! docker ps --format "{{.Names}}" | grep -q "^dcgm-exporter$"; then '
                      'docker run -d --restart unless-stopped --name dcgm-exporter --net=host --gpus all '
                      'nvcr.io/nvidia/k8s/dcgm-exporter:latest >/dev/null 2>&1 && '
                      'echo "dcgm-exporter deployed successfully" || echo "dcgm-exporter deployment failed"; '
                      'else echo "dcgm-exporter already running"; fi; '
                      'else echo "Docker not available"; fi')

        results = await execute_on_cluster(target_nodes,
                                           deploy_cmd,
                                           config.cluster_user,
                                           timeout=config.ssh_timeout + 60)  # Extra time for Docker pulls

        # Process deployment results
        summary_lines = [f"📊 Cluster Monitoring Deployment ({len(target_nodes)} nodes)"]
        summary_lines.append("=" * 60)

        success_count = 0
        already_running = 0
        failed_count = 0

        for node_ip in sorted(results.keys()):
            result = results[node_ip]
            hostname = result["hostname"]
            stdout = result["stdout"]

            if "deployed successfully" in stdout:
                summary_lines.append(f"✅ {hostname} ({node_ip}): dcgm-exporter deployed")
                success_count += 1
            elif "already running" in stdout:
                summary_lines.append(f"ℹ️ {hostname} ({node_ip}): dcgm-exporter already running")
                already_running += 1
            elif "Docker not available" in stdout:
                summary_lines.append(f"⚠️ {hostname} ({node_ip}): Docker not available")
                failed_count += 1
            else:
                error_msg = result["stderr"] or result["stdout"] or "Unknown error"
                summary_lines.append(f"❌ {hostname} ({node_ip}): {error_msg}")
                failed_count += 1

        # Overall summary
        summary_lines.append("=" * 60)
        summary_lines.append(f"📊 Deployment Results:")
        summary_lines.append(f"   ✅ Newly deployed: {success_count}")
        summary_lines.append(f"   ℹ️ Already running: {already_running}")
        summary_lines.append(f"   ❌ Failed: {failed_count}")

        total_monitoring = success_count + already_running
        if total_monitoring > 0:
            summary_lines.append("")
            summary_lines.append(f"🚀 Monitoring active on {total_monitoring}/{len(target_nodes)} nodes")
            summary_lines.append("💡 Metrics available at: http://<NODE_IP>:9400/metrics")
            summary_lines.append("📊 Configure Prometheus to scrape all node:9400 endpoints")

        if failed_count > 0:
            summary_lines.append("⚠️ Check failed nodes for Docker/GPU access issues")

        return sanitize("\n".join(summary_lines))

    yield FunctionInfo.from_fn(
        _cluster_deploy_monitoring,
        description="Deploy dcgm-exporter monitoring across cluster. Optional: nodes=all|spec, force=true|false")


class ClusterCreateDashboardConfig(FunctionBaseConfig, name="cluster_create_dashboard"):
    cluster_host: str = Field(default=DEFAULT_CLUSTER_HOST, description="Cluster head hostname/IP")
    cluster_user: str = Field(default=DEFAULT_CLUSTER_USER, description="SSH username for cluster access")


@register_function(config_type=ClusterCreateDashboardConfig)
async def cluster_create_dashboard(config: ClusterCreateDashboardConfig, builder: Builder):

    async def _cluster_create_dashboard(text: str) -> str:
        """Create cluster-wide Grafana dashboard"""
        opts = parse_kv(text)
        name = opts.get("name", "Cluster GPU Overview")
        refresh = opts.get("refresh", "30s")

        # Import Grafana helpers from the original module
        try:
            # Get list of cluster nodes for dashboard targets
            all_nodes = await discover_cluster_nodes(config.cluster_host, config.cluster_user)

            if not all_nodes:
                return "❌ No cluster nodes discovered for dashboard creation"

            # Build Prometheus targets list
            targets = [f"{node.ip}:9400" for node in all_nodes]

            # Create multi-node Prometheus configuration
            prom_config = {
                "global": {
                    "scrape_interval": "15s"
                },
                "scrape_configs": [{
                    "job_name": "cluster-dcgm", "static_configs": [{
                        "targets": targets
                    }]
                }]
            }

            dashboard_json = {
                "title": name,
                "timezone": "browser",
                "refresh": refresh,
                "panels": [{
                    "type": "stat",
                    "title": "Total GPUs",
                    "gridPos": {
                        "h": 4, "w": 6, "x": 0, "y": 0
                    },
                    "targets": [{
                        "refId": "A", "expr": "count(DCGM_FI_DEV_GPU_TEMP)", "legendFormat": "GPUs"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "color": {
                                "mode": "thresholds"
                            }
                        }
                    }
                },
                           {
                               "type":
                                   "stat",
                               "title":
                                   "Active Nodes",
                               "gridPos": {
                                   "h": 4, "w": 6, "x": 6, "y": 0
                               },
                               "targets": [{
                                   "refId": "A",
                                   "expr": "count(count by (instance) (DCGM_FI_DEV_GPU_TEMP))",
                                   "legendFormat": "Nodes"
                               }]
                           },
                           {
                               "type": "timeseries",
                               "title": "GPU Temperatures by Node",
                               "gridPos": {
                                   "h": 8, "w": 24, "x": 0, "y": 4
                               },
                               "targets": [{
                                   "refId": "A",
                                   "expr": "DCGM_FI_DEV_GPU_TEMP",
                                   "legendFormat": "{{instance}} GPU{{gpu}}"
                               }],
                               "fieldConfig": {
                                   "defaults": {
                                       "unit": "celsius",
                                       "thresholds": {
                                           "steps": [{
                                               "color": "green", "value": None
                                           }, {
                                               "color": "yellow", "value": 70
                                           }, {
                                               "color": "red", "value": 85
                                           }]
                                       }
                                   }
                               }
                           },
                           {
                               "type": "timeseries",
                               "title": "GPU Utilization by Node",
                               "gridPos": {
                                   "h": 8, "w": 24, "x": 0, "y": 12
                               },
                               "targets": [{
                                   "refId": "A",
                                   "expr": "DCGM_FI_DEV_GPU_UTIL",
                                   "legendFormat": "{{instance}} GPU{{gpu}}"
                               }],
                               "fieldConfig": {
                                   "defaults": {
                                       "unit": "percent", "max": 100
                                   }
                               }
                           }],
                "templating": {
                    "list": []
                },
                "time": {
                    "from": "now-1h", "to": "now"
                }
            }

            summary_lines = [
                f"📊 Created cluster dashboard: {name}",
                f"🎯 Monitoring {len(all_nodes)} nodes ({len(targets)} targets)",
                "",
                "📋 Dashboard includes:",
                "   • Total GPU count across cluster",
                "   • Active node count",
                "   • GPU temperatures by node",
                "   • GPU utilization by node",
                "",
                "🔧 Prometheus configuration needed:",
                f"   job_name: cluster-dcgm",
                f"   targets: {targets[:3]}..." if len(targets) > 3 else f"   targets: {targets}",
                "",
                f"🌐 Dashboard JSON created for import into Grafana",
                f"📊 Refresh interval: {refresh}"
            ]

            return sanitize("\n".join(summary_lines))

        except Exception as e:
            return f"❌ Dashboard creation failed: {str(e)}"

    yield FunctionInfo.from_fn(
        _cluster_create_dashboard,
        description="Create cluster-wide Grafana dashboard. Optional: name=DashboardName, refresh=30s")


print("✅ Cluster DCGM tools registered successfully")
