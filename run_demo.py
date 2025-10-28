#!/usr/bin/env python3
"""
MongoDB Atlas Zone Sharding Demo Runner
Interactive demo for Atlas cluster with 2 shards
"""

import sys
import os
import uuid
from colorama import Fore, Style, init
from pymongo import MongoClient
import config
from models import DataGenerator, User, Product, Category, Order, Transaction, Log
from setup_atlas_zones import AtlasZoneShardingManager


class AtlasDemoRunner:
    """Interactive Atlas demo runner with menu options"""
    
    def __init__(self, atlas_uri: str):
        init(autoreset=True)
        self.atlas_uri = atlas_uri
        self.client = MongoClient(atlas_uri)
        self.zone_manager = AtlasZoneShardingManager(atlas_uri)
        self.data_generator = DataGenerator()
        
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{title.center(60)}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
    
    def print_menu(self):
        """Print the main menu"""
        print(f"{Fore.YELLOW}MongoDB Atlas Zone Sharding Demo Menu:{Style.RESET_ALL}")
        print("1. Run Complete Atlas Demo")
        print("2. Setup Zone Sharding Only")
        print("3. Populate Sample Data Only")
        print("4. Check Zone Status")
        print("5. Verify Data Placement")
        print("6. Cleanup Demo Data")
        print("7. Test Atlas Connection")
        print("8. Show Atlas Cluster Info")
        print("9. Exit")
        print()
    
    def test_connection(self):
        """Test Atlas connection"""
        self.print_header("Testing Atlas Connection")
        
        try:
            # Test connection
            self.client.admin.command('ping')
            print(f"{Fore.GREEN}✓ Atlas connection successful{Style.RESET_ALL}")
            
            # Get cluster info
            result = self.client.admin.command("isMaster")
            print(f"{Fore.BLUE}Cluster info:{Style.RESET_ALL}")
            print(f"  Primary: {result.get('primary', 'Unknown')}")
            print(f"  Hosts: {result.get('hosts', [])}")
            
            # Check sharding status
            try:
                shards_result = self.client.admin.command("listShards")
                shards = [shard["_id"] for shard in shards_result["shards"]]
                print(f"{Fore.GREEN}✓ Sharding enabled with {len(shards)} shards: {shards}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}⚠ Could not verify sharding status: {e}{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}✗ Connection failed: {e}{Style.RESET_ALL}")
            return False
        
        return True
    
    def show_cluster_info(self):
        """Show detailed Atlas cluster information"""
        self.print_header("Atlas Cluster Information")
        
        try:
            # Get shard information
            shards_result = self.client.admin.command("listShards")
            print(f"{Fore.BLUE}Shards:{Style.RESET_ALL}")
            for shard in shards_result["shards"]:
                print(f"  {shard['_id']}: {shard.get('host', 'Unknown')}")
            
            # Get databases
            dbs = self.client.list_database_names()
            print(f"\n{Fore.BLUE}Databases:{Style.RESET_ALL}")
            for db_name in dbs:
                if db_name not in ['admin', 'config', 'local']:
                    db = self.client[db_name]
                    collections = db.list_collection_names()
                    print(f"  {db_name}: {len(collections)} collections")
            
            # Get zone information if any
            try:
                zones_result = self.client.admin.command("listShards")
                print(f"\n{Fore.BLUE}Zone Configuration:{Style.RESET_ALL}")
                for shard in zones_result["shards"]:
                    if "tags" in shard:
                        print(f"  {shard['_id']}: {shard['tags']}")
                    else:
                        print(f"  {shard['_id']}: No zones configured")
            except Exception as e:
                print(f"{Fore.YELLOW}Could not get zone info: {e}{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}Error getting cluster info: {e}{Style.RESET_ALL}")
    
    def setup_zone_sharding_only(self):
        """Setup zone sharding configuration only"""
        self.print_header("Setting Up Atlas Zone Sharding")
        
        try:
            success = self.zone_manager.setup_atlas_zone_sharding()
            
            if success:
                print(f"\n{Fore.GREEN}Atlas zone sharding setup completed successfully!{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}Atlas zone sharding setup failed!{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}Error during setup: {e}{Style.RESET_ALL}")
    
    def populate_sample_data_only(self):
        """Populate sample data only"""
        self.print_header("Populating Sample Data")
        
        try:
            # Setup databases and collections
            for zone_name, zone_config in config.ZONES.items():
                database_name = zone_config["database_prefix"]
                db = self.client[database_name]
                
                print(f"\n{Fore.BLUE}Setting up database: {database_name}{Style.RESET_ALL}")
                
                # Create collections
                for collection_name in config.COMMON_COLLECTIONS + config.TENANT_COLLECTIONS:
                    collection = db[collection_name]
                    print(f"  - Created collection: {collection_name}")
            
            # Generate and insert common data
            print(f"\n{Fore.BLUE}Generating common data...{Style.RESET_ALL}")
            users = [self.data_generator.generate_user("GLOBAL", "global") for _ in range(50)]
            products = [self.data_generator.generate_product() for _ in range(100)]
            categories = [self.data_generator.generate_category() for _ in range(20)]
            
            # Insert into all regional databases
            for zone_name, zone_config in config.ZONES.items():
                database_name = zone_config["database_prefix"]
                db = self.client[database_name]
                
                print(f"\n{Fore.BLUE}Populating common data in {database_name}:{Style.RESET_ALL}")
                
                # Insert users
                user_docs = [user.to_dict() for user in users]
                db.users.insert_many(user_docs)
                print(f"  - Inserted {len(user_docs)} users")
                
                # Insert products
                product_docs = [product.to_dict() for product in products]
                db.products.insert_many(product_docs)
                print(f"  - Inserted {len(product_docs)} products")
                
                # Insert categories
                category_docs = [category.to_dict() for category in categories]
                db.categories.insert_many(category_docs)
                print(f"  - Inserted {len(category_docs)} categories")
            
            # Generate and insert tenant-specific data
            print(f"\n{Fore.BLUE}Generating tenant-specific data...{Style.RESET_ALL}")
            
            for zone_name, zone_config in config.ZONES.items():
                database_name = zone_config["database_prefix"]
                countries = zone_config["countries"]
                db = self.client[database_name]
                
                print(f"\n{Fore.BLUE}Populating tenant data in {database_name}:{Style.RESET_ALL}")
                
                # Generate region-specific data
                orders = []
                transactions = []
                logs = []
                
                for country in countries:
                    for i in range(config.DEMO_DATA_SIZE // len(countries)):
                        # Get any user from common data (or create a mock user_id)
                        user = db.users.find_one()
                        user_id = user["user_id"] if user else str(uuid.uuid4())
                        
                        # Generate tenant-specific data with the correct country and region
                        order = self.data_generator.generate_order(
                            user_id, country, zone_name
                        )
                        transaction = self.data_generator.generate_transaction(
                            order.order_id, user_id, country, zone_name
                        )
                        log = self.data_generator.generate_log(
                            user_id, country, zone_name
                        )
                        
                        orders.append(order.to_dict())
                        transactions.append(transaction.to_dict())
                        logs.append(log.to_dict())
                
                # Insert tenant-specific data
                if orders:
                    db.orders.insert_many(orders)
                    print(f"  - Inserted {len(orders)} orders")
                
                if transactions:
                    db.transactions.insert_many(transactions)
                    print(f"  - Inserted {len(transactions)} transactions")
                
                if logs:
                    db.logs.insert_many(logs)
                    print(f"  - Inserted {len(logs)} log entries")
            
            print(f"\n{Fore.GREEN}Sample data population completed!{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}Error populating data: {e}{Style.RESET_ALL}")
    
    def check_zone_status(self):
        """Check current zone status"""
        self.print_header("Zone Status Check")
        
        try:
            zones_info = self.zone_manager.get_zone_status()
            
            if zones_info:
                print(f"{Fore.BLUE}Current Zone Configuration:{Style.RESET_ALL}")
                
                for zone_name, info in zones_info.items():
                    print(f"\n{Fore.CYAN}Zone: {zone_name.upper()}{Style.RESET_ALL}")
                    print(f"  Countries: {', '.join(info['countries'])}")
                    print(f"  Shards: {', '.join(info['configured_shards'])}")
                    print(f"  Database: {info['database']}")
                    
                    # Show shard details
                    for shard_name, shard_info in info['shard_details'].items():
                        print(f"    Shard {shard_name}: {shard_info.get('host', 'Unknown')}")
            else:
                print(f"{Fore.RED}Could not retrieve zone status{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}Error checking zone status: {e}{Style.RESET_ALL}")
    
    def verify_data_placement(self):
        """Verify data placement in zones"""
        self.print_header("Verifying Data Placement")
        
        try:
            for zone_name, zone_config in config.ZONES.items():
                database_name = zone_config["database_prefix"]
                countries = zone_config["countries"]
                db = self.client[database_name]
                
                print(f"\n{Fore.CYAN}Zone: {zone_name.upper()}{Style.RESET_ALL}")
                print(f"Database: {database_name}")
                
                # Check tenant-specific collections
                for collection_name in config.TENANT_COLLECTIONS:
                    count = db[collection_name].count_documents({"country": {"$in": countries}})
                    print(f"  {collection_name}: {count} documents")
                
                # Check common collections
                for collection_name in config.COMMON_COLLECTIONS:
                    count = db[collection_name].count_documents({})
                    print(f"  {collection_name}: {count} documents")
            
        except Exception as e:
            print(f"{Fore.RED}Error verifying data placement: {e}{Style.RESET_ALL}")
    
    def cleanup_demo_data(self):
        """Cleanup demo data and configuration"""
        self.print_header("Cleaning Up Demo Data")
        
        try:
            # Clean up zone configuration
            self.zone_manager.cleanup_zones()
            
            # Clean up databases
            for zone_name, zone_config in config.ZONES.items():
                database_name = zone_config["database_prefix"]
                self.client.drop_database(database_name)
                print(f"{Fore.GREEN}✓ Dropped database: {database_name}{Style.RESET_ALL}")
            
            print(f"\n{Fore.GREEN}Cleanup completed!{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}Error during cleanup: {e}{Style.RESET_ALL}")
    
    def run_complete_demo(self):
        """Run the complete Atlas demo"""
        try:
            self.print_header("MongoDB Atlas Zone Sharding Demo")
            print(f"{Fore.GREEN}Welcome to the Atlas Zone Sharding Demo!{Style.RESET_ALL}")
            print("This demo will show how to implement zone sharding on your Atlas cluster.")
            
            input(f"\n{Fore.GREEN}Press Enter to start the demo...{Style.RESET_ALL}")
            
            # Demo steps
            self.setup_zone_sharding_only()
            self.populate_sample_data_only()
            self.check_zone_status()
            self.verify_data_placement()
            
            self.print_header("Demo Complete!")
            print(f"{Fore.GREEN}Atlas zone sharding demo completed successfully!{Style.RESET_ALL}")
            print("\nKey takeaways:")
            print("1. Data is localized to specific zones in your Atlas cluster")
            print("2. Common collections are duplicated across all regions")
            print("3. Tenant-specific data is sharded by region")
            print("4. Zone sharding works seamlessly with Atlas")
            
        except Exception as e:
            print(f"\n{Fore.RED}Demo failed: {e}{Style.RESET_ALL}")
    
    def run(self):
        """Main run loop"""
        self.print_header("MongoDB Atlas Zone Sharding Demo Runner")
        
        while True:
            self.print_menu()
            
            try:
                choice = input(f"{Fore.GREEN}Enter your choice (1-9): {Style.RESET_ALL}").strip()
                
                if choice == "1":
                    self.run_complete_demo()
                elif choice == "2":
                    self.setup_zone_sharding_only()
                elif choice == "3":
                    self.populate_sample_data_only()
                elif choice == "4":
                    self.check_zone_status()
                elif choice == "5":
                    self.verify_data_placement()
                elif choice == "6":
                    confirm = input(f"{Fore.YELLOW}Are you sure you want to cleanup all demo data? (y/N): {Style.RESET_ALL}")
                    if confirm.lower() == 'y':
                        self.cleanup_demo_data()
                elif choice == "7":
                    self.test_connection()
                elif choice == "8":
                    self.show_cluster_info()
                elif choice == "9":
                    print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED}Invalid choice. Please enter 1-9.{Style.RESET_ALL}")
                
                input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Demo interrupted by user{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")


def main():
    """Main function"""
    init(autoreset=True)
    
    print(f"{Fore.CYAN}{'='*60}")
    print("MongoDB Atlas Zone Sharding Demo")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    # Use Atlas connection string from config
    atlas_uri = config.MONGODB_URI
    
    if atlas_uri == "":
        print(f"{Fore.RED}Please update config.py with your actual Atlas connection string.{Style.RESET_ALL}")
        return
    
    try:
        runner = AtlasDemoRunner(atlas_uri)
        runner.run()
    except Exception as e:
        print(f"{Fore.RED}Failed to initialize demo: {e}{Style.RESET_ALL}")
    finally:
        if 'runner' in locals():
            runner.client.close()


if __name__ == "__main__":
    main()
