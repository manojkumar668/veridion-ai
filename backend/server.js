require("dotenv").config();

const express = require("express");
const cors = require("cors");
const connectDB = require("./config/db");
const Prediction = require("./models/Prediction");

const app = express();

// ================= CORS FIX (IMPORTANT) =================
app.use(cors({
    origin: "*",
    methods: ["GET", "POST", "OPTIONS"],
    allowedHeaders: ["Content-Type"]
}));

// 🔥 FIX for preflight requests
app.options("*", cors());

// ================= MIDDLEWARE =================
app.use(express.json());

// ================= HEALTH CHECK =================
app.get("/", (req, res) => {
    res.status(200).json({
        status: "success",
        message: "Veridion AI Backend is running 🚀"
    });
});

// ================= DB CONNECT =================
connectDB()
    .then(() => console.log("✅ MongoDB Connected Successfully"))
    .catch(err => console.log("❌ MongoDB ERROR:", err.message));

// ================= PREDICT =================
app.post("/predict", async (req, res) => {
    try {
        const { text } = req.body;

        if (!text) {
            return res.status(400).json({
                success: false,
                error: "Text is required"
            });
        }

        console.log("📥 Incoming text:", text);

        // 🔥 SIMPLE AI LOGIC
        const isFake = text.toLowerCase().includes("free");

        const result = {
            success: true,
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
            console.log("⚠️ DB Error:", dbErr.message);
        }

        return res.status(200).json(result);

    } catch (error) {
        console.log("❌ Predict Error:", error.message);

        return res.status(500).json({
            success: false,
            error: "Internal Server Error"
        });
    }
});

// ================= HISTORY =================
app.get("/history", async (req, res) => {
    try {
        const data = await Prediction.find()
            .sort({ createdAt: -1 })
            .limit(10);

        res.json({
            success: true,
            data
        });

    } catch (err) {
        res.status(500).json({
            success: false,
            error: err.message
        });
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
            success: true,
            total,
            fake,
            real: total - fake
        });

    } catch (err) {
        res.status(500).json({
            success: false,
            error: err.message
        });
    }
});

// ================= 404 =================
app.use((req, res) => {
    res.status(404).json({
        success: false,
        error: "Route not found"
    });
});

// ================= START SERVER =================
const PORT = process.env.PORT || 5000;

app.listen(PORT, "0.0.0.0", () => {
    console.log(`🚀 Server running on port ${PORT}`);
});