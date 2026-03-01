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
```
┌──📦Post-Sales-Analysis/                      Root repository
│
├── 📂PCB_BACK_END/                            Main application package
│   │
│   ├── 📂model/                               AI/ML model files & weights
│   │
│   ├── 📂routes/                              Flask API route definitions
│   │
│   ├── 📂static/                              CSS, JS, images & assets
│   │
│   ├── 📂 templates/                          HTML Jinja2 templates
│   │
│   ├── 📂utils/                               Helper functions & utilities
│   │
│   ├── __init__.py                            Package initializer
│   ├── app.py                                 Flask application entry point
│   ├── esp32_firmware.ino                     ESP32 hardware firmware (Arduino)
│   ├── gunicorn.conf.py                       Gunicorn WSGI server config
│   ├── test_detection.py                      PCB defect detection tests
│   └── Procfile                               Process file (Heroku / Cloud)
│
├── .dockerignore                              Files excluded from Docker build
├── Dockerfile                                 Container build instructions (Gunicorn)
├── README.md                                  Project documentation
└── requirements.txt
```
---

## License

This project is developed for educational and hackathon purposes.
