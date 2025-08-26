#!/bin/bash

# Fix inventory parsing issue by regenerating the file with proper format
cat > ansible/inventory.yml <<'YML'
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
YML

# Set proper permissions
chmod 700 ansible
chmod 600 ansible/inventory.yml

# Remove any CRLF line endings
sed -i 's/\r$//' ansible/inventory.yml

echo "Inventory file regenerated with proper format and permissions"
echo "File size: $(wc -c < ansible/inventory.yml) bytes"
echo "First few lines:"
head -5 ansible/inventory.yml
