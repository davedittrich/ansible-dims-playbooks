# vim:ft=make:

SHELL=/bin/bash
SECRETS=~/.secrets/digital-ocean
INVENTORY=$(PBR)/environments/$(TF_VAR_name)/inventory
INVENTORY_GENERATED=inventory/nodes-generated.yml
COMMON_SCRIPTS=$(PBR)/files/common-scripts

# The following checks to see if local sudo requires a password. If so,
# the flag is added to the command line when invoking Ansible.
ASK_SUDO_PASS:=$(shell ansible -i localhost, -m shell -a date --become localhost -c local | grep -q "password is required" && echo "--ask-sudo-pass")

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
	@echo " init - initialize terraform state (this is automatic)"
	@echo " droplets - show list of active droplets using digital_ocean.py dynamic inventory"
	@echo " hosts - show list of hosts in group 'do'"
	@echo " dumpjson - dump all DigitalOcean image related information in JSON"
	@echo " images - lists available DigitalOcean images"
	@echo " regions - lists available DigitalOcean regions"
	@echo " provider - generate terraform provider.tf file for creating nodes in group 'do'"
	@echo ""
	@echo " plan - show the terraform plan for the current state"
	@echo " graph - generate terraform graph (output is 'graph.png')"
	@echo " newkeypair - generate a new SSH user keypair"
	@echo " insertpubkey - insert SSH public key on DigitalOcean"
	@echo " removepubkey - remove SSH public key on DigitalOcean"
	@echo " create - applies terraform plan to create droplets for hosts in group 'do'"
	@echo " bootstrap - create, then run bootstrap.yml and ca-certs.yml playbooks"
	@echo " installcerts - run 'certbot-installcert.yml' playbook to install SSL certs"
	@echo " deploy - run 'master.yml' playbook to deploy roles on droplets"
	@echo ""
	@echo " update - update packages"
	@echo " reboot - reboot the system in +1 minute"
	@echo " cancel - cancel rebooting (if you REALLY DIDN'T MEAN IT)"
	@echo ""
	@echo " addhostkeys - adds SSH host public keys to selected known_hosts files"
	@echo " removehostkeys - removes SSH host public keys from selected known_hosts files"
	@echo ""
	@echo " dumpvars - produces Ansible debug output of vars for hosts in group 'do'"
	@echo " ping - does Ansible ad-hoc ping of hosts in group 'do'"
	@echo " pre.test - run pre-requisite tests for using terraform with DigitalOcean"
	@echo " post.test - run 'test.runner --terse' on all droplets"
	@echo " backup.postgresql - backup Trident postgresql database"
	@echo " backup.letsencrypt - backup Letsencrypt certificate store"
	@echo ""
	@echo " destroy - destroys droplets for hosts in group 'do'"
	@echo " spotless - remove terraform log and state files"
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

.PHONY: droplets
droplets:
	ansible -i $(INVENTORY)/digital_ocean.py $(DIMS_ANSIBLE_ARGS) --list-hosts all |\
	       sed 's/ *//g' |\
	       tail -n +2

.PHONY: hosts
hosts:
	$(MAKE) --always-make inventory/hosts 2>/dev/null

inventory/hosts:
	(echo "[droplets]"; ansible -i $(INVENTORY) $(DIMS_ANSIBLE_ARGS) --list-hosts do|sed 's/ *//g'|tail -n +2) |\
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
		$(DIMS_ANSIBLE_ARGS) \
		create-provider.tf.yml

.PHONY: plan
plan: init provider
	terraform plan

.PHONY: graph
graph: graph.png
	@if [[ "$(shell uname -s)" == "Darwin" ]]; then open graph.png; fi
	@if [[ "$(shell uname -s)" == "Linux" && ! -z "$(shell which evince)" ]] ; then (evince graph.png &); fi
	@if [[ "$(shell uname -s)" == "Linux" && ! -z "$(shell which xdg-open)" ]] ; then (xdg-open graph.png &); fi

graph.png: init
	terraform graph | dot -Tpng -o graph.png

$(INVENTORY_GENERATED):
	$(COMMON_SCRIPTS)/terraform.inventory.generate.sh > $(INVENTORY_GENERATED)

.PHONY: newkeypair
newkeypair:
	@if [ $(shell jq -r '.resources' terraform.tfstate) != "null" ]; then \
		echo '[!] Refusing to replace SSH keys while droplets are running'; \
		echo '[!] Use "make destroy" first or manually re-key droplets'; \
		false; \
	fi
	@echo "[+] Generating new SSH key pair"
	ssh-keygen -t rsa -f $(TF_VAR_private_key)

.PHONY: insertpubkey
insertpubkey:
	terraform apply -target=digitalocean_ssh_key.default -auto-approve

.PHONY: removepubkey
removepubkey:
	terraform destroy -target=digitalocean_ssh_key.default --force

.PHONY: create
create: init hosts provider
	$(MAKE) insertpubkey && sleep 2
	terraform apply | tee -a terraform.log | $(call get_domain_var) $(COMMON_SCRIPTS)//keys.host.extract.sh
	! grep -q "Error: Error applying plan:" terraform.log
	$(MAKE) --always-make $(INVENTORY_GENERATED)
	$(MAKE) addhostkeys
	$(MAKE) ping

.PHONY: sshkeys
sshkeys:
	cat terraform.log | $(call get_domain_var) $(COMMON_SCRIPTS)/keys.host.extract.sh > /dev/null

.PHONY: bootstrap
bootstrap:
	(terraform plan | grep -q "No changes") || $(MAKE) create
	ansible-playbook -i $(INVENTORY) \
		$(DIMS_ANSIBLE_ARGS) \
		$(PBR)/playbooks/bootstrap.yml \
		-e host=do

.PHONY: installcerts
installcerts:
	ansible-playbook -i $(INVENTORY) \
		$(DIMS_ANSIBLE_ARGS) \
		$(PBR)/playbooks/certbot-installcert.yml \
		-e host=do

.PHONY: deploy
deploy:
	ansible-playbook -i $(INVENTORY) \
		$(DIMS_ANSIBLE_ARGS) \
		$(ASK_SUDO_PASS) \
		-e@~/.secrets/digital-ocean/secrets.yml \
		master.yml

.PHONY: update
update:
	ansible-playbook -i $(INVENTORY) \
		$(DIMS_ANSIBLE_ARGS) \
		-e@~/.secrets/digital-ocean/secrets.yml \
		--tags updates \
		-e packages_upgrade=yes \
		master.yml

.PHONY: reboot
reboot:
	ansible -i $(INVENTORY) \
		$(DIMS_ANSIBLE_ARGS) \
		--become \
		-m shell \
		-a '/sbin/shutdown -r +1' \
		do
.PHONY: cancel
cancel:
	ansible -i $(INVENTORY) \
		$(DIMS_ANSIBLE_ARGS) \
		--become \
		-m shell \
		-a '/sbin/shutdown -c && echo "[+] Whew! That was close!"' \
		do

.PHONY: addhostkeys
addhostkeys:
	@echo "[+] Adding host keys to known_hosts on localhost"
	ansible-playbook -i $(INVENTORY) \
		$(DIMS_ANSILE_ARGS) \
		$(ASK_SUDO_PASS) \
		$(PBR)/playbooks/do_rekey.yml \
		-e known_hosts_root="$(shell pwd)/known_hosts"
	@echo "[+] Adding host keys to known_hosts on droplets"
	ansible-playbook -i $(INVENTORY) \
		$(DIMS_ANSILE_ARGS) \
		$(PBR)/playbooks/do_rekey.yml \
		-e known_hosts_root="$(shell pwd)/known_hosts" \
		-e host=do

.PHONY: removehostkeys
removehostkeys:
	-ansible-playbook -i $(INVENTORY) \
		$(DIMS_ANSIBLE_ARGS) \
		$(ASK_SUDO_PASS) \
		$(PBR)/playbooks/do_rekey.yml \
		-e remove_keys=true

.PHONY: dumpvars
dumpvars:
	ansible -i $(INVENTORY) \
		$(DIMS_ANSIBLE_ARGS) \
		-m debug -a "var=hostvars[inventory_hostname]" do |\
			pygmentize -ljson |\
			less -R

.PHONY: ping
ping:
	ansible -i $(INVENTORY) \
		$(DIMS_ANSIBLE_ARGS) \
		-m ping do

.PHONY: pre.test
pre.test:
	bats do.bats

.PHONY: post.test
post.test:
	ansible -i $(INVENTORY) \
		$(DIMS_ANSIBLE_ARGS) \
		-m shell \
		-a 'test.runner --terse --tap' \
		do || (echo '[!] Some test(s) failed' && exit 1)
	@echo '[+] All tests passed!'

.PHONY: backup.postgresql
backup.postgresql:
	-ansible-playbook -i $(INVENTORY) \
		$(DIMS_ANSIBLE_ARGS) \
		$(ASK_SUDO_PASS) \
		-e@~/.secrets/digital-ocean/secrets.yml \
		$(PBR)/playbooks/postgresql_backup.yml

.PHONY: backup.letsencrypt
backup.letsencrypt:
	-ansible-playbook -i $(INVENTORY) \
		$(DIMS_ANSIBLE_ARGS) \
		$(ASK_SUDO_PASS) \
		-e@~/.secrets/digital-ocean/secrets.yml \
		$(PBR)/playbooks/letsencrypt_backup.yml \
		-e host=do

.PHONY: destroy
destroy:
	terraform destroy --force
	-$(MAKE) removehostkeys
	-rm -rf fingerprints/ known_hosts/
	-rm -f ansible-digital_ocean.cache
	-rm -f inventory/hosts inventory/nodes-generated.yml
	-rm -f provider.tf graph.png
	-$(MAKE) removepubkey

.PHONY: spotless
spotless: destroy
	-rm -f terraform.log
	-rm -f terraform.tfstate terraform.tfstate.backup

# vim: ft=make:
