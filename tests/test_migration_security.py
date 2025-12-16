import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.migration_service import MigrationService


class TestMigrationSecurity(unittest.TestCase):
    def test_validate_table_name_whitelist(self):
        for table in MigrationService.ALLOWED_TABLES:
            MigrationService._validate_table_name(table)

    def test_validate_add_column_entrypoint_rejects_invalid_table(self):
        with self.assertRaises(ValueError):
            MigrationService.validate_add_column(
                "users", "user_id", "user_id INTEGER NOT NULL"
            )

    def test_validate_table_name_invalid_characters(self):
        with self.assertRaises(ValueError):
            MigrationService._validate_table_name("123invalid")
        with self.assertRaises(ValueError):
            MigrationService._validate_table_name("table-name")
        with self.assertRaises(ValueError):
            MigrationService._validate_table_name("table name")
        with self.assertRaises(ValueError):
            MigrationService._validate_table_name("table@name")
        with self.assertRaises(ValueError):
            MigrationService._validate_table_name("table.name")

    def test_validate_table_name_whitelist_enforced(self):
        with self.assertRaises(ValueError):
            MigrationService._validate_table_name("users")
        with self.assertRaises(ValueError):
            MigrationService._validate_table_name("admin_table")
        with self.assertRaises(ValueError):
            MigrationService._validate_table_name("transactions; DROP TABLE users; --")
        with self.assertRaises(ValueError):
            MigrationService._validate_table_name("")

    def test_validate_column_name(self):
        MigrationService._validate_column_name("valid_column")
        with self.assertRaises(ValueError):
            MigrationService._validate_column_name("123column")
        with self.assertRaises(ValueError):
            MigrationService._validate_column_name("column-name")
        with self.assertRaises(ValueError):
            MigrationService._validate_column_name("column name")
        with self.assertRaises(ValueError):
            MigrationService._validate_column_name("column@name")
        with self.assertRaises(ValueError):
            MigrationService._validate_column_name("")

    def test_validate_column_definition_sql_injection(self):
        invalid_definitions = [
            "user_id TEXT; DROP TABLE users;",  # semicolon break-out
            "user_id TEXT -- comment chain",
            "user_id TEXT /* comment */",
            "user_id TEXT PRAGMA user_version",  # forbidden keyword
            "user_id TEXT ALTER TABLE transactions",  # forbidden keyword
            "user_id TEXT ATTACH DATABASE 'file.db'",  # forbidden keyword
        ]
        for definition in invalid_definitions:
            with self.subTest(definition=definition):
                with self.assertRaises(ValueError):
                    MigrationService._validate_column_definition("user_id", definition)

    def test_validate_column_definition_wrong_name_and_format(self):
        with self.assertRaises(ValueError):
            MigrationService._validate_column_definition(
                "user_id", "other_column INTEGER NOT NULL"
            )
        with self.assertRaises(ValueError):
            MigrationService._validate_column_definition("user_id", "user_id")
        with self.assertRaises(ValueError):
            MigrationService._validate_column_definition("user_id", "")

    def test_validate_column_definition_invalid_types(self):
        with self.assertRaises(ValueError):
            MigrationService._validate_column_definition("user_id", "user_id JSON")
        with self.assertRaises(ValueError):
            MigrationService._validate_column_definition(
                "user_id", "user_id INTEGER(10)"
            )

    def test_validate_column_definition_invalid_constraints(self):
        invalid_constraints = [
            "user_id TEXT INVALID_CONSTRAINT",
            "user_id TEXT DEFAULT (SELECT * FROM users)",
            "user_id TEXT CHECK(0); DROP TABLE users; --",
            "user_id TEXT PRIMARY KEY AUTOINCREMENT",  # unsupported combo
            "user_id TEXT NOT NULL UNIQUE INVALID",
        ]
        for definition in invalid_constraints:
            with self.subTest(definition=definition):
                with self.assertRaises(ValueError):
                    MigrationService._validate_column_definition("user_id", definition)

    def test_validate_column_definition_valid_cases(self):
        valid_defs = [
            ("user_id", "user_id INTEGER PRIMARY KEY"),
            ("amount", "amount REAL NOT NULL"),
            ("note", "note TEXT DEFAULT 'n/a'"),
            ("created_at", "created_at NUMERIC DEFAULT 0"),
            ("status", "status TEXT CHECK(status IN ('open','closed'))"),
            ("category", "category TEXT UNIQUE"),
        ]
        for column, definition in valid_defs:
            with self.subTest(definition=definition):
                MigrationService._validate_column_definition(column, definition)


if __name__ == "__main__":
    unittest.main()
