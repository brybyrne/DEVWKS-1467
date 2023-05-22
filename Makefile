#Makefile

prep_1467:
	@echo "*** Opening the Lab Guide File ***"
#	xdg-open https://github.com/brybyrne/DEVWKS-1467/blob/main/README.md

provision:
	@echo "*** Provision router ***"
	ansible-playbook provision_rtr1.yaml

yangstart:
	@echo "*** Starting yangsuite ***"
	./yang_up.sh
#	xdg-open http://0.0.0.0

start_1467: yangstart provision prep_1467

cleanup:
	@echo "*** Stopping yangsuite container ***"
	./yang_down.sh