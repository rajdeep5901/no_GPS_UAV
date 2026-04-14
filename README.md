# 🚁 No-GPS-UAV  
### Autonomous UAV Navigation in GPS-Denied Environments  

![Status](https://img.shields.io/badge/Status-Active%20Development-blue)
![Hardware Tested](https://img.shields.io/badge/Hardware-Tested-green)
![ROS2](https://img.shields.io/badge/Future-ROS2-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 🌍 Overview

**No-GPS-UAV** is a research-driven project focused on building a fully autonomous UAV capable of operating in **GPS-denied environments**.

It combines:
- ✈️ **Dead Reckoning Flight Control** (real hardware tested)  
- 🧠 **Semantic AI Navigation System** (vision + memory driven)  

> 🎯 Goal: Enable drones to navigate using **perception + reasoning**, not GPS.

---

## ⚡ Key Highlights

- 🚁 Real drone flight without GPS (Pixhawk + RPi5)
- 🧠 Vision-Language Model integration (Moondream2)
- 🗂️ Persistent semantic memory (SQLite + embeddings)
- 🔁 Object-based navigation ("go to chair")
- 🧭 Return-to-home via visual reasoning
- 🔌 MAVLink-based control pipeline
- 🚀 Future-ready for ROS2 + VIO integration

---

## 🧩 System Modules

### 1️⃣ Dead Reckoning Flight *(Hardware Tested)*

- IMU-based stabilization  
- Barometer altitude hold  
- MAVLink RC override control  
- Fully executed on real drone  

---

### 2️⃣ Drone Brain Continuum *(AI Layer)*

⚠️ Currently tested on laptop (webcam simulation)

- Vision-language understanding  
- Semantic memory formation  
- Object prototype learning  
- Navigation via natural concepts  

---

## 🧠 System Architecture


---

## 🚀 Quick Start
### 1️⃣ Train Semantic Memory (Run Once)
- python teach_memory.py
  Generates:
  - drone_memory.db
  - memory_vectors/

### 2️⃣ Run AI Navigation
- python drone_brain_continuum.py

---

## 🛠️ Setup
### 💻 AI System (Laptop)
  - pip install torch torchvision transformers opencv-python
  - pillow numpy

### 🍓 Flight System (Raspberry Pi)
  - sudo apt update
  - sudo apt install python3-pip
  - pip install pymavlink

### 🔗 MAVLink Configuration
  - Port: /dev/ttyAMA0
  - Baud Rate: 57600

### ✈️ Flight Execution Pipeline
  🚨 Emergency Stop
  - Press:
    - l + ENTER

---

## 🔮 Future Roadmap
  - Visual-Inertial Odometry (VIO)
  - Full onboard AI inference
  - Real-world semantic navigation
  - ROS2-based modular system
  - Multi-object reasoning & planning

---

## 🧭 Future Architecture (ROS2)
### 📊 Tech Stack
  - Flight Control: Pixhawk / ArduPilot
  - Companion Compute: Raspberry Pi 5 + AI hat
  - AI Models: Moondream2, Transformers
  - Vision: OpenCV
  - Memory: SQLite + Embeddings
  - Comm Protocol: MAVLink
  - Future: ROS2 Humble

---

## 📄 Documentation
  📁 Project Drive: https://drive.google.com/drive/folders/1fiI5WlGwTdZvgnb4nc8yaLPC7RyI-fD6

---

## ⚠️ Disclaimer
  - ✅ Dead Reckoning → Tested on real drone
  - ⚠️ AI Navigation → Simulation only
  Hardware-AI integration is currently in progress.

---

## 🤝 Contributing
  - This is an evolving research project. Contributions, ideas, and collaborations are welcome.

---

## ⭐ Support
  - If you find this project interesting:

    - 👉 Star the repo
    - 👉 Share with others in robotics / AI

---

## 📜 License
  - MIT License
