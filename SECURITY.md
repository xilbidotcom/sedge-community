# Security

SEDGE Community is a local review and prototyping tool. It has no authentication,
authorisation, tenancy or rate-limiting gateway. Keep the default loopback binding.
Do not expose the API or preview server to the Internet or untrusted networks.

The API accepts only a bounded configuration, never file paths, code or uploads.
It writes no run files and reads no private datasets. Each request is limited to
50,000 rows, but repeated requests still consume CPU and memory. Use an
authenticated, rate-limited reverse proxy and an appropriate production server
before considering any shared deployment.

## Reporting a vulnerability

Use [private vulnerability reporting](https://github.com/xilbidotcom/sedge-community/security/advisories/new),
enabled for this repository. If that channel is unavailable, request a private
security contact through the contact form on <https://www.xilbi.com/>. Do not send
an exploit, secret or private dataset in the initial contact-form enquiry and
never include it in public issues.

## Supported versions and updates

Security fixes target the latest Community 1.x release. There is no guaranteed
response time or support commitment for earlier releases. Keep Python, Node and
dependencies supported and review advisories when updating the lock files.

Run `npm --prefix web audit` and `pip-audit -r requirements.lock` before release.
The audit queries public advisory services using dependency names and versions;
it does not upload source code. A clean result is not proof of security.

Never upload `.env`, credentials, logs, private datasets or the main SEDGE archive.
Back up any downloaded results separately; this service has no server-side run
storage, authentication or deletion API.
