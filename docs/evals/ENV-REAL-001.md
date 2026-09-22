# ENV-REAL-001 — Cloud Agent without local secrets

**Status:** observed operator failure (not fixed in product)  
**Links:** H-ENV-001 · EnvironmentCompiler · GOS locality of resources  
**Module:** `global_os.evals.environment.env_real_001`

## Failure

Agent selected an execution environment that lacked required machine-local resources.

## Observed

- Cloud Agent Ubuntu VM: `/workspace` git clone present
- Windows path `E:\…\secret\.env` does not exist on the VM
- `live_keys_present()` → all False in cloud
- `.env` / `.env.*` gitignored → secrets never arrive via clone

## Required EnvironmentCompiler dimensions

resource locality · secret locality · filesystem locality · tool availability · privacy · execution authority

## Expected correction

When goal needs local secrets / Docker / local checkout → route to **My Machines**
self-hosted worker; refuse silent “continue without keys” as success.

## Honesty

Recording this case ≠ claiming H-ENV confirmed. Fix is operational (run on worker),
then optionally teach EnvironmentCompiler to prefer that route.
