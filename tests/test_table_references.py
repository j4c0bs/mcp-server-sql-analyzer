import pytest
from mcp_server_sql_analyzer.server import (
    get_all_table_references,
    TableReference,
    TableReferencesResult,
    ParseResult,
)


@pytest.mark.parametrize(
    "sql,dialect,expected_tables",
    [
        (
            "SELECT * FROM users JOIN orders ON users.id = orders.user_id",
            "",
            [
                TableReference(
                    type="table",
                    catalog="",
                    db="",
                    table="users",
                    alias="",
                    fully_qualified="users",
                ),
                TableReference(
                    type="table",
                    catalog="",
                    db="",
                    table="orders",
                    alias="",
                    fully_qualified="orders",
                ),
            ],
        ),
        (
            "WITH cte AS (SELECT * FROM products) SELECT * FROM cte, categories",
            "",
            [
                TableReference(
                    type="table",
                    catalog="",
                    db="",
                    table="products",
                    alias="",
                    fully_qualified="products",
                ),
                TableReference(
                    type="table",
                    catalog="",
                    db="",
                    table="categories",
                    alias="",
                    fully_qualified="categories",
                ),
                TableReference(
                    type="cte",
                    catalog="",
                    db="",
                    table="cte",
                    alias="",
                    fully_qualified="cte",
                ),
            ],
        ),
        (
            """
            SELECT *
            FROM schema1.table1 t1
            LEFT JOIN schema2.table2 t2 ON t1.id = t2.id
            """,
            "",
            [
                TableReference(
                    type="table",
                    catalog="",
                    db="schema1",
                    table="table1",
                    alias="t1",
                    fully_qualified="schema1.table1",
                ),
                TableReference(
                    type="table",
                    catalog="",
                    db="schema2",
                    table="table2",
                    alias="t2",
                    fully_qualified="schema2.table2",
                ),
            ],
        ),
    ],
)
def test_get_all_table_references(
    sql: str, dialect: str, expected_tables: list[TableReference]
):
    result = get_all_table_references(sql, dialect)
    assert isinstance(result, TableReferencesResult)
    assert result.is_valid
    assert result.message == "No syntax errors"
    assert len(result.tables) == len(expected_tables)
    for actual, expected in zip(result.tables, expected_tables):
        assert actual == expected


def test_get_all_table_references_with_error():
    result = get_all_table_references("SELECT * FORM users")  # Misspelled FROM
    assert isinstance(result, ParseResult)
    assert not result.is_valid
