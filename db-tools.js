#!/usr/bin/env node

/**
 * Database Tools - Direct PostgreSQL Operations
 * 
 * This utility script provides direct access to your PostgreSQL database
 * for operations that you want to perform outside of the application.
 * 
 * Usage:
 *   node db-tools.js query "SELECT * FROM users LIMIT 5"
 *   node db-tools.js execute "UPDATE packages SET status = 'DELIVERED' WHERE id = 123"
 *   node db-tools.js tables
 *   node db-tools.js describe packages
 */

import { pool } from './server/db.js';
import readline from 'readline';

// Create interactive readline interface
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Get command line arguments
const [,, command, ...args] = process.argv;

// Format SQL result for display
function formatResult(result) {
  if (!result || !result.rows || result.rows.length === 0) {
    return 'No results found.';
  }
  
  // Get column names
  const columns = Object.keys(result.rows[0]);
  const columnWidths = columns.map(col => Math.max(
    col.length,
    ...result.rows.map(row => String(row[col] || '').length)
  ));
  
  // Create header
  let output = columns.map((col, i) => col.padEnd(columnWidths[i])).join(' | ') + '\n';
  output += columnWidths.map(width => '-'.repeat(width)).join('-+-') + '\n';
  
  // Add rows
  result.rows.forEach(row => {
    output += columns.map((col, i) => 
      String(row[col] === null ? 'NULL' : row[col]).padEnd(columnWidths[i])
    ).join(' | ') + '\n';
  });
  
  return output;
}

// Execute a query and return results
async function executeQuery(sql, params = []) {
  try {
    console.log(`Executing: ${sql}`);
    if (params.length > 0) console.log(`Parameters: ${JSON.stringify(params)}`);
    
    const result = await pool.query(sql, params);
    return result;
  } catch (error) {
    console.error('Database Error:', error.message);
    console.error('Query:', sql);
    if (params.length > 0) console.error('Parameters:', params);
    return { rows: [], rowCount: 0, error: error.message };
  }
}

// Get list of tables
async function listTables() {
  const sql = `
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name
  `;
  
  const result = await executeQuery(sql);
  console.log('Available Tables:');
  console.log('================');
  result.rows.forEach(row => console.log(row.table_name));
  return result;
}

// Describe table structure
async function describeTable(tableName) {
  const sql = `
    SELECT 
      column_name, 
      data_type, 
      is_nullable, 
      column_default
    FROM information_schema.columns 
    WHERE table_schema = 'public' 
      AND table_name = $1
    ORDER BY ordinal_position
  `;
  
  const result = await executeQuery(sql, [tableName]);
  if (result.rows.length === 0) {
    console.log(`Table '${tableName}' not found.`);
    return;
  }
  
  console.log(`Table Structure for '${tableName}':`);
  console.log('==============================');
  console.log(formatResult(result));
  
  // Get indexes for this table
  const indexesSql = `
    SELECT
      i.relname as index_name,
      a.attname as column_name,
      ix.indisunique as is_unique,
      ix.indisprimary as is_primary
    FROM
      pg_class t,
      pg_class i,
      pg_index ix,
      pg_attribute a
    WHERE
      t.oid = ix.indrelid
      and i.oid = ix.indexrelid
      and a.attrelid = t.oid
      and a.attnum = ANY(ix.indkey)
      and t.relkind = 'r'
      and t.relname = $1
    ORDER BY
      i.relname
  `;
  
  const indexesResult = await executeQuery(indexesSql, [tableName]);
  if (indexesResult.rows.length > 0) {
    console.log('\nIndexes:');
    console.log('========');
    console.log(formatResult(indexesResult));
  }
  
  return result;
}

// Interactive mode - for running multiple queries
async function interactiveMode() {
  console.log('Interactive PostgreSQL CLI Mode');
  console.log('Type your SQL queries. Type "exit" or Ctrl+C to quit.');
  console.log('Special commands: "tables", "describe tablename"');
  console.log('=====================================================');
  
  const promptUser = () => {
    rl.question('SQL> ', async (input) => {
      if (input.toLowerCase() === 'exit') {
        console.log('Exiting interactive mode...');
        await pool.end();
        rl.close();
        return;
      }
      
      if (input.toLowerCase() === 'tables') {
        await listTables();
      } else if (input.toLowerCase().startsWith('describe ')) {
        const tableName = input.substring(9).trim();
        await describeTable(tableName);
      } else {
        try {
          const result = await executeQuery(input);
          console.log(formatResult(result));
          console.log(`Query returned ${result.rowCount} rows.`);
        } catch (error) {
          // Error is already logged in executeQuery
        }
      }
      
      promptUser();
    });
  };
  
  promptUser();
}

// Main execution
async function main() {
  try {
    // No args - print usage
    if (!command) {
      console.log(`
Usage:
  node db-tools.js query "SQL QUERY"     - Execute a read-only query
  node db-tools.js execute "SQL COMMAND" - Execute a command that modifies data
  node db-tools.js tables                - List all tables
  node db-tools.js describe TABLE_NAME   - Describe table structure
  node db-tools.js interactive           - Enter interactive SQL mode
      `);
      await pool.end();
      return;
    }
    
    // Handle different commands
    switch (command.toLowerCase()) {
      case 'query':
        if (!args[0]) {
          console.error('Error: No query provided');
          break;
        }
        const queryResult = await executeQuery(args[0]);
        console.log(formatResult(queryResult));
        console.log(`Query returned ${queryResult.rowCount} rows.`);
        break;
        
      case 'execute':
        if (!args[0]) {
          console.error('Error: No command provided');
          break;
        }
        
        // Confirm potentially destructive action
        rl.question(`You are about to execute: "${args[0]}"\nThis might modify data. Continue? (y/n) `, async (answer) => {
          if (answer.toLowerCase() === 'y') {
            const execResult = await executeQuery(args[0]);
            console.log(`Command executed. Affected ${execResult.rowCount} rows.`);
          } else {
            console.log('Command cancelled.');
          }
          await pool.end();
          rl.close();
        });
        return; // Don't close the pool yet
        
      case 'tables':
        await listTables();
        break;
        
      case 'describe':
        if (!args[0]) {
          console.error('Error: No table name provided');
          break;
        }
        await describeTable(args[0]);
        break;
        
      case 'interactive':
        interactiveMode();
        return; // Don't close the pool yet in interactive mode
        
      default:
        console.error(`Error: Unknown command '${command}'`);
        break;
    }
    
    // Close the connection pool and readline interface
    await pool.end();
    rl.close();
    
  } catch (error) {
    console.error('Error:', error.message);
    try {
      await pool.end();
    } catch (e) {
      // Ignore pool closing errors
    }
    rl.close();
    process.exit(1);
  }
}

// Execute main function
main();