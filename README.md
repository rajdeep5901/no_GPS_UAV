# No-GPS-UAV
## 📌 Project Overview
This repository contains research and development work for a GPS-denied autonomous UAV system.
The project currently consists of two independent software tracks:

---

## 🧩 1. Dead Reckoning Flight (REAL DRONE TESTED)
**Demonstration of controlled flight without GPS.**

### Goal
Prove that basic no-GPS flight is possible using:
* IMU stabilization
* Barometer altitude hold
* RC override commands from companion computer

### Hardware Used
* **Flight Controller:** Pixhawk / PX4 Hardware FC
* **Firmware:** ArduPilot (fmuv3-dev)
* **Companion Computer:** Raspberry Pi 5 (16GB)
* **OS:** Ubuntu 24.04 LTS (Headless)
* **Communication:** MAVLink via serial connection

### Calibration Completed
* ✅ Accelerometer
* ✅ Gyroscope
* ✅ Radio calibration

### Parameter Configuration
No-GPS parameters configured using:
* **Mission Planner** (Preferred)
* **QGroundControl** (Alternative)

---

## 🧠 2. Drone Brain Continuum (LAPTOP TESTED)
> **⚠️ WARNING:** Not yet tested on real drone hardware.

This system simulates an intelligent semantic navigation layer. Currently tested using a laptop webcam in a local execution environment.

### Core Capabilities
* Vision-language object understanding (Moondream2)
* Semantic memory storage (SQLite)
* Object prototype learning
* 360° environment scan
* Semantic navigation (e.g., "go to chair")
* Visual return-to-home logic

---

## 🧠 Software Architecture
                    +---------------------+
                    |   Memory Teacher    |
                    |  (teach_memory.py)  |
                    +----------+----------+
                               |
                               v
                    SQLite + Embedding Vectors
                               |
                               v
                    +----------------------+
                    | Drone Brain Continuum|
                    | drone_brain_continuum|
                    +----------------------+
                               |
                               v
                    Vision + Semantic Logic
📂 Repository StructurePlaintextNo-GPS-UAV/
│
├── dead_reckoning.py        # Hardware flight logic
│
├── drone_brain_continuum.py # Semantic navigation logic
├── teach_memory.py          # Training script
│
├── drone_memory.db          # (Auto-generated) Database
├── memory_vectors/          # (Auto-generated) Embeddings folder
│
└── README.md
⚠️ IMPORTANT EXECUTION ORDERStep 1 — Teach Memory (RUN ONCE)You must run this first to generate the necessary database and vector files.Bashpython teach_memory.py
This will:Create SQLite database (drone_memory.db)Generate object prototype embeddings (memory_vectors/)Step 2 — Run Drone BrainOnce the memory is generated, you can run the main brain script.Bashpython drone_brain_continuum.py
❌ NOTE: Do NOT run teach_memory.py repeatedly after the initial training unless you want to reset/update the memory.💾 Auto-Generated FilesWhen running the semantic memory system, the following files are created:drone_memory.db: Stores objects, prototypes, and event logs.memory_vectors/*.npy: Contains learned visual embeddings.🛠️ Setup & Installation💻 Laptop Setup (Semantic Memory System)Required Python Version: Python 3.10+Install Dependencies:Bashpip install torch torchvision
pip install transformers
pip install opencv-python
pip install pillow
pip install numpy
🍓 Raspberry Pi Setup (Dead Reckoning)OS: Ubuntu 24.04 LTS (Headless)Install MAVLink Dependencies:Bashsudo apt update
sudo apt install python3-pip
pip install pymavlink
🔗 MAVLink Connection Settings:Port: /dev/ttyAMA0Baud Rate: 57600✈️ Dead Reckoning Flight LogicThe dead_reckoning.py script executes the following sequence:Connect to FCWait for heartbeatSet ALT_HOLD modeArm droneTakeoff using RC overrideForward motion (dead reckoning)HoverSwitch to LAND mode🚨 Emergency Landing Trigger:Press l + ENTER on the keyboard to trigger an immediate landing.🚧 Future Architecture (ROS Integration)The current system relies on standalone Python scripts. Future migration will introduce ROS2 Humble.Expected ChangesFeatureCurrent (Python Scripts)Future (ROS2)Control LogicDirect script executionDistributed ROS2 NodesCommunicationSerial / PymavlinkMicro-XRCE-DDS / MAVROSVisionOpenCV Loopvision_nodeNavigationHardcoded logicnavigation_nodePlanned FlowPlaintextCamera → ROS Vision Node
       → Semantic Memory Node
       → Navigation Planner
       → MAVROS → Flight Controller
🎯 Upcoming IntegrationVisual-Inertial Odometry (VIO)Real drone semantic navigationOnboard AI acceleration📄 DocumentationDetailed documentation, research logs, and system design diagrams are available in the project drive.Google Drive: Link to Documentation⚠️ DisclaimerDead Reckoning: Tested on real drone hardware (Pixhawk/RPi5).Drone Brain Continuum: Tested ONLY with laptop webcam/simulation. Hardware integration is pending.
Drone Brain Continuum tested only with laptop webcam.

Hardware integration pending.
