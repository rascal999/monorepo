// MongoDB test data insertion script
db = db.getSiblingDB('metrics');

// Drop the collection if it exists
db.metrics.drop();

// Insert some test data
db.metrics.insertMany([
  {
    name: "CPU Usage",
    value: 45,
    timestamp: new Date(),
    host: "server1"
  },
  {
    name: "Memory Usage",
    value: 60,
    timestamp: new Date(),
    host: "server1"
  },
  {
    name: "Disk Usage",
    value: 75,
    timestamp: new Date(),
    host: "server1"
  },
  {
    name: "Network Traffic",
    value: 30,
    timestamp: new Date(),
    host: "server1"
  },
  {
    name: "CPU Usage",
    value: 55,
    timestamp: new Date(),
    host: "server2"
  },
  {
    name: "Memory Usage",
    value: 70,
    timestamp: new Date(),
    host: "server2"
  },
  {
    name: "Disk Usage",
    value: 65,
    timestamp: new Date(),
    host: "server2"
  },
  {
    name: "Network Traffic",
    value: 40,
    timestamp: new Date(),
    host: "server2"
  }
]);

// Verify the data was inserted
print("Inserted documents:");
db.metrics.find().forEach(printjson);