SHELL=/bin/bash
GROUP_NAME:=aws
INVENTORY:=hosts.yml
TMP:=$(shell psec environments path --tmpdir)

all: help

help:
	@echo "Usage: make [something]"
	@echo ""
	@echo "Where 'something' is one of these:"
	@echo ""
	@echo " help - print this help text"
	@echo ""
	@echo " init - initialize stack and virtualenv"
	@echo " console-output - use AWS 'get-console-output' to get instance console log"
	@echo " hosts - generate an Ansible hosts inventory file"
	@echo " up - do 'pulimi up --yes'"
	@echo " update - do 'sudo yum update' and 'sudo reboot' on running instance"
	@echo " destroy - do 'pulimi destroy --yes'"
	@echo " ping - does Ansible ad-hoc ping of hosts in group '$(GROUP_NAME)'"
	@echo " add-keys - update system SSH known_hosts file from instance public keys"
	@echo " remove-keys - remove instance public keys from SSH known_hosts file"
	@echo ""
	@echo " * The default if you just type 'make' is the same as 'make help'"
	@echo ""
	@echo "You can get the public IP address and/or DNS name using the following:"
	@echo "  $$ aws ec2 describe-instances --query "Reservations[*].Instances[*].PublicIpAddress" --output=text"
	@echo "  34.219.144.62"
	@echo "  $$ pulumi stack output public_ip"
	@echo "  34.219.144.62"
	@echo "  $$ aws ec2 describe-instances --query "Reservations[*].Instances[*].PublicDnsName" --output=text"
	@echo "  ec2-34-219-144-62.us-west-2.compute.amazonaws.com"
	@echo "  $$ pulumi stack output public_dns"
	@echo "  ec2-34-219-144-62.us-west-2.compute.amazonaws.com"

.PHONY: init
init:
	python3 -m pip install -r requirements.txt
	pulumi stack init

.PHONY: console-output
console-output:
	@ID=$(shell pulumi stack output instance_id) && [ ! -z "$$ID" ] && aws ec2 get-console-output --instance $$ID --output text

hosts:
	@(pulumi stack output public_ip 2>&1) >/dev/null || (echo "[-] No instance running?"; exit 1)
	@echo "[+] Generating 'hosts' file"
	@(echo "[$(GROUP_NAME)]"; \
		ansible -i $(shell pulumi stack output public_ip), --list-hosts all 2>/dev/null |\
		sed 's/ *//g'|\
		tail -n +2) |\
		tee hosts

# Retrieve the Pulumi ami.py script
ami.py:
	wget https://raw.githubusercontent.com/pulumi/examples/master/aws-py-webserver/ami.py

.PHONY: up
up: ami.py
	@echo "[+] Bringing EC2 instance up with pulumi"
	pulumi up --yes
	@echo "[+] Sleeping to allow console-output to present"
	sleep 30
	$(MAKE) add-keys
	$(MAKE) hosts

.PHONY: update
update:
	@echo "[+] Updating patches in EC2 instance and rebooting"
	ssh "$(shell pulumi stack output public_ip)" "sudo yum update -y && sudo reboot"

.PHONY: destroy
destroy: remove-keys
	@echo "[+] Destroying EC2 instance with pulumi"
	pulumi destroy --yes
	rm -f hosts

.PHONY: ping
ping: hosts
	ansible -i hosts -i $(INVENTORY) -m ping $(GROUP_NAME)

.PHONY: add-keys
add-keys:
	@echo "[+] Extracting SSH host public keys and adding to system known_hosts file"
	psec utils ssh-known-hosts \
		--public-ip "$(shell pulumi stack output public_ip)" \
		--instance-id "$(shell pulumi stack output instance_id)"
	@echo "[+] Saving EC2 instance console-output"
	$(MAKE) console-output > "$(shell pulumi stack output instance_id)-console-output.txt"
	@echo "[+] Generating SSH configuration snippet for EC2 instance"
	psec utils ssh-config --public-ip "$(shell pulumi stack output public_ip)" --public-dns "$(shell pulumi stack output public_dns)"

.PHONY: remove-keys
remove-keys:
	@echo "[+] Removing host keys from system known_hosts file"
	psec utils ssh-known-hosts --remove-keys --public-ip "$(shell pulumi stack output public_ip)"

.PHONY: clean
clean:
	(pulumi stack output instance_id 2>/dev/null 1>/dev/null) && \
		for F in $(shell ls i-*-console-output.txt | egrep -v "$(shell pulumi stack output instance_id)"); do rm -f $$F; done

.PHONY: spotless
spotless:
	rm -f i-*-console.log
