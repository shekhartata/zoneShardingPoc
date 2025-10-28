# MongoDB Atlas Zone Sharding Demo Configuration

# MongoDB Atlas Connection
# Replace with your Atlas connection string
MONGODB_URI = "mongodb+srv://<user:password>@<cluster-url>"

# For Atlas, we use the same URI for both main and config connections
MONGODB_CONFIG_URI = MONGODB_URI

# Zone Configuration for 2-shard Atlas cluster
# Assuming you have 2 shards, we'll create 2 zones
ZONES = {
    "region1": {
        "shards": ["shard00"],  # First shard
        "countries": ["CN", "TR"],  # China and Turkey in first region
        "database_prefix": "app_region1"
    },
    "region2": {
        "shards": ["shard01"],  # Second shard
        "countries": ["AE", "US", "EU", "GB"],  # UAE and Global in second region
        "database_prefix": "app_region2"
    }
}

# Demo Settings
DEMO_DATA_SIZE = 1000
COMMON_COLLECTIONS = ["users", "products", "categories"]
TENANT_COLLECTIONS = ["orders", "transactions", "logs"]

# Atlas-specific settings
ATLAS_CLUSTER_NAME = "<atlas-cluster-name>"
ATLAS_PROJECT_ID = "<project-id>"
