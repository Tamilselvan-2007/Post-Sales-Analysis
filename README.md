# 🛠️ Post-Sales PCB Diagnostic System  
**AI-Powered Visual Inspection for Electronics After-Sales Support**

---

## 📌 Overview
The **Post-Sales PCB Diagnostic System** is a web-based AI application designed to assist technicians in identifying **missing**, **burnt**, and **faulty components** on printed circuit boards (PCBs) after sales or during servicing.

It uses **YOLO-based computer vision models** deployed on a **Flask backend**, providing fast, automated diagnostics through a simple web interface.

---

## 🎯 Key Objectives
- Reduce manual inspection time for PCBs  
- Improve fault detection accuracy  
- Assist post-sales service teams and technicians  
- Provide a scalable, cloud-deployable diagnostic tool  

---

## 🚀 Features
- 🔍 **Missing Components Detection**
- 🔥 **Burnt Components Detection**
- 🖼️ Image upload and AI-based inference
- 📊 JSON-based detection results
- 🌐 Web UI for easy usage
- ☁️ Cloud-deployed backend (Render)

---

## 🧠 Tech Stack

### Backend
- **Python**
- **Flask**
- **Flask-SocketIO**
- **Gunicorn + Eventlet**
- **Ultralytics YOLO**
- **OpenCV**
- **NumPy**

### Frontend
- **HTML**
- **CSS**
- **JavaScript**

### Deployment
- **Render (Web Service)**
- **GitHub (Version Control)**

---

## 📂 Project Structure
Post-Sales-Analysis/
│
├── PCB_BACK_END/
│ ├── app.py
│ ├── requirements.txt
│ ├── model/
│ │ ├── missing.pt
│ │ ├── burnt.pt
│ │ ├── load_models.py
│ │ └── config.py
│ ├── routes/
│ │ ├── detect_routes.py
│ │ ├── upload_routes.py
│ │ └── debug_routes.py
│ ├── utils/
│ ├── static/
│ └── templates/
│
└── README.md


