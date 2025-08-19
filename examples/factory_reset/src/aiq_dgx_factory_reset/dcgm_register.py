# SPDX-FileCopyrightText: Copyright (c) 2024-2025,
# NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import re
import shlex
import subprocess
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from aiq.builder.builder import Builder
from aiq.builder.function_info import FunctionInfo
from aiq.cli.register_workflow import register_function
from aiq.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)

GROUP_NAME = "GPU_ALL"  # dedicated DCGM group name for all GPUs


def run(cmd: str, timeout: Optional[int] = None) -> str:
    return subprocess.check_output(shlex.split(cmd), text=True, timeout=timeout).strip()


def try_run(cmd: str, timeout: Optional[int] = None) -> str:
    try:
        return run(cmd, timeout=timeout)
    except Exception as e:
        return f"ERROR: {e}"


def get_gpu_ids() -> List[str]:
    out = try_run("dcgmi discovery -l")
    return re.findall(r"^\|\s*(\d+)\s*\| Name:\s*NVIDIA", out, flags=re.M)


def ensure_all_group() -> str:
    # Prefer the system group with all supported GPUs
    return "0"


def parse_kv(text: Optional[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not text:
        return out
    for token in text.split():
        if "=" in token:
            k, v = token.split("=", 1)
            out[k.strip().lower()] = v.strip()
    return out


def human_to_flags(s: str) -> str:
    if not s:
        return ""
    s = s.lower().replace(",", " ").replace("/", " ")
    words = s.split()
    mapping = {
        "a": "a",
        "all": "a",
        "p": "p",
        "pcie": "p",
        "m": "m",
        "mem": "m",
        "memory": "m",
        "i": "i",
        "inforom": "i",
        "t": "t",
        "thermal": "t",
        "power": "t",
        "n": "n",
        "nvlink": "n",
    }
    flags = []
    for w in words:
        if w in mapping and mapping[w] not in flags:
            flags.append(mapping[w])
        elif len(w) == 1 and w in mapping and mapping[w] not in flags:
            flags.append(mapping[w])
    return "".join(flags)


def parse_health_report(txt: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    current_gpu: Optional[str] = None
    for line in txt.splitlines():
        m = re.search(r"\|\s*GPU ID:\s*(\d+)\s*\|\s*(OK|Warning|Error)", line)
        if m:
            gpu_id = m.group(1)  # Extract to variable with clear type
            current_gpu = gpu_id
            result[gpu_id] = {"state": m.group(2), "issues": []}
            continue
        if current_gpu is not None and " - " in line:
            issue = line.replace("|", "").strip()
            if issue:
                result[current_gpu]["issues"].append(issue)
    return result


def _to_int(s: Any) -> Optional[int]:
    try:
        return int(float(str(s)))
    except Exception:
        return None


def _to_float(s: Any) -> Optional[float]:
    try:
        return float(str(s))
    except Exception:
        return None


def collect_metrics() -> Dict[str, Any]:
    metrics: Dict[str, Any] = {}

    smi = try_run(
        "nvidia-smi --query-gpu=index,temperature.gpu,power.draw,clocks.sm,utilization.gpu,utilization.memory "
        "--format=csv,noheader,nounits")
    for line in smi.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 6:
            continue
        idx, temp, power, smclk, ug, um = parts
        metrics[idx] = {
            "tempC": _to_int(temp),
            "powerW": _to_float(power),
            "smClockMHz": _to_int(smclk),
            "util_gpu": _to_int(ug),
            "util_mem": _to_int(um),
        }

    dmon = try_run("dcgmi dmon -e 1001,1004,1005 -d 1000 -c 1")
    for r in dmon.splitlines():
        if r.strip().startswith("GPU "):
            parts = r.split()
            if len(parts) >= 5:
                gid = parts[1]
                gr = _to_float(parts[2])
                tens = _to_float(parts[3])
                dram = _to_float(parts[4])
                metrics.setdefault(gid, {})
                metrics[gid].update({"gract": gr, "tensor": tens, "dram": dram})
    return metrics


class GPUStatusToolConfig(FunctionBaseConfig, name="gpu_status"):
    pass


@register_function(config_type=GPUStatusToolConfig)
async def gpu_status(config: GPUStatusToolConfig, builder: Builder):

    async def _gpu_status(text: str) -> str:
        opts = parse_kv(text)
        # Default to compact text to avoid oversized LLM observations
        output = opts.get("output", "text")

        try:
            gid = ensure_all_group()
        except Exception as e:
            return f"Failed to ensure DCGM group: {e}"

        health_txt = try_run(f"dcgmi health -g {gid} -c")
        health = parse_health_report(health_txt)
        metrics = collect_metrics()

        # Check if health data is available
        note = None
        if not health:
            note = "No health results yet. If you just enabled watches, wait ~60s and retry."

        summary = {
            "total": len(get_gpu_ids()),
            "critical": sum(1 for v in health.values() if v.get("state") == "Error"),
            "warning": sum(1 for v in health.values() if v.get("state") == "Warning"),
            "ok": sum(1 for v in health.values() if v.get("state") == "OK"),
        }
        data = {"summary": summary, "gpus": {}}
        for gpu in sorted(set(list(health.keys()) + list(metrics.keys())), key=lambda x: int(x)):
            data["gpus"][gpu] = {"health": health.get(gpu, {}), "metrics": metrics.get(gpu, {})}

        # Build compact text by default
        if output == "text":
            lines = [f"GPUs: {summary['ok']} OK, {summary['warning']} Warning, {summary['critical']} Critical"]
            if note:
                lines.append(f"Note: {note}")
            for g, info in data["gpus"].items():
                h = info["health"].get("state", "Unknown") or "Unknown"
                m = info["metrics"]
                t = m.get("tempC")
                p = m.get("powerW")
                ug = m.get("util_gpu")
                issues = "; ".join(info["health"].get("issues", [])) or "-"
                lines.append(f"GPU {g}: {h} | temp {t}C | power {p}W | util {ug}% | issues: {issues}")
            txt = "\n".join(lines)
            # hard cap to keep LLM happy
            MAXLEN = 6000
            return txt if len(txt) <= MAXLEN else (txt[:MAXLEN] + "\n...truncated...")
        # JSON on demand only
        return json.dumps(data)

    yield FunctionInfo.from_fn(
        _gpu_status,
        description=("Summarize per-GPU health and usage on this node. "
                     "Optional input: 'output=text' (default) or 'output=json'."),
    )


class GPUDiagnosticsToolConfig(FunctionBaseConfig, name="gpu_run_diagnostics"):
    pass


@register_function(config_type=GPUDiagnosticsToolConfig)
async def gpu_run_diagnostics(config: GPUDiagnosticsToolConfig, builder: Builder):

    async def _gpu_run_diagnostics(text: str) -> str:
        opts = parse_kv(text)
        level = opts.get("level", "r2").lower()
        # Default to text; JSON can be huge on r3/r4
        output = opts.get("output", "text")
        timeout = int(opts["timeout"]) if "timeout" in opts else None

        try:
            gid = ensure_all_group()
        except Exception as e:
            return f"Failed to ensure DCGM group: {e}"

        if level == "nvbandwidth":
            cmd = "dcgmi diag -r nvbandwidth -p nvbandwidth.is_allowed=true -j"
        else:
            cmd = f"dcgmi diag -g {gid} -r {level} -j"

        raw = try_run(cmd, timeout=timeout)
        if output == "text":
            # keep some context, but cap size
            MAXLEN = 6000
            if len(raw) <= MAXLEN:
                return raw or "No diagnostic output."
            # Try to preserve the summary tail if present
            head = raw[:3000]
            tail = raw[-2500:]
            return head + "\n...truncated...\n" + tail

        # JSON on demand, compact and capped
        json_obj = None
        for line in raw.splitlines():
            if line.strip().startswith("{"):
                try:
                    json_obj = json.loads(line.strip())
                    break
                except Exception:
                    pass
        payload = json.dumps(json_obj if json_obj is not None else {"raw": raw})
        return payload[:120000]  # cap to ~120 KB

    yield FunctionInfo.from_fn(
        _gpu_run_diagnostics,
        description=(
            "Run DCGM diagnostics on this node. "
            "Optional input: 'level=r1|r2|r3|r4|nvbandwidth' (default r2), 'output=text|json', 'timeout=SECONDS'."),
    )


class GPUHealthEnableToolConfig(FunctionBaseConfig, name="gpu_enable_health"):
    pass


@register_function(config_type=GPUHealthEnableToolConfig)
async def gpu_enable_health(config: GPUHealthEnableToolConfig, builder: Builder):

    async def _gpu_enable_health(text: str) -> str:
        opts = parse_kv(text)
        systems_input = opts.get("systems", "a")  # default to all watches
        flags = human_to_flags(systems_input) or "a"
        gid = ensure_all_group()

        set_out = try_run(f"dcgmi health -g {gid} -s {flags}")
        # Also fetch watch state to confirm and keep output non-empty/small
        fetch_json = try_run(f"dcgmi health -g {gid} -f -j")

        msg = []
        msg.append(set_out or f"Enabled health systems: {flags}")
        if fetch_json and len(fetch_json) > 2000:
            fetch_json = fetch_json[:2000] + "...truncated..."
        if fetch_json:
            msg.append(fetch_json)
        msg.append("Note: watched systems with (*) need ~60 seconds before first check (-c) shows results.")
        return "\n".join(msg)

    yield FunctionInfo.from_fn(
        _gpu_enable_health,
        description="Enable DCGM background health checks. Optional: systems=a|p|m|i|t|n or words like 'pcie nvlink'.",
    )


class GPUNvlinkStatusToolConfig(FunctionBaseConfig, name="gpu_nvlink_status"):
    pass


@register_function(config_type=GPUNvlinkStatusToolConfig)
async def gpu_nvlink_status(config: GPUNvlinkStatusToolConfig, builder: Builder):

    async def _gpu_nvlink_status(text: str) -> str:
        opts = parse_kv(text)
        output = opts.get("output", "text")

        raw = try_run("dcgmi nvlink --link-status")
        if output == "text" or not raw:
            return raw or "No NVLink status output."

        summary = {"gpus": {}, "nvswitches": {}}
        section = None
        current = None
        for line in raw.splitlines():
            if line.strip().startswith("GPUs:"):
                section = "gpus"
                continue
            if line.strip().startswith("NvSwitches:"):
                section = "nvswitches"
                continue
            m = re.match(r"\s*gpuId\s+(\d+):", line)
            if section == "gpus" and m:
                current = f"GPU{m.group(1)}"
                summary["gpus"][current] = []
                continue
            m = re.match(r"\s*physicalId\s+(\d+):", line)
            if section == "nvswitches" and m:
                current = f"SW{m.group(1)}"
                summary["nvswitches"][current] = []
                continue
            tokens = line.strip().split()
            if current and tokens and set(tokens).issubset({"U", "D", "X", "_"}):
                summary["gpus" if section == "gpus" else "nvswitches"][current] = tokens

        return json.dumps(summary)

    yield FunctionInfo.from_fn(
        _gpu_nvlink_status,
        description=("Show NVLink link status (U/D/X/_). Optional input: 'output=json' to return a parsed summary."),
    )


# class GPUOrchestrateToolConfig(FunctionBaseConfig, name="gpu_orchestrate"):
#     pass

# @register_function(config_type=GPUOrchestrateToolConfig)
# async def gpu_orchestrate(config: GPUOrchestrateToolConfig, builder: Builder):
#     """
#     Params (key=value): enable_health=true|false, wait_for_health=true|false,
#     include_nvlink=true|false, diag=r1|r2|r3|r4|nvbandwidth|none,
#     output=text|json, systems=a|p|m|i|t|n (default a)
#     """
#     import time

#     async def _gpu_orchestrate(text: str) -> str:
#         opts = parse_kv(text)
#         enable_health = opts.get("enable_health", "false").lower() in ("true", "1", "yes", "y")
#         wait_for_health = opts.get("wait_for_health", "false").lower() in ("true", "1", "yes", "y")
#         include_nvlink = opts.get("include_nvlink", "false").lower() in ("true", "1", "yes", "y")
#         diag_level = opts.get("diag", "").lower()
#         output = opts.get("output", "text")
#         systems_input = opts.get("systems", "a")
#         flags = human_to_flags(systems_input) or "a"

#         gid = ensure_all_group()
#         notes = []

#         if enable_health:
#             notes.append(try_run(f"dcgmi health -g {gid} -s {flags}") or f"Enabled health: {flags}")
#             if wait_for_health:
#                 time.sleep(65)  # warm-up

#         health_txt = try_run(f"dcgmi health -g {gid} -c")
#         health = parse_health_report(health_txt)
#         metrics = collect_metrics()

#         diag_out = None
#         if diag_level:
#             if diag_level == "nvbandwidth":
#                 diag_out = try_run("dcgmi diag -r nvbandwidth -p nvbandwidth.is_allowed=true -j", timeout=900)
#             else:
#                 diag_out = try_run(f"dcgmi diag -g {gid} -r {diag_level} -j", timeout=1800)
#             if diag_out and len(diag_out) > 4000:
#                 diag_out = diag_out[:4000] + "...truncated..."

#         nvlink_raw = try_run("dcgmi nvlink --link-status") if include_nvlink else None

#         summary = {
#             "total": len(get_gpu_ids()),
#             "critical": sum(1 for v in health.values() if v.get("state") == "Error"),
#             "warning": sum(1 for v in health.values() if v.get("state") == "Warning"),
#             "ok": sum(1 for v in health.values() if v.get("state") == "OK"),
#         }
#         data = {"summary": summary, "gpus": {}}
#         for g in sorted(set(list(health.keys()) + list(metrics.keys())), key=lambda x: int(x)):
#             data["gpus"][g] = {"health": health.get(g, {}), "metrics": metrics.get(g, {})}
#         if diag_out:
#             data["diag"] = diag_out
#         if nvlink_raw:
#             data["nvlink"] = nvlink_raw

#         if output == "json":
#             return json.dumps(data)

#         lines = [f"GPUs: {summary['ok']} OK, {summary['warning']} Warning, {summary['critical']} Critical"]
#         if not health:
#             lines.append("Note: no health results yet. If watches were just enabled, allow ~60s.")
#         for g, info in data["gpus"].items():
#             h = info["health"].get("state", "Unknown") or "Unknown"
#             m = info["metrics"]
#             issues = '; '.join(info['health'].get('issues', [])) or '-'
#             temp = m.get('tempC')
#             power = m.get('powerW')
#             util = m.get('util_gpu')
#             lines.append(f"GPU {g}: {h} | temp {temp}C | power {power}W | util {util}% | issues: {issues}")
#         if diag_out:
#             lines.append("\nDiagnostics (raw/truncated):")
#             lines.append(diag_out)
#         if nvlink_raw:
#             lines.append("\nNVLink Link Status:")
#             lines.append(nvlink_raw)
#         if notes:
#             lines.append("\nNotes:")
#             lines.extend(notes)

#         txt = "\n".join(lines)
#         return txt if len(txt) <= 6000 else (txt[:6000] + "\n...truncated...")

#     yield FunctionInfo.from_fn(
#         _gpu_orchestrate,
#         description="Orchestrate multiple DCGM steps in one call (enable health, wait, status, optional diag, NVLink).",
#     )
