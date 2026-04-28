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

// ================= DB CONNECT (NON-BLOCKING) =================
connectDB()
  .then(() => console.log("✅ MongoDB Connected Successfully"))
  .catch((err) => console.log("❌ MongoDB ERROR:", err.message));

// ================= DEBUG =================
console.log("MONGO URI LOADED");

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

        // ⚠️ SAFE FLASK HANDLING
        const FLASK_API = process.env.FLASK_API_URL;

        let result;

        if (FLASK_API) {
            const response = await axios.post(FLASK_API, { text });
            result = response.data;
        } else {
            result = {
                prediction: "FLASK NOT CONNECTED",
                confidence: 0
            };
        }

        console.log("🤖 ML Response:", result);

        // 🔥 SAVE TO MONGODB (safe)
        try {
            await Prediction.create({
                text: text,
                prediction: result.prediction,
                confidence: result.confidence
            });
        } catch (dbErr) {
            console.log("⚠️ DB Save Error:", dbErr.message);
        }

        return res.json(result);

    } catch (error) {
        console.log("❌ Predict Error:", error.message);
        return res.status(500).json({
            error: "Service error",
            details: error.message
        });
    }
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

// ================= START SERVER (FIXED FOR RENDER) =================
const PORT = process.env.PORT || 5000;

app.listen(PORT, "0.0.0.0", () => {
    console.log(`🚀 Server running on port ${PORT}`);
});