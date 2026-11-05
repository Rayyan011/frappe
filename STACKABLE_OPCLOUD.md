# Stackable OpCloud

Stackable OpCloud is Stackable's branded Frappe installation. Technical app names
and upstream license notices stay intact so the other Frappe apps remain compatible.

## Apply the branding

Deploy this fork's `stackables-branding` branch as the Framework app, build its
assets as part of the production image, then run:

```sh
bench --site YOUR_SITE execute frappe.stackable_opcloud.apply_branding
```

The command updates Website Settings, Navbar Settings, and System Settings. It
does not rename ERPNext Company records or change existing user permissions.
The supplied image's original `Stackables` wordmark is preserved. The product
title is `Stackable OpCloud`.

CRM and Helpdesk have independent frontend branding settings; the Framework
branding does not replace every logo in those apps.

## Logo provenance

`frappe/public/images/stackable-opcloud/logo.png` is a transparent PNG derived
from the user's supplied JPEG using the built-in imagegen tool. No customer
documents, database backups, or credentials are included in this repository.

Prompt: Remove only the white/off-white background, including the white
negative-space channels inside the stacked S emblem and letter counters, to
genuine alpha transparency. Preserve the solid black emblem, proportions,
edges, layout, and exact wordmark `Stackables`. No redesign, shadows, painted
checkerboard, or additional text.

## Hosting target

The proposed pilot is one AWS Lightsail Linux instance in Mumbai, 2 vCPUs,
2 GB RAM, and 60 GB SSD, at the advertised USD 12/month server price before
tax, snapshots, and transfer overages. This small instance needs swap and
conservative worker counts; capacity has not yet been verified. Build the image
off-server. AWS CLI authentication may use a different region from deployment.

The intended hostname is `opcloud.amplii.social`, subject to DNS access and TLS
setup. Do not repoint the existing `amplii.social` website.

## Important documents

Use private attachments and restrict access to the parent records. Frappe
record change history is not equivalent to binary-file version retention or
an immutable document archive. Back up the database, public files, private
files, and the site configuration/encryption key together. Keep a protected
copy outside the instance and verify restoration before treating the service
as the sole store for important documents. The instance price does not include
an independently stored backup service.
