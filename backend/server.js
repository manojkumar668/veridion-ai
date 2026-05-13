require("dotenv").config();

const express = require("express");
const cors = require("cors");
const nodemailer = require("nodemailer");
const path = require("path");

const connectDB = require("./config/db");

const app = express();

/* ================= MIDDLEWARE ================= */
app.use(cors({ origin: "*", methods: ["GET", "POST"] }));
app.use(express.json());

/* ================= STATIC FILES ================= */
app.use(express.static(path.join(__dirname, "public"), {
    index: false
}));

/* ================= ROUTES ================= */

// 🔐 LOGIN PAGE
app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "public", "login.html"));
});

// 🔐 OTP PAGE
app.get("/otp", (req, res) => {
    res.sendFile(path.join(__dirname, "public", "otp.html"));
});

/* =======================================================
   🚀 IMPORTANT FIX
   /chat ALWAYS LOADS index.html
======================================================= */
app.get("/chat", (req, res) => {
    res.sendFile(path.join(__dirname, "public", "index.html"));
});

/* ================= DATABASE ================= */
connectDB()
    .then(() => console.log("✅ MongoDB Connected"))
    .catch(err => console.log("❌ DB Error:", err.message));

/* ================= OTP STORE ================= */
let otpStore = {};

/* ================= EMAIL CONFIG ================= */
const transporter = nodemailer.createTransport({
    service: "gmail",
    auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS
    }
});

/* ================= SEND OTP ================= */
app.post("/send-otp", async (req, res) => {
    try {
        let { email } = req.body;

        if (!email) {
            return res.json({
                success: false,
                message: "Email required"
            });
        }

        email = email.trim().toLowerCase();

        const otp = Math.floor(100000 + Math.random() * 900000);

        otpStore[email] = otp;

        console.log("📩 EMAIL:", email);
        console.log("🔐 OTP:", otp);

        await transporter.sendMail({
            from: process.env.EMAIL_USER,
            to: email,
            subject: "Veridion AI OTP",
            text: `Your OTP is ${otp}`
        });

        return res.json({ success: true });

    } catch (err) {
        console.log("MAIL ERROR:", err);

        return res.status(500).json({
            success: false,
            message: "Server error"
        });
    }
});

/* ================= VERIFY OTP ================= */
app.post("/verify-otp", (req, res) => {
    let { email, otp } = req.body;

    if (!email || !otp) {
        return res.json({ success: false });
    }

    email = email.trim().toLowerCase();

    if (
        otpStore[email] &&
        String(otpStore[email]) === String(otp)
    ) {
        delete otpStore[email];

        return res.json({
            success: true
        });
    }

    return res.json({
        success: false
    });
});

/* ================= FAKE DETECTION ================= */
app.post("/predict", (req, res) => {
    const text = req.body.text || "";

    if (text.toLowerCase().includes("win")) {
        return res.json({
            prediction: "FAKE"
        });
    }

    return res.json({
        prediction: "REAL"
    });
});

/* ================= START SERVER ================= */
const PORT = process.env.PORT || 5000;

app.listen(PORT, "0.0.0.0", () => {
    console.log(`🚀 Server running on port ${PORT}`);
});