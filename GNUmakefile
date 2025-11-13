LOCAL_PY_PATH = ~/wagtail-local
SETTINGS_PATH = ./library_website/settings

.PHONY: docker
docker: local
	./docker-cleanup.sh
	./docker-setup.sh

.PHONY: local
local:
	git -C $(LOCAL_PY_PATH) pull
	rm -f $(SETTINGS_PATH)/local.py
	install -m 444 $(LOCAL_PY_PATH)/local.py $(SETTINGS_PATH)

