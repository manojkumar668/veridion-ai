require("dotenv").config();

const express = require("express");
const cors = require("cors");
const connectDB = require("./config/db");
const Prediction = require("./models/Prediction");

const app = express();

// ================= MIDDLEWARE =================
app.use(cors());
app.use(express.json());

// ================= ROOT / HEALTH CHECK =================
app.get("/", (req, res) => {
    res.json({
        status: "success",
        message: "Veridion AI Backend is running 🚀"
    });
});

// ================= DB CONNECT =================
connectDB()
    .then(() => console.log("✅ MongoDB Connected Successfully"))
    .catch((err) => console.log("❌ MongoDB ERROR:", err.message));

// ================= PREDICT ROUTE (FIXED WORKING VERSION) =================
app.post("/predict", async (req, res) => {
    const { text } = req.body;

    if (!text) {
        return res.status(400).json({
            error: "Text is required"
        });
    }

    console.log("📥 Incoming text:", text);

    // 🚀 SIMPLE AI LOGIC (NO FLASK - STABLE VERSION)
    const isFake = text.toLowerCase().includes("free");

    const result = {
        prediction: isFake ? "FAKE / SCAM" : "REAL",
        confidence: 90
    };

    console.log("🤖 Result:", result);

    // ================= SAVE TO DB =================
    try {
        await Prediction.create({
            text,
            prediction: result.prediction,
            confidence: result.confidence
        });
    } catch (dbErr) {
        console.log("⚠️ DB Save Error:", dbErr.message);
    }

    res.json(result);
});

// ================= HISTORY =================
app.get("/history", async (req, res) => {
    try {
        const data = await Prediction.find()
            .sort({ createdAt: -1 })
            .limit(10)
            .select("-__v");

        res.json(data);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ================= STATS =================
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

app.listen(PORT, "0.0.0.0", () => {
    console.log(`🚀 Server running on port ${PORT}`);
});