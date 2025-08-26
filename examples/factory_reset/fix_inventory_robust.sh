#!/bin/bash

echo "🔧 Fixing Ansible inventory for 2.19+ compatibility..."

# Create multiple inventory formats for maximum compatibility

# 1. Simple YAML format (works with 2.18.x and some 2.19.x)
echo "📄 Creating simple YAML inventory..."
cat > ansible/inventory_simple.yml <<'YAML'
all:
  children:
    compute:
      hosts:
        node001: { ansible_host: 10.141.0.1 }
        node002: { ansible_host: 10.141.0.2 }
        node003: { ansible_host: 10.141.0.3 }
        node004: { ansible_host: 10.141.0.4 }
        node005: { ansible_host: 10.141.0.5 }
        node006: { ansible_host: 10.141.0.6 }
        node007: { ansible_host: 10.141.0.7 }
        node008: { ansible_host: 10.141.0.8 }
        node009: { ansible_host: 10.141.0.9 }
        node010: { ansible_host: 10.141.0.10 }
YAML

# 2. Plugin header format (for strict 2.19.x)
echo "📄 Creating plugin header YAML inventory..."
cat > ansible/inventory_plugin.yml <<'YAML'
plugin: yaml
strict: true
all:
  children:
    compute:
      hosts:
        node001: { ansible_host: 10.141.0.1 }
        node002: { ansible_host: 10.141.0.2 }
        node003: { ansible_host: 10.141.0.3 }
        node004: { ansible_host: 10.141.0.4 }
        node005: { ansible_host: 10.141.0.5 }
        node006: { ansible_host: 10.141.0.6 }
        node007: { ansible_host: 10.141.0.7 }
        node008: { ansible_host: 10.141.0.8 }
        node009: { ansible_host: 10.141.0.9 }
        node010: { ansible_host: 10.141.0.10 }
YAML

# 3. INI format (universal compatibility)
echo "📄 Creating INI inventory..."
cat > ansible/inventory.ini <<'INI'
[compute]
node001 ansible_host=10.141.0.1
node002 ansible_host=10.141.0.2
node003 ansible_host=10.141.0.3
node004 ansible_host=10.141.0.4
node005 ansible_host=10.141.0.5
node006 ansible_host=10.141.0.6
node007 ansible_host=10.141.0.7
node008 ansible_host=10.141.0.8
node009 ansible_host=10.141.0.9
node010 ansible_host=10.141.0.10
INI

# Test which format works and set as default
echo "🔍 Testing inventory formats..."

if ansible-inventory -i ansible/inventory_simple.yml --graph &>/dev/null; then
    echo "✅ Simple YAML format works - using as default"
    cp ansible/inventory_simple.yml ansible/inventory.yml
elif ansible-inventory -i ansible/inventory.ini --graph &>/dev/null; then
    echo "✅ INI format works - using as default"
    cp ansible/inventory.ini ansible/inventory.yml
    # Update ansible.cfg to point to INI
    sed -i 's/inventory.yml/inventory.ini/' ansible.cfg
else
    echo "⚠️  Neither format parsed successfully, using simple YAML"
    cp ansible/inventory_simple.yml ansible/inventory.yml
fi

# Set proper permissions
echo "🔒 Setting secure permissions..."
chmod 700 ansible
chmod 600 ansible/inventory*.yml ansible/inventory*.ini 2>/dev/null

echo "✅ Inventory fix complete!"
echo "📊 Available formats:"
echo "   - ansible/inventory.yml (default)"
echo "   - ansible/inventory_simple.yml (no plugin headers)"
echo "   - ansible/inventory_plugin.yml (with plugin headers)"
echo "   - ansible/inventory.ini (INI format)"

echo ""
echo "🧪 Test with: ansible-inventory -i ansible/inventory.yml --graph"
