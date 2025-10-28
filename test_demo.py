#!/usr/bin/env python3
"""
Test script for MongoDB Atlas Zone Sharding Demo
Verifies Atlas-specific components are working correctly
"""

import sys
import os
from colorama import Fore, Style, init
from pymongo import MongoClient
import config

def test_atlas_imports():
    """Test that all Atlas-specific modules can be imported"""
    print(f"{Fore.BLUE}Testing Atlas imports...{Style.RESET_ALL}")
    
    try:
        import pymongo
        print(f"{Fore.GREEN}✓ pymongo imported{Style.RESET_ALL}")
    except ImportError as e:
        print(f"{Fore.RED}✗ Failed to import pymongo: {e}{Style.RESET_ALL}")
        return False
    
    try:
        import colorama
        print(f"{Fore.GREEN}✓ colorama imported{Style.RESET_ALL}")
    except ImportError as e:
        print(f"{Fore.RED}✗ Failed to import colorama: {e}{Style.RESET_ALL}")
        return False
    
    try:
        from models import DataGenerator, User, Product, Order
        print(f"{Fore.GREEN}✓ models imported{Style.RESET_ALL}")
    except ImportError as e:
        print(f"{Fore.RED}✗ Failed to import models: {e}{Style.RESET_ALL}")
        return False
    
    try:
        from setup_atlas_zones import AtlasZoneShardingManager
        print(f"{Fore.GREEN}✓ AtlasZoneShardingManager imported{Style.RESET_ALL}")
    except ImportError as e:
        print(f"{Fore.RED}✗ Failed to import AtlasZoneShardingManager: {e}{Style.RESET_ALL}")
        return False
    
    return True

def test_atlas_configuration():
    """Test Atlas configuration settings"""
    print(f"\n{Fore.BLUE}Testing Atlas configuration...{Style.RESET_ALL}")
    
    try:
        # Check zones configuration
        assert len(config.ZONES) > 0
        print(f"{Fore.GREEN}✓ Zones configured: {len(config.ZONES)}{Style.RESET_ALL}")
        
        # Check that we have exactly 2 zones for 2-shard cluster
        assert len(config.ZONES) == 2
        print(f"{Fore.GREEN}✓ Correct number of zones for 2-shard cluster{Style.RESET_ALL}")
        
        # Check collections configuration
        assert len(config.COMMON_COLLECTIONS) > 0
        assert len(config.TENANT_COLLECTIONS) > 0
        print(f"{Fore.GREEN}✓ Collections configured{Style.RESET_ALL}")
        
        # Check demo data size
        assert config.DEMO_DATA_SIZE > 0
        print(f"{Fore.GREEN}✓ Demo data size configured: {config.DEMO_DATA_SIZE}{Style.RESET_ALL}")
        
        # Check Atlas-specific settings
        assert hasattr(config, 'ATLAS_CLUSTER_NAME')
        assert hasattr(config, 'ATLAS_PROJECT_ID')
        print(f"{Fore.GREEN}✓ Atlas-specific settings configured{Style.RESET_ALL}")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}✗ Atlas configuration test failed: {e}{Style.RESET_ALL}")
        return False

def test_atlas_connection():
    """Test Atlas connection (requires valid connection string)"""
    print(f"\n{Fore.BLUE}Testing Atlas connection...{Style.RESET_ALL}")
    
    # Check if connection string is configured
    if config.MONGODB_URI == "mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/?retryWrites=true&w=majority":
        print(f"{Fore.YELLOW}⚠ Atlas connection string not configured{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please update config.py with your actual Atlas connection string{Style.RESET_ALL}")
        return False
    
    try:
        # Test connection
        client = MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print(f"{Fore.GREEN}✓ Atlas connection successful{Style.RESET_ALL}")
        
        # Check if cluster has sharding enabled
        try:
            shards_result = client.admin.command("listShards")
            shards = [shard["_id"] for shard in shards_result["shards"]]
            print(f"{Fore.GREEN}✓ Sharding enabled with {len(shards)} shards: {shards}{Style.RESET_ALL}")
            
            if len(shards) < 2:
                print(f"{Fore.YELLOW}⚠ Cluster has only {len(shards)} shard(s). Zone sharding requires at least 2 shards.{Style.RESET_ALL}")
                return False
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Could not verify sharding status: {e}{Style.RESET_ALL}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"{Fore.RED}✗ Atlas connection failed: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Make sure your Atlas connection string is correct and accessible{Style.RESET_ALL}")
        return False

def test_data_generation():
    """Test data generation functionality"""
    print(f"\n{Fore.BLUE}Testing data generation...{Style.RESET_ALL}")
    
    try:
        from models import DataGenerator
        
        generator = DataGenerator()
        
        # Test user generation
        user = generator.generate_user("CN", "region1")
        assert user.country == "CN"
        assert user.region == "region1"
        print(f"{Fore.GREEN}✓ User generation works{Style.RESET_ALL}")
        
        # Test product generation
        product = generator.generate_product()
        assert product.product_id is not None
        print(f"{Fore.GREEN}✓ Product generation works{Style.RESET_ALL}")
        
        # Test order generation
        order = generator.generate_order(user.user_id, "CN", "region1")
        assert order.country == "CN"
        assert order.region == "region1"
        print(f"{Fore.GREEN}✓ Order generation works{Style.RESET_ALL}")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}✗ Data generation test failed: {e}{Style.RESET_ALL}")
        return False

def main():
    """Run all Atlas tests"""
    init(autoreset=True)
    
    print(f"{Fore.CYAN}{'='*60}")
    print("MongoDB Atlas Zone Sharding Demo - Test Suite")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    tests = [
        ("Import Test", test_atlas_imports),
        ("Atlas Configuration Test", test_atlas_configuration),
        ("Data Generation Test", test_data_generation),
        ("Atlas Connection Test", test_atlas_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{Fore.YELLOW}Running {test_name}...{Style.RESET_ALL}")
        if test_func():
            passed += 1
            print(f"{Fore.GREEN}✓ {test_name} PASSED{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ {test_name} FAILED{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"Test Results: {passed}/{total} tests passed")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    if passed == total:
        print(f"{Fore.GREEN}🎉 All tests passed! Atlas demo is ready to run.{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Next steps:{Style.RESET_ALL}")
        print("1. Update config_atlas.py with your Atlas connection string")
        print("2. Run the Atlas demo: python run_atlas_demo.py")
        return 0
    else:
        print(f"{Fore.RED}❌ Some tests failed. Please fix the issues before running the demo.{Style.RESET_ALL}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
