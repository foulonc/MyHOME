# Changelog

Modifications made in this fork, relative to
[`anotherjulien/MyHOME`](https://github.com/anotherjulien/MyHOME). Recorded to
satisfy AGPL-3.0 §5(a), which requires a modified work to carry prominent
notices stating that it was changed.

## 0.9.5 — 2026-09-06

Ownership and documentation only. **No functional change**: the integration
code is identical to 0.9.4, so there is no need to rush this onto a working
installation.

- `codeowners` set to `@foulonc`. The fork is maintained here, and issues filed
  against it should not page the original author.
- `README.md` rewritten for this fork: what it is, why it exists, what it
  fixes, how to install it, and the licence-required fork notice and
  attribution.
- This changelog added, recording every modification relative to upstream as
  AGPL-3.0 §5(a) requires.
- Dependency mirrored: [`foulonc/OWNd`](https://github.com/foulonc/OWNd)
  tagged [`0.7.48`](https://github.com/foulonc/OWNd/releases/tag/0.7.48) at the
  commit that matches the PyPI release byte for byte. The manifest still
  requires `OWNd==0.7.48` from PyPI on purpose; see the README for why
  pointing it at the mirror would make startup depend on GitHub.

## 0.9.4 — 2026-09-06

First release of this fork. Fixes only; no new features and no configuration
changes. `myhome.yaml` and every `unique_id` are unchanged, so an existing
installation keeps all of its entities and their history.

### Carried from upstream, unreleased there

- Nested device schemas run their post-processing again on Home Assistant
  2026.9+, where `probatio` compiles a nested `Schema` without going through an
  overridden `__call__`. Upstream PR
  [#223](https://github.com/anotherjulien/MyHOME/pull/223) by
  [@cedric1067](https://github.com/cedric1067), merged upstream on 2026-09-04
  but not part of any upstream release.

### Fixed in this fork

- **Options dialog no longer returns HTTP 500.** `OptionsFlow.config_entry` has
  been a read-only property without a setter since Home Assistant 2024.11, so
  `MyhomeOptionsFlowHandler.__init__` raised `AttributeError`. It keeps its own
  reference now.
- **Device registry no longer receives a list.** OWNd reports `manufacturer` as
  a list for some gateways. Home Assistant warns about this today and rejects
  non-string values from 2026.12. `manufacturer`, `model` and `sw_version` are
  coerced through a helper.
- **Device lookup modernised.** `device_registry.devices` used as a mapping is
  removed in Home Assistant 2027.9; replaced with
  `dr.async_entries_for_config_entry()`.
- **Platform unload fixed.** Unloading platforms one at a time with
  `async_forward_entry_unload()` left the entry half-loaded, so reloading raised
  `ValueError: Config entry ... has already been setup!`. Replaced with
  `async_unload_platforms()`.
- **`via_device` replaced with `via_device_id`,** removed in Home Assistant
  2027.8. These are not interchangeable: the old field took an identifier
  tuple, the new one takes a device registry id. The gateway's id is now
  carried on `MyHOMEGatewayHandler.device_registry_id` and populated in
  `async_setup_entry` before the platforms are forwarded, so the device
  hierarchy is preserved.

### Packaging

- `hacs.json`: dropped `zip_release` and `filename`. Forking does not copy
  releases, so this fork had none, while the inherited `0.9.3` tag points at
  pre-fix code. HACS now installs from the source tree.
- `manifest.json`: version `0.9.4`; `documentation`, `issue_tracker` and
  `codeowners` point at this fork.
- `README.md` rewritten for this fork, with the upstream fork notice and
  attribution required by the licence.

### Verified on

Home Assistant Core 2026.9.0, with a real installation of 33 lights, 4
switches and 1 climate zone: all 38 entities retained, 0 pruned from the
registry, all 38 devices still parented to the gateway, 0 errors and 0
deprecation warnings after restart.
