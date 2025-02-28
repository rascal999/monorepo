#!/usr/bin/env python3
"""
MongoDB Test Script

This script tests basic MongoDB functionality by:
1. Connecting to the MongoDB server
2. Creating a test database and collection
3. Inserting test data
4. Retrieving and verifying the data
5. Cleaning up by dropping the test database

Usage:
    python test_mongodb.py
"""

import sys
import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def test_mongodb():
    """Test MongoDB connectivity and basic operations."""
    print("MongoDB Test Script")
    print("==================")
    
    # Connection parameters
    host = "127.0.0.1"
    port = 27017
    connection_string = f"mongodb://{host}:{port}/"
    
    print(f"\nAttempting to connect to MongoDB at {connection_string}")
    
    # Try to connect to MongoDB with timeout
    try:
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        # Force a connection to verify server is available
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB server")
    except ConnectionFailure:
        print("❌ Failed to connect to MongoDB server")
        print("   Please ensure MongoDB is running and accessible")
        return False
    except ServerSelectionTimeoutError:
        print("❌ Server selection timeout - MongoDB server not responding")
        print("   Please ensure MongoDB is running and accessible")
        return False
    
    # Get server info
    try:
        server_info = client.server_info()
        print(f"\nMongoDB Server Information:")
        print(f"  Version: {server_info.get('version', 'Unknown')}")
        print(f"  Uptime: {server_info.get('uptime', 'Unknown')} seconds")
    except Exception as e:
        print(f"⚠️ Could not retrieve server info: {e}")
    
    # Create a test database and collection
    db_name = "mongodb_test"
    collection_name = "test_collection"
    
    print(f"\nCreating test database '{db_name}' and collection '{collection_name}'")
    db = client[db_name]
    collection = db[collection_name]
    
    # Insert test data
    print("Inserting test documents")
    test_docs = [
        {"name": "Document 1", "value": 42, "tags": ["test", "mongodb"]},
        {"name": "Document 2", "value": 73, "tags": ["example", "database"]},
        {"name": "Document 3", "value": 100, "tags": ["mongodb", "database"]}
    ]
    
    try:
        result = collection.insert_many(test_docs)
        print(f"✅ Successfully inserted {len(result.inserted_ids)} documents")
    except Exception as e:
        print(f"❌ Failed to insert documents: {e}")
        return False
    
    # Query the data
    print("\nQuerying documents")
    try:
        # Find all documents
        all_docs = list(collection.find({}))
        print(f"✅ Found {len(all_docs)} documents in total")
        
        # Find documents with specific tag
        mongodb_docs = list(collection.find({"tags": "mongodb"}))
        print(f"✅ Found {len(mongodb_docs)} documents with 'mongodb' tag")
        
        # Find document with highest value
        highest_value_doc = collection.find_one(sort=[("value", -1)])
        print(f"✅ Document with highest value: {highest_value_doc['name']} (value: {highest_value_doc['value']})")
    except Exception as e:
        print(f"❌ Failed to query documents: {e}")
        return False
    
    # Update a document
    print("\nUpdating a document")
    try:
        update_result = collection.update_one(
            {"name": "Document 1"},
            {"$set": {"value": 99, "updated": True}}
        )
        print(f"✅ Updated {update_result.modified_count} document")
        
        # Verify update
        updated_doc = collection.find_one({"name": "Document 1"})
        print(f"✅ Updated document value: {updated_doc['value']}")
    except Exception as e:
        print(f"❌ Failed to update document: {e}")
        return False
    
    # Clean up
    print("\nCleaning up - dropping test database")
    try:
        client.drop_database(db_name)
        print("✅ Successfully dropped test database")
    except Exception as e:
        print(f"❌ Failed to drop database: {e}")
        return False
    
    # Close connection
    client.close()
    print("\n✅ All MongoDB tests completed successfully!")
    return True

if __name__ == "__main__":
    success = test_mongodb()
    sys.exit(0 if success else 1)