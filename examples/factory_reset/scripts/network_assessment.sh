#!/bin/bash
# network_assessment.sh - Comprehensive BCM cluster networking assessment

# Set output directory
OUTPUT_DIR="/tmp/cluster_assessment_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "Starting comprehensive network assessment..."
echo "Output directory: $OUTPUT_DIR"

# Function to run command and save output
run_cmd() {
    local cmd="$1"
    local output_file="$2"
    local description="$3"

    echo "[$description] Running: $cmd"
    echo "Command: $cmd" > "$OUTPUT_DIR/$output_file"
    echo "Description: $description" >> "$OUTPUT_DIR/$output_file"
    echo "Timestamp: $(date)" >> "$OUTPUT_DIR/$output_file"
    echo "=====================================" >> "$OUTPUT_DIR/$output_file"
    echo "" >> "$OUTPUT_DIR/$output_file"

    eval "$cmd" >> "$OUTPUT_DIR/$output_file" 2>&1
    echo -e "\n\n" >> "$OUTPUT_DIR/$output_file"
}

# 1. General Device Status
run_cmd 'cmsh -c "device status"' "01_device_status.txt" "Overall device status"
run_cmd 'cmsh -c "device list -f hostname,ip,mac,status"' "02_device_list.txt" "Detailed device information"

# 2. Network Configuration
run_cmd 'cmsh -c "network list"' "03_networks.txt" "All configured networks"
run_cmd 'cmsh -c "device; interfaces; list"' "04_interfaces.txt" "All device interfaces"

# 3. Connectivity Assessment
run_cmd 'cmsh -c "device; connectivity"' "05_connectivity.txt" "Inter-node connectivity"
run_cmd 'cmsh -c "device; connectivity --statistics --count 10"' "06_connectivity_stats.txt" "Connectivity statistics"

# 4. Routing Information
run_cmd 'cmsh -c "device; routes"' "07_routes.txt" "All routing information"
run_cmd 'cmsh -c "device; routes --category default"' "08_default_routes.txt" "Default routes"

# 5. Network Connections
run_cmd 'cmsh -c "device; connections --no-tcp6 --no-udp6"' "09_connections.txt" "Active network connections"

# 6. Switch Information (if switches exist)
echo "Checking for switches..."
SWITCHES=$(cmsh -c "device list -f hostname --category switch" 2>/dev/null | tail -n +2)
for switch in $SWITCHES; do
    if [ ! -z "$switch" ]; then
        run_cmd "cmsh -c \"device; use $switch; switchoverview\"" "10_switch_${switch}_overview.txt" "Switch $switch overview"
        run_cmd "cmsh -c \"device; use $switch; switchports\"" "11_switch_${switch}_ports.txt" "Switch $switch port configuration"
        run_cmd "cmsh -c \"device; use $switch; uplinks\"" "12_switch_${switch}_uplinks.txt" "Switch $switch uplinks"

        # Cumulus-specific if applicable
        run_cmd "cmsh -c \"device; use $switch; cumulus; show\"" "13_switch_${switch}_cumulus.txt" "Switch $switch Cumulus config"
    fi
done

# 7. Fabric Networks (if applicable)
run_cmd 'cmsh -c "partition use base; fabrics"' "14_fabrics.txt" "Fabric configurations"

# 8. System Information
run_cmd 'cmdaemonctl full-status' "15_cmdaemon_status.txt" "CMDaemon status"

# 9. Create summary
echo "Creating assessment summary..."
cat > "$OUTPUT_DIR/00_SUMMARY.txt" << EOF
BCM Cluster Network Assessment Summary
======================================
Assessment Date: $(date)
Output Directory: $OUTPUT_DIR

Files Generated:
$(ls -la "$OUTPUT_DIR"/*.txt | awk '{print $9, $5}' | sed 's|.*/||')

Total Devices Found: $(cmsh -c "device list" 2>/dev/null | wc -l)
Networks Configured: $(cmsh -c "network list" 2>/dev/null | wc -l)
Switches Found: $(echo "$SWITCHES" | wc -w)

Assessment Complete!
EOF

echo "Assessment complete! Results saved to: $OUTPUT_DIR"
echo "Summary file: $OUTPUT_DIR/00_SUMMARY.txt"
