# Security

SEDGE Community is a local review and prototyping tool. It has no authentication,
authorisation, tenancy or rate-limiting gateway. Keep the default loopback binding.
Do not expose the API or preview server to the Internet or untrusted networks.

The API accepts only a bounded configuration, never file paths, code or uploads.
It writes no run files and reads no private datasets. Each request is limited to
50,000 rows, but repeated requests still consume CPU and memory. Use an
authenticated, rate-limited reverse proxy and an appropriate production server
before considering any shared deployment.

Dependencies need ongoing security review. Before public release, run `npm audit`
and a Python dependency audit, review brand permissions, and test in the intended
environment. Send security reports privately to XILBI using the contact channel
on <https://www.xilbi.com/> rather than including sensitive details in public issues.
