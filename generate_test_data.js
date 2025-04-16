// Test data generation script for Logistics application
import { Pool, neonConfig } from '@neondatabase/serverless';
import ws from 'ws';
import { v4 as uuidv4 } from 'uuid';
import fs from 'fs';

// Configure WebSocket for Neon serverless
neonConfig.webSocketConstructor = ws;

const NUM_CUSTOMERS = 500;
const NUM_DRIVERS = 50;
const NUM_ORDERS = 5000;
const NUM_CLUSTERS = 15;

async function main() {
  console.log('Starting test data generation...');
  
  if (!process.env.DATABASE_URL) {
    throw new Error('DATABASE_URL must be set');
  }
  
  const pool = new Pool({ connectionString: process.env.DATABASE_URL });
  
  try {
    // Generate random coordinates within a specific area (India as an example)
    const generateLocation = () => {
      // Rough boundaries for India
      const minLat = 8.0, maxLat = 35.0;
      const minLng = 68.0, maxLng = 98.0;
      
      return {
        latitude: minLat + (Math.random() * (maxLat - minLat)),
        longitude: minLng + (Math.random() * (maxLng - minLng))
      };
    };
    
    // Generate random phone number
    const generatePhone = () => {
      return '+91' + Math.floor(7000000000 + Math.random() * 3000000000);
    };
    
    // Generate random email based on name
    const generateEmail = (name) => {
      const providers = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'logisticstracker.com'];
      const normalizedName = name.toLowerCase().replace(/\s/g, '.');
      return `${normalizedName}@${providers[Math.floor(Math.random() * providers.length)]}`;
    };
    
    // Generate random address
    const generateAddress = (city) => {
      const streetNumbers = ['123', '456', '789', '234', '567', '890', '321', '654', '987', '432'];
      const streetNames = ['Main Street', 'Park Avenue', 'Oak Road', 'Maple Lane', 'Cedar Court', 'Pine Drive', 'Elm Street', 'Market Road', 'Station Road', 'Temple Street'];
      const areas = ['Sector 1', 'Sector 15', 'Phase 2', 'Central Area', 'North Extension', 'South Colony', 'East Side', 'West Heights', 'Old Town', 'New Layout'];
      
      return `${streetNumbers[Math.floor(Math.random() * streetNumbers.length)]} ${streetNames[Math.floor(Math.random() * streetNames.length)]}, ${areas[Math.floor(Math.random() * areas.length)]}, ${city}`;
    };
    
    // Generate random pincode
    const generatePincode = () => {
      return String(Math.floor(100000 + Math.random() * 900000));
    };
    
    // Generate city names
    const cities = [
      'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 
      'Pune', 'Ahmedabad', 'Jaipur', 'Surat', 'Lucknow', 'Kanpur', 
      'Nagpur', 'Indore', 'Thane', 'Bhopal', 'Visakhapatnam', 'Patna', 
      'Vadodara', 'Ghaziabad', 'Ludhiana', 'Agra', 'Nashik', 'Ranchi', 
      'Faridabad', 'Coimbatore', 'Rajkot', 'Amritsar', 'Jodhpur', 'Madurai'
    ];
    
    // Generate customer names
    const firstNames = [
      'Amit', 'Ananya', 'Anil', 'Priya', 'Raj', 'Neha', 'Sanjay', 'Deepa', 
      'Rahul', 'Pooja', 'Vikram', 'Kavita', 'Ajay', 'Meena', 'Ravi', 
      'Sunita', 'Vijay', 'Shweta', 'Rajesh', 'Ritu'
    ];
    
    const lastNames = [
      'Sharma', 'Patel', 'Singh', 'Kumar', 'Gupta', 'Joshi', 'Verma', 
      'Rao', 'Malhotra', 'Kapoor', 'Mehta', 'Shah', 'Das', 'Nair', 
      'Iyer', 'Reddy', 'Gandhi', 'Desai', 'Chatterjee', 'Bose'
    ];
    
    // Generate random customer name
    const generateCustomerName = () => {
      return `${firstNames[Math.floor(Math.random() * firstNames.length)]} ${lastNames[Math.floor(Math.random() * lastNames.length)]}`;
    };
    
    // 1. Create drivers (as users with 'Driver' role)
    console.log('Creating drivers...');
    for (let i = 0; i < NUM_DRIVERS; i++) {
      const name = generateCustomerName();
      const location = generateLocation();
      
      await pool.query(`
        INSERT INTO users (username, password, full_name, role, email, phone)
        VALUES ($1, $2, $3, $4, $5, $6)
      `, [
        `driver${i + 1}`, 
        `password${i + 1}`, 
        name, 
        'Driver',
        generateEmail(name),
        generatePhone()
      ]);
    }
    
    // 2. Create clusters
    console.log('Creating clusters...');
    for (let i = 0; i < NUM_CLUSTERS; i++) {
      const location = generateLocation();
      const city = cities[Math.floor(Math.random() * cities.length)];
      
      await pool.query(`
        INSERT INTO clusters (name, pincode, latitude, longitude, radius)
        VALUES ($1, $2, $3, $4, $5)
      `, [
        `Cluster ${i + 1} - ${city}`,
        generatePincode(),
        location.latitude,
        location.longitude,
        0.5 + Math.random() * 2.0 // Random radius between 0.5 and 2.5
      ]);
    }
    
    // Get all cluster IDs
    const clusterResult = await pool.query('SELECT id FROM clusters');
    const clusterIds = clusterResult.rows.map(row => row.id);
    
    // 3. Create customers
    console.log('Creating customers...');
    for (let i = 0; i < NUM_CUSTOMERS; i++) {
      const name = generateCustomerName();
      const location = generateLocation();
      const city = cities[Math.floor(Math.random() * cities.length)];
      
      await pool.query(`
        INSERT INTO customers (name, phone, email, address, city, pincode, latitude, longitude, instructions)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
      `, [
        name,
        generatePhone(),
        generateEmail(name),
        generateAddress(city),
        city,
        generatePincode(),
        location.latitude,
        location.longitude,
        Math.random() > 0.7 ? 'Call before delivery' : null
      ]);
    }
    
    // Get all customer IDs
    const customerResult = await pool.query('SELECT id FROM customers');
    const customerIds = customerResult.rows.map(row => row.id);
    
    // Get all driver IDs
    const driverResult = await pool.query('SELECT id FROM users WHERE role = $1', ['Driver']);
    const driverIds = driverResult.rows.map(row => row.id);
    
    // 4. Create orders
    console.log('Creating orders...');
    const orderStatuses = ['pending', 'assigned', 'in_transit', 'delivered', 'failed', 'cancelled'];
    const packageSizes = ['small', 'medium', 'large', 'extra_large'];
    const priorities = ['low', 'normal', 'high', 'urgent'];
    
    for (let i = 0; i < NUM_ORDERS; i++) {
      const customerId = customerIds[Math.floor(Math.random() * customerIds.length)];
      const statusIndex = Math.floor(Math.random() * orderStatuses.length);
      const status = orderStatuses[statusIndex];
      
      // Assign cluster and driver for some orders
      const clusterId = Math.random() > 0.2 ? clusterIds[Math.floor(Math.random() * clusterIds.length)] : null;
      const driverId = ['assigned', 'in_transit'].includes(status) ? 
                      driverIds[Math.floor(Math.random() * driverIds.length)] : null;
      
      // Generate creation date (between 1 month ago and now)
      const createdAt = new Date();
      createdAt.setDate(createdAt.getDate() - Math.floor(Math.random() * 30));
      
      // Generate updated date (after creation date)
      const updatedAt = new Date(createdAt);
      updatedAt.setHours(updatedAt.getHours() + Math.floor(Math.random() * 48));
      
      // Generate estimated delivery (for future orders)
      const estimatedDelivery = status === 'pending' || status === 'assigned' || status === 'in_transit' ? 
                               new Date(updatedAt.getTime() + Math.floor(Math.random() * 3 * 24 * 60 * 60 * 1000)) : null;
      
      // Generate QR code URL for all orders
      const uuid = uuidv4();
      const qrCode = `https://api.qrserver.com/v1/create-qr-code/?data=${uuid}&size=150x150`;
      
      await pool.query(`
        INSERT INTO orders (
          uuid, customer_id, status, created_at, updated_at, 
          package_size, priority, cluster_id, driver_id, qr_code, estimated_delivery
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
      `, [
        uuid,
        customerId,
        status,
        createdAt,
        updatedAt,
        packageSizes[Math.floor(Math.random() * packageSizes.length)],
        priorities[Math.floor(Math.random() * priorities.length)],
        clusterId,
        driverId,
        qrCode,
        estimatedDelivery
      ]);
      
      // Progress indicator
      if ((i + 1) % 500 === 0) {
        console.log(`Created ${i + 1} orders...`);
      }
    }
    
    // 5. Create location history for drivers
    console.log('Creating location history for drivers...');
    for (const driverId of driverIds) {
      // Create 10-50 location points per driver
      const numPoints = 10 + Math.floor(Math.random() * 40);
      
      for (let i = 0; i < numPoints; i++) {
        const location = generateLocation();
        
        // Generate timestamp (between 1 week ago and now)
        const timestamp = new Date();
        timestamp.setDate(timestamp.getDate() - Math.floor(Math.random() * 7));
        timestamp.setHours(timestamp.getHours() - Math.floor(Math.random() * 24));
        
        await pool.query(`
          INSERT INTO location_history (
            user_id, latitude, longitude, timestamp, 
            speed, battery_level, accuracy
          )
          VALUES ($1, $2, $3, $4, $5, $6, $7)
        `, [
          driverId,
          location.latitude,
          location.longitude,
          timestamp,
          Math.floor(Math.random() * 60), // Speed: 0-60 km/h
          Math.floor(Math.random() * 100), // Battery: 0-100%
          Math.random() * 10 // Accuracy: 0-10 meters
        ]);
      }
    }
    
    // 6. Create meeting points
    console.log('Creating meeting points...');
    for (let i = 0; i < 10; i++) {
      const location = generateLocation();
      const city = cities[Math.floor(Math.random() * cities.length)];
      
      await pool.query(`
        INSERT INTO meeting_points (
          name, description, latitude, longitude, address, is_active
        )
        VALUES ($1, $2, $3, $4, $5, $6)
      `, [
        `Meeting Point ${i + 1}`,
        `Central meeting location for handovers in ${city}`,
        location.latitude,
        location.longitude,
        generateAddress(city),
        Math.random() > 0.2 // 80% active
      ]);
    }
    
    // Get all meeting point IDs
    const meetingPointResult = await pool.query('SELECT id FROM meeting_points');
    const meetingPointIds = meetingPointResult.rows.map(row => row.id);
    
    // 7. Create handovers
    console.log('Creating handovers...');
    for (let i = 0; i < 20; i++) {
      const fromDriverId = driverIds[Math.floor(Math.random() * driverIds.length)];
      
      // Make sure toDriverId is different from fromDriverId
      let toDriverId;
      do {
        toDriverId = driverIds[Math.floor(Math.random() * driverIds.length)];
      } while (toDriverId === fromDriverId);
      
      const meetingPointId = meetingPointIds[Math.floor(Math.random() * meetingPointIds.length)];
      
      // Generate scheduled time (between now and 1 week in future)
      const scheduledTime = new Date();
      scheduledTime.setDate(scheduledTime.getDate() + Math.floor(Math.random() * 7));
      
      // Generate random orders (between 1 and 5 orders)
      const numHandoverOrders = 1 + Math.floor(Math.random() * 5);
      const handoverOrders = [];
      
      for (let j = 0; j < numHandoverOrders; j++) {
        handoverOrders.push({
          id: Math.floor(Math.random() * NUM_ORDERS) + 1,
          status: 'in_transit'
        });
      }
      
      await pool.query(`
        INSERT INTO handovers (
          from_driver_id, to_driver_id, meeting_point_id, scheduled_time, 
          status, orders_json, notes
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
      `, [
        fromDriverId,
        toDriverId,
        meetingPointId,
        scheduledTime,
        Math.random() > 0.7 ? 'completed' : 'pending',
        JSON.stringify(handoverOrders),
        Math.random() > 0.7 ? 'Handle with care, fragile items included' : null
      ]);
    }
    
    // 8. Create default clustering configuration if it doesn't exist
    console.log('Creating default clustering configuration...');
    const configResult = await pool.query('SELECT count(*) FROM clustering_configs');
    
    if (parseInt(configResult.rows[0].count) === 0) {
      await pool.query(`
        INSERT INTO clustering_configs (
          method, frequency, num_clusters, proximity_threshold, 
          auto_assignment, balance_workload, enable_meeting_points
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
      `, [
        'kmeans',
        'daily',
        NUM_CLUSTERS,
        1.0,
        true,
        true,
        true
      ]);
    }
    
    console.log('Test data generation completed successfully!');
  } catch (error) {
    console.error('Error generating test data:', error);
    throw error;
  } finally {
    await pool.end();
  }
}

main().catch(console.error);