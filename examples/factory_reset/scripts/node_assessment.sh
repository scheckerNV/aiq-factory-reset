#!/bin/bash
# node_assessment.sh - Comprehensive BCM node assessment (OS/BIOS/Firmware/BMC/Health)

set -euo pipefail

OUTPUT_DIR="/tmp/node_assessment_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "Starting comprehensive node assessment..."
echo "Output directory: $OUTPUT_DIR"

run_cmd() {
  local cmd="$1"
  local output_file="$2"
  local description="$3"
  echo "[$description] Running: $cmd"
  {
    echo "Command: $cmd"
    echo "Description: $description"
    echo "Timestamp: $(date)"
    echo "====================================="
    echo
    eval "$cmd"
    echo
  } > "$OUTPUT_DIR/$output_file" 2>&1 || true
}

# 1) Basic node information
run_cmd 'cmsh -c "device status"' \
        "01_device_status.txt" \
        "Overall device status"

run_cmd 'cmsh -c "device list -f name,status,mac,ip,category,softwareimage"' \
        "02_device_list.txt" \
        "Detailed device information"

# GPU information across nodes (for reader compatibility)
run_cmd 'cmsh -c "device foreach * (nvidia-smi -L)"' \
        "10_gpu_list.txt" \
        "Per-node GPU list"

run_cmd 'cmsh -c "device foreach * (nvidia-smi -q)"' \
        "11_gpu_info.txt" \
        "Per-node detailed GPU info"

# 2) BCM and package versions
run_cmd 'cmsh -c "main; versioninfo"' \
        "16_bcm_version_info.txt" \
        "BCM version information"

run_cmd 'cm-package-release-info -f cmdaemon' \
        "17_pkg_cmdaemon.txt" \
        "BCM cmdaemon package release info"

run_cmd 'cm-package-release-info -f cluster-tools' \
        "18_pkg_cluster_tools.txt" \
        "BCM cluster-tools package release info"

# Fetch list of nodes for per-node commands
NODES=$(cmsh -c "device list -f name --category node" 2>/dev/null | tail -n +2)

# 3) OS version on nodes
{
  echo "Per-node /etc/os-release"
  for n in $NODES; do
    echo "--- $n ---"
    cmsh -c "device use $n; shell cat /etc/os-release" 2>&1 || cmsh -c "device foreach $n (cat /etc/os-release)"
    echo
  done
} > "$OUTPUT_DIR/19_os_release.txt"

# 4) BIOS information per node
{
  echo "Per-node dmidecode BIOS info"
  for n in $NODES; do
    echo "--- $n ---"
    cmsh -c "device use $n; shell dmidecode -t bios" 2>&1 || cmsh -c "device foreach $n (dmidecode -t bios)"
    echo
  done
} > "$OUTPUT_DIR/20_bios_info.txt"

# BIOS settings status per node
{
  echo "Per-node BIOS settings status"
  for n in $NODES; do
    echo "--- $n ---"
    cmsh -c "device use $n; biossettings; status" 2>&1
    echo
  done
} > "$OUTPUT_DIR/21_bios_settings_status.txt"

# BIOS check differences per node
{
  echo "Per-node BIOS check"
  for n in $NODES; do
    echo "--- $n ---"
    cmsh -c "device use $n; bios check" 2>&1
    echo
  done
} > "$OUTPUT_DIR/22_bios_check.txt"

# 5) Firmware information
run_cmd 'cmsh -c "device firmware info"' \
        "23_firmware_info.txt" \
        "Firmware files available on head node"

{
  echo "Per-node firmware status"
  for n in $NODES; do
    echo "--- $n ---"
    cmsh -c "device firmware status -n $n" 2>&1
    echo
  done
} > "$OUTPUT_DIR/24_firmware_status.txt"

# 6) BMC information via ipmitool
{
  echo "Per-node BMC: ipmitool mc info"
  cmsh -c "device foreach * (ipmitool mc info)" 2>&1
} > "$OUTPUT_DIR/25_bmc_mc_info.txt" || true

{
  echo "Per-node BMC: sensor list"
  cmsh -c "device foreach * (ipmitool sensor list)" 2>&1
} > "$OUTPUT_DIR/26_bmc_sensors.txt" || true

{
  echo "Per-node BMC: chassis status"
  cmsh -c "device foreach * (ipmitool chassis status)" 2>&1
} > "$OUTPUT_DIR/27_bmc_chassis_status.txt" || true

# Reader-compatible BMC files
run_cmd 'cmsh -c "device foreach * (ipmitool chassis status)"' \
        "20_bmc_chassis.txt" \
        "Per-node BMC chassis status"

run_cmd 'cmsh -c "device foreach * (ipmitool sel elist)"' \
        "21_bmc_sel.txt" \
        "Per-node BMC SEL entries"

# 7) Health and overview
run_cmd 'cmsh -c "device overview"' \
        "28_device_overview.txt" \
        "Cluster device overview (health)"

run_cmd 'cmsh -c "monitoring healthconfigs"' \
        "29_health_configs.txt" \
        "Health configurations"

# Reader-compatible device peripheral files
run_cmd 'cmsh -c "device foreach * (lspci | grep -i nvidia)"' \
        "30_lspci_nvidia.txt" \
        "Per-node NVIDIA PCIe devices"

run_cmd 'cmsh -c "device foreach * (lsblk)"' \
        "40_block_devices.txt" \
        "Per-node block devices"

# 8) Summary
{
  echo "DGX Node Assessment Summary"
  echo "============================"
  echo "Assessment Date: $(date)"
  echo "Output Directory: $OUTPUT_DIR"
  echo
  echo "Files Generated:"
  ls -la "$OUTPUT_DIR"/*.txt | awk '{print $9, $5}' | sed 's|.*/||'
} > "$OUTPUT_DIR/00_SUMMARY.txt"

echo "Assessment complete! Results saved to: $OUTPUT_DIR"
echo "$OUTPUT_DIR"
