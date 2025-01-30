import pytest
from mcp_server_sql_analyzer.server import (
    get_all_column_references,
    ColumnReference,
    ColumnReferencesResult,
    ParseResult,
)


@pytest.mark.parametrize(
    "sql,dialect,expected_columns",
    [
        (
            "SELECT id, name, email FROM users",
            "",
            [
                ColumnReference(column="id", table="", fully_qualified="id"),
                ColumnReference(column="name", table="", fully_qualified="name"),
                ColumnReference(column="email", table="", fully_qualified="email"),
            ],
        ),
        (
            "SELECT u.id, o.order_date FROM users u JOIN orders o ON u.id = o.user_id",
            "",
            [
                ColumnReference(column="id", table="u", fully_qualified="u.id"),
                ColumnReference(
                    column="order_date", table="o", fully_qualified="o.order_date"
                ),
                ColumnReference(column="id", table="u", fully_qualified="u.id"),
                ColumnReference(
                    column="user_id", table="o", fully_qualified="o.user_id"
                ),
            ],
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
            [
                ColumnReference(
                    column="column1", table="t1", fully_qualified="t1.column1"
                ),
                ColumnReference(
                    column="column2", table="t2", fully_qualified="t2.column2"
                ),
                ColumnReference(column="id", table="t1", fully_qualified="t1.id"),
                ColumnReference(column="id", table="t2", fully_qualified="t2.id"),
                ColumnReference(
                    column="active", table="t1", fully_qualified="t1.active"
                ),
            ],
        ),
    ],
)
def test_get_all_column_references(
    sql: str, dialect: str, expected_columns: list[ColumnReference]
):
    result = get_all_column_references(sql, dialect)
    assert isinstance(result, ColumnReferencesResult)
    assert result.is_valid
    assert result.message == "No syntax errors"
    assert len(result.columns) == len(expected_columns)
    for actual, expected in zip(result.columns, expected_columns):
        assert actual == expected


def test_get_all_column_references_with_error():
    result = get_all_column_references("SELECT id FROM")  # Missing table reference
    assert isinstance(result, ParseResult)
    assert not result.is_valid
