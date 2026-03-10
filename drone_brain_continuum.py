
import cv2
import torch
import numpy as np
import time
import os
import sqlite3
import uuid
import random
import re

from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image

# --- CONFIGURATION ---
MODEL_ID = "vikhyatk/moondream2" 
REVISION = "2024-03-06"
DB_PATH = "drone_memory.db"

class ContinuumDatabase:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.setup_tables()
        if not os.path.exists("memory_vectors"): os.makedirs("memory_vectors")
        
        self.orb = cv2.ORB_create(nfeatures=1000)
        self.dest_panorama = {} 

    def setup_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS objects (
            id TEXT, label TEXT, pos_x REAL, pos_y REAL, timestamp REAL, embedding_file TEXT
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS prototypes (
            id TEXT, class_label TEXT, embedding_file TEXT
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS events (
            id TEXT, event_type TEXT, description TEXT, angle REAL, timestamp REAL
        )''')
        self.conn.commit()

    def log_event(self, event_type, description, angle=None):
        if angle is None: angle = -1 
        self.cursor.execute("INSERT INTO events VALUES (?, ?, ?, ?, ?)", 
                           (str(uuid.uuid4()), event_type, description, angle, time.time()))
        self.conn.commit()

    # --- VISUAL MEMORY ---
    def save_scan_slice(self, location_type, angle, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        kp, des = self.orb.detectAndCompute(gray, None)
        if des is None: return
        if location_type == 'DEST':
            self.dest_panorama[angle] = des
            
    def compare_multiview(self, current_angle, current_frame):
        ref_des = self.dest_panorama.get(current_angle)
        if ref_des is None: return 0
        gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        _, curr_des = self.orb.detectAndCompute(gray, None)
        if curr_des is None: return 0
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(curr_des, ref_des)
        return len(matches)

    # --- VLM RECOGNITION ---
    def identify_object(self, img_emb):
        try:
            self.cursor.execute("SELECT class_label, embedding_file FROM prototypes")
            prototypes = self.cursor.fetchall()
            best_score, best_label = -1, "unknown"
            u_vec = img_emb.flatten()
            n_u = np.linalg.norm(u_vec) + 1e-10
            for label, path in prototypes:
                if not os.path.exists(path): continue
                p_vec = np.load(path).flatten()
                score = np.dot(u_vec, p_vec) / (n_u * (np.linalg.norm(p_vec)+1e-10))
                if score > best_score: best_score, best_label = score, label
            return (best_label, best_score) if best_score > 0.4 else ("unknown", 0.0)
        except: return "unknown", 0.0

    def add_object_to_map(self, label, angle, emb):
        self.cursor.execute("INSERT INTO objects VALUES (?, ?, ?, ?, ?, ?)", 
                           (str(uuid.uuid4()), label, angle, 0, time.time(), "NONE"))
        self.conn.commit()

    def get_object_angle(self, label):
        self.cursor.execute("SELECT pos_x FROM objects WHERE label LIKE ?", (f"%{label}%",))
        res = self.cursor.fetchone()
        return res[0] if res else None

    # --- INTELLIGENT DEBRIEF & MID-FLIGHT QUERY ---
    def query_memory(self, query_text):
        query_text = query_text.lower()
        
        # 1. SUMMARY
        if "summarize" in query_text or "what happened" in query_text:
            self.cursor.execute("SELECT event_type, description FROM events ORDER BY timestamp ASC")
            events = self.cursor.fetchall()
            if not events: return "   Mission Log is empty."
            report = "\n   [MISSION SUMMARY]:\n"
            for etype, desc in events:
                report += f"   - [{etype}]: {desc}\n"
            return report

        # 2. OBJECT SEARCH ("Do you see X?")
        match = re.search(r'(?:see|find|there)\s+(?:a|an)\s+(\w+)', query_text)
        if match:
            target = match.group(1)
            self.cursor.execute("SELECT pos_x, timestamp FROM objects WHERE label LIKE ?", (f"%{target}%",))
            results = self.cursor.fetchall()
            
            if results:
                count = len(results)
                last_angle = results[-1][0]
                return f"FOUND: Yes. I see {count} '{target}'(s). Last known at {last_angle}°."
            else:
                return "NOT_FOUND" # Special code to trigger Active Look
            
        # 3. OPEN ENDED ("What do you see?")
        if "what do you see" in query_text:
            # Get objects seen in last 30 seconds
            cutoff = time.time() - 30
            self.cursor.execute("SELECT label, pos_x FROM objects WHERE timestamp > ?", (cutoff,))
            recent = self.cursor.fetchall()
            if recent:
                desc = ", ".join([f"{r[0]} at {r[1]}°" for r in recent])
                return f"   [CURRENT VIEW]: In the last 30s, I have seen: {desc}."
            else:
                return "NOT_FOUND" # Trigger Scan to see NOW
            
        return "   [SYSTEM] Unknown Query."

    def generate_recommendations(self):
        self.cursor.execute("SELECT angle, description FROM events WHERE event_type IN ('ABORT', 'THREAT_IDENTIFIED')")
        risks = self.cursor.fetchall()
        report = "\n   [ADVICE]:\n"
        if risks:
            for ang, desc in risks:
                report += f"   - Avoid {ang}° (History: {desc})\n"
        else:
            report += "   - All explored paths seem safe.\n"
        return report

class DroneBrain:
    def __init__(self):
        print(">> [SYSTEM] Booting Drone Brain (Interactive)...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = AutoModelForCausalLM.from_pretrained(MODEL_ID, trust_remote_code=True, revision=REVISION).to(self.device)
        self.memory = ContinuumDatabase()
        self.cap = cv2.VideoCapture(0)
        self.width, self.height = 640, 480
        self.path_history = [] 

    '''def perform_360_scan(self, location_name, save_to_memory=False):
        print(f"\n>> [SCAN] Initiating 360° Scan ({location_name})...")
        scan_angles = [0, 90, 180, 270] 
        scene_match_scores = []

        for angle in scan_angles:
            input(f"   -> Rotate Laptop to {angle}° and Press ENTER...")
            for _ in range(5): self.cap.read()
            ret, frame = self.cap.read()
            
            if ret:
                frame = cv2.resize(frame, (self.width, self.height))
                
                # VLM Analysis
                img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                with torch.no_grad():
                    emb = self.model.encode_image(img_pil).cpu().detach().numpy()
                lbl, _ = self.memory.identify_object(emb)
                
                if lbl != "unknown":
                    print(f"      [VLM] Detected '{lbl}' at {angle}°")
                    self.memory.add_object_to_map(lbl, angle, emb)

                if save_to_memory:
                    self.memory.save_scan_slice('DEST', angle, frame)
                elif location_name == "RTH_START_CHECK":
                    score = self.memory.compare_multiview(angle, frame)
                    scene_match_scores.append(score)

        if location_name == "RTH_START_CHECK":
            return sum(scene_match_scores) / len(scene_match_scores)
        return 0'''
        
    def perform_360_scan(self, location_name, save_to_memory=False):
        print(f"\n>> [SCAN] Initiating 360° Scan ({location_name})...")
        scan_angles = [0, 90, 180, 270] 
        scene_match_scores = []

        for angle in scan_angles:
            input(f"   -> Rotate Laptop to {angle}° and Press ENTER...")
            for _ in range(5): self.cap.read()
            ret, frame = self.cap.read()
            
            if ret:
                frame = cv2.resize(frame, (self.width, self.height))
                
                # VLM Analysis
                img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                with torch.no_grad():
                    raw_emb = self.model.encode_image(img_pil)
                    # --- THE FIX: Apply the same averaging here ---
                    emb = raw_emb.mean(dim=1).cpu().detach().numpy()
                
                lbl, score = self.memory.identify_object(emb)
                
                if lbl != "unknown":
                    print(f"      [VLM] Detected '{lbl}' (Conf: {score:.2f}) at {angle}°")
                    self.memory.add_object_to_map(lbl, angle, emb)

                if save_to_memory:
                    self.memory.save_scan_slice('DEST', angle, frame)
                elif location_name == "RTH_START_CHECK":
                    score = self.memory.compare_multiview(angle, frame)
                    scene_match_scores.append(score)

        if location_name == "RTH_START_CHECK":
            return sum(scene_match_scores) / len(scene_match_scores)
        return 0

    def check_active_threats(self):
        if random.random() < 0.1: # Reduced chance for demo usability
            print("\n!! [SENSORS] OBSTACLE DETECTED !!")
            return True
        return False

    def handle_midflight_interaction(self):
        """
        PAUSES flight to answer user questions. 
        If it doesn't know the answer, it LOOKS around.
        """
        print("\n" + "="*40)
        print("   HOVERING - INTERACTIVE MODE")
        print("   (Drone is holding position. Ask a question.)")
        print("="*40)
        
        while True:
            query = input(">> [PILOT] Ask (e.g., 'What do you see?', 'Do you see a bottle?', 'resume'): ")
            
            if query.lower() == 'resume':
                print(">> [SYSTEM] Resuming Mission...")
                break
                
            # 1. Check Memory First
            answer = self.memory.query_memory(query)
            
            # 2. If Memory fails, perform ACTIVE LOOK
            if answer == "NOT_FOUND":
                print(f"   [BRAIN] I don't recall seeing that. Let me look around...")
                self.perform_360_scan("ACTIVE_QUERY_SCAN", save_to_memory=False)
                
                # 3. Check Memory Again (after scan)
                answer = self.memory.query_memory(query)
                if answer == "NOT_FOUND":
                    print("   [BRAIN] Update: I still don't see it after scanning.")
                else:
                    print(f"   [BRAIN] Update: {answer}")
            else:
                # Answer found in existing memory
                print(f"   {answer}")

    def fly_guarded(self, heading, duration_steps=5, mission_phase="MISSION"):
        print(f">> [{mission_phase}] Flying Heading {heading}° (Press Ctrl+C to Interact)...")
        self.memory.log_event("MOVEMENT", f"Transit {heading}°", heading)
        
        try:
            for i in range(duration_steps):
                progress = int((i+1)/duration_steps * 100)
                print(f"   [FLIGHT] Moving... {progress}%", end='\r')
                time.sleep(1)
                
                if self.check_active_threats():
                    print(f"\n!! [EMERGENCY] ABORTING {mission_phase}.")
                    self.perform_semantic_replan()
                    return False 

            print(f"\n>> [{mission_phase}] Leg Complete.")
            return True

        except KeyboardInterrupt:
            # CATCH THE INTERRUPT -> GO TO INTERACTIVE MODE -> THEN RESUME
            self.handle_midflight_interaction()
            print(f">> [SYSTEM] Resuming flight leg...")
            # Recursive call to finish the remaining steps would be better, 
            # but for demo, we assume the pilot just resumes/lands.
            return True 

    '''def execute_mission(self, prompt):
        print(f"\n>> [MISSION] Processing: '{prompt}'")
        self.memory.log_event("USER_PROMPT", f"Command: {prompt}")
        
        target_name = next((w for w in prompt.split() if self.memory.get_object_angle(w) is not None), None)
        if not target_name:
            print("!! [ERROR] Target unknown. Please scan first.")
            return

        heading = self.memory.get_object_angle(target_name)
        success = self.fly_guarded(heading, duration_steps=5, mission_phase="OUTBOUND")
        
        if success:
            self.path_history.append(heading)
            self.memory.log_event("ARRIVAL", f"Arrived at {target_name}", heading)
            print("\n>> [Status] Destination Reached.")
            
            # Prompt for check at destination
            print(">> [SYSTEM] At destination. (Press Ctrl+C now if you want to ask questions before I scan).")
            try:
                time.sleep(2)
                self.perform_360_scan("DESTINATION", save_to_memory=True)
            except KeyboardInterrupt:
                self.handle_midflight_interaction()
                self.perform_360_scan("DESTINATION", save_to_memory=True)'''
    
    def execute_mission(self, prompt):
        print(f"\n>> [MISSION] Processing: '{prompt}'")
        self.memory.log_event("USER_PROMPT", f"Command: {prompt}")
        
        # 1. Parse target from prompt
        target_name = next((w for w in prompt.split() if self.memory.get_object_angle(w) is not None), None)
        
        # 2. If target is NOT in memory, trigger a scan to find it
        if not target_name:
            # Try to guess the target word even if we don't know the location
            # (Simple heuristic: take the last word of the prompt as the target for now)
            probable_target = prompt.split()[-1] 
            print(f"   [BRAIN] I don't know where '{probable_target}' is. Initiating search...")
            
            self.perform_360_scan("EXPLORATION_SCAN", save_to_memory=True)
            
            # Check memory again after the scan
            if self.memory.get_object_angle(probable_target):
                target_name = probable_target
            else:
                # Try finding any word from prompt in memory again
                target_name = next((w for w in prompt.split() if self.memory.get_object_angle(w) is not None), None)

            if not target_name:
                print("!! [ABORT] Target still not found after 360° scan.")
                return

        # 3. Fly to Target
        heading = self.memory.get_object_angle(target_name)
        success = self.fly_guarded(heading, duration_steps=5, mission_phase="OUTBOUND")
        
        if success:
            self.path_history.append(heading)
            self.memory.log_event("ARRIVAL", f"Arrived at {target_name}", heading)
            print("\n>> [Status] Destination Reached.")
            
            print(">> [SYSTEM] At destination. (Press Ctrl+C to interact).")
            try:
                time.sleep(2)
                self.perform_360_scan("DESTINATION", save_to_memory=True)
            except KeyboardInterrupt:
                self.handle_midflight_interaction()
                self.perform_360_scan("DESTINATION", save_to_memory=True)

    def return_to_base_advanced(self):
        print("\n" + "="*50)
        print(">> [MISSION] PHASE 3: GUARDED RETURN TO HOME")
        print("="*50)
        
        if not self.path_history: return
        arrival_heading = self.path_history[-1] 
        return_heading = (arrival_heading + 180) % 360
        
        print(f">> [NAV] Return Heading: {return_heading}°")
        input(f"   -> Rotate to {return_heading}° & Enter...")

        avg_match = self.perform_360_scan("RTH_START_CHECK", save_to_memory=False)
        if avg_match < 20:
            print("!! [ALERT] ENVIRONMENT CHANGED.")
            self.perform_semantic_replan()
            return

        print(">> [DECISION] Returning...")
        self.fly_guarded(return_heading, duration_steps=5, mission_phase="RETURN")
        print(">> [SUCCESS] Landed.")

    def perform_semantic_replan(self):
        print("\n>> [REPLANNER] Scanning for new path...")
        self.perform_360_scan("EMERGENCY_REPLAN", save_to_memory=False)
        print(">> [ACTION] Executing Safe Escape...")
        time.sleep(2)

if __name__ == "__main__":
    bot = DroneBrain()
    try:
        print(">> [SETUP] Ready.")
        
        # 1. Mission
        prompt = input("\n>> [USER] Where to? (e.g. 'go to chair'): ")
        bot.execute_mission(prompt)
        
        # 2. Return
        bot.return_to_base_advanced()
        
    except KeyboardInterrupt:
        # Global catch if they cancel at top level
        bot.handle_midflight_interaction()
    finally: bot.cap.release()
