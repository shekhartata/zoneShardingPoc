# MongoDB Atlas Zone Sharding Demo

## 🎯 Demo Overview

This demo demonstrates MongoDB Atlas zone sharding for data localization in restrictive regions (China, Turkey, UAE) with your existing 2-shard Atlas cluster.

## 📁 Project Structure

```
zoneShardingDemo/
├── config.py              # Atlas configuration - UPDATE YOUR CONNECTION STRING HERE
├── models.py              # Data models and generators
├── setup_atlas_zones.py   # Atlas zone sharding setup
├── run_demo.py            # Interactive demo runner
├── test_demo.py           # Test suite
├── requirements.txt       # Python dependencies
├── ATLAS_SETUP_GUIDE.md   # Detailed setup guide
└── venv/                  # Python virtual environment
```

## 🚀 Setup Instructions

### Step 1: Configure Your Atlas Connection

Edit `config.py` and update the connection string:

```python
MONGODB_URI = "mongodb+srv://<username:password>@<cluster-uri>/?retryWrites=true&w=majority"
```

### Step 2: Activate Virtual Environment

```bash
cd zoneShardingDemo
source venv/bin/activate
```

### Step 3: Set Up Zone Sharding

```bash
python setup_atlas_zones.py
```

This will:
- Detect your Atlas shards
- Create zones (region1 for China/Turkey, region2 for UAE/Global)
- Assign shards to zones
- Enable sharding for regional databases
- Shard collections with zone-aware ranges

## 🎮 Demo Execution

### Interactive Demo Runner

```bash
python run_demo.py
```

**Demo Menu Options:**
1. **Run Complete Atlas Demo** - Full end-to-end demonstration (Recommended for first run)
2. **Setup Zone Sharding Only** - Configure zones and sharding (if already populated data)
3. **Populate Sample Data Only** - Generate test data without setting up zones
4. **Check Zone Status** - View current zone configuration
5. **Verify Data Placement** - Confirm data is in correct zones
6. **Cleanup Demo Data** - Reset for fresh demo
7. **Test Atlas Connection** - Verify connectivity
8. **Show Atlas Cluster Info** - View cluster details
9. **Exit**

### Recommended Demo Flow

```bash
# Step 1: Test connection
python run_demo.py
# Choose option 7: Test Atlas Connection

# Step 2: Setup zones and populate data
python run_demo.py
# Choose option 1: Run Complete Atlas Demo
# This will:
# - Setup zone sharding
# - Populate common data (users, products, categories)
# - Generate tenant-specific data (orders, transactions, logs)
# - Verify data placement

# Step 3: Verify the setup
python run_demo.py
# Choose option 5: Verify Data Placement
# This will show counts by region

# Step 4: Check zone configuration
python run_demo.py
# Choose option 4: Check Zone Status
```

## 🏗️ Zone Configuration

Your Atlas cluster will be configured with:

### Zone 1: Region1 (First Shard)
- **Countries**: CN (China), TR (Turkey)
- **Database**: app_region1
- **Use Case**: Restrictive regions requiring data residency

### Zone 2: Region2 (Second Shard)
- **Countries**: AE (UAE), US, EU, GB
- **Database**: app_region2
- **Use Case**: Global regions with standard compliance

## 🎮 Atlas Demo Options

The Atlas demo runner provides these options:

1. **Run Complete Atlas Demo** - Full end-to-end demonstration
2. **Setup Zone Sharding Only** - Configure zones and sharding
3. **Populate Sample Data Only** - Generate test data
4. **Check Zone Status** - View current configuration
5. **Verify Data Placement** - Confirm data localization
6. **Cleanup Demo Data** - Reset for fresh demo
7. **Test Atlas Connection** - Verify connectivity
8. **Show Atlas Cluster Info** - View cluster details
9. **Exit** - Close the demo

## 📊 Data Architecture

### Common Collections (Duplicated Across All Zones)
These collections are **NOT SHARDED** and exist in both databases:
- **users** - Global user data (50 records per zone)
- **products** - Product catalog (100 records per zone)
- **categories** - Category information (20 records per zone)

### Tenant-Specific Collections (SHARDED by Region)
These collections are **SHARDED** and data goes to specific zones based on country:
- **orders** - Regional order data (500 per country)
- **transactions** - Payment data (500 per country)
- **logs** - Activity logs (500 per country)

## 🔧 MongoDB Commands Being Executed

### Commands Run Automatically by setup_atlas_zones.py

```javascript
// 1. Get shard list
db.adminCommand({listShards: 1})

// 2. Add shards to zones
db.adminCommand({
  addShardToZone: "atlas-xxx-shard-0",  // Your actual first shard
  zone: "region1"
})

db.adminCommand({
  addShardToZone: "atlas-xxx-shard-0",  // Your actual second shard  
  zone: "region2"
})

// 3. Enable sharding for databases
db.adminCommand({enableSharding: "app_region1"})
db.adminCommand({enableSharding: "app_region2"})

// 4. Move database primary to specific shard
db.adminCommand({
  movePrimary: "app_region1",
  to: "atlas-xxx-shard-0"  // First shard
})

db.adminCommand({
  movePrimary: "app_region2",
  to: "atlas-xxx-shard-0"  // Second shard
})

// 5. Shard collections with compound key
db.adminCommand({
  shardCollection: "app_region1.orders",
  key: {country: 1, region: 1}
})

db.adminCommand({
  shardCollection: "app_region1.transactions",
  key: {country: 1, region: 1}
})

db.adminCommand({
  shardCollection: "app_region1.logs",
  key: {country: 1, region: 1}
})

db.adminCommand({
  shardCollection: "app_region2.orders",
  key: {country: 1, region: 1}
})

db.adminCommand({
  shardCollection: "app_region2.transactions",
  key: {country: 1, region: 1}
})

db.adminCommand({
  shardCollection: "app_region2.logs",
  key: {country: 1, region: 1}
})

// 6. Set up zone ranges for collections
db.adminCommand({
  updateZoneKeyRange: "app_region1.orders",
  min: {country: "CN", region: ""},
  max: {country: "CN", region: MaxKey()},
  zone: "region1"
})

db.adminCommand({
  updateZoneKeyRange: "app_region1.orders",
  min: {country: "TR", region: ""},
  max: {country: "TR", region: MaxKey()},
  zone: "region1"
})

db.adminCommand({
  updateZoneKeyRange: "app_region2.orders",
  min: {country: "AE", region: ""},
  max: {country: "AE", region: MaxKey()},
  zone: "region2"
})

// Similar commands for US, EU, GB to region2
// Similar commands for transactions and logs collections
```

### Connect to Atlas

```javascript
// From MongoDB shell or Compass
mongosh "mongodb+srv://your-cluster.mongodb.net/"
```

### Check Zone Status

```javascript
// View all shards and their zone assignments
sh.status()

// Or specifically list shards
db.adminCommand({listShards: 1})
```

### Verify Data Placement

```javascript
// Check distribution for a specific collection
db.runCommand({dataDistribution: "app_region1.orders"})

// Count documents by country in each database
use app_region1
db.orders.countDocuments({country: "CN"})
db.orders.countDocuments({country: "TR"})

use app_region2
db.orders.countDocuments({country: "AE"})
db.orders.countDocuments({country: "US"})
```

### Query Data by Region

```javascript
// Query data and see execution stats
use app_region1
db.orders.find({country: "CN"}).explain("executionStats")

use app_region2
db.orders.find({country: "AE"}).explain("executionStats")
```

### Check Zone Ranges

```javascript
// View zone key ranges
use config
db.tags.find()
```

## 🎤 Demo Presentation Flow

### Before the Demo

1. **Prepare**: Update `config.py` with your Atlas connection string
2. **Cleanup**: Run option 6 to start fresh
3. **Test**: Run option 7 to verify connectivity

### During the Demo

**Part 1: Setup (2-3 minutes)**
```bash
python run_demo.py
# Choose option 2: Setup Zone Sharding Only
# Show team:
# - Creating zones for restrictive regions
# - Assigning shards to zones
# - Enabling sharding
```

**Part 2: Data Population (3-5 minutes)**
```bash
python run_demo.py
# Choose option 3: Populate Sample Data Only
# Show team:
# - Common collections (users, products, categories) duplicated in both zones
# - Tenant collections (orders, transactions, logs) being generated
```

**Part 3: Verification (2-3 minutes)**
```bash
python run_demo.py
# Choose option 5: Verify Data Placement
# Show team:
# - app_region1 has CN and TR data
# - app_region2 has AE, US, EU, GB data
# - Each zone has its own regional data
```

**Part 4: Live Query Demo**
```bash
# Use option 8: Show Atlas Cluster Info
# Or connect via MongoDB Compass/mongosh and demonstrate:
# - Querying data from app_region1 shows only China/Turkey data
# - Querying data from app_region2 shows only UAE/Global data
# - No cross-zone data transfer
```

## 🚨 Troubleshooting

### Test Your Setup

```bash
# Run the test suite
source venv/bin/activate
python test_demo.py
```

### Common Issues and Solutions

1. **Connection Refused**
   ```bash
   # Verify your Atlas connection string in config.py
   # Run option 7: Test Atlas Connection
   python run_demo.py
   ```

2. **Insufficient Shards**
   ```bash
   # Check you have at least 2 shards
   python run_demo.py
   # Choose option 8: Show Atlas Cluster Info
   ```

3. **Zone Errors**
   ```bash
   # Clean up and start fresh
   python run_demo.py
   # Choose option 6: Cleanup Demo Data
   # Then option 2: Setup Zone Sharding Only
   ```

4. **Data Not Showing in Zones**
   ```bash
   # Verify data was populated after zone setup
   python run_demo.py
   # Choose option 5: Verify Data Placement
   ```

## 📈 Key Benefits Demonstrated

### ✅ Compliance & Data Residency
- **Automatic Data Placement**: Data for China/Turkey goes to region1 zone
- **Regional Compliance**: Data for UAE/Global goes to region2 zone
- **No Cross-border Transfer**: Data stays in assigned shards
- **Audit Trail**: Complete data access logging

### ✅ Performance Optimization
- **Local Data Access**: Reduced latency for regional queries
- **Query Optimization**: Efficient routing to appropriate shards
- **Resource Utilization**: Optimal use of Atlas resources
- **Scalability**: Independent scaling per zone

### ✅ Simplified Management
- **Unified Cluster**: Single Atlas cluster for all regions
- **Centralized Monitoring**: Atlas monitoring and alerting
- **Simplified Operations**: Easy backup and recovery
- **Cost Efficiency**: Reduced cross-region data transfer costs

## 🎯 Demo Key Points for Team

### Zone Sharding Concept
1. **Why Zones?**: Ensure data residency for restrictive regions (China, Turkey, UAE)
2. **How It Works**: Map countries to zones, zones to shards
3. **Data Placement**: MongoDB automatically routes data based on shard key
4. **Query Routing**: Queries go to the correct shard based on country

### Architecture Highlights
- **2 Zones**: region1 (restrictive countries) and region2 (global countries)
- **2 Shards**: Each zone mapped to one of your Atlas shards
- **2 Databases**: app_region1 and app_region2 for isolation
- **6 Collections**: 3 common (duplicated) + 3 tenant (sharded)

### Compliance Demonstration
- **China Data**: All CN records in region1 → Shard assigned to region1
- **Turkey Data**: All TR records in region1 → Shard assigned to region1
- **UAE Data**: All AE records in region2 → Shard assigned to region2
- **Global Data**: All US/EU/GB records in region2 → Shard assigned to region2

## 📝 Quick Reference Commands

```bash
# Navigate to project
cd zoneShardingDemo

# Activate environment
source venv/bin/activate

# Run demo
python run_demo.py

# Test setup
python test_demo.py

# Check configuration
cat config.py
```

## 📚 Additional Resources

- **ATLAS_SETUP_GUIDE.md**: Comprehensive setup and troubleshooting guide
- **config.py**: Update your Atlas connection string here
- MongoDB Atlas Documentation: https://docs.atlas.mongodb.com/
- MongoDB Zone Sharding: https://docs.mongodb.com/manual/core/zone-sharding/

---

## 🚀 Ready to Demo!

**Your MongoDB Atlas Zone Sharding demo is ready!**

**Next Steps:**
1. Update `config.py` with your Atlas connection string
2. Run `python run_demo.py` and follow the interactive menu
3. Choose option 1 for complete demo or options 2+3 separately
4. Use option 5 to verify data is in correct zones
5. Show your team how data is automatically routed based on country codes

**Happy Presenting! 🎉**
