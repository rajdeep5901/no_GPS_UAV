import os
import cv2
import sqlite3
import numpy as np
import uuid
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image

# --- CONFIGURATION ---
DATASET_PATH = "dataset_objects"
DB_PATH = "drone_memory.db"
MODEL_ID = "vikhyatk/moondream2"
REVISION = "2024-03-06"

class MemoryTeacher:
    def __init__(self):
        print("\n" + "="*50)
        print(">> [TEACHER] Initializing VLM (Moondream2)...")
        print("   (First run will download ~3GB model. Please wait.)")
        print("="*50)
        
        # Check for GPU, fallback to CPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f">> Running on: {self.device.upper()}")

        # Load Model
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID, trust_remote_code=True, revision=REVISION
        ).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=REVISION)
        
        # Connect to Database
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.create_knowledge_table()
        
        # Create storage folder for vector files
        if not os.path.exists("memory_vectors"):
            os.makedirs("memory_vectors")

    def create_knowledge_table(self):
        """Creates the 'Prototypes' table to store learned object features."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS prototypes (
                id TEXT PRIMARY KEY,
                class_label TEXT,
                embedding_file TEXT
            )
        ''')
        self.conn.commit()

    '''def encode_and_store(self, label, image_path):
        """Converts an image into a math vector and saves it."""
        try:
            image = Image.open(image_path).convert("RGB")
            
            # --- VLM INFERENCE ---
            with torch.no_grad():
                # Moondream encode_image returns a tensor
                image_embeds = self.model.encode_image(image)
                # Convert to numpy and detach from graph
                vector_numpy = image_embeds.cpu().detach().numpy()

            # Save Vector to Disk
            obj_id = str(uuid.uuid4())
            npy_path = f"memory_vectors/proto_{label}_{obj_id}.npy"
            np.save(npy_path, vector_numpy)

            # Save Metadata to DB
            self.cursor.execute(
                "INSERT INTO prototypes VALUES (?, ?, ?)",
                (obj_id, label, npy_path)
            )
            self.conn.commit()
            print(f"   [LEARNED] Class: '{label}' | Source: {os.path.basename(image_path)}")
            
        except Exception as e:
            print(f"!! [ERROR] Could not process {image_path}: {e}")'''

    def encode_and_store(self, label, image_path):
        """Converts an image into a math vector and saves it."""
        try:
            image = Image.open(image_path).convert("RGB")
            
            # --- VLM INFERENCE ---
            with torch.no_grad():
                # Moondream returns a tensor of shape [1, Sequence_Length, Hidden_Dim]
                image_embeds = self.model.encode_image(image)
                
                # --- THE FIX: Global Average Pooling ---
                # We average across dimension 1 to squash the spatial grid into one vector.
                # This makes the memory "Position Invariant" (center vs corner doesn't matter).
                summary_vector = image_embeds.mean(dim=1)
                
                # Convert to numpy
                vector_numpy = summary_vector.cpu().detach().numpy()

            # Save Vector to Disk
            obj_id = str(uuid.uuid4())
            npy_path = f"memory_vectors/proto_{label}_{obj_id}.npy"
            np.save(npy_path, vector_numpy)

            # Save Metadata to DB
            self.cursor.execute(
                "INSERT INTO prototypes VALUES (?, ?, ?)",
                (obj_id, label, npy_path)
            )
            self.conn.commit()
            print(f"   [LEARNED] Class: '{label}' | Source: {os.path.basename(image_path)}")
            
        except Exception as e:
            print(f"!! [ERROR] Could not process {image_path}: {e}")
            
    def run(self):
        print(f">> [TEACHER] Scanning dataset at '{DATASET_PATH}'...")
        
        if not os.path.exists(DATASET_PATH):
            print(f"!! [ERROR] Folder '{DATASET_PATH}' not found!")
            print("   Please create it and add subfolders (e.g., dataset_objects/chair/)")
            return

        count = 0
        # Walk through folders
        for root, dirs, files in os.walk(DATASET_PATH):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    label = os.path.basename(root) # Folder name is the label
                    full_path = os.path.join(root, file)
                    self.encode_and_store(label, full_path)
                    count += 1
                    
        if count == 0:
            print("!! [WARNING] No images found. Did you add .jpg or .png files?")
        else:
            print(f"\n>> [SUCCESS] Processed {count} images. Drone memory updated.")

if __name__ == "__main__":
    teacher = MemoryTeacher()
    teacher.run()