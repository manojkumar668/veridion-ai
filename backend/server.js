require("dotenv").config();

const express = require("express");
const cors = require("cors");

const connectDB = require("./config/db");
const Prediction = require("./models/Prediction");

const app = express();

// ================= CORS FIX =================
app.use(cors({
    origin: "*",
    methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"]
}));

app.options("*", cors());

// ================= MIDDLEWARE =================
app.use(express.json());

// ================= HEALTH CHECK =================
app.get("/", (req, res) => {

    res.status(200).json({
        success: true,
        message: "🚀 Veridion AI Backend Running"
    });

});

// ================= DATABASE CONNECTION =================
connectDB()
    .then(() => {

        console.log("✅ MongoDB Connected Successfully");

    })
    .catch((err) => {

        console.log("❌ MongoDB Connection Error:", err.message);

    });

// ================= PREDICT ROUTE =================
app.post("/predict", async (req, res) => {

    try {

        const { text } = req.body;

        // ================= VALIDATION =================
        if (!text || text.trim() === "") {

            return res.status(400).json({
                success: false,
                error: "Text is required"
            });

        }

        console.log("📥 Incoming Text:", text);

        // ================= SIMPLE AI DETECTION =================
        const lowerText = text.toLowerCase();

        let prediction = "REAL";
        let confidence = 95;

        if (
            lowerText.includes("free") ||
            lowerText.includes("won") ||
            lowerText.includes("click below") ||
            lowerText.includes("claim now") ||
            lowerText.includes("lottery") ||
            lowerText.includes("5 lakhs") ||
            lowerText.includes("urgent") ||
            lowerText.includes("limited offer")
        ) {

            prediction = "FAKE / SCAM";
            confidence = 98;

        }

        // ================= RESULT =================
        const result = {
            success: true,
            prediction,
            confidence
        };

        console.log("🤖 Prediction Result:", result);

        // ================= SAVE TO DATABASE =================
        try {

            await Prediction.create({
                text,
                prediction,
                confidence
            });

            console.log("✅ Prediction Saved");

        } catch (dbErr) {

            console.log("⚠️ Database Save Error:", dbErr.message);

        }

        // ================= RESPONSE =================
        return res.status(200).json(result);

    } catch (error) {

        console.log("❌ Predict Route Error:", error.message);

        return res.status(500).json({
            success: false,
            error: "Internal Server Error"
        });

    }

});

// ================= HISTORY ROUTE =================
app.get("/history", async (req, res) => {

    try {

        const history = await Prediction.find()
            .sort({ createdAt: -1 })
            .limit(10);

        return res.status(200).json({
            success: true,
            data: history
        });

    } catch (error) {

        return res.status(500).json({
            success: false,
            error: error.message
        });

    }

});

// ================= STATS ROUTE =================
app.get("/stats", async (req, res) => {

    try {

        const total = await Prediction.countDocuments();

        const fake = await Prediction.countDocuments({
            prediction: "FAKE / SCAM"
        });

        const real = total - fake;

        return res.status(200).json({
            success: true,
            total,
            fake,
            real
        });

    } catch (error) {

        return res.status(500).json({
            success: false,
            error: error.message
        });

    }

});

// ================= 404 ROUTE =================
app.use((req, res) => {

    res.status(404).json({
        success: false,
        error: "Route Not Found"
    });

});

// ================= START SERVER =================
const PORT = process.env.PORT || 5001;

app.listen(PORT, "0.0.0.0", () => {

    console.log(`🚀 Server Running On Port ${PORT}`);

});