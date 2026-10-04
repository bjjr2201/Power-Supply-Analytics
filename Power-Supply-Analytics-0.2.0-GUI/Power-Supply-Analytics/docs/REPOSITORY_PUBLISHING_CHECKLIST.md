# Repository Publishing Checklist

Before pushing this repository to a GitHub location outside the intended engineering audience, review the following repository-specific assets:

- `load_map_with_magnetid.json` contains facility-specific IP, cabinet, magnet, resistance, and inductance mappings used by the live workflow.
- `ANL_RGB-APS-fullname_horiz.png` is an institutional branding asset. Confirm the intended repository visibility and branding use before public distribution.
- Generated operating data, PMM captures, calibration reports, screenshots, and parallel logs are intentionally excluded from this source baseline and should remain outside source control unless there is a deliberate reason to publish them.
- Do not commit credentials, passwords, private keys, or write-enabled control-system secrets. The current source baseline is designed to operate without embedding them.

For a private/internal engineering repository, the existing load map may be retained as the operational configuration. For a public repository, consider replacing it with a sanitized example and loading the operational map through `CDCU_LOAD_MAP`.
