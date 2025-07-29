# Schema Directory

This directory contains all database schema and table-related files for the Oracle MCP Server.

## Directory Structure

```
schema/
├── db_index.json              # Main schema index with table summaries and relationships
├── tables/                    # Individual table schema files (JSON format)
├── database_tables/           # HTML documentation for database tables
├── catalogs/                  # CSV catalog files
│   ├── column_catalog.csv     # Column definitions and metadata
│   └── table_catalog.csv      # Table definitions and metadata
└── docs/                      # Schema documentation
    ├── database_schema.md     # Markdown documentation
    └── database_schema.json   # JSON schema documentation
```

## File Descriptions

### db_index.json
- **Purpose**: Lightweight index with table summaries, primary keys, and foreign key relationships
- **Usage**: Used by the MCP server for quick table discovery and relationship mapping
- **Format**: JSON with table metadata and relationship information

### tables/
- **Purpose**: Detailed schema for individual tables
- **Usage**: Loaded on-demand for specific table information
- **Format**: JSON files with complete column definitions

### database_tables/
- **Purpose**: HTML documentation for database tables
- **Usage**: Human-readable table documentation
- **Format**: HTML files with table structure and examples

### catalogs/
- **Purpose**: CSV catalog files for bulk schema information
- **Usage**: Import/export of schema data
- **Format**: CSV files with structured schema data

### docs/
- **Purpose**: Comprehensive schema documentation
- **Usage**: Reference documentation for developers
- **Format**: Markdown and JSON documentation files

## Usage in MCP Server

The MCP server references these files through the following paths:
- Schema index: `schema/db_index.json`
- Table files: `schema/tables/{table_name}.json`
- Documentation: `schema/docs/`

## Benefits of This Organization

1. **Clear Separation**: All schema files are organized in one location
2. **Scalability**: Easy to add new schema file types
3. **Maintainability**: Clear structure for finding and updating schema files
4. **Version Control**: Better organization for git tracking
5. **Documentation**: Self-documenting structure

## Migration Notes

- All schema files have been moved from the root directory to the `schema/` directory
- The MCP server has been updated to reference the new paths
- The `.gitignore` file has been updated to reflect the new structure 