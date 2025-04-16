#!/usr/bin/env python3
"""
Complete Setup of Test Data for Logistics Application

This script runs the full workflow:
1. Trains machine learning models using city data
2. Generates test data with realistic clusters and assignments
3. Imports the test data into the system

Usage:
  python setup_test_data.py --num-orders 5000 --import-method direct
"""

import os
import sys
import argparse
import subprocess
import time
import json

# Constants
MODELS_DIR = 'server/models'
TEST_DATA_DIR = 'server/test_data'

def ensure_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"Created directory: {path}")

def run_command(command, description):
    """Run a shell command and return the result"""
    print(f"\n{description}...")
    print(f"Command: {' '.join(command)}")
    
    start_time = time.time()
    result = subprocess.run(command, capture_output=True, text=True)
    elapsed_time = time.time() - start_time
    
    print(f"Finished in {elapsed_time:.2f} seconds with exit code {result.returncode}")
    
    if result.returncode != 0:
        print("ERROR:")
        print(result.stderr)
        return False
    
    return True

def train_models():
    """Train machine learning models using cities data"""
    # Create models directory if needed
    ensure_directory(MODELS_DIR)
    
    # Check if training is needed
    clustering_model_path = os.path.join(MODELS_DIR, 'clustering_model.pkl')
    distance_model_path = os.path.join(MODELS_DIR, 'distance_prediction_model.pkl')
    
    if os.path.exists(clustering_model_path) and os.path.exists(distance_model_path):
        print("Models already exist. Skipping training.")
        return True
    
    # Train models using geomodels.py
    return run_command(
        ["python", "server/geomodels.py"],
        "Training machine learning models"
    )

def generate_test_data(options):
    """Generate test data using generated_test_data.py"""
    # Create test data directory if needed
    ensure_directory(TEST_DATA_DIR)
    
    # Build command with options
    command = [
        "python", "server/generate_test_data.py",
        "--num-agents", str(options.num_agents),
        "--num-stores", str(options.num_stores),
        "--num-customers", str(options.num_customers),
        "--num-orders", str(options.num_orders),
        "--num-clusters", str(options.num_clusters)
    ]
    
    return run_command(
        command,
        f"Generating test data with {options.num_orders} orders"
    )

def import_test_data(options):
    """Import test data using the specified method"""
    if options.import_method == "api":
        # Import through API
        command = [
            "python", "server/import_test_data.py",
            "--batch-size", str(options.batch_size)
        ]
        
        if options.max_orders > 0:
            command.extend(["--max-orders", str(options.max_orders)])
        
        return run_command(
            command,
            f"Importing test data through API"
        )
    else:
        # Direct import to storage
        command = [
            "python", "server/direct_import.py"
        ]
        
        if options.max_orders > 0:
            command.extend(["--max-orders", str(options.max_orders)])
        
        return run_command(
            command,
            f"Directly importing test data to storage"
        )

def main():
    parser = argparse.ArgumentParser(description='Setup test data for logistics application')
    
    # Data generation options
    parser.add_argument('--num-agents', type=int, default=50, help='Number of field agents to generate')
    parser.add_argument('--num-stores', type=int, default=100, help='Number of stores to generate')
    parser.add_argument('--num-customers', type=int, default=2000, help='Number of customers to generate')
    parser.add_argument('--num-orders', type=int, default=5000, help='Number of orders to generate')
    parser.add_argument('--num-clusters', type=int, default=20, help='Number of clusters to create')
    
    # Import options
    parser.add_argument('--import-method', choices=['api', 'direct'], default='direct',
                        help='Method to use for importing data (api = through API, direct = directly to storage)')
    parser.add_argument('--batch-size', type=int, default=10, help='Batch size for API imports')
    parser.add_argument('--max-orders', type=int, default=0, help='Maximum number of orders to import (0 for all)')
    
    # Skip options
    parser.add_argument('--skip-training', action='store_true', help='Skip model training')
    parser.add_argument('--skip-generation', action='store_true', help='Skip data generation')
    parser.add_argument('--skip-import', action='store_true', help='Skip data import')
    
    options = parser.parse_args()
    
    print("Logistics Test Data Setup")
    print("========================")
    print(f"Orders to generate: {options.num_orders}")
    print(f"Import method: {options.import_method}")
    
    start_time = time.time()
    
    # Step 1: Train models (if needed)
    if not options.skip_training:
        if not train_models():
            print("Error training models. Exiting.")
            return 1
    
    # Step 2: Generate test data
    if not options.skip_generation:
        if not generate_test_data(options):
            print("Error generating test data. Exiting.")
            return 1
    
    # Step 3: Import test data
    if not options.skip_import:
        if not import_test_data(options):
            print("Error importing test data. Exiting.")
            return 1
    
    total_time = time.time() - start_time
    print(f"\nSetup completed successfully in {total_time:.2f} seconds!")
    
    # Print summary of generated data
    print("\nData Summary:")
    try:
        if os.path.exists(os.path.join(TEST_DATA_DIR, 'test_agents.json')):
            with open(os.path.join(TEST_DATA_DIR, 'test_agents.json'), 'r') as f:
                agent_count = len(json.load(f))
                print(f"- Field Agents: {agent_count}")
        
        if os.path.exists(os.path.join(TEST_DATA_DIR, 'test_stores.json')):
            with open(os.path.join(TEST_DATA_DIR, 'test_stores.json'), 'r') as f:
                store_count = len(json.load(f))
                print(f"- Stores: {store_count}")
        
        if os.path.exists(os.path.join(TEST_DATA_DIR, 'test_customers.json')):
            with open(os.path.join(TEST_DATA_DIR, 'test_customers.json'), 'r') as f:
                customer_count = len(json.load(f))
                print(f"- Customers: {customer_count}")
        
        if os.path.exists(os.path.join(TEST_DATA_DIR, 'test_orders.json')):
            with open(os.path.join(TEST_DATA_DIR, 'test_orders.json'), 'r') as f:
                orders = json.load(f)
                print(f"- Orders: {len(orders)}")
                
                # Count orders by status
                status_counts = {}
                for order in orders:
                    status = order.get('status', 'Unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                print("  Order Status Distribution:")
                for status, count in status_counts.items():
                    print(f"  - {status}: {count} ({count/len(orders)*100:.1f}%)")
        
        if os.path.exists(os.path.join(TEST_DATA_DIR, 'test_clusters.json')):
            with open(os.path.join(TEST_DATA_DIR, 'test_clusters.json'), 'r') as f:
                cluster_count = len(json.load(f))
                print(f"- Clusters: {cluster_count}")
        
    except Exception as e:
        print(f"Error generating summary: {e}")
    
    print("\nYou can now access this data through the logistics application!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())