#!/usr/bin/env python3
"""
Quick Test Data Generator for Logistics Application

This script generates test data for the logistics application
without waiting for full ML model training.
"""

import os
import sys
import json
import random
import time
import uuid
from datetime import datetime, timedelta
import csv
import argparse

# Constants
CITIES_CSV_PATH = 'attached_assets/cities.csv'
OUTPUT_DIR = 'server/test_data'
TEST_AGENTS_PATH = os.path.join(OUTPUT_DIR, 'test_agents.json')
TEST_STORES_PATH = os.path.join(OUTPUT_DIR, 'test_stores.json')
TEST_CUSTOMERS_PATH = os.path.join(OUTPUT_DIR, 'test_customers.json')
TEST_ORDERS_PATH = os.path.join(OUTPUT_DIR, 'test_orders.json')
TEST_CLUSTERS_PATH = os.path.join(OUTPUT_DIR, 'test_clusters.json')

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_city_sample(limit=1000):
    """
    Load a sample of cities from the CSV file
    
    Args:
        limit: Maximum number of cities to load
        
    Returns:
        List of city dictionaries
    """
    try:
        print(f"Loading sample data from {CITIES_CSV_PATH}")
        cities = []
        
        with open(CITIES_CSV_PATH, 'r') as f:
            reader = csv.DictReader(f)
            
            for i, row in enumerate(reader):
                if i >= limit:
                    break
                    
                try:
                    city = {
                        'id': int(row.get('id', i)),
                        'name': row.get('name', f'City {i}'),
                        'country': row.get('country_name', 'Unknown'),
                        'state': row.get('state_name', 'Unknown'),
                        'latitude': float(row.get('latitude', 0)),
                        'longitude': float(row.get('longitude', 0))
                    }
                    cities.append(city)
                except (ValueError, TypeError):
                    # Skip rows with invalid data
                    continue
            
        print(f"Loaded {len(cities)} cities")
        return cities
    except Exception as e:
        print(f"Error loading cities data: {e}")
        # Generate some random cities as fallback
        print("Generating random city locations instead")
        cities = []
        for i in range(limit):
            cities.append({
                'id': i,
                'name': f'City {i}',
                'country': 'Test Country',
                'state': 'Test State',
                'latitude': random.uniform(-90, 90),
                'longitude': random.uniform(-180, 180)
            })
        return cities

def generate_phone_number():
    """Generate a realistic phone number"""
    area_code = random.randint(200, 999)
    exchange = random.randint(200, 999)
    number = random.randint(1000, 9999)
    return f"+1 ({area_code}) {exchange}-{number}"

def generate_email(name):
    """Generate an email based on name"""
    name = name.lower().replace(' ', '.')
    domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'company.com']
    return f"{name}@{random.choice(domains)}"

def generate_field_agents(num_agents=50, cities=None):
    """Generate test field agents"""
    print(f"Generating {num_agents} field agents")
    
    if not cities:
        cities = []
    
    # Use cities for agent locations, or generate random locations
    agents = []
    for i in range(1, num_agents + 1):
        first_name = f"Agent{i}"
        last_name = f"Field{i}"
        full_name = f"{first_name} {last_name}"
        
        # Get city or random location
        if cities and i <= len(cities):
            city = cities[i - 1]
            location = {
                'latitude': city['latitude'],
                'longitude': city['longitude'],
                'city': city['name']
            }
        else:
            location = {
                'latitude': random.uniform(-80, 80),
                'longitude': random.uniform(-170, 170),
                'city': f"City {i}"
            }
        
        agent = {
            "id": i,
            "username": f"agent{i}",
            "password": "password123",  # In a real system, would be hashed
            "email": generate_email(full_name),
            "phone": generate_phone_number(),
            "fullName": full_name,
            "role": "driver",
            "status": random.choice(["Active", "Inactive", "On Leave"]),
            "homeBase": location['city'],
            "latitude": location['latitude'],
            "longitude": location['longitude'],
            "licenseNumber": f"DL{random.randint(100000, 999999)}",
            "vehicleType": random.choice(["Car", "Van", "Motorcycle", "Truck"]),
            "maxCapacity": random.randint(5, 50),
            "availability": random.choice(["Full-time", "Part-time", "Weekends Only"]),
            "rating": round(random.uniform(3.0, 5.0), 1),
            "joinDate": (datetime.now() - timedelta(days=random.randint(30, 1000))).strftime("%Y-%m-%d")
        }
        agents.append(agent)
    
    # Save to file
    with open(TEST_AGENTS_PATH, 'w') as f:
        json.dump(agents, f, indent=2)
    
    print(f"Saved {len(agents)} agents to {TEST_AGENTS_PATH}")
    return agents

def generate_stores(num_stores=100, cities=None):
    """Generate test stores/warehouses"""
    print(f"Generating {num_stores} stores/warehouses")
    
    if not cities:
        cities = []
    
    # Use cities for store locations, or generate random locations
    stores = []
    for i in range(1, num_stores + 1):
        # Get city or random location
        if cities and i <= len(cities):
            city = cities[i - 1]
            location = {
                'latitude': city['latitude'],
                'longitude': city['longitude'],
                'city': city['name'],
                'state': city['state'],
                'country': city['country']
            }
        else:
            location = {
                'latitude': random.uniform(-80, 80),
                'longitude': random.uniform(-170, 170),
                'city': f"City {i}",
                'state': 'State',
                'country': 'Country'
            }
        
        store_name = f"Store {location['city']} #{i}"
        
        store = {
            "id": i,
            "name": store_name,
            "type": random.choice(["Warehouse", "Retail Store", "Distribution Center", "Fulfillment Center"]),
            "address": f"{random.randint(100, 9999)} Main St, {location['city']}, {location['state']}",
            "city": location['city'],
            "country": location['country'],
            "latitude": location['latitude'],
            "longitude": location['longitude'],
            "capacity": random.randint(1000, 10000),
            "manager": f"Manager {i}",
            "contact": generate_phone_number(),
            "email": f"store{i}@company.com",
            "operatingHours": "8:00 AM - 6:00 PM",
            "isActive": random.random() > 0.1  # 90% are active
        }
        stores.append(store)
    
    # Save to file
    with open(TEST_STORES_PATH, 'w') as f:
        json.dump(stores, f, indent=2)
    
    print(f"Saved {len(stores)} stores to {TEST_STORES_PATH}")
    return stores

def generate_customers(num_customers=2000, cities=None):
    """Generate test customers"""
    print(f"Generating {num_customers} customers")
    
    if not cities:
        cities = []
    
    # Use cities for customer locations, or generate random locations
    customers = []
    for i in range(1, num_customers + 1):
        first_name = f"Customer{i}"
        last_name = f"User{i}"
        full_name = f"{first_name} {last_name}"
        
        # Get city or random location with some randomness added
        if cities:
            city_idx = i % len(cities)  # Cycle through cities for large customer counts
            city = cities[city_idx]
            
            # Add some randomness to the exact location (within the city)
            lat_offset = random.uniform(-0.02, 0.02)
            lon_offset = random.uniform(-0.02, 0.02)
            
            location = {
                'latitude': city['latitude'] + lat_offset,
                'longitude': city['longitude'] + lon_offset,
                'city': city['name'],
                'country': city['country']
            }
        else:
            location = {
                'latitude': random.uniform(-80, 80),
                'longitude': random.uniform(-170, 170),
                'city': f"City {i % 100 + 1}",  # Cycle through 100 city names
                'country': 'Country'
            }
        
        customer = {
            "id": i,
            "name": full_name,
            "email": generate_email(full_name),
            "phone": generate_phone_number(),
            "address": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Maple', 'Cedar'])} St, {location['city']}",
            "city": location['city'],
            "country": location['country'],
            "latitude": location['latitude'],
            "longitude": location['longitude'],
            "customerSince": (datetime.now() - timedelta(days=random.randint(1, 700))).strftime("%Y-%m-%d"),
            "type": random.choice(["Residential", "Business", "Government", "Educational"]),
            "priorityLevel": random.choice(["Standard", "High", "Premium"])
        }
        customers.append(customer)
    
    # Save to file
    with open(TEST_CUSTOMERS_PATH, 'w') as f:
        json.dump(customers, f, indent=2)
    
    print(f"Saved {len(customers)} customers to {TEST_CUSTOMERS_PATH}")
    return customers

def generate_orders(num_orders=5000, customers=None, stores=None):
    """Generate test orders/leads"""
    print(f"Generating {num_orders} orders/leads")
    
    if not customers or not stores:
        print("Need customers and stores to generate orders")
        return []
    
    # Order statuses with weightings
    status_weights = {
        "Pending": 0.3,
        "Assigned": 0.2,
        "InTransit": 0.2,
        "Delivered": 0.1,
        "Failed": 0.05,
        "Cancelled": 0.05,
        "Returned": 0.05,
        "OnHold": 0.05
    }
    statuses = list(status_weights.keys())
    weights = list(status_weights.values())
    
    # Generate orders
    orders = []
    for i in range(1, num_orders + 1):
        # Select random customer and store
        customer = random.choice(customers)
        store = random.choice(stores)
        
        # Generate order date (between 1 and 60 days ago)
        order_date = datetime.now() - timedelta(days=random.randint(1, 60))
        order_date_str = order_date.strftime("%Y-%m-%d")
        
        # Generate expected delivery date (between order date and 15 days later)
        delivery_date = order_date + timedelta(days=random.randint(1, 15))
        delivery_date_str = delivery_date.strftime("%Y-%m-%d")
        
        # Generate a unique ID for tracking
        tracking_uuid = str(uuid.uuid4())
        
        # Generate a QR code URL (simulated)
        qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={tracking_uuid}"
        
        # Select a random status based on weights
        status = random.choices(statuses, weights=weights)[0]
        
        order = {
            "id": i,
            "uuid": tracking_uuid,
            "customerId": customer["id"],
            "storeId": store["id"],
            "status": status,
            "priority": random.choice(["Low", "Medium", "High", "Urgent"]),
            "orderDate": order_date_str,
            "expectedDeliveryDate": delivery_date_str,
            "items": random.randint(1, 10),
            "totalWeight": round(random.uniform(0.5, 50.0), 2),
            "value": round(random.uniform(10.0, 500.0), 2),
            "currency": "USD",
            "qrCode": qr_code_url,
            "notes": f"Test order {i}",
            "pickupLatitude": store["latitude"],
            "pickupLongitude": store["longitude"],
            "deliveryLatitude": customer["latitude"],
            "deliveryLongitude": customer["longitude"],
            "clusterId": None,  # Will be set later
            "driverId": None    # Will be set later
        }
        orders.append(order)
    
    print(f"Generated {len(orders)} orders")
    return orders

def create_simple_clusters(orders, num_clusters=20):
    """Create simple clusters for orders based on proximity"""
    print(f"Creating {num_clusters} clusters from {len(orders)} orders")
    
    # Simple approach: divide the orders into regions based on coordinates
    min_lat = min(order["deliveryLatitude"] for order in orders)
    max_lat = max(order["deliveryLatitude"] for order in orders)
    min_lon = min(order["deliveryLongitude"] for order in orders)
    max_lon = max(order["deliveryLongitude"] for order in orders)
    
    # Create latitude and longitude ranges
    lat_step = (max_lat - min_lat) / (num_clusters ** 0.5)
    lon_step = (max_lon - min_lon) / (num_clusters ** 0.5)
    
    # Assign cluster IDs to orders
    for order in orders:
        lat_bin = int((order["deliveryLatitude"] - min_lat) / lat_step)
        lon_bin = int((order["deliveryLongitude"] - min_lon) / lon_step)
        cluster_id = lat_bin * int(num_clusters ** 0.5) + lon_bin + 1
        order["clusterId"] = min(cluster_id, num_clusters)  # Cap at num_clusters
    
    # Create cluster definitions
    clusters = {}
    for order in orders:
        cluster_id = order["clusterId"]
        if cluster_id not in clusters:
            clusters[cluster_id] = {
                "lat_sum": 0,
                "lon_sum": 0,
                "count": 0
            }
        
        clusters[cluster_id]["lat_sum"] += order["deliveryLatitude"]
        clusters[cluster_id]["lon_sum"] += order["deliveryLongitude"]
        clusters[cluster_id]["count"] += 1
    
    # Convert clusters to proper format
    cluster_defs = []
    for cluster_id, data in clusters.items():
        count = data["count"]
        if count > 0:
            cluster_def = {
                "id": cluster_id,
                "name": f"Cluster {cluster_id}",
                "latitude": data["lat_sum"] / count,
                "longitude": data["lon_sum"] / count,
                "radius": random.uniform(2.0, 10.0),
                "orderCount": count,
                "createdAt": datetime.now().strftime("%Y-%m-%d"),
                "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
                "status": "Active",
                "description": f"Automatically generated cluster with {count} orders"
            }
            cluster_defs.append(cluster_def)
    
    print(f"Created {len(cluster_defs)} cluster definitions")
    
    # Save orders and clusters
    with open(TEST_ORDERS_PATH, 'w') as f:
        json.dump(orders, f, indent=2)
    
    with open(TEST_CLUSTERS_PATH, 'w') as f:
        json.dump(cluster_defs, f, indent=2)
    
    return orders, cluster_defs

def assign_drivers_to_orders(orders, agents, num_assigned_percentage=0.6):
    """Assign drivers to a percentage of orders"""
    print(f"Assigning drivers to {num_assigned_percentage*100:.0f}% of orders")
    
    # Calculate number of orders to assign
    num_to_assign = int(len(orders) * num_assigned_percentage)
    
    # Select random orders to assign
    orders_to_assign = random.sample(orders, num_to_assign)
    
    # For each cluster, try to assign the same driver to all orders in that cluster
    clusters = {}
    for order in orders_to_assign:
        cluster_id = order["clusterId"]
        if cluster_id not in clusters:
            clusters[cluster_id] = []
        clusters[cluster_id].append(order)
    
    # Assign drivers to clusters
    for cluster_id, cluster_orders in clusters.items():
        # Randomly select a driver
        driver = random.choice(agents)
        
        # Assign to all orders in this cluster
        for order in cluster_orders:
            order["driverId"] = driver["id"]
            
            # If order is Pending, update to Assigned
            if order["status"] == "Pending":
                order["status"] = "Assigned"
    
    print(f"Assigned drivers to {num_to_assign} orders")
    
    # Save updated orders
    with open(TEST_ORDERS_PATH, 'w') as f:
        json.dump(orders, f, indent=2)
    
    return orders

def generate_all_test_data(options):
    """Generate all test data"""
    start_time = time.time()
    
    print(f"Generating test data with {options.num_orders} orders")
    
    # 1. Load city data
    cities = load_city_sample(limit=options.city_limit)
    
    # 2. Generate agents, stores, and customers
    agents = generate_field_agents(options.num_agents, cities)
    stores = generate_stores(options.num_stores, cities)
    customers = generate_customers(options.num_customers, cities)
    
    # 3. Generate orders
    orders = generate_orders(options.num_orders, customers, stores)
    
    # 4. Create clusters for orders
    orders, clusters = create_simple_clusters(orders, options.num_clusters)
    
    # 5. Assign drivers to orders
    orders = assign_drivers_to_orders(orders, agents, options.driver_assignment_percentage)
    
    elapsed_time = time.time() - start_time
    print(f"\nTest data generation completed in {elapsed_time:.2f} seconds!")
    print(f"Generated {len(agents)} agents, {len(stores)} stores, {len(customers)} customers, {len(orders)} orders, and {len(clusters)} clusters")
    print(f"Data saved to {OUTPUT_DIR}")

def main():
    parser = argparse.ArgumentParser(description='Generate test data for logistics application')
    parser.add_argument('--num-agents', type=int, default=50, help='Number of field agents to generate')
    parser.add_argument('--num-stores', type=int, default=100, help='Number of stores to generate')
    parser.add_argument('--num-customers', type=int, default=2000, help='Number of customers to generate')
    parser.add_argument('--num-orders', type=int, default=5000, help='Number of orders to generate')
    parser.add_argument('--num-clusters', type=int, default=20, help='Number of clusters to create')
    parser.add_argument('--city-limit', type=int, default=1000, help='Maximum number of cities to load from CSV')
    parser.add_argument('--driver-assignment-percentage', type=float, default=0.6, help='Percentage of orders to assign drivers to')
    
    options = parser.parse_args()
    
    # Generate all test data
    generate_all_test_data(options)

if __name__ == "__main__":
    main()