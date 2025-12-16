import re
from typing import Iterable, List


class MigrationService:
    """Lightweight validation helpers to secure migration inputs."""

    # Explicit whitelist of tables that can be modified via migrations
    ALLOWED_TABLES: List[str] = [
        "assets",
        "budget",
        "liabilities",
        "real_estate",
        "transactions",
    ]

    # Simple SQLite storage classes permitted for new columns
    ALLOWED_COLUMN_TYPES: List[str] = ["INTEGER", "REAL", "TEXT", "BLOB", "NUMERIC"]

    # Optional constraints that are considered safe to append after the type
    ALLOWED_SIMPLE_CONSTRAINTS: List[str] = ["NOT NULL", "PRIMARY KEY", "UNIQUE"]

    # Regexes for constraints that include values or expressions
    DEFAULT_CONSTRAINT_PATTERN = re.compile(
        r"DEFAULT\s+(?:-?\d+(?:\.\d+)?|'[^']*'|\"[^\"]*\")",
        re.IGNORECASE,
    )
    CHECK_CONSTRAINT_PATTERN = re.compile(
        r"CHECK\s*\([\w\s<>=!+\-*/'%\.,()]+\)", re.IGNORECASE
    )

    @classmethod
    def _validate_table_name(cls, table_name: str) -> None:
        if not table_name:
            raise ValueError("Table name is required")
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", table_name):
            raise ValueError("Invalid table identifier")
        if table_name not in cls.ALLOWED_TABLES:
            raise ValueError("Table not in whitelist")

    @classmethod
    def _validate_column_name(cls, column_name: str) -> None:
        if not column_name:
            raise ValueError("Column name is required")
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", column_name):
            raise ValueError("Invalid column identifier")

    @classmethod
    def _check_for_dangerous_tokens(cls, value: str) -> None:
        # Quick checks for obvious SQL injection or chaining
        dangerous_tokens: Iterable[str] = [";", "--", "/*", "*/", "\\"]
        lowered = value.lower()
        forbidden_keywords: Iterable[str] = [
            "drop",
            "alter",
            "delete",
            "truncate",
            "attach",
            "detach",
            "pragma",
        ]
        if any(token in value for token in dangerous_tokens):
            raise ValueError("Column definition rejected (dangerous characters)")
        if any(keyword in lowered for keyword in forbidden_keywords):
            raise ValueError("Column definition rejected (dangerous keywords)")

    @classmethod
    def _validate_column_definition(cls, column_name: str, definition: str) -> None:
        if not definition:
            raise ValueError("Column definition is required")

        cls._validate_column_name(column_name)
        cls._check_for_dangerous_tokens(definition)

        # Definition must start with the exact column name
        if not definition.startswith(column_name + " "):
            raise ValueError("Column definition rejected (wrong column name)")

        definition_body = definition[len(column_name) :].strip()
        if not definition_body:
            raise ValueError("Column definition rejected (invalid format)")

        # Extract the column type (first token) and any constraints
        parts = definition_body.split()
        col_type = parts[0].upper()
        constraints = " ".join(parts[1:]) if len(parts) > 1 else ""

        if col_type not in cls.ALLOWED_COLUMN_TYPES:
            raise ValueError("Column definition rejected (invalid type)")

        if constraints:
            cls._check_for_dangerous_tokens(constraints)
            cls._validate_constraints(constraints)

    @classmethod
    def _validate_constraints(cls, constraints: str) -> None:
        # Normalize consecutive whitespace for easier pattern checks
        normalized = re.sub(r"\s+", " ", constraints.strip())
        remaining = normalized

        # Consume allowed simple constraints greedily
        for constraint in cls.ALLOWED_SIMPLE_CONSTRAINTS:
            pattern = re.compile(rf"\b{re.escape(constraint)}\b", re.IGNORECASE)
            remaining = pattern.sub("", remaining)

        # Handle value/expr constraints separately
        remaining = cls.DEFAULT_CONSTRAINT_PATTERN.sub("", remaining)
        remaining = cls.CHECK_CONSTRAINT_PATTERN.sub("", remaining)

        # After stripping known-safe constraints, any leftover content is unsafe
        if remaining.strip():
            raise ValueError("Column definition rejected (invalid constraints)")

    @classmethod
    def validate_add_column(
        cls, table_name: str, column_name: str, column_definition: str
    ) -> bool:
        """Public entry point to vet an add-column migration.

        This helper wraps the internal validation steps so callers outside the
        tests do not need to use the private methods directly.  A ``True``
        return value signals that the inputs are safe for use in migration SQL.
        """

        cls._validate_table_name(table_name)
        cls._validate_column_definition(column_name, column_definition)
        return True

