import sqlglot
from pydantic import BaseModel
from typing import Literal
from sqlglot import parse_one, exp
from sqlglot.expressions import Expression
from sqlglot.optimizer.scope import build_scope
from mcp.server.fastmcp import FastMCP
from sqlglot.dialects.dialect import Dialects

mcp = FastMCP("SQL Analyzer")


class ParseResult(BaseModel):
    is_valid: bool
    message: str
    position: dict[str, int] | None


class TranspileResult(BaseModel):
    is_valid: bool
    message: str
    read_dialect: str
    write_dialect: str
    sql: str


class ColumnReference(BaseModel):
    column: str
    table: str | None
    fully_qualified: str


class ColumnReferencesResult(BaseModel):
    is_valid: bool
    message: str
    columns: list[ColumnReference]


class TableReference(BaseModel):
    type: Literal["table", "cte"]
    catalog: str | None
    db: str | None
    table: str
    alias: str | None
    fully_qualified: str


class TableReferencesResult(BaseModel):
    is_valid: bool
    message: str
    tables: list[TableReference]


def _valid_dialect(dialect: str) -> bool:
    if not dialect:
        return True
    return len({dialect.lower(), dialect.upper()} & set(Dialects.__members__)) > 0


def _parse(sql: str, dialect: str) -> tuple[Expression | None, ParseResult]:
    """Parse SQL and return AST and any errors"""
    if not _valid_dialect(dialect):
        return None, ParseResult(
            is_valid=False,
            message=f"Unsupported dialect: {dialect}",
            position=None,
        )

    ast = None
    try:
        ast = parse_one(sql, dialect=dialect)
        result = ParseResult(
            is_valid=True,
            message="No syntax errors",
            position=None,
        )
    except sqlglot.errors.ParseError as e:
        errors = e.errors[0]
        result = ParseResult(
            is_valid=False,
            message=str(e),
            position={"line": errors["line"], "column": errors["col"]},
        )
    return ast, result


@mcp.tool()
def lint_sql(sql: str, dialect: str = "") -> ParseResult:
    """
    Lint SQL query and return syntax errors

    Some syntax errors are not detected by the parser like trailing commas

    Args:
        sql: SQL query to analyze
        dialect: Optional SQL dialect (e.g., 'mysql', 'postgres')

    Returns:
        error message or "No syntax errors" if parsing succeeds
    """
    _, result = _parse(sql, dialect)
    return result


@mcp.tool()
def transpile_sql(
    sql: str, read_dialect: str, write_dialect: str
) -> ParseResult | TranspileResult:
    """
    Transpile SQL statement to another dialect

    Args:
        sql: SQL statement to transpile
        read_dialect: SQL dialect to read from
        write_dialect: SQL dialect to write to

    Returns:
        transpiled SQL or syntax error
    """
    _, errors = _parse(sql, read_dialect)
    if not errors.is_valid:
        return errors

    if not _valid_dialect(write_dialect):
        return ParseResult(
            is_valid=False,
            message=f"Unsupported write dialect: {write_dialect}",
            position=None,
        )

    transpiled_sql = ""
    try:
        transpiled_sql = sqlglot.transpile(
            sql,
            read=read_dialect,
            write=write_dialect,
            unsupported_level=sqlglot.ErrorLevel.RAISE,
        )
        is_valid = True
        message = "No syntax errors"
    except sqlglot.errors.UnsupportedError as e:
        is_valid = False
        message = str(e)

    return TranspileResult(
        is_valid=is_valid,
        message=message,
        read_dialect=read_dialect,
        write_dialect=write_dialect,
        sql=transpiled_sql,
    )


@mcp.tool()
def get_all_table_references(
    sql: str, dialect: str = ""
) -> TableReferencesResult | ParseResult:
    """
    Extract table and CTE names from SQL statement

    Args:
        sql: SQL statement to analyze
        dialect: Optional SQL dialect (e.g., 'mysql', 'postgres')
    Returns:
        JSON object containing tables with catalog, database, and alias attributes
        CTEs are returned as "cte" type
    """
    ast, errors = _parse(sql, dialect)
    if not errors.is_valid:
        return errors

    table_refs = []

    root = build_scope(ast)
    for scope in root.traverse():
        for alias, (node, source) in scope.selected_sources.items():
            if isinstance(source, exp.Table):
                table_alias = source.alias if source.alias != source.name else None
                fully_qualified = ".".join(map(str, source.parts))

                table_refs.append(
                    TableReference(
                        type="table",
                        catalog=source.catalog,
                        db=source.db,
                        table=source.name,
                        alias=table_alias,
                        fully_qualified=fully_qualified,
                    )
                )

    for cte in ast.find_all(exp.CTE):
        table_refs.append(
            TableReference(
                type="cte",
                catalog="",
                db="",
                table=cte.alias_or_name,
                alias="",
                fully_qualified=cte.alias_or_name,
            )
        )

    return TableReferencesResult(
        is_valid=True,
        message="No syntax errors",
        tables=table_refs,
    )


@mcp.tool()
def get_all_column_references(
    sql: str, dialect: str = ""
) -> ColumnReferencesResult | ParseResult:
    """
    Extract column references from SQL statement with table context

    Args:
        sql: SQL statement to analyze
        dialect: Optional SQL dialect (e.g., 'mysql', 'postgres')
    Returns:
        JSON object containing column references with table context and any errors
    """
    ast, errors = _parse(sql, dialect)
    if not errors.is_valid:
        return errors

    columns = ast.find_all(exp.Column)
    column_refs = []

    for col in columns:
        column = col.name
        table = col.table
        fully_qualified = f"{table}.{column}" if table else column

        column_refs.append(
            ColumnReference(column=column, table=table, fully_qualified=fully_qualified)
        )

    return ColumnReferencesResult(
        is_valid=True,
        message="No syntax errors",
        columns=column_refs,
    )


@mcp.resource("dialects://all")
def list_sql_dialects() -> list[str]:
    """
    List all supported SQL dialects

    Returns:
        list of supported SQL dialects
    """
    return [d.value for d in Dialects if d.value]


def main():
    mcp.run()


if __name__ == "__main__":
    main()
