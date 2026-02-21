# No-GPS-UAV
📌 Project Overview

This repository contains research and development work for a GPS-denied autonomous UAV system.

The project currently consists of two independent software tracks:

🧩 1. Dead Reckoning Flight (REAL DRONE TESTED)

Demonstration of controlled flight without GPS using:

PX4 hardware flight controller

ArduPilot firmware (fmuv3-dev)

Raspberry Pi 5 companion computer

MAVLink communication via pymavlink

Goal

Prove that basic no-GPS flight is possible using:

IMU stabilization

Barometer altitude hold

RC override commands from companion computer

Hardware Used

Pixhawk / PX4 Hardware FC

ArduPilot firmware (fmuv3-dev)

Raspberry Pi 5 (16GB)

Ubuntu 24.04 LTS (Headless)

MAVLink serial connection

Calibration Completed

Accelerometer

Gyroscope

Radio calibration

Parameter Configuration

No-GPS parameters configured using:

Mission Planner (Preferred)

QGroundControl (alternative)

🧠 2. Drone Brain Continuum (LAPTOP TESTED)

⚠️ Not yet tested on real drone hardware.

This system simulates an intelligent semantic navigation layer.

Tested using:

Laptop camera (webcam)

Local execution environment

Core Capabilities

Vision-language object understanding (Moondream2)

Semantic memory storage (SQLite)

Object prototype learning

360° environment scan

Semantic navigation ("go to chair")

Visual return-to-home logic

🧠 Software Architecture
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
📂 Repository Structure
No-GPS-UAV/
│
├── dead_reckoning.py
│
├── drone_brain_continuum.py
├── teach_memory.py
│
├── drone_memory.db          (auto generated)
├── memory_vectors/          (auto generated)
│
└── README.md
⚠️ IMPORTANT EXECUTION ORDER
Step 1 — Teach Memory (RUN ONCE)
python teach_memory.py

This will:

Create SQLite database

Generate object prototype embeddings

Create:

drone_memory.db
memory_vectors/
Step 2 — Run Drone Brain
python drone_brain_continuum.py

This uses previously learned memory.

After initial training:

❌ Do NOT run teach_memory repeatedly
✔ Run only drone_brain_continuum.py

💾 Auto-Generated Files

When running semantic memory system:

Database
drone_memory.db

Stores:

Objects

Prototypes

Events

Embedding Vectors
memory_vectors/*.npy

Contains learned visual embeddings.

💻 Laptop Setup (Semantic Memory System)
Required Python Version
Python 3.10+
Install Dependencies
pip install torch torchvision
pip install transformers
pip install opencv-python
pip install pillow
pip install numpy
🍓 Raspberry Pi Setup (Dead Reckoning)
OS
Ubuntu 24.04 LTS (Headless)
Install MAVLink Dependencies
sudo apt update
sudo apt install python3-pip
pip install pymavlink
🔗 MAVLink Connection

Serial connection:

/dev/ttyAMA0
baud = 57600
✈️ Dead Reckoning Flight Logic

Sequence:

Connect to FC

Wait for heartbeat

Set ALT_HOLD mode

Arm drone

Takeoff using RC override

Forward motion (dead reckoning)

Hover

LAND mode

Emergency landing:

Press l + ENTER
🚧 Future Architecture (ROS Integration)

Current system is non-ROS, but future migration will introduce ROS2.

Expected Changes
Current
Python scripts directly controlling logic
Future (ROS)
ROS2 Nodes:

vision_node
semantic_memory_node
navigation_node
flight_interface_node
Benefits

Sensor synchronization

Modular pipeline

VIO integration

Real-time communication

Easier scaling

Planned Flow
Camera → ROS Vision Node
       → Semantic Memory Node
       → Navigation Planner
       → MAVROS → Flight Controller
🎯 Upcoming Integration

Visual-Inertial Odometry (VIO)

Real drone semantic navigation

ROS2 migration

Onboard AI acceleration

📄 Documentation

Detailed documentation, research logs, and system design diagrams are provided here:

Google Drive:
<ADD_LINK_HERE>
⚠️ Disclaimer

Dead Reckoning tested on real drone hardware.

Drone Brain Continuum tested only with laptop webcam.

Hardware integration pending.
