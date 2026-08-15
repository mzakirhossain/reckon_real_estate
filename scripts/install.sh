#!/usr/bin/env bash
# Install this already-fetched app into a Frappe/ERPNext v15 or v16 site.
set -euo pipefail

site="${1:?Usage: bash apps/reckon_real_estate/scripts/install.sh <site-name>}"
app="reckon_real_estate"

if ! command -v bench >/dev/null 2>&1; then
  echo "Run this script from a Frappe Bench environment." >&2
  exit 1
fi

bench --site "$site" install-app "$app"
bench --site "$site" migrate
bench build --app "$app"
bench --site "$site" clear-cache
bench --site "$site" execute "$app.setup.install.validate_installation"
