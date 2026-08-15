#!/usr/bin/env bash
# Verify a completed Reckon Real Estate installation on a Frappe site.
set -euo pipefail

site="${1:?Usage: bash apps/reckon_real_estate/scripts/validate_install.sh <site-name>}"
app="reckon_real_estate"

if ! command -v bench >/dev/null 2>&1; then
  echo "Run this script from a Frappe Bench environment." >&2
  exit 1
fi

bench --site "$site" list-apps
bench --site "$site" execute "$app.setup.install.validate_installation"
