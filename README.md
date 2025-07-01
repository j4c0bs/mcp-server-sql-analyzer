# mcp-server-sql-analyzer

A Model Context Protocol (MCP) server that provides SQL analysis, linting, and dialect conversion capabilities using [SQLGlot](https://sqlglot.com/sqlglot.html).

## Overview

The SQL Analyzer MCP server provides tools for analyzing and working with SQL queries. It helps with:

- SQL syntax validation and linting
- Converting queries between different SQL dialects (e.g., MySQL to PostgreSQL)
- Extracting and analyzing table references and dependencies
- Identifying column usage and relationships
- Discovering supported SQL dialects

### How Claude Uses This Server

As an AI assistant, this server enhances my ability to help users work with SQL efficiently by:

1. **Query Validation**: I can instantly validate SQL syntax before suggesting it to users, ensuring I provide correct and dialect-appropriate queries.

2. **Dialect Conversion**: When users need to migrate queries between different database systems, I can accurately convert the syntax while preserving the query's logic.

3. **Code Analysis**: The table and column reference analysis helps me understand complex queries, making it easier to explain query structure and suggest optimizations.

4. **Compatibility Checking**: By knowing the supported dialects and their specific features, I can guide users toward database-specific best practices.

This toolset allows me to provide more accurate and helpful SQL-related assistance while reducing the risk of syntax errors or dialect-specific issues.

### Tips

Update your personal preferences in Claude Desktop settings to request that generated SQL is first validated using the `lint_sql` tool.

## Tools

1. lint_sql
   - Validates SQL query syntax and returns any errors
   - Input:
     - sql (string): SQL query to analyze
     - dialect (string, optional): SQL dialect (e.g., 'mysql', 'postgres')
   - Returns: ParseResult containing:
     - is_valid (boolean): Whether the SQL is valid
     - message (string): Error message or "No syntax errors"
     - position (object, optional): Line and column of error if present

2. transpile_sql
   - Converts SQL between different dialects
   - Inputs:
     - sql (string): SQL statement to transpile
     - read_dialect (string): Source SQL dialect
     - write_dialect (string): Target SQL dialect
   - Returns: TranspileResult containing:
     - is_valid (boolean): Whether transpilation succeeded
     - message (string): Error message or success confirmation
     - sql (string): Transpiled SQL if successful

3. get_all_table_references
   - Extracts table and CTE references from SQL
   - Inputs:
     - sql (string): SQL statement to analyze
     - dialect (string, optional): SQL dialect
   - Returns: TableReferencesResult containing:
     - is_valid (boolean): Whether analysis succeeded
     - message (string): Status message
     - tables (array): List of table references with type, catalog, database, table name, alias, and fully qualified name

4. get_all_column_references
   - Extracts column references with table context
   - Inputs:
     - sql (string): SQL statement to analyze
     - dialect (string, optional): SQL dialect
   - Returns: ColumnReferencesResult containing:
     - is_valid (boolean): Whether analysis succeeded
     - message (string): Status message
     - columns (array): List of column references with column name, table name, and fully qualified name

## Resources

### SQL Dialect Discovery

```
dialects://all
```

Returns a list of all supported SQL dialects for use in all tools.

## Configuration

### Using uvx (recommended)

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
      "sql-analyzer": {
          "command": "uvx",
          "args": [
              "--from",
              "git+https://github.com/j4c0bs/mcp-server-sql-analyzer.git",
              "mcp-server-sql-analyzer"
          ]
      }
  }
}
```

### Using uv

After cloning this repo, add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
      "sql-analyzer": {
          "command": "uv",
          "args": [
              "--directory",
              "/path/to/mcp-server-sql-analyzer",
              "run",
              "mcp-server-sql-analyzer"
          ]
      }
  }
}
```

## Development

To run the server in development mode:

```bash
# Clone the repository
git clone git@github.com:j4c0bs/mcp-server-sql-analyzer.git

# Run the server
npx @modelcontextprotocol/inspector uv --directory /path/to/mcp-server-sql-analyzer run mcp-server-sql-analyzer
```

To run unit tests:

```bash
uv run pytest .
```

## License

MIT
