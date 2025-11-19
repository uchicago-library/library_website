SECRETS_PY_PATH = ~/lw-config
SETTINGS_PATH = ./library_website/settings
CURRENT_BRANCH = $$(git -C $(SECRETS_PY_PATH) symbolic-ref --short HEAD)

.PHONY: docker
docker: secrets docker-clean docker-cache

.PHONY: docker-cache
docker-cache: secrets
	./docker-setup.sh

.PHONY: docker-clean
docker-clean:
	./docker-cleanup.sh

.PHONY: secrets
secrets:
	git -C $(SECRETS_PY_PATH) pull origin $(CURRENT_BRANCH)
	$(RM) $(SETTINGS_PATH)/secrets.py || true
	install -m 444 $(SECRETS_PY_PATH)/secrets.py $(SETTINGS_PATH)

.PHONY: clean
clean:
	$(RM) $(SETTINGS_PATH)/secrets.py || true
