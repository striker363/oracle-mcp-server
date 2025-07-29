# Oracle Database MCP Server

> A Model Context Protocol (MCP) server that enables AI assistants to execute SQL queries and explore Oracle databases through a standardized interface.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Protocol-orange.svg)](https://modelcontextprotocol.io/)

A Model Context Protocol (MCP) server that provides direct SQL query execution capabilities for Oracle databases. This server enables AI assistants and MCP clients to interact with Oracle databases through a standardized interface, allowing for database exploration, query execution, and performance analysis.

## 🚀 Core Features

### SQL Query Execution
- Execute any SQL query (SELECT, INSERT, UPDATE, DELETE) against Oracle databases
- Support for parameterized queries to prevent SQL injection
- Automatic result formatting with configurable row limits
- Transaction handling with automatic commit for DML operations

### Database Schema Exploration
- **Table Discovery**: List all tables in the database or specific schemas
- **Table Structure**: Get detailed column information including data types, constraints, and defaults
- **Foreign Key Relationships**: Discover table relationships and dependencies
- **Query Performance Analysis**: Generate and analyze execution plans for query optimization

### MCP Protocol Integration
- Full Model Context Protocol (MCP) compliance
- Tool-based interface for database operations
- Resource-based schema information access
- Async/await support for concurrent operations
- Comprehensive error handling and logging

## 📋 Requirements

- Python 3.8+
- Oracle Database (11g, 12c, 18c, 19c, 21c)
- Oracle Client Libraries (Instant Client or full client)
- MCP-compatible client (Cursor, Claude Desktop, etc.)

## 🛠️ Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/oracle-mcp-server.git
   cd oracle-mcp-server
   ```

2. **Run the setup script** (recommended):
   ```bash
   python setup.py
   ```
   
   This will:
   - Check Python version compatibility
   - Install required dependencies
   - Create `config.json` from example
   - Verify Oracle client availability

3. **Install Oracle Client Libraries** (if not already installed):
   
   **Option A: Oracle Instant Client (Recommended)**
   - Download Oracle Instant Client from Oracle website
   - Extract to a directory (e.g., `C:\oracle\instantclient_21_3`)
   - Add the directory to your PATH environment variable
   
   **Option B: Using thick mode with oracledb**
   ```bash
   pip install oracledb[thick]
   ```

4. **Configure database connection**:
   ```bash
   # Edit config.json with your database details
   # Use your preferred editor to modify config.json
   ```

5. **Run the server**:
   ```bash
   python mcp_server.py
   ```

## ⚙️ Configuration

The server uses `config.json` for configuration. Copy `config.example.json` to `config.json` and update with your Oracle database details:

```json
{
    "database": {
        "host": "your-oracle-host",
        "port": 1521,
        "username": "your-username",
        "password": "your-password",
        "sid": "your-sid",
        "service_name": null
    },
    "mcp": {
        "server_name": "oracle-sql-helper",
        "version": "1.0.0",
        "description": "Oracle Database MCP Server for SQL query execution",
        "max_results": 1000,
        "timeout_seconds": 30
    },
    "logging": {
        "level": "INFO",
        "file": "mcp_server.log"
    }
}
```

### Configuration Options

- **database**: Oracle database connection details
  - `host`: Database server hostname/IP
  - `port`: Database port (usually 1521)
  - `username`: Database username
  - `password`: Database password
  - `sid`: Database SID (Service Identifier)
  - `service_name`: Alternative to SID (use one or the other)

- **mcp**: MCP server settings
  - `max_results`: Maximum number of rows to return (default: 1000)
  - `timeout_seconds`: Query timeout in seconds (default: 30)

- **logging**: Logging configuration
  - `level`: Log level (DEBUG, INFO, WARNING, ERROR)
  - `file`: Log file name

## 🛠️ Available Tools

The MCP server provides the following tools:

#### 1. execute_sql
Execute SQL queries against the Oracle database.

**Parameters:**
- `query` (required): SQL query to execute
- `params` (optional): Array of parameters for parameterized queries

**Example:**
```sql
SELECT customer_name, account_balance 
FROM account a 
JOIN customer_node c ON a.customer_node_id = c.customer_node_id 
WHERE account_balance > 1000
```

#### 2. describe_table
Get detailed table structure and column information.

**Parameters:**
- `table_name` (required): Name of the table to describe
- `schema` (optional): Schema name

**Example:**
```
Table: ACCOUNT

Column Name | Data Type | Length | Precision | Scale | Nullable | Default
ACCOUNT_ID | NUMBER | | 10 | 0 | N | 
CUSTOMER_NODE_ID | NUMBER | | 10 | 0 | Y | 
ACCOUNT_TYPE_ID | NUMBER | | 10 | 0 | Y | 
ACCOUNT_BALANCE | NUMBER | | 15 | 2 | Y | 0
```

#### 3. list_tables
List all tables in the database or specific schema.

**Parameters:**
- `schema` (optional): Schema name to filter tables
- `pattern` (optional): Pattern to match table names

#### 4. get_table_relationships
Get foreign key relationships for a table.

**Parameters:**
- `table_name` (required): Name of the table
- `schema` (optional): Schema name

#### 5. analyze_query_plan
Get execution plan for SQL query performance analysis.

**Parameters:**
- `query` (required): SQL query to analyze

### Resources

The server also provides these resources:

- `oracle://database/schema`: Complete database schema information (JSON)
- `oracle://database/tables`: List of all database tables with metadata (JSON)

## 🔗 MCP Client Configuration

To use this server with an MCP client, add the following to your MCP client configuration:

```json
{
  "mcpServers": {
    "oracle-sql-helper": {
      "command": "python",
      "args": ["path/to/oracle-mcp-server/mcp_server.py"],
      "env": {}
    }
  }
}
```

## 🔒 Security Features

- Secure credential management via configuration files
- Parameterized query support to prevent SQL injection
- Configurable result limits to prevent memory issues
- Comprehensive logging for audit trails
- Connection timeout and error handling

## 📊 Performance Features

- Configurable result set limits (default: 1000 rows)
- Query timeout protection (default: 30 seconds)
- Execution plan analysis for query optimization
- Efficient connection management
- Async operation support

## 🐛 Troubleshooting

### Common Issues

1. **Oracle client not found**:
   - Ensure Oracle Instant Client is installed and in PATH
   - Try installing `oracledb[thick]` package

2. **Connection timeout**:
   - Verify database host and port are correct
   - Check network connectivity
   - Verify database is running and accepting connections

3. **Authentication failed**:
   - Verify username and password
   - Check if account is locked or expired
   - Ensure proper privileges are granted

4. **TNS errors**:
   - Verify SID or service_name is correct
   - Check Oracle listener is running
   - Verify network configuration

### Debugging

Enable debug logging by setting log level to "DEBUG" in config.json:

```json
{
    "logging": {
        "level": "DEBUG",
        "file": "mcp_server.log"
    }
}
```

Check the log file `mcp_server.log` for detailed error messages.

## 📝 Sample Queries

Here are some sample queries you can try:

### Basic Account Information
```sql
SELECT account_id, account_balance, created_date 
FROM account 
WHERE account_balance > 100 
ORDER BY account_balance DESC
```

### Customer Account Summary
```sql
SELECT c.customer_name, COUNT(a.account_id) as account_count, 
       SUM(a.account_balance) as total_balance
FROM customer_node c
LEFT JOIN account a ON c.customer_node_id = a.customer_node_id
GROUP BY c.customer_name
HAVING COUNT(a.account_id) > 0
ORDER BY total_balance DESC
```

### Account History Analysis
```sql
SELECT ah.account_id, ah.transaction_type, ah.amount, ah.transaction_date
FROM account_history ah
WHERE ah.transaction_date >= SYSDATE - 30
ORDER BY ah.transaction_date DESC
```

## ⚡ Performance Tips

1. **Use Indexes**: Ensure proper indexes exist for your queries
2. **Limit Results**: Use the `max_results` configuration to prevent memory issues
3. **Parameterized Queries**: Use parameters to prevent SQL injection and improve performance
4. **Query Analysis**: Use the `analyze_query_plan` tool to optimize slow queries
5. **Connection Pooling**: Consider implementing connection pooling for high-load scenarios

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the log files
3. Verify Oracle client installation
4. Test database connectivity outside of MCP
5. Open an issue on GitHub
