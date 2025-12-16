import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.migration_service import MigrationService


class SmokeTests(unittest.TestCase):
    def test_migration_service_allows_valid_table(self):
        # Should not raise for whitelisted table name
        MigrationService._validate_table_name("transactions")

    def test_migration_service_valid_definition(self):
        MigrationService._validate_column_definition(
            "amount", "amount REAL DEFAULT 0"
        )

    def test_public_validate_add_column_entrypoint(self):
        self.assertTrue(
            MigrationService.validate_add_column(
                "transactions", "note", "note TEXT DEFAULT 'n/a'"
            )
        )


if __name__ == "__main__":
    unittest.main()
