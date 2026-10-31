---
name: aws-login-cli-panic
description: HUIT aws-login SAML CLI 2.0.3 `login_all` panics after the Okta push (nil map in okta.KeepMeSignedIn) as of 2026-10-26; use the `aws login` console-attach path instead
metadata:
  type: reference
---

On 2026-10-26, `aws-login login_all` (HUIT aws-login-saml-cli 2.0.3, built
from `~/workshop/aws-login-saml-cli`) got through "Waiting for user to ack"
and then crashed:

```
panic: interface conversion: interface {} is nil, not map[string]interface {}
aws-login/okta.KeepMeSignedIn(...) okta/okta.go:177
```

So the "one push refreshes every `*-login` profile" path is broken until the
CLI is fixed (Okta's keep-me-signed-in response shape presumably changed, or
the push timed out and the code does not check). The `aws login`
console-attach path (branch B in the `huit-aws:aws-login` skill) worked
fine for `admints-prod` and `admints-dev`, one console session each; console
multi-session lets both coexist without logging out.

**How to apply:** when the aws-login skill would pick branch A, expect this
panic and go straight to branch B unless the CLI has been updated past 2.0.3.
