# MongoDB Atlas Zone Sharding Setup Guide

## 🎯 Overview

This guide will help you set up zone sharding on your existing MongoDB Atlas cluster with 2 shards. The setup will create two zones to demonstrate data localization across your shards.

## 📋 Prerequisites

- MongoDB Atlas cluster with **2 shards** (shard00, shard01)
- Cluster with **sharding enabled**
- Atlas connection string with admin privileges
- Python 3.8+ with virtual environment

## 🚀 Quick Setup

### 1. Prepare Your Environment

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (if not already done)
pip install -r requirements.txt
```

### 2. Configure Your Atlas Connection

Edit `config_atlas.py` and update the connection string:

```python
# Replace with your actual Atlas connection string
MONGODB_URI = "mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/?retryWrites=true&w=majority"
```

### 3. Run the Atlas Demo

```bash
# Run the interactive Atlas demo
python run_atlas_demo.py
```

## 🏗️ Zone Configuration

The demo creates two zones on your 2-shard Atlas cluster:

### Zone 1: Region1
- **Shard**: shard00
- **Countries**: CN (China), TR (Turkey)
- **Database**: app_region1
- **Use Case**: Restrictive regions requiring data residency

### Zone 2: Region2
- **Shard**: shard01
- **Countries**: AE (UAE), US, EU, GB
- **Database**: app_region2
- **Use Case**: Global regions with standard compliance

## 🔧 Manual Setup Commands

If you prefer to run commands manually, here are the MongoDB commands:

### 1. Connect to Your Atlas Cluster

```bash
# Use your Atlas connection string
mongo "mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/?retryWrites=true&w=majority"
```

### 2. Create Zones

```javascript
// Add shards to zones
sh.addShardToZone("shard00", "region1")
sh.addShardToZone("shard01", "region2")
```

### 3. Define Zone Ranges

```javascript
// Define ranges for each country
sh.updateZoneKeyRange("config.region1", {country: "CN"}, {country: "CN"}, "region1")
sh.updateZoneKeyRange("config.region1", {country: "TR"}, {country: "TR"}, "region1")
sh.updateZoneKeyRange("config.region2", {country: "AE"}, {country: "AE"}, "region2")
sh.updateZoneKeyRange("config.region2", {country: "US"}, {country: "US"}, "region2")
sh.updateZoneKeyRange("config.region2", {country: "EU"}, {country: "EU"}, "region2")
sh.updateZoneKeyRange("config.region2", {country: "GB"}, {country: "GB"}, "region2")
```

### 4. Enable Sharding for Databases

```javascript
// Enable sharding for regional databases
sh.enableSharding("app_region1")
sh.enableSharding("app_region2")
```

### 5. Move Database Primaries

```javascript
// Move primaries to regional shards
db.runCommand({movePrimary: "app_region1", to: "shard00"})
db.runCommand({movePrimary: "app_region2", to: "shard01"})
```

### 6. Shard Collections

```javascript
// Shard tenant-specific collections
sh.shardCollection("app_region1.orders", {country: 1, region: 1})
sh.shardCollection("app_region1.transactions", {country: 1, region: 1})
sh.shardCollection("app_region1.logs", {country: 1, region: 1})

sh.shardCollection("app_region2.orders", {country: 1, region: 1})
sh.shardCollection("app_region2.transactions", {country: 1, region: 1})
sh.shardCollection("app_region2.logs", {country: 1, region: 1})
```

## 🎮 Demo Options

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

### Common Collections (Duplicated)
- **users**: Global user data accessible from all zones
- **products**: Product catalog available everywhere
- **categories**: Category information shared globally

### Tenant Collections (Sharded)
- **orders**: Regional order data sharded by country
- **transactions**: Payment data localized by region
- **logs**: Activity logs stored in appropriate zones

## 🔍 Verification Commands

### Check Zone Status
```javascript
// List all shards and their zones
sh.status()
```

### Verify Data Placement
```javascript
// Check data distribution
db.runCommand({dataDistribution: "app_region1.orders"})
db.runCommand({dataDistribution: "app_region2.orders"})
```

### Query Data by Region
```javascript
// Query data from specific regions
db.orders.find({country: "CN"}).explain("executionStats")
db.orders.find({country: "AE"}).explain("executionStats")
```

## 🚨 Troubleshooting

### Common Issues

1. **Connection Refused**
   ```bash
   # Verify your Atlas connection string
   python run_atlas_demo.py
   # Select option 7: Test Atlas Connection
   ```

2. **Insufficient Shards**
   ```bash
   # Check your Atlas cluster has 2 shards
   python run_atlas_demo.py
   # Select option 8: Show Atlas Cluster Info
   ```

3. **Zone Configuration Errors**
   ```bash
   # Check zone status
   python run_atlas_demo.py
   # Select option 4: Check Zone Status
   ```

4. **Data Placement Issues**
   ```bash
   # Verify data placement
   python run_atlas_demo.py
   # Select option 5: Verify Data Placement
   ```

### Reset Demo Environment

```bash
python run_atlas_demo.py
# Select option 6: Cleanup Demo Data
```

## 📈 Performance Considerations

### Shard Key Design
- **Compound keys**: `{country: 1, region: 1}` for optimal distribution
- **Query patterns**: Aligned with regional access patterns
- **Cardinality**: High cardinality for even distribution

### Atlas-Specific Optimizations
- **Connection pooling**: Use Atlas connection string efficiently
- **Read preferences**: Configure for regional reads
- **Write concerns**: Use appropriate write concern levels

## 🔒 Security Considerations

### Atlas Security
- **Network access**: Configure IP whitelist
- **Authentication**: Use strong credentials
- **Encryption**: Atlas provides encryption at rest and in transit

### Data Isolation
- **Zone boundaries**: Enforce data residency
- **Access controls**: Regional access policies
- **Audit logging**: Track data access and modifications

## 📚 Additional Resources

- [MongoDB Atlas Zone Sharding](https://docs.atlas.mongodb.com/cluster-config/zones/)
- [MongoDB Zone Sharding Documentation](https://docs.mongodb.com/manual/core/zone-sharding/)
- [Atlas Cluster Management](https://docs.atlas.mongodb.com/cluster-config/)

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review Atlas documentation
3. Run the test connection option
4. Contact MongoDB support

---

**Ready to demonstrate Atlas Zone Sharding! 🚀**
