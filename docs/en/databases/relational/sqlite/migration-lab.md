<a id="проверить-перестроение-таблицы-sqlite"></a>
# Verify a SQLite table rebuild

[Русский](../../../../ru/databases/relational/sqlite/migration-lab.md)

Use this example when a schema change requires creating a replacement table.
The example preserves a known index, trigger, and foreign key in a database with synthetic data.
[Migration and WAL](backup-and-migrations.md) · [SQLite](README.md).

Use Python 3.14 with SQLite 3.37 or later for STRICT. You should be familiar with foreign keys and transactions.

<a id="полный-пример-перестроение-таблицы"></a>
## Complete example of a table rebuild

Save the example as `migration.py`.
Run `python3.14 migration.py`.
The dependencies are part of the Python standard library.
The script creates its own temporary directory and synthetic database, then deletes that directory.
Before changing your own schema, obtain a [verified backup](backup-and-restore.md#verify-the-restored-database).

The example rebuilds and replaces a known table in one transaction.
For an arbitrary schema, inspect its views and triggers before running a migration.
The DROP in this example affects only the practice database the script creates.

[`sqlite/migration.py`](../../../../../examples/databases/relational/sqlite/migration.py)

The user's name becomes `alice-updated`, and the trigger writes an audit record.
The foreign key and index remain in place.
The new CHECK rejects an empty name.
For an arbitrary schema, also preserve and adapt views, triggers, and other dependencies.
Follow the official [table rebuild procedure](https://www.sqlite.org/lang_altertable.html#making_other_kinds_of_table_schema_changes).
Copy the data and replace the table in a single transaction.

<a id="источники"></a>
## Sources

- [Schema changes](https://www.sqlite.org/lang_altertable.html), [transactions](https://www.sqlite.org/lang_transaction.html), [foreign_keys](https://www.sqlite.org/pragma.html#pragma_foreign_keys).
- [WAL](https://www.sqlite.org/wal.html), [integrity_check](https://www.sqlite.org/pragma.html#pragma_integrity_check), [foreign_key_check](https://www.sqlite.org/pragma.html#pragma_foreign_key_check).
- [3.53.4 release notes](https://www.sqlite.org/releaselog/3_53_4.html).
