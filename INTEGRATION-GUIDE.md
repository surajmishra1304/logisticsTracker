# Logistics Application - Integration Guide & Core Concepts

## Table of Contents
1. [System Overview](#system-overview)
2. [Core Components](#core-components)
3. [Integration Options](#integration-options)
4. [E-commerce Integrations](#e-commerce-integrations)
5. [API Reference](#api-reference)
6. [Webhook Handling](#webhook-handling)
7. [Database Schema](#database-schema)
8. [Environment Variables](#environment-variables)
9. [Troubleshooting](#troubleshooting)
10. [Release & Update Process](#release-and-update-process)

---

## System Overview

The Logistics Application is a comprehensive platform designed to streamline shipping, tracking, and collaboration processes for businesses. It provides real-time package tracking, inventory management, role-based access control, and integration with e-commerce platforms.

### Key Features
- **Package Tracking**: Real-time tracking via QR codes and GPS coordinates
- **User Authentication**: Role-based access control (Admin, Warehouse, Driver)
- **Inventory Management**: Stock tracking and transfer between locations
- **Analytics Dashboard**: Performance metrics and system insights
- **Notification System**: Status change alerts and system notifications
- **E-commerce Integration**: Automatic order to package conversion
- **Force Management**: Local work environment for operational commands
- **Admin Panel**: Direct database access for advanced operations

---

## Core Components

### Frontend Architecture
- **React**: Component-based UI framework
- **TanStack Query**: Data fetching and state management
- **Wouter**: Lightweight routing solution
- **Shadcn UI**: Component library for consistent design

### Backend Architecture
- **Express**: Web server framework
- **PostgreSQL**: Relational database
- **Drizzle ORM**: Type-safe database interactions
- **Caching**: In-memory cache with TTL support
- **WebSockets**: Real-time updates for critical components

### Performance Optimizations
- **Caching Strategy**: Endpoint-specific TTLs with proper invalidation
- **Database Indexing**: Optimized for high-volume queries
- **Connection Pooling**: Efficient database connection management
- **Load Distribution**: Horizontal scaling capabilities

---

## Integration Options

The system supports multiple integration points for external systems:

### REST API Integration
External systems can interact with the logistics platform through REST API endpoints. Authentication is required via JWT tokens.

### Webhook Integration
The system can receive webhooks from external platforms and trigger appropriate actions based on the payload.

### Database Integration
For internal systems, direct database integration is possible with proper access controls.

---

## E-commerce Integrations

### WooCommerce Integration
The system supports seamless integration with WooCommerce stores:

#### Configuration Steps
1. Navigate to WooCommerce → Settings → Advanced → Webhooks
2. Add a new webhook with the target URL: `https://your-app-url.com/api/webhook/woocommerce`
3. Set the topic to "Order created" and "Product updated"
4. Choose the latest API version
5. Set the status to "Active"

#### Data Mapping
- WooCommerce orders are converted to packages with the following mapping:
  - Order ID → External ID
  - Shipping address → Recipient information
  - Billing address → Sender information
  - Products → Package details (weight, dimensions)
  - Shipping method → Shipping information

### Shopify Integration
Similar to WooCommerce, with different webhook configuration:

#### Configuration Steps
1. Go to Shopify Admin → Settings → Notifications → Webhooks
2. Add webhook with target URL: `https://your-app-url.com/api/webhook/shopify`
3. Select events: "Order creation" and "Product update"
4. Set format to JSON

### Amazon Integration
For Amazon integration, use the webhook endpoint:
`https://your-app-url.com/api/webhook/amazon`

### Custom Integration
For any custom e-commerce platform:
1. Configure webhooks to point to: `https://your-app-url.com/api/webhook/custom`
2. Include the integration type in the request header: `X-Integration-Type: your_integration_name`
3. Ensure the payload follows the expected format (see API Reference)

---

## API Reference

### Authentication Endpoints
- `POST /api/auth/login`: User authentication 
- `POST /api/auth/verify-email/:token`: Email verification
- `POST /api/auth/request-verification`: Request email verification

### Package Endpoints
- `GET /api/packages`: List all packages (filterable by status/user)
- `GET /api/packages/:id`: Get package details
- `POST /api/packages`: Create new package
- `PUT /api/packages/:id`: Update package details
- `DELETE /api/packages/:id`: Delete package
- `POST /api/packages/:id/status-change`: Update package status

### Inventory Endpoints
- `GET /api/inventory`: List inventory items
- `GET /api/inventory/:id`: Get inventory item details
- `POST /api/inventory`: Create inventory item
- `PUT /api/inventory/:id`: Update inventory item
- `DELETE /api/inventory/:id`: Delete inventory item
- `POST /api/inventory/transfer`: Transfer inventory between locations

### Integration Endpoints
- `GET /api/integrations`: List configured integrations
- `POST /api/integrations`: Add new integration
- `PUT /api/integrations/:id`: Update integration
- `DELETE /api/integrations/:id`: Remove integration
- `POST /api/webhook/:integrationType`: Webhook receiver for integrations

### User & Force Management
- `GET /api/users`: List all users
- `POST /api/users`: Create new user
- `GET /api/force-details`: List force details
- `POST /api/force-details`: Create force detail
- `PUT /api/force-details/:id`: Update force detail
- `DELETE /api/force-details/:id`: Delete force detail
- `POST /api/force-management/query`: Execute force management query

### Third-Party Endpoints
- `POST /api/third-party/packages`: Accept package from external system
- `PUT /api/third-party/packages/:externalId/status`: Update package status
- `GET /api/third-party/packages/:externalId`: Get package by external ID

---

## Webhook Handling

### Expected Payload Structure
Webhooks should send data in the following format:

```json
{
  "externalId": "order_12345",
  "sender": {
    "name": "John Doe",
    "email": "john@example.com",
    "address": "123 Sender St, City, Country",
    "phone": "+1234567890"
  },
  "recipient": {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "address": "456 Recipient Ave, City, Country",
    "phone": "+0987654321"
  },
  "packageDetails": {
    "weight": 2.5,
    "dimensions": {
      "length": 30,
      "width": 20,
      "height": 10
    },
    "description": "Fragile items",
    "value": 150,
    "category": "Electronics"
  },
  "shipping": {
    "method": "Express",
    "priority": "High",
    "trackingNumber": "TRACK123456",
    "estimatedDelivery": "2023-05-15T14:00:00Z"
  }
}
```

### Error Handling
- If webhook processing fails, the system will return a 4xx or 5xx status code
- Failed webhooks should be retried with exponential backoff
- Webhook logs are available in the admin panel

---

## Database Schema

### Core Tables
- **users**: User accounts and authentication
- **packages**: Package tracking and details
- **package_history**: Historical records of package status changes
- **inventory**: Inventory item tracking
- **inventory_history**: Inventory movement logs
- **force_details**: Force management configuration
- **integrations**: External system integration settings
- **user_logins**: Login history with IP and location data
- **notifications**: User notification storage

### Key Relationships
- Packages have one-to-many relationship with package_history
- Users have one-to-many relationship with packages (assigned driver)
- Users have one-to-one relationship with force_details (optional)
- Inventory items have one-to-many relationship with inventory_history

---

## Environment Variables

### Required Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Secret for session encryption
- `PORT`: Server port (default: 5000)

### Optional Variables
- `NODE_ENV`: Environment (development/production)
- `LOG_LEVEL`: Logging verbosity (debug/info/warn/error)
- `CACHE_TTL`: Default cache time-to-live in milliseconds
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`: Email configuration

---

## Troubleshooting

### Common Issues

#### Integration Issues
- **Webhook Not Received**: Check firewall settings and webhook URL configuration
- **Data Mapping Errors**: Verify payload structure matches expected format
- **Authentication Failures**: Ensure API keys are valid and not expired

#### Performance Issues
- **Slow Response Times**: Check database query performance and consider adding indexes
- **Memory Leaks**: Monitor server memory usage and restart if necessary
- **Database Connection Issues**: Verify connection string and credentials

### Logging
- All system events are logged with contextual information
- API requests are logged with request details
- Integration events have dedicated logging for troubleshooting
- Log levels can be configured via environment variables

---

## Release and Update Process

### Version Naming Convention
- **Major Version**: Significant changes with breaking API changes
- **Minor Version**: New features with backward compatibility
- **Patch Version**: Bug fixes and minor improvements

### Update Steps
1. **Backup**: Always backup database before updates
2. **Release Notes**: Review release notes for breaking changes
3. **Database Migrations**: Run migrations if schema changes exist
4. **Testing**: Test integration points after each update
5. **Rollback Plan**: Have a rollback strategy for critical issues

### Update Frequency
- Security updates: Immediate deployment
- Feature updates: Monthly release cycle
- Major versions: Quarterly with advance notice

---

*This documentation is subject to updates. Last revised: April 6, 2025.*
