import sqlglot
from pydantic import BaseModel
from sqlglot import parse_one, exp
from sqlglot.expressions import Expression
from sqlglot.optimizer.scope import build_scope
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SQL Analyzer")


class ParseResult(BaseModel):
    isValid: bool
    message: str
    position: dict[str, int] | None


class TranspileResult(BaseModel):
    isValid: bool
    message: str
    read_dialect: str
    write_dialect: str
    sql: str


def _parse(sql: str, dialect: str) -> tuple[Expression | None, ParseResult]:
    """Parse SQL and return AST and any errors"""
    ast = None
    try:
        ast = parse_one(sql, dialect=dialect)
        result = ParseResult(
            isValid=True,
            message="No syntax errors",
            position=None,
        )
    except sqlglot.errors.ParseError as e:
        errors = e.errors[0]
        result = ParseResult(
            isValid=False,
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
        dialect: Optional SQL dialect (e.g., 'mysql', 'postgresql')

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
    if not errors.isValid:
        return errors

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
        isValid=is_valid,
        message=message,
        read_dialect=read_dialect,
        write_dialect=write_dialect,
        sql=transpiled_sql,
    )


@mcp.tool()
def get_all_table_references(sql: str, dialect: str = "") -> list[str] | ParseResult:
    """
    Extract table names from SQL statement

    Args:
        sql: SQL statement to analyze
        dialect: Optional SQL dialect (e.g., 'mysql', 'postgresql')
    Returns:
        comma-separated list of table names or syntax error message
    """
    ast, errors = _parse(sql, dialect)
    if not errors.isValid:
        return errors

    root = build_scope(ast)
    objects = [
        source
        for scope in root.traverse()
        for alias, (node, source) in scope.selected_sources.items()
        if isinstance(source, exp.Table)
    ]

    return [".".join(map(str, obj.parts)) for obj in objects]


@mcp.tool()
def get_all_column_references(sql: str, dialect: str = "") -> list[str] | ParseResult:
    """
    Extract column names from SQL statement

    Args:
        sql: SQL statement to analyze
        dialect: Optional SQL dialect (e.g., 'mysql', 'postgresql')
    Returns:
        comma-separated list of column names or syntax error message
    """
    ast, errors = _parse(sql, dialect)
    if not errors.isValid:
        return errors

    columns = ast.find_all(exp.Column)
    return [".".join(map(str, col.parts)) for col in columns]


@mcp.resource("dialects://all")
def list_sql_dialects() -> str:
    """
    List all supported SQL dialects

    Returns:
        comma-separated list of supported SQL dialects
    """
    dialects = [
        name.lower()
        for name in sqlglot.dialects.Dialects._member_names_
        if name != "DIALECT"
    ]
    return ", ".join(dialects)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
