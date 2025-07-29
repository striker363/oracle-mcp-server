#!/usr/bin/env python3
"""
Oracle Database MCP Server
A Model Context Protocol server for executing SQL queries against Oracle Database
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional, Union
import traceback
import os
from datetime import datetime

# MCP imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
from types import SimpleNamespace

# Oracle database imports
try:
    import oracledb
except ImportError:
    oracledb = None

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("oracle-mcp-server")

class OracleMCPServer:
    """Oracle Database MCP Server"""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the Oracle MCP Server"""
        self.config = self._load_config(config_path)
        self.connection = None
        self.server = Server("oracle-sql-helper")
        self._setup_tools()
        self._setup_resources()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file {config_path} not found")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            raise
    
    def _setup_tools(self):
        """Setup MCP tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="execute_sql",
                    description="Execute SQL query against Oracle database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL query to execute"
                            },
                            "params": {
                                "type": "array",
                                "description": "Optional parameters for parameterized queries",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="describe_table",
                    description="Get table structure and column information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Name of the table to describe"
                            },
                            "schema": {
                                "type": "string",
                                "description": "Schema name (optional)"
                            }
                        },
                        "required": ["table_name"]
                    }
                ),
                Tool(
                    name="list_tables",
                    description="List all tables in the database or specific schema",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "schema": {
                                "type": "string",
                                "description": "Schema name to filter tables (optional)"
                            },
                            "pattern": {
                                "type": "string",
                                "description": "Pattern to match table names (optional)"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_table_relationships",
                    description="Get foreign key relationships for a table",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Name of the table"
                            },
                            "schema": {
                                "type": "string",
                                "description": "Schema name (optional)"
                            }
                        },
                        "required": ["table_name"]
                    }
                ),
                Tool(
                    name="analyze_query_plan",
                    description="Get execution plan for a SQL query",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL query to analyze"
                            }
                        },
                        "required": ["query"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            try:
                if name == "execute_sql":
                    return await self._execute_sql(arguments)
                elif name == "describe_table":
                    return await self._describe_table(arguments)
                elif name == "list_tables":
                    return await self._list_tables(arguments)
                elif name == "get_table_relationships":
                    return await self._get_table_relationships(arguments)
                elif name == "analyze_query_plan":
                    return await self._analyze_query_plan(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                logger.error(traceback.format_exc())
                return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]
    
    def _setup_resources(self):
        """Setup MCP resources"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available resources"""
            return [
                Resource(
                    uri="oracle://database/schema",
                    name="Database Schema",
                    description="Complete database schema information",
                    mimeType="application/json"
                ),
                Resource(
                    uri="oracle://database/tables",
                    name="Database Tables",
                    description="List of all database tables",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Handle resource reading"""
            try:
                if uri == "oracle://database/schema":
                    return await self._get_database_schema()
                elif uri == "oracle://database/tables":
                    return await self._get_database_tables()
                else:
                    raise ValueError(f"Unknown resource: {uri}")
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                raise
    
    async def _connect_database(self):
        """Connect to Oracle database"""
        if self.connection is not None:
            return
            
        if oracledb is None:
            raise ImportError("oracledb library not installed. Install with: pip install oracledb")
        
        try:
            db_config = self.config["database"]
            
            # Create connection string
            if db_config.get("service_name"):
                dsn = f"{db_config['host']}:{db_config['port']}/{db_config['service_name']}"
            else:
                dsn = f"{db_config['host']}:{db_config['port']}/{db_config['sid']}"
            
            self.connection = oracledb.connect(
                user=db_config["username"],
                password=db_config["password"],
                dsn=dsn
            )
            
            logger.info("Successfully connected to Oracle database")
            
        except Exception as e:
            logger.error(f"Failed to connect to Oracle database: {e}")
            raise
    
    async def _execute_sql(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute SQL query"""
        await self._connect_database()
        
        query = arguments["query"]
        params = arguments.get("params", [])
        
        try:
            cursor = self.connection.cursor()
            
            # Execute query
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Handle different query types
            if query.strip().upper().startswith(("SELECT", "WITH")):
                # Fetch results for SELECT queries
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                # Limit results
                max_results = self.config["mcp"].get("max_results", 1000)
                if len(rows) > max_results:
                    rows = rows[:max_results]
                    truncated_msg = f"\n\n(Results truncated to {max_results} rows)"
                else:
                    truncated_msg = ""
                
                # Format results
                if rows:
                    # Create table format
                    result = f"Query executed successfully. Found {len(rows)} rows.\n\n"
                    result += " | ".join(columns) + "\n"
                    result += "-" * (len(" | ".join(columns))) + "\n"
                    
                    for row in rows:
                        formatted_row = []
                        for val in row:
                            if val is None:
                                formatted_row.append("NULL")
                            elif isinstance(val, (datetime,)):
                                formatted_row.append(val.strftime("%Y-%m-%d %H:%M:%S"))
                            else:
                                formatted_row.append(str(val))
                        result += " | ".join(formatted_row) + "\n"
                    
                    result += truncated_msg
                else:
                    result = "Query executed successfully. No rows returned."
                    
            else:
                # For INSERT, UPDATE, DELETE, etc.
                self.connection.commit()
                result = f"Query executed successfully. {cursor.rowcount} rows affected."
            
            cursor.close()
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            return [TextContent(type="text", text=f"SQL Error: {str(e)}")]
    
    async def _describe_table(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Describe table structure"""
        await self._connect_database()
        
        table_name = arguments["table_name"].upper()
        schema = arguments.get("schema", "").upper()
        
        try:
            cursor = self.connection.cursor()
            
            # Query for column information
            if schema:
                query = """
                SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH, DATA_PRECISION, 
                       DATA_SCALE, NULLABLE, DATA_DEFAULT
                FROM ALL_TAB_COLUMNS 
                WHERE TABLE_NAME = :table_name AND OWNER = :schema
                ORDER BY COLUMN_ID
                """
                cursor.execute(query, [table_name, schema])
            else:
                query = """
                SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH, DATA_PRECISION, 
                       DATA_SCALE, NULLABLE, DATA_DEFAULT
                FROM USER_TAB_COLUMNS 
                WHERE TABLE_NAME = :table_name
                ORDER BY COLUMN_ID
                """
                cursor.execute(query, [table_name])
            
            columns = cursor.fetchall()
            
            if not columns:
                return [TextContent(type="text", text=f"Table {table_name} not found")]
            
            # Format table description
            result = f"Table: {table_name}\n\n"
            result += "Column Name | Data Type | Length | Precision | Scale | Nullable | Default\n"
            result += "-" * 80 + "\n"
            
            for col in columns:
                col_name, data_type, length, precision, scale, nullable, default = col
                
                # Format data type
                if precision and scale:
                    type_info = f"{data_type}({precision},{scale})"
                elif length and data_type in ('VARCHAR2', 'CHAR', 'NVARCHAR2', 'NCHAR'):
                    type_info = f"{data_type}({length})"
                else:
                    type_info = data_type
                
                default_val = str(default) if default else ""
                result += f"{col_name} | {type_info} | {length or ''} | {precision or ''} | {scale or ''} | {nullable} | {default_val}\n"
            
            cursor.close()
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            logger.error(f"Error describing table: {e}")
            return [TextContent(type="text", text=f"Error describing table: {str(e)}")]
    
    async def _list_tables(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """List database tables"""
        await self._connect_database()
        
        schema = arguments.get("schema", "").upper()
        pattern = arguments.get("pattern", "")
        
        try:
            cursor = self.connection.cursor()
            
            if schema:
                query = "SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER = :schema"
                params = [schema]
            else:
                query = "SELECT TABLE_NAME FROM USER_TABLES"
                params = []
            
            if pattern:
                query += " AND TABLE_NAME LIKE :pattern"
                params.append(f"%{pattern.upper()}%")
            
            query += " ORDER BY TABLE_NAME"
            
            cursor.execute(query, params)
            tables = cursor.fetchall()
            
            if not tables:
                return [TextContent(type="text", text="No tables found")]
            
            result = f"Found {len(tables)} tables:\n\n"
            for table in tables:
                result += f"- {table[0]}\n"
            
            cursor.close()
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            return [TextContent(type="text", text=f"Error listing tables: {str(e)}")]
    
    async def _get_table_relationships(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get table foreign key relationships"""
        await self._connect_database()
        
        table_name = arguments["table_name"].upper()
        schema = arguments.get("schema", "").upper()
        
        try:
            cursor = self.connection.cursor()
            
            # Query for foreign keys
            if schema:
                query = """
                SELECT a.CONSTRAINT_NAME, a.COLUMN_NAME, c_pk.TABLE_NAME as REFERENCED_TABLE,
                       a_pk.COLUMN_NAME as REFERENCED_COLUMN
                FROM ALL_CONS_COLUMNS a
                JOIN ALL_CONSTRAINTS c ON a.CONSTRAINT_NAME = c.CONSTRAINT_NAME
                JOIN ALL_CONSTRAINTS c_pk ON c.R_CONSTRAINT_NAME = c_pk.CONSTRAINT_NAME
                JOIN ALL_CONS_COLUMNS a_pk ON c_pk.CONSTRAINT_NAME = a_pk.CONSTRAINT_NAME
                WHERE c.CONSTRAINT_TYPE = 'R'
                AND a.TABLE_NAME = :table_name
                AND a.OWNER = :schema
                ORDER BY a.CONSTRAINT_NAME, a.POSITION
                """
                cursor.execute(query, [table_name, schema])
            else:
                query = """
                SELECT a.CONSTRAINT_NAME, a.COLUMN_NAME, c_pk.TABLE_NAME as REFERENCED_TABLE,
                       a_pk.COLUMN_NAME as REFERENCED_COLUMN
                FROM USER_CONS_COLUMNS a
                JOIN USER_CONSTRAINTS c ON a.CONSTRAINT_NAME = c.CONSTRAINT_NAME
                JOIN USER_CONSTRAINTS c_pk ON c.R_CONSTRAINT_NAME = c_pk.CONSTRAINT_NAME
                JOIN USER_CONS_COLUMNS a_pk ON c_pk.CONSTRAINT_NAME = a_pk.CONSTRAINT_NAME
                WHERE c.CONSTRAINT_TYPE = 'R'
                AND a.TABLE_NAME = :table_name
                ORDER BY a.CONSTRAINT_NAME, a.POSITION
                """
                cursor.execute(query, [table_name])
            
            relationships = cursor.fetchall()
            
            if not relationships:
                return [TextContent(type="text", text=f"No foreign key relationships found for table {table_name}")]
            
            result = f"Foreign Key Relationships for {table_name}:\n\n"
            result += "Constraint Name | Column | Referenced Table | Referenced Column\n"
            result += "-" * 70 + "\n"
            
            for rel in relationships:
                constraint_name, column, ref_table, ref_column = rel
                result += f"{constraint_name} | {column} | {ref_table} | {ref_column}\n"
            
            cursor.close()
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            logger.error(f"Error getting table relationships: {e}")
            return [TextContent(type="text", text=f"Error getting relationships: {str(e)}")]
    
    async def _analyze_query_plan(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Analyze query execution plan"""
        await self._connect_database()
        
        query = arguments["query"]
        
        try:
            cursor = self.connection.cursor()
            
            # Generate unique statement ID
            stmt_id = f"MCP_PLAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Explain plan
            explain_query = f"EXPLAIN PLAN SET STATEMENT_ID = '{stmt_id}' FOR {query}"
            cursor.execute(explain_query)
            
            # Get plan
            plan_query = """
            SELECT LPAD(' ', 2 * LEVEL) || OPERATION || ' ' || 
                   NVL(OPTIONS, '') || ' ' || 
                   NVL(OBJECT_NAME, '') as PLAN_LINE,
                   COST, CARDINALITY
            FROM PLAN_TABLE 
            WHERE STATEMENT_ID = :stmt_id
            START WITH ID = 0 
            CONNECT BY PRIOR ID = PARENT_ID 
            ORDER BY ID
            """
            cursor.execute(plan_query, [stmt_id])
            plan_rows = cursor.fetchall()
            
            if not plan_rows:
                return [TextContent(type="text", text="No execution plan generated")]
            
            result = f"Execution Plan for Query:\n{query}\n\n"
            result += "Operation | Cost | Cardinality\n"
            result += "-" * 50 + "\n"
            
            for row in plan_rows:
                plan_line, cost, cardinality = row
                result += f"{plan_line} | {cost or ''} | {cardinality or ''}\n"
            
            # Clean up
            cursor.execute("DELETE FROM PLAN_TABLE WHERE STATEMENT_ID = :stmt_id", [stmt_id])
            self.connection.commit()
            
            cursor.close()
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            logger.error(f"Error analyzing query plan: {e}")
            return [TextContent(type="text", text=f"Error analyzing plan: {str(e)}")]
    
    async def _get_database_schema(self) -> str:
        """Get complete database schema as JSON"""
        await self._connect_database()
        
        try:
            # Load existing schema index if available
            schema_file = "db_index.json"
            if os.path.exists(schema_file):
                with open(schema_file, 'r') as f:
                    return f.read()
            
            # If not available, generate basic schema info
            cursor = self.connection.cursor()
            cursor.execute("SELECT TABLE_NAME FROM USER_TABLES ORDER BY TABLE_NAME")
            tables = [row[0] for row in cursor.fetchall()]
            
            schema_info = {
                "tables": tables,
                "generated_at": datetime.now().isoformat(),
                "note": "Basic schema info - load db_index.json for detailed information"
            }
            
            cursor.close()
            return json.dumps(schema_info, indent=2)
            
        except Exception as e:
            logger.error(f"Error getting database schema: {e}")
            return json.dumps({"error": str(e)})
    
    async def _get_database_tables(self) -> str:
        """Get database tables as JSON"""
        await self._connect_database()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT TABLE_NAME, NUM_ROWS, LAST_ANALYZED 
                FROM USER_TABLES 
                ORDER BY TABLE_NAME
            """)
            
            tables = []
            for row in cursor.fetchall():
                table_name, num_rows, last_analyzed = row
                tables.append({
                    "name": table_name,
                    "row_count": num_rows,
                    "last_analyzed": last_analyzed.isoformat() if last_analyzed else None
                })
            
            cursor.close()
            return json.dumps({"tables": tables}, indent=2)
            
        except Exception as e:
            logger.error(f"Error getting database tables: {e}")
            return json.dumps({"error": str(e)})
    
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting Oracle MCP Server")
        
        try:
            # Initialize server
            async with stdio_server() as (read_stream, write_stream):
                logger.info("stdio server initialized successfully")
                
                # Create empty notification options
                notification_options = SimpleNamespace()
                notification_options.tools_changed = False
                notification_options.resources_changed = False
                notification_options.prompts_changed = False
                
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name=self.config["mcp"]["server_name"],
                        server_version=self.config["mcp"]["version"],
                        capabilities=self.server.get_capabilities(
                            notification_options=notification_options,
                            experimental_capabilities={}
                        )
                    )
                )
        except Exception as e:
            logger.error(f"Error in server run: {e}")
            logger.error(traceback.format_exc())
            raise

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "config.json"
    
    try:
        server = OracleMCPServer(config_path)
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
