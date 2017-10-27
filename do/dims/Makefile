# vim:ft=make:

SHELL=/bin/bash
INVENTORY=../../inventory

.PHONY: help
help:
	@echo "Usage: make [something]"
	@echo ""
	@echo "Where 'something' is one of these:"
	@echo " hosts - show list of hosts in group 'do'"
	@echo " plan - show the terraform plan for the current state"
	@echo " templates - generate terraform .tf templates for hosts in group 'do'"
	@echo " create - applies terraform plan to create droplets for hosts in group 'do'"
	@echo " destroy - destroys droplets for hosts in group 'do'"
	@echo " graph - generate terraform graph (output is 'graph.png')"
	@echo " ping - does Ansible ad-hoc ping of hosts in group 'do'"
	@echo " addkeys - adds SSH host public keys to selected known_hosts files"
	@echo " removekeys - removes SSH host public keys from selected known_hosts files"
	@echo " dumpvars - produces Ansible debug output of vars for hosts in group 'do'"
	@echo ""
	@echo " The default if you just type 'make' is the same as 'make pdf'"

.PHONY: hosts
hosts:
	@ansible -i $(INVENTORY)/DO/digital_ocean.py --list-hosts all|sed 's/ *//g'|tail -n +2

.PHONY: templates
templates:
	-ansible-playbook -i $(INVENTORY) -vvvv create-tf.yml

.PHONY: plan
plan:
	terraform plan

.PHONY: graph
graph: graph.png
	@[ "$(shell uname -s)" == "Darwin" ] && open graph.png
	@[ "$(shell uname -s)" == "Linux" && ! -z "$(which evince)" ] && evince graph.png &
	@[ "$(shell uname -s)" == "Linux" && ! -z "$(which xdg-open)" ] && xdg-open graph.png &

graph.png:
	terraform graph | dot -Tpng -o graph.png

.PHONY: create
create: templates
	terraform apply | tee terraform.log
	$(MAKE) hosts | awk -f generate-inventory.awk < terraform.log > $(INVENTORY)/DO/nodes-droplets.yml
	$(MAKE) addkeys
	$(MAKE) dumpvars
	$(MAKE) ping

.PHONY: addkeys
addkeys:
	-ansible-playbook -i $(INVENTORY) ../../playbooks/do_rekey.yml --ask-sudo-pass

.PHONY: removekeys
removekeys:
	-ansible-playbook -i $(INVENTORY) ../../playbooks/do_rekey.yml -e remove_keys=true --ask-sudo-pass

.PHONY: dumpvars
dumpvars:
	ansible -i $(INVENTORY) -m debug -a "var=hostvars[inventory_hostname].ansible_host" do

.PHONY: ping
ping:
	ansible -i $(INVENTORY) -m ping do

.PHONY: destroy
destroy:
	terraform destroy --force
	-$(MAKE) removekeys
	-rm -f ansible-digital_ocean.cache
	-rm -f $(INVENTORY)/DO/nodes-droplets.yml

.PHONY: spotless
spotless:
	$(MAKE) hosts | parallel 2>/dev/null echo rm -f {}
