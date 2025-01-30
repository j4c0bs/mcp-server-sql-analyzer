import pytest
from mcp_server_sql_analyzer.server import lint_sql, ParseResult


@pytest.mark.parametrize(
    "sql,dialect,expected",
    [
        (
            "SELECT * FROM users",
            "",
            ParseResult(is_valid=True, message="No syntax errors", position=None),
        ),
        (
            "SELECT * FROM users WHERE",
            "",
            ParseResult(
                is_valid=False,
                message="",
                position=None,
            ),
        ),
        (
            "SELECT * FROM users;",  # With semicolon
            "",
            ParseResult(is_valid=True, message="No syntax errors", position=None),
        ),
        (
            "SELECT * FROM users LIMIT 5",
            "postgres",  # Test with specific dialect
            ParseResult(is_valid=True, message="No syntax errors", position=None),
        ),
        (
            "SELEC * FROM users",  # Misspelled SELECT
            "",
            ParseResult(
                is_valid=False,
                message="",
                position=None,
            ),
        ),
    ],
)
def test_lint_sql(sql: str, dialect: str, expected: ParseResult):
    result = lint_sql(sql, dialect)
    assert result.is_valid == expected.is_valid


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
    assert result.is_valid
    assert result.message == "No syntax errors"
    assert result.position is None
