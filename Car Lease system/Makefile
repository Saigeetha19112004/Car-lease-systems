.PHONY: export-openapi test-e2e

export-openapi:
	python scripts/export_openapi.py

test-e2e:
	cd apps/web && npm ci && npx playwright install --with-deps && npm run test:e2e
