
#!/usr/bin/env bash

echo "root:root" | chpasswd
echo "metsis:metsis" | chpasswd
echo "metsis     ALL=(ALL:ALL) ALL" >> /etc/sudoers