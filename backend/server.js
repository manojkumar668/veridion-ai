require("dotenv").config();

const express = require("express");
const cors = require("cors");
const axios = require("axios");
const connectDB = require("./config/db");

// 🔥 Mongo Model
const Prediction = require("./models/Prediction");

const app = express();

// ================= MIDDLEWARE =================
app.use(cors());
app.use(express.json());

// ================= DEBUG =================
console.log("MONGO URI:", process.env.MONGO_URI);

// ================= ROUTES =================
app.get("/", (req, res) => {
    res.send("Backend Running 🚀");
});

// ================= PREDICT ROUTE =================
app.post("/predict", async (req, res) => {
    try {
        const { text } = req.body;

        if (!text) {
            return res.status(400).json({ error: "Text is required" });
        }

        console.log("📥 Incoming text:", text);

        // 🔥 Call Flask ML API
        const response = await axios.post("http://127.0.0.1:5001/predict", {
            text
        });

        const result = response.data;

        console.log("🤖 ML Response:", result);

        // 🔥 SAVE TO MONGODB
        console.log("🔥 Saving to DB...");

        const saved = await Prediction.create({
            text: text,
            prediction: result.prediction,
            confidence: result.confidence
        });

        console.log("✅ Saved Document:", saved);

        return res.json(result);

    } catch (error) {
        console.log("❌ Predict Error:", error.message);
        return res.status(500).json({
            error: "ML service error",
            details: error.message
        });
    }
});

// ================= HISTORY ROUTE =================
app.get("/history", async (req, res) => {
    try {
        const data = await Prediction.find()
            .sort({ createdAt: -1 })
            .limit(10)        // 🔥 last 10 records
            .select("-__v");  // 🔥 remove __v

        res.json(data);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ================= STATS ROUTE =================
app.get("/stats", async (req, res) => {
    try {
        const total = await Prediction.countDocuments();
        const fake = await Prediction.countDocuments({
            prediction: "FAKE / SCAM"
        });

        res.json({
            total,
            fake,
            real: total - fake
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ================= START SERVER =================
const PORT = process.env.PORT || 5000;

const server = app.listen(PORT, "127.0.0.1", async () => {
    console.log(`🚀 Server running on http://127.0.0.1:${PORT}`);

    try {
        await connectDB();
        console.log("✅ MongoDB Connected Successfully");
    } catch (err) {
        console.log("❌ MongoDB ERROR:", err.message);
    }
});

// ================= DEBUG EVENTS =================
server.on("listening", () => {
    console.log("✅ SERVER IS ACTUALLY LISTENING");
});

server.on("error", (err) => {
    console.log("❌ SERVER ERROR:", err.message);
});

// ================= GLOBAL ERROR HANDLERS =================
process.on("uncaughtException", (err) => {
    console.log("❌ UNCAUGHT ERROR:", err.message);
});

process.on("unhandledRejection", (err) => {
    console.log("❌ UNHANDLED REJECTION:", err);
});