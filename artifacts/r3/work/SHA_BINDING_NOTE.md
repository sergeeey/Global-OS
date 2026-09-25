# SHA binding note (R3 remediation)

Y20–Y22 `process_log.public_pack_sha256` is a **directory merkle** (`_dir_sha256(public/)` including README), **not** `sha256(public_pack.json)`.

Do not treat file-hash mismatch as pack tampering without checking dir hash.
Frozen arm logs are not rewritten (immutable evidence).
