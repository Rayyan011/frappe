#!/usr/bin/env python3
"""Export versioned app source and the reviewed local bench's browser assets.

Requires Python 3.12+, Docker, and the local crm-frappe-1 bench. This deliberately
does not export sites, database backups, credentials, logs, or configuration.
"""
import io
import json
import os
import subprocess
import tarfile
from pathlib import Path

here = Path(__file__).resolve().parent
framework = here.parents[1]
manifest = json.loads((here / "manifest.json").read_text())
container = os.environ.get("SOURCE_BENCH_CONTAINER", "crm-frappe-1")
output = Path(os.environ.get("OPCLOUD_BUILD_CONTEXT", str(here))) / "snapshot"
output.mkdir(parents=True, exist_ok=True)

def extract(data, destination, local_assets=False):
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        for member in archive.getmembers():
            if member.name.startswith("/") or ".." in Path(member.name).parts:
                raise ValueError(f"Unsafe archive member: {member.name}")
            if member.issym() and member.linkname.startswith("/"):
                if not member.linkname.startswith("/home/frappe/frappe-bench/apps/"):
                    raise ValueError(f"Unexpected asset link: {member.name}")
        archive.extractall(destination, filter="fully_trusted" if local_assets else "data")

for app, revision in manifest["apps"].items():
    if app == "frappe":
        command = ["git", "-C", str(framework), "archive", revision]
    else:
        command = ["docker", "exec", container, "git", "-C",
                   f"/home/frappe/frappe-bench/apps/{app}", "archive", revision]
        current = subprocess.check_output(command[:-2] + ["rev-parse", "HEAD"], text=True).strip()
        if current != revision:
            raise ValueError(f"{app} local bench differs from manifest; review before exporting")
    target = output / "apps" / app
    target.mkdir(parents=True, exist_ok=True)
    extract(subprocess.check_output(command), target)
    public = f"apps/{app}/{app}/public"
    data = subprocess.check_output(["docker", "exec", container, "tar", "-C",
                                   "/home/frappe/frappe-bench", "-cf", "-", public])
    extract(data, output, local_assets=True)
    print("Exported", app, revision)

data = subprocess.check_output(["docker", "exec", container, "tar", "-C",
                               "/home/frappe/frappe-bench/sites", "-cf", "-", "assets"])
extract(data, output, local_assets=True)
(output / "apps.txt").write_text("\n".join(manifest["apps"]) + "\n")
print("Snapshot ready at", output)
