# Contributing to This Project

Thank you for your interest in contributing! This guide will help you get started with the contribution process.

## Development Workflow

This project uses `uv` for development. Install and documentation is [here](https://docs.astral.sh/uv/getting-started/installation/).

1. **Fork and Clone the Repository**

   ```bash
   git clone https://github.com/j4c0bs/mcp-server-sql-analyzer.git
   cd mcp-server-sql-analyzer
   ```

2. **Create a New Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

   Name your branch with a descriptive prefix like `feat` or `fix`.

3. **Make Your Changes**
   - Write your code
   - Add tests if applicable
   - Ensure all tests pass
   - Update documentation as needed

4. **Code Style and Linting**
   - We use `ruff` for linting and formatting
   - Run linting:

     ```bash
     ruff check .
     ```

   - Run formatting:

     ```bash
     ruff format .
     ```

5. **Commit Your Changes**

   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

   Write clear, concise commit messages that explain your changes.

6. **Push and Create a Pull Request**

   ```bash
   git push origin feature/your-feature-name
   ```

   Then go to the repository on GitHub and create a Pull Request from your branch.

## Pull Request Guidelines

- Provide a clear title and description of your changes
- Link any related issues
- Ensure all tests pass
- Make sure your code has been linted and formatted with ruff
- Keep changes focused and atomic

## Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, your PR will be merged

## Questions?

If you have any questions, feel free to open an issue for discussion.

Thank you for contributing!
