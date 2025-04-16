# Logistics Management System Documentation

## System Overview

The Logistics Management System is a comprehensive platform designed to optimize order tracking, route planning, and real-time location monitoring. It provides tools for managing the entire logistics workflow from order creation to delivery, with advanced features for clustering, route optimization, and driver management.

## FIFO Task Flow Implementation

The system implements a strict First-In-First-Out (FIFO) methodology for order processing to ensure fair and sequential handling of tasks.

### FIFO Workflow

1. **Order Queuing**:
   - New orders are timestamped and placed at the end of the processing queue
   - Each order maintains its original timestamp throughout the system
   - Priority flags can adjust queue position but within reasonable boundaries

2. **Driver Assignment**:
   - Drivers receive tasks in chronological order based on order creation time
   - The system maintains separate queues for different geographical clusters
   - Each driver's task list is organized by timestamp, not by location proximity

3. **Processing Sequence**:
   - Orders progress through status changes in the exact sequence they entered the system
   - The dashboard shows a chronological view of pending tasks
   - Performance metrics track adherence to FIFO principles

4. **Handover Management**:
   - When orders are transferred between drivers, they maintain their original queue position
   - Meeting points are scheduled based on the sequence of orders in the queue
   - The oldest orders in the system get priority for handovers

## Technology Stack

- **Frontend**: React with TypeScript, Tailwind CSS, Shadcn UI components
- **Backend**: Express.js (Node.js) with TypeScript
- **Database**: PostgreSQL with Drizzle ORM
- **Real-time Communication**: WebSockets for live location tracking
- **Machine Learning**: Python with scikit-learn for geographical clustering and route optimization
- **QR Code**: Built-in QR code generation for order tracking

## System Architecture

### Core Components

1. **Authentication & User Management**
   - Role-based access control (Admin, WarehouseStaff, FieldPartner, Driver)
   - User location tracking during login
   - Access level permissions (standard, elevated, admin)

2. **Order Management**
   - FIFO-based order processing queue
   - Order creation, tracking, and status updates
   - Customer management
   - QR code generation for quick scanning and updates

3. **Clustering & Route Optimization**
   - ML-based geographical clustering of orders
   - FIFO-respecting order assignment within clusters
   - Automatic driver assignment based on queue position and workload balancing

4. **Real-time Tracking**
   - WebSocket-based live location updates
   - Battery and speed monitoring for drivers
   - Historical location data analysis

5. **Meeting Points & Handovers**
   - Driver-to-driver package transfers at optimal meeting points
   - Scheduled handovers with status tracking
   - Meeting point management based on FIFO task sequence

6. **Admin Dashboard & Analytics**
   - Performance metrics and KPIs
   - Driver efficiency reports
   - FIFO adherence monitoring
   - Delivery time analysis

7. **Model Training & Management**
   - Geographic data upload and processing
   - ML model training for clustering
   - Model performance monitoring

## Database Schema

The system uses a PostgreSQL database with the following key tables:

1. **Users** - Store user accounts and authentication information
2. **Orders** - Track delivery orders and their status with timestamps for FIFO implementation
3. **Customers** - Manage customer data and delivery locations
4. **Clusters** - Group orders by geographical proximity
5. **LocationHistory** - Store driver location updates
6. **MeetingPoints** - Define handover locations
7. **Handovers** - Manage driver-to-driver transfers
8. **ClusteringConfigs** - Store ML configuration for clustering

## Workflow

### Order Creation Process

1. Customer information is captured (name, contact, address, coordinates)
2. Order details are recorded (package size, priority, etc.)
3. A unique QR code is generated for the order
4. The order is added to the pending orders queue with its creation timestamp
5. Orders are processed in strict FIFO sequence

### Clustering & Assignment Process

1. Pending orders are periodically clustered by geographical proximity
2. Clusters respect the chronological order of order creation
3. Drivers are assigned to orders based on:
   - Queue position (FIFO)
   - Current location (within FIFO constraints)
   - Workload balance
   - Vehicle capacity
   - Driver availability

### Delivery Process

1. Driver receives assigned orders on their mobile application in FIFO sequence
2. Real-time navigation guidance to each delivery point
3. Order status updates via QR code scanning
4. Handover coordination for long-distance deliveries
5. Delivery confirmation and proof of delivery

### Model Training Process

1. Upload geographical data in CSV format
2. Configure training parameters (clusters, proximity threshold, etc.)
3. Train models using Python ML components
4. Apply trained models to optimize order clustering while respecting FIFO principles

## API Endpoints

The system provides RESTful API endpoints for all major functions:

### Authentication
- `POST /api/auth/login` - User login
- `GET /api/users` - List users
- `GET /api/users/role/:role` - List users by role

### Orders
- `GET /api/orders` - List orders (sorted by creation time for FIFO)
- `GET /api/orders/status/:status` - List orders by status
- `GET /api/orders/:id` - Get order details
- `POST /api/orders` - Create new order
- `PUT /api/orders/:id` - Update order
- `POST /api/orders/scan/:uuid` - Process QR code scan

### Clustering
- `GET /api/clusters` - List clusters
- `POST /api/clustering/run` - Run clustering algorithm
- `POST /api/clustering/assign` - Assign drivers to clusters
- `GET /api/clustering/nearby/:orderId` - Find nearby orders

### Meeting Points & Handovers
- `GET /api/meeting-points` - List meeting points
- `POST /api/meeting-points` - Create meeting point
- `POST /api/meeting-points/generate` - Generate meeting points based on assigned orders
- `GET /api/meeting-points/nearest` - Find nearest meeting point to coordinates
- `GET /api/handovers` - List handovers
- `POST /api/handovers` - Create handover
- `PUT /api/handovers/:id` - Update handover status

### Model Training
- `POST /api/upload/locations` - Upload location data
- `GET /api/models/info` - Get model information
- `POST /api/models/train` - Train models

## Real-time Communication

The system uses WebSockets for real-time communication:

1. **Driver Location Updates** - Continuous streaming of driver coordinates
2. **Order Status Notifications** - Real-time updates on order status changes
3. **Handover Coordination** - Live communication for driver handovers
4. **Queue Position Updates** - Notifications about changes in FIFO queue

## Security Considerations

1. Password hashing (currently in plain text for development - must be updated)
2. Role-based access controls
3. Access level permissions
4. Secure WebSocket connections

## Performance Optimization

1. Database query optimization with proper indexing
2. Efficient geographical calculations with ML models
3. Batch processing for clustering operations
4. WebSocket connection management for minimal overhead
5. Queue management optimization for FIFO processing

## Installation & Setup

1. Clone the repository
2. Install dependencies (`npm install`)
3. Set up PostgreSQL database and update environment variables
4. Run migrations to create database schema
5. Start the application (`npm run dev`)

## Configuration Options

1. Clustering parameters (frequency, method, cluster size)
2. FIFO queue management settings
3. Automatic assignment settings
4. Meeting point enablement
5. ML model training parameters