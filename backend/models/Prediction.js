const mongoose = require("mongoose");

const PredictionSchema = new mongoose.Schema({
    text: String,
    prediction: String,
    confidence: Number,
    createdAt: {
        type: Date,
        default: Date.now
    }
});

module.exports = mongoose.model("Prediction", PredictionSchema);