# Recursion v2 registries

These registries are declarative, versioned, and inert. They do not enable an engine,
authenticate an account, change routing flags, or launch work. Every file is validated by
`scripts/v2_contracts.py` before it can participate in dry assignment resolution.

Credential fields are references only (`secret:<name>`); secret values never belong here.
The v1 files under `scripts/engines/` and `state/` remain the compatibility source until a
later phase migrates live state.
