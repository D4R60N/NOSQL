use Transparency;

// indexy
db.Load.createIndex({"Actual Total Load (MW)": 1});
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
//odstřanění N/A hodnot
db.Load.aggregate([
    { $match: { $nor: [
        { "Actual Total Load (MW)": "n/e" },
        { "Day-ahead Total Load Forecast (MW)": "n/e" }
            ]} },
    { $out: "LoadClean" }
]);
db.Production.aggregate([
    { $match: { "Generation (MW)": { $ne: "n/e" } } },
    { $out: "ProductionClean" }
]);

// agregační funkce
// rozdíl mezy skutečnou a předpovězenou spotřebou zagregováno na dny (dny jsou od 00:00 do 23:00) seřazeno podle difference
db.Load.aggregate([
    { $sort: { _id: -1 } },
    {
        $group: {
            _id: { $substr: ["$MTU (CET/CEST)", 0, 10] },
            actualLoad: { $sum: "$Actual Total Load (MW)" },
            forecastLoad: { $sum: "$Day-ahead Total Load Forecast (MW)" }
        }
    },
    {
        $project: {
            _id: 1,
            difference: { $subtract: ["$actualLoad", "$forecastLoad"] }
        }
    },
    { $sort: { difference: -1 } }
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
// nalezení top 10 nejdražších dní z hlediska ceny (dny jsou od 00:00 do 23:00)
db.Prices.aggregate([
    { $group: { _id: { $substr: ["$MTU (CET/CEST)", 0, 10] }, averagePrice: { $avg: "$Day-ahead Price (EUR/MWh)" } } },
    { $sort: { averagePrice: -1 } },
    { $limit: 10 }
]);

// výpočet celkem peněz vydělaných za každý měsíc cena*spotřeba a spotřeba
db.LoadClean.aggregate([
    { $lookup: {
        from: "Prices",
        localField: "MTU (CET/CEST)",
        foreignField: "MTU (CET/CEST)",
        as: "price"
    }},
    { $unwind: "$price" },
    {
        $group: {
            _id: { $substr: ["$MTU (CET/CEST)", 3, 7] },
            totalMoney: { $sum: { $multiply: ["$Actual Total Load (MW)", "$price.Day-ahead Price (EUR/MWh)"] } },
            totalLoad: { $sum: "$Actual Total Load (MW)" }
        }
    },
    { $project: { _id: 1, totalMoney: 1, totalLoad: 1 } },
    { $sort: { _id: 1 } }
]);

// najdi nejvyšší cenu a vypočti podíly typu výroby na celkové výrobě
db.Prices.aggregate([
    { $sort: { "Day-ahead Price (EUR/MWh)": -1 } },
    { $limit: 1 },
    { $lookup: {
        from: "ProductionClean",
        localField: "MTU (CET/CEST)",
        foreignField: "MTU (CET/CEST)",
        as: "production"
    }},
    { $unwind: "$production" },
    {
        $group: {
            _id: "$MTU (CET/CEST)" ,
            maxPrice: { $max: "$Day-ahead Price (EUR/MWh)" },
            totalProduction: { $sum: "$production.Generation (MW)" },
            productionType: { $push: { type: "$production.Production Type", generation: "$production.Generation (MW)" } }
        }
    },
    {
        $project: {
            _id: 1,
            maxPrice: 1,
            totalProduction: 1,
            productionType: {
                $map: {
                    input: "$productionType",
                    as: "type",
                    in: {
                        type: "$$type.type",
                        share: { $divide: ["$$type.generation", "$totalProduction"] }
                    }
                }
            }
        }
    },
    {
        $set: {
            productionType: {
                $sortArray: {
                    input: "$productionType",
                    sortBy: { share: -1 }
                }
            }
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






