"""Create the cloud site and restore the authorized local review backup."""
import json
import os
import subprocess
import sys
from pathlib import Path

transfer = Path("/transfer")
site = "opcloud.amplii.online"
credentials = json.loads((transfer / "credentials.json").read_text())
def run(command, **kwargs):
    if subprocess.run(command, **kwargs).returncode:
        sys.exit("Site restore step failed. Password-bearing command arguments are withheld.")

run(["env/bin/python", "/transfer/configure-site.py"])
if os.environ.get("OPCLOUD_EXISTING_SITE") != "1":
    run([
        "bench", "new-site", site, "--db-host", "db",
        "--db-root-password", credentials["db_root_password"],
        "--admin-password", credentials["administrator_password"],
        "--mariadb-user-host-login-scope", "%", "--set-default",
    ])
run([
    "bench", "--site", site, "restore", str(next(transfer.glob("*-database.sql.gz"))),
    "--db-root-password", credentials["db_root_password"],
    "--with-public-files", str(next(p for p in transfer.glob("*-files.tar")
                                   if not p.name.endswith("-private-files.tar"))),
    "--with-private-files", str(next(transfer.glob("*-private-files.tar"))),
    "--admin-password", credentials["administrator_password"],
])
run(["env/bin/python", "/transfer/configure-site.py"],
               env={**os.environ, "OPCLOUD_AFTER_RESTORE": "1"})
run(["bench", "--site", site, "migrate"])
run(["bench", "--site", site, "enable-scheduler"])
