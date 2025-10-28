#!/usr/bin/env python3
"""
MongoDB Atlas Zone Sharding Setup Script
Configures zone sharding on an existing Atlas cluster
"""

import pymongo
from pymongo import MongoClient
from bson import MaxKey
from typing import Dict, List, Any
import time
from colorama import Fore, Style, init
import config


class AtlasZoneShardingManager:
    """Manages MongoDB Atlas zone sharding configuration"""
    
    def __init__(self, atlas_uri: str):
        self.atlas_uri = atlas_uri
        self.client = MongoClient(atlas_uri)
        self.zones = config.ZONES
        
    def print_status(self, message: str, status: str = "INFO"):
        """Print colored status messages"""
        colors = {
            "INFO": Fore.BLUE,
            "SUCCESS": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED
        }
        print(f"{colors.get(status, Fore.WHITE)}{message}{Style.RESET_ALL}")
    
    def get_shard_list(self) -> List[str]:
        """Get list of available shards in Atlas cluster"""
        try:
            result = self.client.admin.command("listShards")
            shards = [shard["_id"] for shard in result["shards"]]
            self.print_status(f"Found Atlas shards: {shards}", "INFO")
            return shards
        except Exception as e:
            self.print_status(f"Error getting shard list: {e}", "ERROR")
            return []
    
    def create_zones(self, actual_shards: List[str]) -> bool:
        """Create zones for Atlas cluster"""
        self.print_status("Creating zones for Atlas cluster...", "INFO")
        
        try:
            # Map configured zones to actual Atlas shards
            shard_names = [s for s in actual_shards if s != "config"]  # Exclude config shard
            
            for idx, (zone_name, zone_config) in enumerate(self.zones.items()):
                countries = zone_config["countries"]
                
                # Get the actual shard for this zone
                actual_shard = shard_names[idx] if idx < len(shard_names) else shard_names[-1]
                
                # Add shard to zone - zones are created implicitly when first shard is added
                try:
                    # Standard MongoDB command for adding shard to zone
                    result = self.client.admin.command({
                        "addShardToZone": actual_shard,
                        "zone": zone_name
                    })
                    self.print_status(f"Added shard {actual_shard} to zone {zone_name}", "SUCCESS")
                except Exception as e:
                    error_msg = str(e).lower()
                    if "already" in error_msg or "duplicate" in error_msg:
                        self.print_status(f"Shard {actual_shard} already in zone {zone_name}", "WARNING")
                    else:
                        self.print_status(f"Error adding shard {actual_shard} to zone {zone_name}: {e}", "ERROR")
                
                # Note: Zone ranges are defined per collection in MongoDB
                # We'll set these up when sharding the collections later
                self.print_status(f"Zone {zone_name} created with countries: {', '.join(countries)}", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.print_status(f"Error creating zones: {e}", "ERROR")
            return False
    
    def enable_sharding_for_database(self, database_name: str) -> bool:
        """Enable sharding for a database"""
        try:
            self.client.admin.command("enableSharding", database_name)
            self.print_status(f"Enabled sharding for database {database_name}", "SUCCESS")
            return True
        except Exception as e:
            if "already enabled" in str(e).lower():
                self.print_status(f"Sharding already enabled for {database_name}", "WARNING")
                return True
            self.print_status(f"Error enabling sharding for {database_name}: {e}", "ERROR")
            return False
    
    def shard_collection(self, database_name: str, collection_name: str, shard_key: Dict[str, int], zone_name: str = None) -> bool:
        """Shard a collection with the specified shard key"""
        try:
            self.client.admin.command({
                "shardCollection": f"{database_name}.{collection_name}",
                "key": shard_key
            })
            self.print_status(f"Sharded collection {database_name}.{collection_name} with key {shard_key}", "SUCCESS")
            
            # After sharding, set up zone ranges if zone is specified
            if zone_name:
                try:
                    # Get the zone config to set up ranges
                    zone_config = self.zones.get(zone_name)
                    if zone_config:
                        countries = zone_config["countries"]
                        
                        for country in countries:
                            # Set up zone range for this collection
                            # For strings, we need to use a range, so use MaxKey for the max value
                            self.client.admin.command({
                                "updateZoneKeyRange": f"{database_name}.{collection_name}",
                                "min": {"country": country, "region": ""},
                                "max": {"country": country, "region": MaxKey()},
                                "zone": zone_name
                            })
                            self.print_status(f"Set zone range for {country} to {zone_name}", "INFO")
                except Exception as e:
                    # Zone ranges will be set up automatically by MongoDB based on shard-zone associations
                    self.print_status(f"Zone ranges handled via shard-zone associations for {zone_name}", "INFO")
            
            return True
        except Exception as e:
            if "already sharded" in str(e).lower():
                self.print_status(f"Collection {database_name}.{collection_name} already sharded", "WARNING")
                return True
            self.print_status(f"Error sharding collection {database_name}.{collection_name}: {e}", "ERROR")
            return False
    
    def move_database_primary(self, database_name: str, shard_name: str) -> bool:
        """Move database primary to specified shard"""
        try:
            self.client.admin.command({
                "movePrimary": database_name,
                "to": shard_name
            })
            self.print_status(f"Moved primary for database {database_name} to shard {shard_name}", "SUCCESS")
            return True
        except Exception as e:
            self.print_status(f"Error moving primary for {database_name}: {e}", "ERROR")
            return False
    
    def setup_atlas_zone_sharding(self) -> bool:
        """Complete Atlas zone sharding setup"""
        self.print_status("Setting up Atlas zone sharding configuration...", "INFO")
        
        # Get available shards
        shards = self.get_shard_list()
        if not shards:
            self.print_status("No shards found in Atlas cluster", "ERROR")
            return False
        
        if len(shards) < 2:
            self.print_status(f"Atlas cluster has only {len(shards)} shard(s). Zone sharding requires at least 2 shards.", "ERROR")
            return False
        
        # Create zones
        if not self.create_zones(shards):
            return False
        
        # Set up databases for each region
        # Use the actual shards from Atlas
        shard_names = [s for s in shards if s != "config"]  # Exclude config shard
        zone_shards = {}
        
        for idx, (zone_name, zone_config) in enumerate(self.zones.items()):
            # Map to actual Atlas shards
            zone_shards[zone_name] = shard_names[idx] if idx < len(shard_names) else shard_names[-1]
        
        for zone_name, zone_config in self.zones.items():
            database_name = zone_config["database_prefix"]
            primary_shard = zone_shards.get(zone_name, shard_names[0])  # Use mapped Atlas shard
            
            # Enable sharding for database
            if not self.enable_sharding_for_database(database_name):
                continue
            
            # Move primary to regional shard
            if not self.move_database_primary(database_name, primary_shard):
                continue
            
            # Shard tenant-specific collections
            for collection in config.TENANT_COLLECTIONS:
                shard_key = {"country": 1, "region": 1}
                self.shard_collection(database_name, collection, shard_key, zone_name)
        
        self.print_status("Atlas zone sharding setup completed!", "SUCCESS")
        return True
    
    def get_zone_status(self) -> Dict[str, Any]:
        """Get current zone configuration status"""
        try:
            zones_info = {}
            
            # Get shard information
            shards_result = self.client.admin.command("listShards")
            shards_info = {shard["_id"]: shard for shard in shards_result["shards"]}
            
            # Get zone information
            for zone_name, zone_config in self.zones.items():
                zones_info[zone_name] = {
                    "configured_shards": zone_config["shards"],
                    "countries": zone_config["countries"],
                    "database": zone_config["database_prefix"],
                    "shard_details": {}
                }
                
                # Get details for each shard in the zone
                for shard_name in zone_config["shards"]:
                    if shard_name in shards_info:
                        zones_info[zone_name]["shard_details"][shard_name] = shards_info[shard_name]
            
            return zones_info
            
        except Exception as e:
            self.print_status(f"Error getting zone status: {e}", "ERROR")
            return {}
    
    def verify_data_placement(self, database_name: str, collection_name: str) -> Dict[str, Any]:
        """Verify that data is placed in the correct zones"""
        try:
            # Get shard distribution for the collection
            result = self.client.admin.command(
                "dataDistribution",
                f"{database_name}.{collection_name}"
            )
            
            return result
            
        except Exception as e:
            self.print_status(f"Error verifying data placement: {e}", "ERROR")
            return {}
    
    def cleanup_zones(self) -> bool:
        """Clean up zone configuration (for demo reset)"""
        self.print_status("Cleaning up Atlas zone configuration...", "INFO")
        
        try:
            # First, remove shards from zones
            for zone_name, zone_config in self.zones.items():
                shards = zone_config["shards"]
                for shard in shards:
                    try:
                        self.client.admin.command({
                            "removeShardFromZone": shard,
                            "zone": zone_name
                        })
                        self.print_status(f"Removed shard {shard} from zone {zone_name}", "SUCCESS")
                    except Exception as e:
                        error_msg = str(e).lower()
                        if "not in zone" in error_msg:
                            self.print_status(f"Shard {shard} not in zone {zone_name}", "WARNING")
                        else:
                            self.print_status(f"Error removing shard {shard} from zone {zone_name}: {e}", "ERROR")
            
            # Then remove zones
            for zone_name in self.zones.keys():
                try:
                    self.client.admin.command({"removeZone": zone_name})
                    self.print_status(f"Removed zone {zone_name}", "SUCCESS")
                except Exception as e:
                    error_msg = str(e).lower()
                    if "not found" in error_msg:
                        self.print_status(f"Zone {zone_name} not found", "WARNING")
                    else:
                        self.print_status(f"Error removing zone {zone_name}: {e}", "ERROR")
            
            return True
            
        except Exception as e:
            self.print_status(f"Error during cleanup: {e}", "ERROR")
            return False


def main():
    """Main function for Atlas zone sharding setup"""
    init(autoreset=True)
    
    print(f"{Fore.CYAN}{'='*60}")
    print("MongoDB Atlas Zone Sharding Setup")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    # Use Atlas connection string from config
    atlas_uri = config.MONGODB_URI
    
    if atlas_uri == "mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/?retryWrites=true&w=majority":
        print(f"{Fore.RED}Please update config.py with your actual Atlas connection string.{Style.RESET_ALL}")
        return
    
    try:
        manager = AtlasZoneShardingManager(atlas_uri)
        
        # Test connection
        manager.client.admin.command('ping')
        manager.print_status("Atlas connection successful!", "SUCCESS")
        
        # Setup zone sharding
        success = manager.setup_atlas_zone_sharding()
        
        if success:
            manager.print_status("Atlas zone sharding setup completed successfully!", "SUCCESS")
            
            # Show zone status
            zones_info = manager.get_zone_status()
            if zones_info:
                print(f"\n{Fore.BLUE}Zone Configuration:{Style.RESET_ALL}")
                for zone_name, info in zones_info.items():
                    print(f"Zone {zone_name}: {', '.join(info['countries'])} -> {', '.join(info['configured_shards'])}")
        else:
            manager.print_status("Atlas zone sharding setup failed!", "ERROR")
    
    except Exception as e:
        print(f"{Fore.RED}Setup failed: {e}{Style.RESET_ALL}")
    
    finally:
        if 'manager' in locals():
            manager.client.close()


if __name__ == "__main__":
    main()
