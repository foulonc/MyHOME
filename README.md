# MyHOME

Home Assistant integration for BTicino / Legrand **MyHOME** systems over the
OpenWebNet bus. Local only: it talks to the gateway on your own network and
needs no cloud account.

This repository is a maintained fork of
[`anotherjulien/MyHOME`](https://github.com/anotherjulien/MyHOME), kept working
against current Home Assistant releases. It is maintained by
[@foulonc](https://github.com/foulonc) for a single private installation.

> **Fork notice (AGPL-3.0 §5).** This is a modified version of the original
> work by [@anotherjulien](https://github.com/anotherjulien). The original
> project is licensed AGPL-3.0 and so is this fork. Modifications are listed
> in [CHANGELOG.md](CHANGELOG.md) and in this repository's commit history.

## Why this fork exists

Home Assistant **2026.9** replaced `voluptuous` with a reimplementation called
`probatio`, installed over the same module name. Its compiler unwraps a nested
`Schema` instance to its precompiled validator when that schema is used as a
value inside another schema, which silently skips a `Schema` subclass's
overridden `__call__`.

The original `validate.py` did all of its post-processing in exactly such an
override, so devices were never re-keyed to `who-where` and the optional
config keys were never filled in. Every platform then failed at setup:

| Platform | Error |
|---|---|
| `light`, `switch` | `KeyError: 'icon'` |
| `climate`, `button` | `KeyError: 'model'` |
| the integration itself | `KeyError: 'entities'` |

Because setup aborted on the last one, the `myhome.send_message` and
`myhome.sync_time` services were never registered either.

Upstream merged a fix for that specific bug on 2026-09-04, but has not cut a
release since **0.9.3, in March 2024**, and its `hacs.json` pointed HACS at
release assets. The fix was therefore unreachable through a normal install.
This fork exists so the code that actually runs can be released and pinned.

## What this fork fixes

Everything upstream's fix does, plus five things it does not:

| Fix | Without it |
|---|---|
| Nested schema post-processing (upstream PR #223) | integration fails to set up on HA 2026.9+ |
| `OptionsFlow.config_entry` no longer assigned | the Configure dialog returns HTTP 500 (HA 2024.11+) |
| `manufacturer` / `model` / `sw_version` coerced to `str` | device registry rejects OWNd's list value (HA 2026.12) |
| `dr.async_entries_for_config_entry()` replaces `device_registry.devices` | breaks in HA 2027.9 |
| `async_unload_platforms()` replaces the per-platform unload loop | reload raises `has already been setup!` |
| `via_device_id` replaces `via_device` | breaks in HA 2027.8 |

That last one deserves a warning if you are patching this yourself: the two
are **not** interchangeable. `via_device` took an identifier tuple, while
`via_device_id` takes a device registry **id**. Renaming the key in place is
accepted silently and detaches every device from its gateway. This fork
carries the real id on `MyHOMEGatewayHandler.device_registry_id`, populated in
`async_setup_entry` before the platforms are forwarded.

## Installation

Through HACS, as a custom repository:

1. HACS → three-dot menu → **Custom repositories**
2. Repository `https://github.com/foulonc/MyHOME`, category **Integration**
3. Download **MyHOME**, then restart Home Assistant
4. Add the integration under **Settings → Devices & Services**

Gateways on the same network are usually discovered automatically, and one can
also be added by hand. The gateway has to be reachable on the same network as
Home Assistant.

The devices themselves are configured in YAML rather than through the UI.

## Configuration

Device configuration lives in `myhome.yaml` in your Home Assistant config
directory. The format is unchanged from upstream, so the original wiki still
applies:

- [Configuration](https://github.com/anotherjulien/MyHOME/wiki/Configuration)
- [Advanced uses](https://github.com/anotherjulien/MyHOME/wiki/Advanced-uses)

Coming from version 0.8 or earlier, the configuration structure changed and
you need to create and populate that file.

### Read this before restarting after a config change

`async_setup_entry` removes every registry entity whose `unique_id` is no
longer produced by `myhome.yaml`. That is usually what you want, but it means
an accidental edit, or an older copy of the file restored over the current
one, will **permanently delete** the affected entities on the next successful
start, together with their history and any dashboard references. Check the
file before restarting after you touch it.

## Dependency

This integration needs [OWNd](https://pypi.org/project/OWNd/), the OpenWebNet
protocol library, pinned to `0.7.48` and installed from PyPI.

A controlled mirror is kept at
[`foulonc/OWNd`](https://github.com/foulonc/OWNd), tagged
[`0.7.48`](https://github.com/foulonc/OWNd/releases/tag/0.7.48) at the exact
commit whose modules are byte-for-byte identical to the PyPI release. It is
there so this integration is not stranded if the upstream package disappears.

The manifest deliberately still requires `OWNd==0.7.48` from PyPI rather than
that mirror. Home Assistant's `is_installed()` returns `False` for a PEP 508
direct URL reference even when the package is already present, so pointing the
manifest at the mirror would make Home Assistant re-download it from GitHub on
**every** startup, and fail to set the integration up whenever GitHub is
unreachable. A local lighting system should not depend on that.

## Credits

Original work, and all of the protocol implementation, by
[@anotherjulien](https://github.com/anotherjulien), who also wrote OWNd. The
nested-schema fix carried here is by
[@cedric1067](https://github.com/cedric1067), via upstream PR
[#223](https://github.com/anotherjulien/MyHOME/pull/223).

## License

AGPL-3.0, unchanged from the original project. See [LICENSE](LICENSE).
