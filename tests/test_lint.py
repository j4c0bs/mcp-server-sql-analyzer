import pytest
from unittest.mock import patch
from mcp_server_sql_analyzer.server import (
    lint_sql,
    ParseResult,
    get_all_table_references,
    get_all_column_references,
)


def mock_mcp_decorator():
    def decorator(f):
        return f

    return decorator


patch("mcp.server.fastmcp.FastMCP.tool", mock_mcp_decorator).start()


@pytest.mark.parametrize(
    "sql,dialect,expected",
    [
        (
            "SELECT * FROM users",
            "",
            ParseResult(isValid=True, message="No syntax errors", position=None),
        ),
        (
            "SELECT * FROM users WHERE",
            "",
            ParseResult(
                isValid=False,
                message="",
                position=None,
            ),
        ),
        (
            "SELECT * FROM users;",  # With semicolon
            "",
            ParseResult(isValid=True, message="No syntax errors", position=None),
        ),
        (
            "SELECT * FROM users LIMIT 5",
            "postgres",  # Test with specific dialect
            ParseResult(isValid=True, message="No syntax errors", position=None),
        ),
        (
            "SELEC * FROM users",  # Misspelled SELECT
            "",
            ParseResult(
                isValid=False,
                message="",
                position=None,
            ),
        ),
    ],
)
def test_lint_sql(sql: str, dialect: str, expected: ParseResult):
    result = lint_sql(sql, dialect)
    assert result.isValid == expected.isValid


def test_lint_sql_with_complex_query():
    sql = """
    WITH user_stats AS (
        SELECT user_id, COUNT(*) as login_count
        FROM login_history
        GROUP BY user_id
    )
    SELECT u.name, us.login_count
    FROM users u
    JOIN user_stats us ON u.id = us.user_id
    WHERE u.active = true
    ORDER BY us.login_count DESC
    LIMIT 10
    """
    result = lint_sql(sql)
    assert result.isValid
    assert result.message == "No syntax errors"
    assert result.position is None


@pytest.mark.parametrize(
    "sql,dialect,expected",
    [
        (
            "SELECT * FROM users JOIN orders ON users.id = orders.user_id",
            "",
            "users, orders",
        ),
        (
            "WITH cte AS (SELECT * FROM products) SELECT * FROM cte, categories",
            "",
            "products, categories",
        ),
        (
            """
            SELECT *
            FROM schema1.table1 t1
            LEFT JOIN schema2.table2 t2 ON t1.id = t2.id
            """,
            "",
            "schema1.table1, schema2.table2",
        ),
    ],
)
def test_get_all_table_references(sql: str, dialect: str, expected: str):
    result = get_all_table_references(sql, dialect)
    assert result == expected


def test_get_all_table_references_with_error():
    result = get_all_table_references("SELECT * FORM users")  # Misspelled FROM
    assert isinstance(result, ParseResult)
    assert not result.isValid


@pytest.mark.parametrize(
    "sql,dialect,expected",
    [
        (
            "SELECT id, name, email FROM users",
            "",
            "id, name, email",
        ),
        (
            "SELECT u.id, o.order_date FROM users u JOIN orders o ON u.id = o.user_id",
            "",
            "u.id, o.order_date, u.id, o.user_id",
        ),
        (
            """
            SELECT
                t1.column1,
                t2.column2 as alias
            FROM table1 t1
            JOIN table2 t2 ON t1.id = t2.id
            WHERE t1.active = true
            """,
            "",
            "t1.column1, t2.column2, t1.id, t2.id, t1.active",
        ),
    ],
)
def test_get_all_column_references(sql: str, dialect: str, expected: str):
    result = get_all_column_references(sql, dialect)
    assert result == expected


def test_get_all_column_references_with_error():
    result = get_all_column_references("SELECT id FROM")  # Missing table reference
    assert isinstance(result, ParseResult)
    assert not result.isValid
