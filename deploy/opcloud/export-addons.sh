#!/usr/bin/env bash
set -euo pipefail
# Export only versioned app source and generated frontend assets from a local bench.
# Do not include sites, databases, configuration, backups, or credentials.
bench_container=${SOURCE_BENCH_CONTAINER:-crm-frappe-1}
output_dir=${1:?Pass an output directory}
mkdir -p "$output_dir/apps"
for app in wiki drive insights; do
  mkdir -p "$output_dir/apps/$app"
  docker exec "$bench_container" git -C "/home/frappe/frappe-bench/apps/$app" archive HEAD | tar -xf - -C "$output_dir/apps/$app"
  docker exec "$bench_container" tar -C "/home/frappe/frappe-bench/apps/$app" -cf - "$app/public" | tar -xf - -C "$output_dir/apps/$app"
done
for entry in wiki/wiki/www/wiki-app.html drive/drive/www/drive.html insights/insights/www/insights.html insights/insights/www/insights_v2.html; do
  docker cp "$bench_container:/home/frappe/frappe-bench/apps/$entry" "$output_dir/apps/$entry"
done
docker cp "$bench_container:/home/frappe/frappe-bench/sites/assets/assets.json" "$output_dir/new-assets.json"
