#Makefile

prepenv:
	@echo "*** Creating Virtual Environment ***"
	( \
		python3 -m venv venv; \
		source venv/bin/activate; \
		pip install --upgrade pip; \
		pip install -r requirements.txt; \
)

vagrant:
	@echo "*** Stopping Existing VMs ***"
	vboxmanage list runningvms | sed -E 's/.*\{(.*)\}/\1/' | xargs -L1 -I {} VBoxManage controlvm {} savestate
	@echo "*** Bringing Up the Router ***"
	vagrant up

yangstart:
	@echo "*** Starting yangsuite ***"
	./yang_up.sh

provision_1467:
	@echo "*** Configuring the Router ***"
	python provision/provision_lab.py -hn DEVWKS-1467

prep_1467:
	@echo "*** Opening the Lab Guide File ***"
	open https://github.com/brybyrne/DEVWKS-1467/blob/main/README.md

start_1467: vagrant provision_1467 prep_1467 yangstart

cleanup:
	@echo "*** Destroying the Vagrant box ***"
	vagrant destroy -f
	@echo "*** Stopping yangsuite container ***"
	./yang_down.sh

