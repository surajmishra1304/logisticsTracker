# PostgreSQL Database Direct Access Guide

This guide explains how to access and manage your logistics application's PostgreSQL database directly without going through the frontend interface.

## Table of Contents
1. [Connection Information](#connection-information)
2. [Connection Methods](#connection-methods)
3. [Essential SQL Commands](#essential-sql-commands)
4. [Table Structure](#table-structure)
5. [Common Queries](#common-queries)
6. [Database Maintenance](#database-maintenance)
7. [Security Best Practices](#security-best-practices)

---

## Connection Information

To connect to your PostgreSQL database, you need the following information (available as environment variables in your deployment):

- **Host**: The database server hostname (`PGHOST`)
- **Port**: The database port (`PGPORT`, typically 5432)
- **Database Name**: Your database name (`PGDATABASE`)
- **Username**: Your database username (`PGUSER`)
- **Password**: Your database password (`PGPASSWORD`)
- **Connection URI**: Full connection string (`DATABASE_URL`)

---

## Connection Methods

### Using psql (CLI)

The most direct method is using the PostgreSQL command-line client:

```bash
# Using individual parameters
psql -h $PGHOST -p $PGPORT -d $PGDATABASE -U $PGUSER

# Using connection URI
psql $DATABASE_URL
```

You'll be prompted for your password unless you've set up environment variables or `.pgpass` file.

### Using pgAdmin (GUI)

1. Download and install [pgAdmin](https://www.pgadmin.org/download/)
2. Add a new server connection:
   - General tab: Enter any name for the connection
   - Connection tab: Enter host, port, database name, username, and password

### Using DBeaver (Cross-Platform GUI)

1. Download and install [DBeaver](https://dbeaver.io/download/)
2. Create a new PostgreSQL connection
3. Enter your connection details
4. Test the connection and save

### Using Database Management Scripts

For programmatic access, you can use scripts:

```javascript
// Node.js example using pool from server/db.ts
const { pool } = require('./server/db');

async function queryDatabase() {
  const result = await pool.query('SELECT * FROM users');
  console.log(result.rows);
}
```

---

## Essential SQL Commands

### View Data

```sql
-- List all tables in the database
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- View table structure
\d table_name

-- Query data from a table
SELECT * FROM users LIMIT 10;

-- Query with filter
SELECT * FROM packages WHERE status = 'PENDING';

-- Join tables
SELECT p.*, u.username
FROM packages p
JOIN users u ON p.assigned_to = u.id
WHERE p.status = 'IN_TRANSIT';
```

### Modify Data

```sql
-- Insert a new record
INSERT INTO users (username, email, password, role)
VALUES ('newuser', 'new@example.com', 'hashedpassword', 'DRIVER');

-- Update records
UPDATE packages 
SET status = 'DELIVERED', 
    delivery_date = CURRENT_TIMESTAMP 
WHERE id = 123;

-- Delete records (use with caution)
DELETE FROM notifications WHERE created_at < NOW() - INTERVAL '6 months';
```

### Database Administration

```sql
-- Create index for performance
CREATE INDEX idx_packages_status ON packages(status);

-- View query execution plan
EXPLAIN ANALYZE SELECT * FROM packages WHERE status = 'PENDING';

-- Check table size
SELECT pg_size_pretty(pg_total_relation_size('packages')) AS size;

-- Optimize database
VACUUM ANALYZE;
```

---

## Table Structure

The database contains the following primary tables:

### users
- id: Serial (Primary Key)
- username: Text
- email: Text
- password: Text (hashed)
- role: Text (ADMIN, WAREHOUSE, DRIVER)
- created_at: Timestamp
- updated_at: Timestamp
- verification_token: Text (nullable)
- email_verified: Boolean
- verification_expires: Timestamp (nullable)

### packages
- id: Serial (Primary Key)
- package_id: Text (tracking code)
- sender_name: Text
- sender_address: Text
- sender_email: Text
- sender_phone: Text
- recipient_name: Text
- recipient_address: Text
- recipient_email: Text
- recipient_phone: Text
- weight: Numeric
- dimensions: JSON
- status: Text (PENDING, IN_TRANSIT, DELIVERED, etc.)
- assigned_to: Integer (Foreign Key to users)
- location: Text
- latitude: Numeric (nullable)
- longitude: Numeric (nullable)
- created_at: Timestamp
- updated_at: Timestamp
- estimated_delivery: Timestamp (nullable)
- actual_delivery: Timestamp (nullable)
- description: Text
- external_id: Text (nullable)
- metadata: JSON (nullable)

### package_history
- id: Serial (Primary Key)
- package_id: Integer (Foreign Key to packages)
- status: Text
- location: Text
- latitude: Numeric (nullable)
- longitude: Numeric (nullable)
- timestamp: Timestamp
- ip_address: Text (nullable)
- updated_by: Integer (Foreign Key to users)
- notes: Text (nullable)

---

## Common Queries

### Dashboard Statistics

```sql
-- Count packages by status
SELECT status, COUNT(*) as count
FROM packages
GROUP BY status
ORDER BY count DESC;

-- Packages assigned to each driver
SELECT u.username, COUNT(p.id) as package_count
FROM users u
LEFT JOIN packages p ON u.id = p.assigned_to
WHERE u.role = 'DRIVER'
GROUP BY u.username
ORDER BY package_count DESC;

-- Average delivery time in days
SELECT AVG(EXTRACT(EPOCH FROM (actual_delivery - created_at))/86400) as avg_days
FROM packages
WHERE status = 'DELIVERED' AND actual_delivery IS NOT NULL;
```

### Security Auditing

```sql
-- Recent login attempts
SELECT 
  u.username, 
  ul.ip_address, 
  ul.timestamp, 
  ul.login_success
FROM user_logins ul
JOIN users u ON ul.user_id = u.id
ORDER BY ul.timestamp DESC
LIMIT 100;

-- Failed login attempts by IP
SELECT ip_address, COUNT(*) as attempts
FROM user_logins
WHERE login_success = false AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY ip_address
HAVING COUNT(*) > 5
ORDER BY attempts DESC;
```

### Operational Queries

```sql
-- Packages in transit for more than 3 days
SELECT p.*, u.username as driver
FROM packages p
JOIN users u ON p.assigned_to = u.id
WHERE p.status = 'IN_TRANSIT'
AND p.updated_at < NOW() - INTERVAL '3 days';

-- Recent package status changes
SELECT 
  p.package_id, 
  ph.status, 
  ph.timestamp, 
  u.username as updated_by
FROM package_history ph
JOIN packages p ON ph.package_id = p.id
JOIN users u ON ph.updated_by = u.id
ORDER BY ph.timestamp DESC
LIMIT 50;
```

---

## Database Maintenance

### Regular Maintenance Tasks

1. **Backup Database**
   ```bash
   pg_dump -h $PGHOST -p $PGPORT -d $PGDATABASE -U $PGUSER -F c -f backup_filename.dump
   ```

2. **Restore from Backup**
   ```bash
   pg_restore -h $PGHOST -p $PGPORT -d $PGDATABASE -U $PGUSER -c -F c backup_filename.dump
   ```

3. **Optimize Database**
   ```sql
   VACUUM ANALYZE;
   ```

4. **Monitor Database Size**
   ```sql
   SELECT pg_size_pretty(pg_database_size(current_database()));
   ```

5. **Check for Slow Queries**
   ```sql
   SELECT 
     query,
     calls,
     total_time,
     mean_time,
     rows
   FROM pg_stat_statements
   ORDER BY total_time DESC
   LIMIT 10;
   ```

---

## Security Best Practices

1. **Never connect to the database from public networks without SSL/TLS encryption**
2. **Use strong, unique passwords for database access**
3. **Limit database user permissions to only what's needed**
4. **Regularly audit database access logs**
5. **Implement IP restrictions for database access when possible**
6. **Never store sensitive data unencrypted**
7. **Regularly back up the database and test restoration procedures**
8. **Use prepared statements to prevent SQL injection**
9. **Keep PostgreSQL software updated to the latest secure version**

---

*This guide is subject to updates. Last revised: April 6, 2025.*
