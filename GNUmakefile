LOCAL_PY_PATH = ~/lw-config
SETTINGS_PATH = ./library_website/settings

.PHONY: docker
docker: local clean docker-cache

.PHONY: docker-cache
docker-cache: local
	./docker-setup.sh

.PHONY: clean
clean:
	./docker-cleanup.sh

.PHONY: local
local:
	git -C $(LOCAL_PY_PATH) pull
	$(RM) $(SETTINGS_PATH)/local.py
	install -m 444 $(LOCAL_PY_PATH)/local.py $(SETTINGS_PATH)
