# vim:ft=make:

SHELL=/bin/bash
SECRETS=$(HOME)/.secrets/digital-ocean
INVENTORY=$(PBR)/environments/$(TF_VAR_environment)/inventory
INVENTORY_GENERATED=inventory/nodes-generated.yml
COMMON_SCRIPTS=$(PBR)/files/common-scripts

# Generate SSH public key fingerprint for terraform to use
SSH_FINGERPRINT=$(shell ssh-keygen -E md5 -lf ${TF_VAR_public_key}|awk '{print $$2}'|sed 's/^[Mm][Dd]5://')
TF_VARS=-var 'ssh_fingerprint=$(SSH_FINGERPRINT)'

# The following checks to see if local sudo requires a password. If so,
# the flag is added to the command line when invoking Ansible.
ASK_BECOME_PASS:=$(shell ansible -i localhost, -m shell -a date --become localhost -c local | grep -q "password is required" && echo "--ask-become-pass")

define get_domain_var
   $(shell ansible -i $(INVENTORY) -m debug -a 'msg=^DIMS_DOMAIN={{ dims_domain }}^' --one-line do | head -n 1 | cut -d^ -f 2)
endef

# By nature of being defined first, 'make help' is the default.

.PHONY: help
help:
	@echo "Usage: make [something]"
	@echo ""
	@echo "Where 'something' is one of these:"
	@echo ""
	@echo " help - print this help text"
	@echo ""
	@echo " ---- Build state functions ----"
	@echo " init - initialize terraform state (this is automatic)"
	@echo " prerequisites - install prerequisite programs"
	@echo " pre.test - run pre-requisite tests for using terraform with DigitalOcean"
	@echo " droplets - show list of active droplets using digital_ocean.py dynamic inventory"
	@echo " hosts - show list of hosts in group 'do'"
	@echo " dumpjson - dump all DigitalOcean image related information in JSON"
	@echo " dumpvars - produces Ansible debug output of vars for hosts in group 'do'"
	@echo " updatefacts - run 'ansible -m setup' to refresh cached facts"
	@echo " images - lists available DigitalOcean images"
	@echo " regions - lists available DigitalOcean regions"
	@echo " provider - generate terraform provider.tf and user-data file for creating nodes in group 'do'"
	@echo " plan - show the terraform plan for the current state"
	@echo " graph - generate terraform graph (output is 'graph.png')"
	@echo " newkeypair - generate a new SSH user keypair"
	@echo " insertpubkey - insert SSH public key on DigitalOcean"
	@echo " removepubkey - remove SSH public key on DigitalOcean"
	@echo " addhostkeys - adds SSH host public keys to selected known_hosts files"
	@echo " removehostkeys - removes SSH host public keys from selected known_hosts files"
	@echo " destroy - destroys droplets and related resources for hosts in group 'do'"
	@echo " spotless - remove terraform log and state files"
	@echo ""
	@echo " ---- Provisioning functions ----"
	@echo " create - applies terraform plan to create droplets for hosts in group 'do'"
	@echo " ping - does Ansible ad-hoc ping of hosts in group 'do'"
	@echo " bootstrap - create, then run bootstrap.yml and ca-certs.yml playbooks"
	@echo " installcerts - run 'certbot-installcert.yml' playbook to install SSL certs"
	@echo " deploy - run 'master.yml' playbook to deploy roles on droplets"
	@echo " post.test - run 'test.runner --terse' on all droplets"
	@echo ""
	@echo " ---- Maintenance functions ----"
	@echo " update - update packages on droplets"
	@echo " reboot - reboot droplets in +1 minute"
	@echo " cancel - cancel rebooting (if you REALLY DIDN'T MEAN IT)"
	@echo " backup.letsencrypt - backup Letsencrypt certificate store"
	@echo " backup.trident - backup Trident postgresql database and other ancillary files"
	@echo " restore.trident - restore Trident postgresql database and other ancillary files"
	@echo ""
	@echo " * The default if you just type 'make' is the same as 'make help'"
	@echo " * To control Ansible, set DIMS_ANSIBLE_ARGS to the arguments you want"
	@echo "   to pass along on the command line, for example:"
	@echo '     $$ make DIMS_ANSIBLE_ARGS="--tags tests --limit purple" deploy'
	@echo '     $$ make DIMS_ANSIBLE_ARGS="--limit purple" post.test'
	@echo '     $$ make DIMS_ANSIBLE_ARGS="--limit trident" backup.postgresql'

.PHONY: init
init: terraform.tfstate
	@[ -d $(HOME)/.secrets/digital-ocean ] || mkdir -p $(HOME)/.secrets/digital-ocean
	@chmod 700 $(HOME)/.secrets $(HOME)/.secrets/digital-ocean
	@touch $(HOME)/.secrets/digital-ocean/token
	@chmod 600 $(HOME)/.secrets/digital-ocean/token

terraform.tfstate:
	terraform init

.PHONY: prerequisites
prerequisites:
	sudo apt-get install bats pip python-pip jq
	sudo pip install ansible==2.4.0.0

.PHONY: droplets
droplets:
	ansible -i $(INVENTORY)/digital_ocean.py --list-hosts all $(DIMS_ANSIBLE_ARGS) |\
	       sed 's/ *//g' |\
	       tail -n +2

.PHONY: hosts
hosts:
	$(MAKE) --always-make inventory/hosts 2>/dev/null

inventory/hosts:
	(echo "[droplets]"; ansible -i $(INVENTORY) --list-hosts do $(DIMS_ANSIBLE_ARGS)|sed 's/ *//g'|tail -n +2) |\
		tee inventory/hosts

.PHONY: etchosts
etchosts:
	@#ansible -i $(INVENTORY) -m debug -a 'msg="{{ hostvars[inventory_hostname].ansible_default_ipv4.address }} {{ inventory_hostname }}"' do |\
		grep '\"msg\":' |\
		awk -F\" '{ print $$4; }'
	@$ansible -i $(INVENTORY) -m debug -a 'msg="{{ hostvars[inventory_hostname].ansible_host }} {{ inventory_hostname }}"' do |\
		grep '\"msg\":' |\
		awk -F\" '{ print $$4; }'

.PHONY: dumpjson
dumpjson:
	curl -X GET --silent "https://api.digitalocean.com/v2/images?per_page=999" -H "Authorization: Bearer $(DO_API_TOKEN)" |\
		python -m json.tool |\
		less

.PHONY: images
images:
	@curl -X GET --silent "https://api.digitalocean.com/v2/images?per_page=999" -H "Authorization: Bearer $(DO_API_TOKEN)" |\
		jq -rc '.images[] | select(.slug | length >= 1) | { slug: .slug, distribution: .distribution, name: .name }' | sort

.PHONY: regions
regions:
	@curl -X GET --silent "https://api.digitalocean.com/v2/images?per_page=999" -H "Authorization: Bearer $(DO_API_TOKEN)" |\
		jq -rc '.images[] | select(.slug | length >= 1) | .regions' | sort | uniq

.PHONY: provider
provider:
	ansible-playbook -i $(INVENTORY) \
		create-provider.tf.yml \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: plan
plan: init provider
	terraform plan $(TF_VARS)
	$(MAKE) --always-make $(INVENTORY_GENERATED)

.PHONY: graph
graph: graph.png
	@if [[ "$(shell uname -s)" == "Darwin" ]]; then open graph.png; fi
	@if [[ "$(shell uname -s)" == "Linux" && ! -z "$(shell which evince)" ]] ; then (evince graph.png &); fi
	@if [[ "$(shell uname -s)" == "Linux" && ! -z "$(shell which xdg-open)" ]] ; then (xdg-open graph.png &); fi

graph.png: init
	terraform graph $(TF_VARS) | dot -Tpng -o graph.png

$(INVENTORY_GENERATED):
	$(COMMON_SCRIPTS)/terraform.inventory.generate.sh > $(INVENTORY_GENERATED)

.PHONY: newkeypair
newkeypair:
	@if [ -f terraform.tfstate -a "$(shell jq -r '.resources' terraform.tfstate)" != "null" ]; then \
	        echo '[!] Refusing to replace SSH keys while droplets are running'; \
	        echo '[!] Use "make destroy" first or manually re-key droplets'; \
	        false; \
	 fi
	@echo "[+] Generating new SSH key pair"
	ssh-keygen -t rsa -f $(TF_VAR_private_key)
	ssh-add $(TF_VAR_private_key) || true

.PHONY: insertpubkey
insertpubkey:
	terraform apply $(TF_VARS) -target=digitalocean_ssh_key.default -auto-approve

.PHONY: removepubkey
removepubkey:
	terraform destroy $(TF_VARS) -target=digitalocean_ssh_key.default

.PHONY: create
create: init hosts provider
	terraform apply $(TF_VARS) | tee -a terraform.log | $(call get_domain_var) $(COMMON_SCRIPTS)//keys.host.extract.sh
	! grep -q "Error: Error applying plan:" terraform.log
	$(MAKE) --always-make $(INVENTORY_GENERATED)
	$(MAKE) addhostkeys
	$(MAKE) ping

.PHONY: sshkeys
sshkeys:
	cat terraform.log | $(call get_domain_var) $(COMMON_SCRIPTS)/keys.host.extract.sh > /dev/null

.bootstrapped: bootstrap
	touch .bootstrapped

.PHONY: bootstrap
bootstrap:
	rm -f .bootstrapped
	(terraform plan $(TF_VARS) | grep -q "No changes") || $(MAKE) create
	ansible-playbook -i $(INVENTORY) \
		$(PBR)/playbooks/bootstrap.yml \
		-e host=do \
		$(DIMS_ANSIBLE_ARGS)
	ansible-playbook -i $(INVENTORY) \
		$(ASK_BECOME_PASS) \
		-e@~/.secrets/digital-ocean/secrets.yml \
		--tags opendkim-genkey \
		master.yml \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: installcerts
installcerts:
	ansible-playbook -i $(INVENTORY) \
		$(PBR)/playbooks/certbot-installcert.yml \
		-e host=do \
		$(DIMS_ANSIBLE_ARGS)

# TODO(dittrich): Remove the trident_backup_restorefrom after debugging. :(
.PHONY: deploy
deploy:
	ansible-playbook -i $(INVENTORY) \
		$(ASK_BECOME_PASS) \
		-e@~/.secrets/digital-ocean/secrets.yml \
		-e trident_backup_restorefrom='' \
		master.yml \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: update
update:
	ansible-playbook -i $(INVENTORY) \
		-e@~/.secrets/digital-ocean/secrets.yml \
		--tags updates \
		-e packages_upgrade=yes \
		master.yml \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: reboot
reboot:
	ansible -i $(INVENTORY) \
		--become \
		-m shell \
		-a '/sbin/shutdown -r +1' \
		do \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: cancel
cancel:
	ansible -i $(INVENTORY) \
		--become \
		-m shell \
		-a '/sbin/shutdown -c && echo "[+] Whew! That was close!"' \
		do \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: addhostkeys
addhostkeys:
	@echo "[+] Adding host keys to known_hosts on localhost"
	ansible-playbook -i $(INVENTORY) \
		$(ASK_BECOME_PASS) \
		$(PBR)/playbooks/do_rekey.yml \
		-e known_hosts_root="$(shell pwd)/known_hosts" \
		$(DIMS_ANSILE_ARGS)
	@echo "[+] Adding host keys to known_hosts on droplets"
	ansible-playbook -i $(INVENTORY) \
		$(DIMS_ANSILE_ARGS) \
		$(PBR)/playbooks/do_rekey.yml \
		-e known_hosts_root="$(shell pwd)/known_hosts" \
		-e host=do

.PHONY: removehostkeys
removehostkeys:
	-ansible-playbook -i $(INVENTORY) \
		$(ASK_BECOME_PASS) \
		$(PBR)/playbooks/do_rekey.yml \
		-e remove_keys=true \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: dumpvars
dumpvars:
	ansible -i $(INVENTORY) \
		-m debug -a "var=hostvars[inventory_hostname]" do \
		$(DIMS_ANSIBLE_ARGS) |\
			pygmentize -ljson |\
			less -R
.PHONY: updatefacts
updatefacts:
	ansible -i $(INVENTORY) \
		-m setup do \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: ping
ping:
	ansible -i $(INVENTORY) \
		-m ping do

.PHONY: pre.test
pre.test:
	bats do.bats

.PHONY: post.test
post.test:
	ansible -i $(INVENTORY) \
		-m shell \
		-a 'test.runner --terse --tap' \
		do \
		$(DIMS_ANSIBLE_ARGS) || (echo '[!] Some test(s) failed' && exit 1)
	@echo '[+] All tests passed!'

.PHONY: backup.trident
backup.trident:
	-ansible-playbook -i $(INVENTORY) \
		$(ASK_BECOME_PASS) \
		-e@~/.secrets/digital-ocean/secrets.yml \
		$(PBR)/playbooks/trident_backup.yml \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: restore.trident
restore.trident:
	-ansible-playbook -i $(INVENTORY) \
		$(ASK_BECOME_PASS) \
		-e@~/.secrets/digital-ocean/secrets.yml \
		$(PBR)/playbooks/trident_restore.yml \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: backup.letsencrypt
backup.letsencrypt:
	-ansible-playbook -i $(INVENTORY) \
		$(ASK_BECOME_PASS) \
		-e@~/.secrets/digital-ocean/secrets.yml \
		$(PBR)/playbooks/letsencrypt_backup.yml \
		-e host=do \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: destroy
destroy:
	terraform destroy $(TF_VARS) --force
	-$(MAKE) removehostkeys
	-rm -rf fingerprints/ known_hosts/ user-data/
	-rm -f ansible-digital_ocean.cache
	-rm -f inventory/hosts inventory/nodes-generated.yml
	-rm -f provider.tf graph.png
	-rm -f .bootstrapped
	-$(MAKE) removepubkey

.PHONY: spotless
spotless: destroy
	-rm -f terraform.log
	-rm -f terraform.tfstate terraform.tfstate.backup

# vim: ft=make:
