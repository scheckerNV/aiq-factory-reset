#!/bin/bash
# universal_cluster_assessment.sh - Works with any BCM-managed cluster

OUTPUT_DIR="/tmp/node_assessment_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "Starting universal cluster assessment..."
echo "Output directory: $OUTPUT_DIR"

run_cmd() {
  local cmd="$1"
  local output_file="$2"
  local description="$3"
  local timeout_seconds="${4:-30}"
  echo "[$description] Running: $cmd"
  {
    echo "Command: $cmd"
    echo "Description: $description"
    echo "Timestamp: $(date)"
    echo "Timeout: ${timeout_seconds}s"
    echo "====================================="
    echo
    timeout "$timeout_seconds" bash -c "$cmd" 2>&1 || {
      local exit_code=$?
      if [ $exit_code -eq 124 ]; then
        echo "Command timed out after ${timeout_seconds} seconds"
      else
        echo "Command failed with exit code $exit_code"
      fi
    }
    echo
  } > "$OUTPUT_DIR/$output_file"
}

# Auto-detect compute node categories and IPs
echo "Auto-detecting cluster configuration..."

# Get all categories with node counts > 0
CATEGORIES=$(cmsh -c "category list" 2>/dev/null | awk '$3 > 0 && $1 !~ /^(default|k8s|slogin)/ {print $1}' | tr '\n' ' ')
echo "Found compute categories: $CATEGORIES"

# Get IPs for compute categories (exclude management/infrastructure)
if [ -n "$CATEGORIES" ]; then
    COMPUTE_IPS=""
    for category in $CATEGORIES; do
        category_ips=$(cmsh -c "device list -f ip,category" 2>/dev/null | grep "$category" | awk '{print $1}' | tr '\n' ' ')
        COMPUTE_IPS="$COMPUTE_IPS $category_ips"
    done
else
    # Fallback: get all IPs except headnode
    COMPUTE_IPS=$(cmsh -c "device list -f ip,hostname" 2>/dev/null | grep -v headnode | awk '{print $1}' | tr '\n' ' ')
fi

COMPUTE_IPS=$(echo $COMPUTE_IPS | tr ' ' '\n' | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' | sort -u | tr '\n' ' ')
NODE_COUNT=$(echo $COMPUTE_IPS | wc -w)

echo "Found $NODE_COUNT compute nodes: $COMPUTE_IPS"

# 1) BCM cluster status
run_cmd 'cmsh -c "device status"' \
        "01_device_status.txt" \
        "Overall device status from BCM"

run_cmd 'cmsh -c "device list -f hostname,status,mac,ip,category,softwareimage"' \
        "02_device_list.txt" \
        "Detailed device information from BCM"

# 2) Node connectivity test
run_cmd "for ip in $COMPUTE_IPS; do echo \"=== \$ip ===\"; ssh -o ConnectTimeout=5 \$ip 'hostname && uptime' 2>/dev/null || echo \"Failed to connect to \$ip\"; done" \
        "03_connectivity.txt" \
        "Node connectivity test" \
        120

# 3) OS and system info
run_cmd "for ip in $COMPUTE_IPS; do echo \"=== \$ip ===\"; ssh \$ip 'echo \"OS:\"; cat /etc/os-release 2>/dev/null | grep VERSION || echo \"Unknown OS\"; echo \"Kernel:\"; uname -r 2>/dev/null || echo \"Unknown kernel\"; echo \"Memory:\"; free -h 2>/dev/null | head -2 || echo \"Memory info unavailable\"' 2>/dev/null || echo \"Failed to get system info from \$ip\"; done" \
        "04_system_info.txt" \
        "OS and system information" \
        120

# 4) GPU detection (if available)
run_cmd "for ip in $COMPUTE_IPS; do echo \"=== \$ip ===\"; ssh \$ip 'if command -v nvidia-smi >/dev/null 2>&1; then nvidia-smi --query-gpu=index,name,driver_version,memory.total,power.limit --format=csv,noheader 2>/dev/null; else echo \"No NVIDIA GPUs or nvidia-smi not found\"; fi' 2>/dev/null || echo \"Failed to get GPU info from \$ip\"; done" \
        "05_gpu_info.txt" \
        "GPU information (if available)" \
        120

# 5) DCGM status (if available)
run_cmd "for ip in $COMPUTE_IPS; do echo \"=== \$ip ===\"; ssh \$ip 'if command -v dcgmi >/dev/null 2>&1; then echo \"DCGM Discovery:\"; dcgmi discovery -l 2>/dev/null; else echo \"DCGM not installed\"; fi' 2>/dev/null || echo \"Failed to connect to \$ip\"; done" \
        "06_dcgm_status.txt" \
        "DCGM status (if available)" \
        120

# 6) Network interfaces
run_cmd "for ip in $COMPUTE_IPS; do echo \"=== \$ip ===\"; ssh \$ip 'ip addr show 2>/dev/null | grep -E \"^[0-9]+:\" | head -10 || echo \"Network info unavailable\"' 2>/dev/null || echo \"Failed to get network info from \$ip\"; done" \
        "07_network_interfaces.txt" \
        "Network interface information" \
        120

# 7) Storage info
run_cmd "for ip in $COMPUTE_IPS; do echo \"=== \$ip ===\"; ssh \$ip 'df -h 2>/dev/null | head -10 || echo \"Storage info unavailable\"' 2>/dev/null || echo \"Failed to get storage info from \$ip\"; done" \
        "08_storage_info.txt" \
        "Storage information" \
        90

# 8) Hardware detection
run_cmd "for ip in $COMPUTE_IPS; do echo \"=== \$ip ===\"; ssh \$ip 'echo \"CPU:\"; lscpu 2>/dev/null | grep \"Model name\" || echo \"CPU info unavailable\"; echo \"Memory:\"; dmidecode -t memory 2>/dev/null | grep \"Size:\" | head -5 || echo \"Memory details unavailable\"' 2>/dev/null || echo \"Failed to get hardware info from \$ip\"; done" \
        "09_hardware_info.txt" \
        "Hardware information" \
        120

# Summary
{
  echo "Universal Cluster Assessment Summary"
  echo "==================================="
  echo "Assessment Date: $(date)"
  echo "Output Directory: $OUTPUT_DIR"
  echo "Compute Categories: $CATEGORIES"
  echo "Compute Node Count: $NODE_COUNT"
  echo "Compute Node IPs: $COMPUTE_IPS"
  echo
  echo "Files Generated:"
  ls -la "$OUTPUT_DIR/"*.txt 2>/dev/null | awk '{print $9, "("$5" bytes)"}' | sed 's|.*/||'
  echo
  echo "Key Files to Review:"
  echo "- 01_device_status.txt: BCM cluster status"
  echo "- 03_connectivity.txt: Node SSH connectivity"
  echo "- 05_gpu_info.txt: GPU hardware details (if available)"
  echo "- 06_dcgm_status.txt: DCGM functionality (if available)"
  echo "- 04_system_info.txt: OS and system information"
} > "$OUTPUT_DIR/00_SUMMARY.txt"

# Create a stable symlink for easy discovery by the Python tools
SYMLINK_PATH="/tmp/node_assessment_latest"
if [ -L "$SYMLINK_PATH" ]; then
    rm "$SYMLINK_PATH"
fi
ln -sf "$OUTPUT_DIR" "$SYMLINK_PATH"

echo "Assessment complete! Results saved to: $OUTPUT_DIR"
echo "Symlink created: $SYMLINK_PATH -> $OUTPUT_DIR"
echo "Cluster type: $(echo $CATEGORIES | wc -w) category(ies) detected"
echo "Nodes found: $NODE_COUNT"
