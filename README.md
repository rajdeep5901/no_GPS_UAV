No-GPS-UAV

📌 Project Overview



This repository contains research and development work for a GPS-denied autonomous UAV system.



The project currently consists of two independent software tracks.



🧩 1. Dead Reckoning Flight (REAL DRONE TESTED)



Demonstration of controlled flight without GPS.



Goal



Prove that basic no-GPS flight is possible using:



IMU stabilization



Barometer altitude hold



RC override commands from companion computer



Hardware Used



Flight Controller: Pixhawk / PX4 Hardware FC



Firmware: ArduPilot (fmuv3-dev)



Companion Computer: Raspberry Pi 5 (16GB)



OS: Ubuntu 24.04 LTS (Headless)



Communication: MAVLink via serial connection



Calibration Completed



✅ Accelerometer



✅ Gyroscope



✅ Radio calibration



Parameter Configuration



No-GPS parameters configured using:



Mission Planner (Preferred)



QGroundControl (Alternative)



🧠 2. Drone Brain Continuum (LAPTOP TESTED)



⚠️ WARNING: Not yet tested on real drone hardware.



This system simulates an intelligent semantic navigation layer.



Currently tested using a laptop webcam in a local execution environment.



Core Capabilities



Vision-language object understanding (Moondream2)



Semantic memory storage (SQLite)



Object prototype learning



360° environment scan



Semantic navigation (e.g., "go to chair")



Visual return-to-home logic



🧠 Software Architecture

&nbsp;                   +---------------------+

&nbsp;                   |   Memory Teacher    |

&nbsp;                   |  (teach\_memory.py)  |

&nbsp;                   +----------+----------+

&nbsp;                              |

&nbsp;                              v

&nbsp;                   SQLite + Embedding Vectors

&nbsp;                              |

&nbsp;                              v

&nbsp;                   +----------------------+

&nbsp;                   | Drone Brain Continuum|

&nbsp;                   | drone\_brain\_continuum|

&nbsp;                   +----------------------+

&nbsp;                              |

&nbsp;                              v

&nbsp;                   Vision + Semantic Logic

📂 Repository Structure

No-GPS-UAV/

│

├── dead\_reckoning.py        # Hardware flight logic

│

├── drone\_brain\_continuum.py # Semantic navigation logic

├── teach\_memory.py          # Training script

│

├── drone\_memory.db          # (Auto-generated) Database

├── memory\_vectors/          # (Auto-generated) Embeddings folder

│

└── README.md

⚠️ IMPORTANT EXECUTION ORDER

Step 1 — Teach Memory (RUN ONCE)



You must run this first to generate the necessary database and vector files.



python teach\_memory.py



This will:



Create SQLite database (drone\_memory.db)



Generate object prototype embeddings (memory\_vectors/)



Step 2 — Run Drone Brain



Once the memory is generated, run the main brain script.



python drone\_brain\_continuum.py



❌ Note:

Do NOT run teach\_memory.py repeatedly after the initial training unless you want to reset or update memory.



💾 Auto-Generated Files



When running the semantic memory system, the following files are created:



drone\_memory.db → Stores objects, prototypes, and event logs



memory\_vectors/\*.npy → Contains learned visual embeddings



🛠️ Setup \& Installation

💻 Laptop Setup (Semantic Memory System)



Required Python Version: Python 3.10+



Install dependencies:



pip install torch torchvision

pip install transformers

pip install opencv-python

pip install pillow

pip install numpy

🍓 Raspberry Pi Setup (Dead Reckoning)



OS: Ubuntu 24.04 LTS (Headless)



Install MAVLink dependencies:



sudo apt update

sudo apt install python3-pip

pip install pymavlink

🔗 MAVLink Connection Settings



Port: /dev/ttyAMA0



Baud Rate: 57600



✈️ Dead Reckoning Flight Logic



The dead\_reckoning.py script executes the following sequence:



Connect to Flight Controller



Wait for heartbeat



Set ALT\_HOLD mode



Arm drone



Takeoff using RC override



Forward motion (dead reckoning)



Hover



Switch to LAND mode



🚨 Emergency Landing Trigger



Press:



l + ENTER



to trigger an immediate landing.



🚧 Future Architecture (ROS Integration)



The current system relies on standalone Python scripts.



Future migration will introduce ROS2 Humble.



Expected Changes

Feature	Current (Python Scripts)	Future (ROS2)

Control Logic	Direct script execution	Distributed ROS2 nodes

Communication	Serial / Pymavlink	Micro-XRCE-DDS / MAVROS

Vision	OpenCV loop	vision\_node

Navigation	Hardcoded logic	navigation\_node

Planned Flow

Camera → ROS Vision Node

&nbsp;      → Semantic Memory Node

&nbsp;      → Navigation Planner

&nbsp;      → MAVROS → Flight Controller

🎯 Upcoming Integration



Visual-Inertial Odometry (VIO)



Real drone semantic navigation



Onboard AI acceleration



📄 Documentation



Detailed documentation, research logs, and system design diagrams are available in the project drive.



Google Drive: [Link to Documentation](https://drive.google.com/drive/folders/1fiI5WlGwTdZvgnb4nc8yaLPC7RyI-fD6)



⚠️ Disclaimer



Dead Reckoning: Tested on real drone hardware (Pixhawk / RPi5)



Drone Brain Continuum: Tested only with laptop webcam / simulation



Hardware integration is still pending.

