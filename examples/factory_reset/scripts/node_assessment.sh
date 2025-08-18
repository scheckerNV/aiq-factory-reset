#!/bin/bash
# node_assessment.sh - Comprehensive BCM node assessment (OS/BIOS/Firmware/BMC/Health)

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
    eval "$cmd" 2>&1 || echo "Command failed with exit code $?"
    echo
  } > "$OUTPUT_DIR/$output_file"
}

# 1) Basic node information
run_cmd 'cmsh -c "device status"' \
        "01_device_status.txt" \
        "Overall device status"

# Use proper formatting for the device list command
run_cmd 'cmsh -t -c "device list -f hostname,status,mac,ip,category,softwareimage"' \
        "02_device_list.txt" \
        "Detailed device information"

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

# 3) Hardware information through hardware-profile
run_cmd 'cmsh -c "device hardwareprofile list"' \
        "19_hardware_profiles.txt" \
        "Hardware profiles in the cluster"

# 4) Node OS versions - using a more reliable approach
# Use foreach with specific node type instead of wildcard
run_cmd 'cmsh -c "device foreach -t physicalnode (cat /etc/os-release | grep ^VERSION)"' \
        "20_os_versions.txt" \
        "OS versions across physical nodes"

# 5) BIOS information
run_cmd 'cmsh -c "device foreach -t physicalnode (dmidecode -s bios-version)"' \
        "21_bios_versions.txt" \
        "BIOS versions across nodes"

# 6) Firmware management
run_cmd 'cmsh -c "device firmware info"' \
        "22_firmware_info.txt" \
        "Available firmware files"

# 7) BIOS settings status - first check if model is set
# Split into two commands - first check if the BIOS model is defined
run_cmd 'cmsh -c "device use node001; biossettings; get model"' \
        "23a_bios_model_check.txt" \
        "Check BIOS model for node001"

# Then try getting the settings status, with error handling
run_cmd 'cmsh -c "device use node001; biossettings; status 2>/dev/null || echo \"BIOS settings not available or model not defined\""' \
        "23_sample_bios_settings.txt" \
        "Sample BIOS settings for node001"

# 8) BMC status check using ipmitool
run_cmd 'cmsh -c "device foreach -t physicalnode (ipmitool mc info 2>/dev/null || echo \"BMC not accessible on this node\")"' \
        "24_bmc_info.txt" \
        "BMC information where accessible"

# 9) Device health overview
run_cmd 'cmsh -c "device overview"' \
        "25_device_overview.txt" \
        "Cluster health overview"

# 10) Check for burn configurations
run_cmd 'cmsh -c "partition use base; burnconfigs list 2>/dev/null || echo \"No burn configs available\""' \
        "26_burn_configs.txt" \
        "Available hardware burn configurations"

# 11) Try using sysinfo for detailed hardware info for one node
run_cmd 'cmsh -c "device use node001; sysinfo"' \
        "27_sysinfo_node001.txt" \
        "Detailed system info for node001"

# 12) Summary
{
  echo "BCM Node Assessment Summary"
  echo "============================"
  echo "Assessment Date: $(date)"
  echo "Output Directory: $OUTPUT_DIR"
  echo
  echo "Files Generated:"
  ls -la "$OUTPUT_DIR/"*.txt | awk '{print $9, "("$5" bytes)"}' | sed 's|.*/||'
} > "$OUTPUT_DIR/00_SUMMARY.txt"

# Create symlink for easy access by the results reader
ln -sfn "$OUTPUT_DIR" /tmp/node_assessment_latest 2>/dev/null || true

echo "Assessment complete! Results saved to: $OUTPUT_DIR"
echo "Summary file: $OUTPUT_DIR/00_SUMMARY.txt"
