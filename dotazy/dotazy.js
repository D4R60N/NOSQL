use Transparency;

// indexy
db.Load.createIndex({"MTU (CET/CEST)": 1});
// složený index
db.Production.createIndex({"Production Type": 1, "MTU (CET/CEST)": 1});

// práce s daty
// vložení dat
db.Load.insertOne({
    "MTU (CET/CEST)": "01/01/2024 00:00 - 01/01/2024 01:00",
    Area: "BZN|CZ", "Actual Total Load (MW)": 5373.27, "Day-ahead Total Load Forecast (MW)": 5231
});
// update dat
db.Load.updateOne(
    {"MTU (CET/CEST)": "01/01/2024 00:00 - 01/01/2024 01:00"},
    {$set: {"Actual Total Load (MW)": 0}}
);
// smazání dat
db.Load.deleteOne(
    {"MTU (CET/CEST)": "01/01/2024 00:00 - 01/01/2024 01:00"},
);
// merge dat do nové kolekce
db.Production.aggregate([
    { $match: { "Production Type": "Nuclear" } },
    { $merge: { into: "NuclearProduction" } }
]);

// agregační funkce
// průměrná hodnota
db.Load.aggregate([
    { $group: { _id: "$Area", averageLoad: { $avg: "$Actual Total Load (MW)" } } }
]);
// počet n/e hodnot
db.Production.aggregate([
    { $match: { "Generation (MW)": "n/e" } },
    { $group: { _id: "$Area", count: { $sum: 1 } } }
]);
// porovnání spotřeby a ceny 1.4.2023
db.Load.aggregate([
    { $match: { "MTU (CET/CEST)": { $regex: /01\/04\/2023/ } } },
    {
        $lookup: {
            from: "Prices",
            localField: "MTU (CET/CEST)",
            foreignField: "MTU (CET/CEST)",
            as: "price"
        }
    },
    { $unwind: "$price" },
    {
        $project: {
            _id: 0,
            "MTU (CET/CEST)": 1,
            Area: 1,
            "Actual Total Load (MW)": 1,
            "Day-ahead Price (EUR/MWh)": "$price.Day-ahead Price (EUR/MWh)"
        }
    }
]);

// konfigurace
// sharding
sh.enableSharding("Transparency");
db.adminCommand({ shardCollection: "Transparency.Load", key: { "Area": 1, "MTU (CET/CEST)": 1 } });
db.adminCommand({ shardCollection: "Transparency.Prices", key: { "Area": 1, "MTU (CET/CEST)": 1 } });
db.adminCommand({ shardCollection: "Transparency.Production", key: { "Area": 1, "MTU (CET/CEST)": 1, "Production Type": 1 } });
// vytvoření kolekce s validací
db.createCollection("Prices", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["MTU (CET/CEST)", "Area", "Day-ahead Price (EUR/MWh)"],
            properties: {
                "MTU (CET/CEST)": { bsonType: "string" },
                Area: { bsonType: "string" },
                "Day-ahead Price (EUR/MWh)": { bsonType: ["double", "string"] }
            }
        }
    }
});
db.createCollection("Load", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["MTU (CET/CEST)", "Area", "Actual Total Load (MW)"],
            properties: {
                "MTU (CET/CEST)": { bsonType: "string" },
                Area: { bsonType: "string" },
                "Actual Total Load (MW)": { bsonType: ["double", "string"] },
                "Day-ahead Total Load Forecast (MW)": { bsonType: ["double", "string"] }
            }
        }
    }
});
db.createCollection("Production", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["MTU (CET/CEST)", "Area", "Production Type", "Generation (MW)"],
            properties: {
                "MTU (CET/CEST)": { bsonType: "string" },
                Area: { bsonType: "string" },
                "Production Type": { bsonType: "string" },
                "Generation (MW)": { bsonType: ["double", "string"] }
            }
        }
    }
});
// kontorla validace
db.getCollection('Load').getValidators()






