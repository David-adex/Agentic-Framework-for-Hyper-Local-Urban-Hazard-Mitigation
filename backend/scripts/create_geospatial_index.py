import os
import sys
from pymongo import MongoClient
from pymongo.errors import OperationFailure

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.db import get_sensor_collection


def create_geospatial_index():
    try:
        collection = get_sensor_collection()
        
        print("📍 Creating geospatial index on 'location' field...")
        
        index_name = collection.create_index([("location", "2dsphere")])
        
        print(f"✅ Geospatial index created successfully: {index_name}")
        
        indexes = collection.list_indexes()
        print("\n📊 Current indexes:")
        for idx in indexes:
            print(f"  - {idx['name']}: {idx.get('key', [])}")
        
        return True
        
    except OperationFailure as e:
        print(f"❌ MongoDB Operation Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("MongoDB Geospatial Index Creator")
    print("=" * 60)
    print()
    
    success = create_geospatial_index()
    
    print()
    if success:
        print("✅ Index creation completed successfully!")
        print("   Geospatial queries will now use the optimized index.")
    else:
        print("❌ Index creation failed. Please check your MongoDB connection.")
    
    sys.exit(0 if success else 1)
