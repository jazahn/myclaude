---
name: harvard-vpn-google-oauth-youtube-block
description: gcloud auth login (and any Google Workspace OAuth sign-in) fails with "This site can't be reached" / ERR_SOCKET_NOT_CONNECTED on accounts.youtube.com when the local network blocks YouTube, even on the Harvard VPN, because Cisco Secure Client dynamically excludes youtube.com (and googleapis.com, gstatic.com, ...) from the tunnel. Fix is a hotspot for the browser step; diagnose with `vpn stats`. Found 2026-10-04.
metadata:
  type: reference
---

**Symptom.** `gcloud auth login` (either the default loopback flow or
`--no-launch-browser`) gets through HarvardKey, then right after choosing the
g.harvard.edu account the browser lands on
`https://accounts.youtube.com/accounts/SetSID?...` with "This site can't be
reached", `ERR_SOCKET_NOT_CONNECTED`. Google's Workspace sign-in always bounces
through `accounts.youtube.com` once to sync the session cookie, so this breaks
every Google OAuth login, not just gcloud. An old gcloud is NOT the cause.

**Why the VPN doesn't help.** The Harvard Cisco Secure Client connection
(`vpn.harvard.edu`, any group) reports `Tunnel Mode: Tunnel All Traffic` but the
headend pushes a **Dynamic Tunnel Exclusion** list that sends these domains
straight out the local network: `youtube.com ytimg.com youtube-nocookie.com
googleapis.com gstatic.com gmail.com` plus Netflix, Zoom, Teams, Office 365,
Apple, Amazon, Spotify, etc. So a café/hotel network that blocks streaming
drops the `accounts.youtube.com` TLS handshake (SNI filtering: the same Google
IP works under a different server name). Cannot be disabled client-side; the
exclusion list is server policy and the local profile XML is rewritten on
connect. Switching VPN groups most likely carries the same list.

**Diagnose in 10 seconds.**
```sh
/opt/cisco/secureclient/bin/vpn stats | grep -E 'Tunnel Mode|Dynamic Tunnel'
route -n get 142.250.191.14          # Google IP -> en0 means it bypasses the tunnel
curl -s -o /dev/null -w '%{http_code}\n' --max-time 10 https://accounts.youtube.com/
```
`lsof -iTCP:8085` being empty is normal for `--no-launch-browser` (no local
listener in that mode) and is NOT the problem.

**Fix.** Leave `gcloud auth login --no-launch-browser` waiting in the terminal,
switch the browser to a phone hotspot (or any network that doesn't block
YouTube), finish the sign-in, copy the verification code, switch back, paste.
The code is network-independent. Reconnect the VPN afterwards: nonprod Apigee
needs it. Longer term: ask HUIT networking to drop `youtube.com` (or at least
`accounts.youtube.com`) from the exclusion list.

**Side effect to remember.** `googleapis.com` is excluded too, so
`apigee.googleapis.com` management calls also bypass the tunnel and are subject
to whatever the local network allows.

**gcloud install note (this Mac).** Homebrew cask `gcloud-cli`; update with
`brew upgrade --cask gcloud-cli`, not `gcloud components update`.

Related: [[huit-github-enterprise-api]] (other HUIT auth gotchas).
