.PHONY: rebuild rebuild-site preview preview-demo deploy-firebase

PORT ?= 8767
FIREBASE_PROJECT ?=

rebuild:
	python3 build_all.py

rebuild-site:
	python3 build_all.py --skip-demo

preview:
	python3 -m http.server $(PORT) --bind 127.0.0.1 --directory site

preview-demo:
	python3 -m http.server $(PORT) --bind 127.0.0.1 --directory demo

deploy-firebase:
	@if [ -n "$(FIREBASE_PROJECT)" ]; then \
		firebase deploy --project "$(FIREBASE_PROJECT)"; \
	else \
		firebase deploy; \
	fi
