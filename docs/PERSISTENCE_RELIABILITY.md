# Persistence reliability

Milestone 2 protects the local JSON repository from partial writes, corrupted
documents, and silent data loss. These guarantees apply to `expenses.json`,
`budgets.json`, and `settings.json`.

## Save guarantees

Each save follows this sequence:

1. Build and validate the complete version 2 document in memory.
2. Read and validate the current primary document, if it exists.
3. Atomically write that previous valid document to `<name>.json.bak`.
4. Write the new document to a temporary file in the same directory.
5. Flush the complete temporary file to disk.
6. Atomically replace the primary file.

A serialization, permission, flush, or replacement failure raises a
`StorageWriteError`. The incomplete temporary file is removed and the current
primary is left unchanged. Services also roll back their in-memory expense or
budget mutation before the error reaches the CLI.

The backup contains the version immediately before the latest successful
save. A new repository has no backup until an existing valid document is
overwritten for the first time.

## Load and recovery guarantees

Every loaded document is validated as a complete unit. Invalid JSON, malformed
fields, invalid domain values, unknown budget categories, and cross-file
currency conflicts raise `DataCorruptionError`; they are never converted into
an empty expense list, empty budget set, or default setting.

If a primary document is missing or corrupt and a valid backup exists, storage:

1. validates the backup;
2. atomically restores it as the primary document;
3. emits `StorageRecoveryWarning`; and
4. returns the recovered data.

Recovery intentionally returns the previous saved version, so the most recent
save may be lost. An unreadable primary raises `StorageReadError` instead of
silently falling back because a permission problem must be fixed explicitly.

Documents with a schema version newer than the application supports raise
`UnsupportedSchemaVersionError`. The backup is not used in this case because
doing so could discard valid data created by a newer application version.

## Manual recovery procedure

When the CLI reports that both the primary and backup are invalid or unreadable:

1. Stop the application; do not add or edit financial data.
2. Copy the affected primary and `.bak` files to a separate safe directory.
3. Check file permissions and confirm both files contain complete JSON.
4. Restore the newest document that passes the version 2 contract in
   `DATA_SCHEMA.md`.
5. Start the CLI and confirm all expenses, budgets, settings, and currency
   labels agree before making another change.

Never rename a newer-schema document to bypass the version check. Upgrade the
application or migrate the document deliberately instead.

## Exception contract

- `PersistenceError`: base error handled by the CLI and entry point.
- `StorageReadError`: the operating system prevented a read.
- `StorageWriteError`: an atomic save or recovery write failed.
- `DataCorruptionError`: JSON or stored values violate the supported contract.
- `UnsupportedSchemaVersionError`: the document belongs to a newer schema.
- `StorageRecoveryWarning`: recovery succeeded from the previous valid backup.
