# Stackable OpCloud deployment

Target: `opcloud.amplii.online`, AWS Lightsail `ap-southeast-2a` (Sydney), Linux
bundle `small_3_2`: USD 12/month before taxes, backups, or transfer overages.
This is a constrained six-user pilot with 2 GB RAM, 2 vCPUs, 60 GB SSD and 4 GB
swap. Worker capacity and application availability must be checked after restore.

## Build

The image contains source at the revisions in `manifest.json` and the compiled
browser assets already reviewed in the local bench. No database, site settings,
encryption keys, uploaded documents or passwords are included in the image.
The official Frappe builder/base AMD64 image manifests are pinned in the recipe.
`python-dependencies-resolved.txt` records the packages resolved for the initial
image; retain them when rebuilding this release.

Clone `frappe/frappe_docker` at the manifest's revision into a build directory.
Copy this directory's `Containerfile.opcloud` and `python-constraints.txt` into
that build directory. Export
the local bench's sources/assets there with Python 3.12+:

```sh
OPCLOUD_BUILD_CONTEXT=/absolute/build/directory python3 export-snapshot.py
docker buildx build --platform linux/amd64 --load \
  -f Containerfile.opcloud -t stackable-opcloud:20261105 /absolute/build/directory
```

When changing application source, update the manifest and rebuild matching
frontend assets first. Do not mix assets from a different app revision. App
upgrades require a fresh backup and a reviewed database migration.

## Host configuration

`bootstrap.sh` installs Ubuntu's Docker/Compose packages, creates swap, rotates
Docker logs, and disables SSH password/root login. Lightsail's launch script
accepts shell script user data; do not submit a cloud-config YAML document.

`opcloud-compose.yaml` runs MariaDB, two Redis processes, Gunicorn, websocket,
one worker, scheduler, frontend Nginx and Caddy. Only Caddy ports 80/443 publish
to the host. Restrict Lightsail port 22 to the administrator's source IP.
Store a freshly generated `DB_ROOT_PASSWORD` in a mode-0600 `.env` beside it.
Keep backups, site encryption keys and credentials out of Git.

Copy the generated `web-entrypoints/` directory beside Compose before running
any Compose command. Keep `mariadb-client.cnf` beside Compose: it matches the application's plain
database connection across the single host's unpublished Docker network. Enable
verified database TLS if later moving the database to another host. Public web
traffic uses HTTPS through Caddy. The `bench-config` volume contains the bench's
runtime `config/pids` directory. For the initial image, initialize it once with:

```sh
docker compose -f opcloud-compose.yaml run --rm --no-deps --user root \
  --entrypoint bash backend -c 'mkdir -p config/pids && chown -R 1000:0 config /home/frappe/nltk_data'
```

Helpdesk requires Redis Search. The cache image is pinned to Redis 8.10.3,
matching the local bench, and includes `FT.CREATE`. The separate queue Redis
uses 7.4. The shared `nltk-data` volume retains Helpdesk search corpora.

Copy the generated `web-entrypoints/` directory from the build context beside
Compose. It contains the ignored build output for CRM, Helpdesk, HR and roster
HTML routes, paired with the same compiled browser assets as the image. The
export script includes these in both the image source and this overlay.

## Restore and configuration

Create the new site with a fresh database password, then restore the approved
database plus public/private file archives using `bench restore`. Restore the
original site encryption key, reset the Administrator and test-user passwords,
and invalidate OAuth tokens that came from localhost. `configure-site.py`
implements the settings/password/branding steps and expects a protected
`/transfer/credentials.json` and original `*-site_config_backup.json`.

Run it once to set shared configuration and again with
`OPCLOUD_AFTER_RESTORE=1` after database restore. It disables developer mode and
server scripts, mutes outgoing mail, and sets the HTTPS hostname. Public signup and email-link login are disabled until reviewed mail setup.
Start public services only after this step. Run `bench --site opcloud.amplii.online migrate`
and enable the scheduler. No email or outreach is configured by this deployment.

Create a Cloudflare A record `opcloud` pointing at the attached Lightsail static
IP. DNS-only mode allows Caddy to obtain and renew its own public certificate.
If later enabling Cloudflare proxying, retain a valid origin certificate and use
Full (strict) TLS. Never use Flexible mode for this application.

## Operations and important documents

Use private attachments on records with restricted roles. Public attachments
are publicly accessible. The default file limit here is 10 MB per file.
This stack provides no immutable document archive or binary file versioning.

`backup.sh` and the included systemd service/timer schedule server-local backups
at 22:00 UTC (03:00 Maldives). Configure `keep_backups_for_hours=168` to keep
seven days; the site configuration script sets this. Copy the service/timer
into `/etc/systemd/system`, run `systemctl daemon-reload`, then
`systemctl enable --now opcloud-backup.timer`. This does not copy data off-server.

Back up the database, public files, private files and site configuration together
with `bench --site opcloud.amplii.online backup --with-files`, then copy the
backup off the server to a protected location. Keep the encryption key. A backup
on the same Lightsail disk is insufficient. Automated independent backups are a
remaining operational requirement, outside the USD 12 compute bundle. Confirm
an independent restore before making this the only copy of important documents.

Operational commands from the server deployment directory:

```sh
docker compose -f opcloud-compose.yaml ps
docker compose -f opcloud-compose.yaml logs --tail 100 backend worker
docker compose -f opcloud-compose.yaml exec backend bench --site opcloud.amplii.online backup --with-files
docker stats --no-stream
```

Use `stop`/`start` for a temporary service stop. Removing volumes destroys data.
Stopping a Lightsail instance still incurs the monthly bundle charge.
