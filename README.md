# hybrid-core
Oregon State University (OSU) hybrid rocket team senior capstone

dhcpcd.conf used for setting static ip to 192.168.0.10 (may need to changed depending on router config to 192.168.1.10, would require editing other .0s to .1s). Use following commands to set up:
	sudo cp /etc/dhcpcd.conf
	reboot
only needs to run once

for i2c (likely already on board)
	sudo apt install -y i2c-tools
https://circuitpython.readthedocs.io/projects/ads1x15/en/latest/
