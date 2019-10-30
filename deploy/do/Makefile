# vim:ft=make:

SHELL=/bin/bash
TMP:=$(shell psec environments path --tmpdir)
PLAN:=$(TMP)/tfplan
DATE=$(shell date +%Y%m%d%H%M)
LAST_LOGFILE=$(shell ls -1 terraform-*.log 2>/dev/null | tail -n 1 2>/dev/null || echo "")
LOGFILE=$(shell [ ! -z "$(LAST_LOGFILE)" ] && echo "$(LAST_LOGFILE)" || echo "terraform-$(DATE).log")
#LOGFILE=terraform-$(DATE).log
PBR=$(shell pwd)/ansible-dims-playbooks
CLOUD=do
INVENTORY=$(PBR)/environments/$(CLOUD)/inventory
#INVENTORY=$(PBR)/environments/$(TF_VAR_environment)/inventory
INVENTORY_GENERATED=inventory/nodes-generated.yml
COMMON_SCRIPTS=$(PBR)/files/common-scripts
TFSTATE:=$(shell psec utils tfstate backend --path)
PRIVATE_KEY_FILE=$(shell psec secrets get do_private_key_file 2>/dev/null || echo "")
KEYNAME=$(shell psec secrets get do_keyname 2>/dev/null || echo "")
SSH_KEY_ID=$(shell psec secrets get do_ssh_key_id 2>/dev/null || echo "")

# Ensure Digital Ocean env vars set
DO_API_VERSION=2
DO_API_TOKEN=$(shell psec -q secrets get do_api_token 2>/dev/null || echo "")

GROUP_NAME:=$(shell psec environments default)
REQUIRED_APT_PACKAGES=bats ansible git make jq opendkim-tools
REQUIRED_BREW_PACKAGES=bats ansible git make jq opendkim-tools

# Generate SSH public key fingerprint for terraform to use
SSH_KEY_ID=$(shell ssh-keygen -E md5 -lf ${TF_VAR_ssh_key_id}.pub|awk '{print $$2}'|sed 's/^[Mm][Dd]5://')
TF_VARS=

# The following checks to see if local sudo requires a password. If so,
# the flag is added to the command line when invoking Ansible.
ASK_BECOME_PASS:=$(shell ansible -i localhost, -m shell -a date --become localhost -c local 2>/dev/null | grep -q "password is required" && echo "--ask-become-pass")

# define get_domain_var
#    $(shell ansible -i $(INVENTORY) -m debug -a 'msg=^DIMS_DOMAIN={{ dims_domain }}^' --one-line $(GROUP_NAME) | head -n 1 | cut -d^ -f 2)
# endef
define get_domain_var
   $(shell echo DIMS_DOMAIN=`psec secrets get do_domain`)
endef

# By nature of being defined first, 'make help' is the default.

DEBUG_STRING:=var=vars
debug:
	@echo ASK_BECOME_PASS=$(ASK_BECOME_PASS)
	psec -E run -- ansible -i $(INVENTORY) \
			-i inventory/ \
			-m debug \
			-a "$(DEBUG_STRING)" \
			$(GROUP_NAME)

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
	@echo " dumpjson - dump all DigitalOcean image related information in JSON"
	@echo " dumpvars - produces Ansible debug output of vars for hosts in group '$(GROUP_NAME)'"
	@echo " updatefacts - run 'ansible -m setup' to refresh cached facts"
	@echo " images - lists available images"
	@echo " regions - lists available regions"
	@echo " provider - generate terraform provider.tf and user-data file for creating nodes in group '$(GROUP_NAME)'"
	@echo " plan - show the terraform plan for the current state"
	@echo " refresh - refresh terraform state"
	@echo " graph - generate terraform graph (output is 'graph.png')"
	@echo " newkeypair - generate a new SSH user keypair"
	@echo " insertpubkey - insert SSH public key on cloud provider"
	@echo " removepubkey - remove SSH public key on cloud provider"
	@echo " addhostkeys - adds SSH host public keys to selected known_hosts files"
	@echo " removehostkeys - removes SSH host public keys from selected known_hosts files"
	@echo " destroy - destroys droplets and related resources for hosts in group '$(GROUP_NAME)'"
	@echo " spotless - remove terraform log and state files"
	@echo ""
	@echo " ---- Provisioning functions ----"
	@echo " create - applies terraform plan to create droplets for hosts in group '$(GROUP_NAME)'"
	@echo " ping - does Ansible ad-hoc ping of hosts in group '$(GROUP_NAME)'"
	@echo " bootstrap - create, then run bootstrap.yml and ca-certs.yml playbooks"
	@echo " bootstrap-opendkim - just create opendkim keys and terraform modules"
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
init: $(TFSTATE) ansible.cfg

ansible.cfg:
	wget https://raw.githubusercontent.com/ansible/ansible/devel/examples/ansible.cfg
	patch ansible.cfg < diffs.ansible_cfg

$(TFSTATE):
	psec utils tfstate backend
	terraform init

.PHONY: prerequisites
prerequisites:
	if [ "$(shell uname -s)" = "Darwin" ]; then \
		brew install $(REQUIRED_BREW_PACKAGES); \
	elif [ "$(shell uname -s)" = "Linux" ]; then \
		sudo apt-get install $(REQUIRED_APT_PACKAGES); \
	else \
		echo "Not prepared to handle prerequisites for $(shell uname -s)"; \
		exit 1; \
	fi
	if [ ! -d venv ]; then \
		virtualenv venv; \
		venv/bin/pip install -r requirements.txt; \
	fi; \

digital_ocean.py:
	wget https://raw.githubusercontent.com/ansible/ansible/devel/contrib/inventory/digital_ocean.py

.PHONY: droplets
droplets: digital_ocean.py
	@python digital_ocean.py --list | python -m json.tool
	@# ansible -i digital_ocean.py --list-hosts all $(DIMS_ANSIBLE_ARGS) |\
	       sed 's/ *//g' |\
	       tail -n +2

# inventory/hosts:
#	@(echo "[$(GROUP_NAME)]"; \
#	 for I in $(shell python digital_ocean.py --list | jq -rc '.all.hosts[]' | sort); do echo "  $$I"; \
#	 done) | tee inventory/hosts

.PHONY: etchosts
etchosts:
	@#ansible -i $(INVENTORY) -m debug -a 'msg="{{ hostvars[inventory_hostname].ansible_default_ipv4.address }} {{ inventory_hostname }}"' $(GROUP_NAME) |\
		grep '\"msg\":' |\
		awk -F\" '{ print $$4; }'
	@psec -E run -- ansible -i $(INVENTORY) \
			-i inventory/ \
			-m debug \
			-a 'msg="{{ hostvars[inventory_hostname].ansible_host }} {{ inventory_hostname }}"' $(GROUP_NAME) |\
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
	@doctl --access-token "$(DO_API_TOKEN)" compute image list-user

.PHONY: regions
regions:
	curl -X GET --silent "https://api.digitalocean.com/v2/images?per_page=999" -H "Authorization: Bearer $(DO_API_TOKEN)" |\
		jq -rc '.images[] | select(.slug | length >= 1) | .regions' | sort | uniq

.PHONY: provider
provider:
	psec -E run -- ansible-playbook -i $(INVENTORY) \
		-i inventory \
		create-provider.tf.yml \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: plan
plan: $(PLAN)
	psec -E run -- terraform show $(PLAN)

# Generate plan in the secrets environment directory (see definintion of PLAN variable
# above for location). This keeps the plan (which contains secrets) outside of the
# source repository for greater security against secrets leaks.

$(PLAN): init provider
	psec -E run -- terraform plan $(TF_VARS) -out=$(PLAN)
	# TODO(dittrich): Remove?   $(MAKE) --always-make $(INVENTORY_GENERATED)

.PHONY: refresh
refresh:
	psec -E run -- terraform refresh $(TF_VARS)

.PHONY: graph
graph: graph.png
	@if [[ "$(shell uname -s)" == "Darwin" ]]; then open graph.png; fi
	@if [[ "$(shell uname -s)" == "Linux" && ! -z "$(shell which evince)" ]] ; then (evince graph.png &); fi
	@if [[ "$(shell uname -s)" == "Linux" && ! -z "$(shell which xdg-open)" ]] ; then (xdg-open graph.png &); fi

graph.png: init
	psec -E run -- terraform graph $(TF_VARS) | dot -Tpng -o graph.png

$(INVENTORY_GENERATED):
	$(COMMON_SCRIPTS)/terraform.inventory.generate.sh $(GROUP_NAME) > $(INVENTORY_GENERATED)

.PHONY: newkeypair
newkeypair:
	@if [ -z "$(PRIVATE_KEY_FILE)" -o "$(PRIVATE_KEY_FILE)" == "None" ]; then echo '[-] No private key file name set'; exit 1; fi
	@if [ "$(shell [ ! -f \"$(TFSTATE)\" ] && echo 'null' || jq -r '.resources' $(TFSTATE))" != "null" ]; then \
	        echo '[!] Refusing to replace SSH keys while droplets are running'; \
	        echo '[!] Use "make destroy" first or manually re-key droplets'; \
	        false; \
	 fi
	@echo "[+] Generating new SSH key pair \"$(PRIVATE_KEY_FILE)\""
	ssh-keygen -t rsa -f "$(PRIVATE_KEY_FILE)"
	psec secrets set do_ssh_key_id="$(shell ssh-keygen -E md5 -lf $(PRIVATE_KEY_FILE).pub|awk '{print $$2}'|sed 's/^[Mm][Dd]5://')"
	@echo MD5 fingerprint: `psec secrets get do_ssh_key_id`
	ssh-add "$(PRIVATE_KEY_FILE)" || true

.PHONY: insertpubkey
insertpubkey:
	@# psec -E run -- terraform apply -target=digitalocean_ssh_key.default -auto-approve
	@doctl --access-token "$(DO_API_TOKEN)" compute ssh-key import "$(KEYYNAME)" --public-key-file "$(PRIVATE_KEY_FILE).pub"
	@echo '[+] Available keys in DigitalOcean:'
	@doctl --access-token "$(DO_API_TOKEN)" compute ssh-key list

.PHONY: removepubkey
removepubkey:
	psec -E run -- terraform destroy $(TF_VARS) -target=digitalocean_ssh_key.default

.PHONY: create
create:
	psec --elapsed -E run -- terraform apply $(PLAN) | tee $(LOGFILE)
	! grep "^Error: Error" $(LOGFILE)
	@# $(MAKE) --always-make $(INVENTORY_GENERATED)
	psec ssh known-hosts extract $(LOGFILE)
	$(MAKE) addhostkeys
	$(MAKE) ping

.PHONY: bootstrap
bootstrap:
	@# (psec -E run -- terraform plan $(TF_VARS) | grep -q "No changes") || $(MAKE) create
	psec -E run -- ansible-playbook -i $(INVENTORY) \
	        -i inventory \
		$(PBR)/playbooks/bootstrap.yml \
		-e host=$(GROUP_NAME) \
		-e ansible_user='root' \
		$(DIMS_ANSIBLE_ARGS)
	$(MAKE) bootstrap-opendkim

.PHONY: bootstrap-opendkim
bootstrap-opendkim:
	psec -E run -- ansible-playbook -i $(INVENTORY) \
	        -i inventory \
		$(ASK_BECOME_PASS) \
		-e@"$(shell psec secrets path)" \
		--tags opendkim-genkey \
		master.yml \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: installcerts
installcerts:
	psec -E run -- ansible-playbook -i $(INVENTORY) \
	        -i inventory \
		$(PBR)/playbooks/certbot-installcert.yml \
		-e host=$(GROUP_NAME) \
		$(DIMS_ANSIBLE_ARGS)

# TODO(dittrich): Remove the trident_backup_restorefrom after debugging. :(
.PHONY: deploy
deploy:
	psec -E run -- ansible-playbook -i $(INVENTORY) \
	        -i inventory \
		--ask-become-pass \
		-e@"$(shell psec secrets path)" \
		-e"psec_environment=$(shell psec environments default)" \
		-e trident_backup_restorefrom='' \
		master.yml \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: update
update:
	psec -E run -- ansible-playbook -i $(INVENTORY) \
	        -i inventory \
		-e@"$(shell psec secrets path)" \
		-e"psec_environment=$(shell psec environments default)" \
		--tags updates \
		-e packages_upgrade=yes \
		master.yml \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: reboot
reboot:
	psec -E run -- ansible-playbook -i $(INVENTORY) \
	        -i inventory \
		--become \
		-e "target=$(GROUP_NAME)" \
		-e "psec_environment=$(shell psec environments default)" \
		$(PBR)/playbooks/host_reboot.yml \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: cancel
cancel:
	psec -E run -- ansible -i $(INVENTORY) \
	        -i inventory \
		--become \
		-m shell \
		-a '/sbin/shutdown -c && echo "[+] Whew! That was close!"' \
		$(GROUP_NAME) \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: addhostkeys
addhostkeys:
	@echo "[+] Adding host keys to known_hosts on localhost"
	psec ssh known-hosts add --ask-become-pass
	psec ssh config --clean
	@echo "[+] Adding host keys to known_hosts on droplets"
	psec -E run -- ansible-playbook -i $(INVENTORY) \
	        -i inventory \
		$(ASK_BECOME_PASS) \
		$(DIMS_ANSILE_ARGS) \
		$(PBR)/playbooks/do_rekey.yml \
		-e known_hosts_root="$(shell pwd)/known_hosts" \
		-e host=$(GROUP_NAME)

.PHONY: removehostkeys
removehostkeys:
	-psec -E run -- ansible-playbook -i $(INVENTORY) \
	        -i inventory \
		$(ASK_BECOME_PASS) \
		$(PBR)/playbooks/do_rekey.yml \
		-e remove_keys=true \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: dumpvars
dumpvars:
	psec -E run -- ansible -i $(INVENTORY) \
	        -i inventory \
		-m debug -a "var=hostvars[inventory_hostname]" $(GROUP_NAME) \
		$(DIMS_ANSIBLE_ARGS) |\
			pygmentize -ljson |\
			less -R
.PHONY: updatefacts
updatefacts:
	psec -E run -- ansible -i $(INVENTORY) \
	        -i inventory \
		-m setup $(GROUP_NAME) \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: ping
ping:
	psec -E run -- ansible -i $(INVENTORY) \
	        -i inventory \
		-m ping $(GROUP_NAME)

.PHONY: pre.test
pre.test:
	psec -E run -- bats do.bats

.PHONY: post.test
post.test:
	psec -E run -- ansible -i $(INVENTORY) \
	        -i inventory \
		-m shell \
		-a 'test.runner --terse --tap' \
		$(GROUP_NAME) \
		$(DIMS_ANSIBLE_ARGS) || (echo '[!] Some test(s) failed' && exit 1)
	@echo '[+] All tests passed!'

.PHONY: backup.trident
backup.trident:
	-psec -E run -- ansible-playbook -i $(INVENTORY) \
	        -i inventory \
		$(ASK_BECOME_PASS) \
		-e@"$(shell psec secrets path)" \
		$(PBR)/playbooks/trident_backup.yml \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: restore.trident
restore.trident:
	-psec -E run -- ansible-playbook -i $(INVENTORY) \
	        -i inventory \
		$(ASK_BECOME_PASS) \
		-e@"$(shell psec secrets path)" \
		$(PBR)/playbooks/trident_restore.yml \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: backup.letsencrypt
backup.letsencrypt:
	-psec -E run -- ansible-playbook -i $(INVENTORY) \
	        -i inventory \
		$(ASK_BECOME_PASS) \
		-e@"$(shell psec secrets path)" \
		$(PBR)/playbooks/letsencrypt_backup.yml \
		-e host=$(GROUP_NAME) \
		$(DIMS_ANSIBLE_ARGS)

.PHONY: destroy
destroy:
	psec -E run -- terraform destroy $(TF_VARS) --force && rm $(PLAN)
	-$(MAKE) removepubkey
	-$(MAKE) removehostkeys
	-$(MAKE) clean

.PHONY: clean
clean:
	-rm -rf {fingerprints,known_hosts,user-data}/
	-rm -f ansible-digital_ocean.cache
	-rm -f inventory/hosts
	-rm -f inventory/nodes-generated.yml
	-rm -f .bootstrapped
	-rm -f provider.tf
	-rm -f graph.png

.PHONY: spotless
spotless: destroy
	-rm -f terraform-*.log
	-rm -f digital_ocean.py
	-rm -f $(TFSTATE)
	-rm -f $(TFSTATE).backup

# vim: ft=make:
