# veridion-ai eridion AI – Fake News & Scam Detection System

An AI-powered web application that detects whether a given text is FAKE / SCAM or REAL, built using Machine Learning + Full Stack Web Development
 Live Demo
 Frontend: https://boisterous-frangollo-f28ba5.netlify.app
 Backend: https://veridion-ai.onrender.com
 Features
 Fake news & scam message detection
 Machine Learning model (TF-IDF + Classifier)
 Real-time API response
 Voice input support (Web Speech API)
💬 Chat-style AI interface
 History tracking
Light/Dark mode UI
Fully deployed (Netlify + Render + MongoDB)
Tech Stack
Frontend:
HTML
CSS
JavaScript
Netlify (Hosting)
Backend:
Node.js (Express)
Flask (ML API)
MongoDB Atlas
Render (Deployment)
Machine Learning:
Scikit-learn

Project Structure
veridion-ai/
│
├── backend/              # Node.js + API server
├── ml-model/             # Flask ML model
├── frontend/             # UI (HTML, CSS, JS)
│   ├── index.html
│   ├── login.html
│   └── otp.html
├── models/               # Trained ML model files
└── README.md

How It Works
User enters text in UI
Frontend sends request to backend /predict
Backend sends data to ML model
Model predicts:
FAKE / SCAM
REAL
Response sent back to UI
TF-IDF Vectorizer
Logistic Regression / Classification Model
Joblib
