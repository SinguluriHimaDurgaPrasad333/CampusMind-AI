import sys
import time

print("Step 1: Importing sentence_transformers...", flush=True)
t0 = time.time()
from sentence_transformers import SentenceTransformer
print(f"Step 1 Complete: Imported in {time.time()-t0:.2f}s", flush=True)

print("Step 2: Initializing SentenceTransformer('all-MiniLM-L6-v2')...", flush=True)
t1 = time.time()
model = SentenceTransformer("all-MiniLM-L6-v2")
print(f"Step 2 Complete: Loaded in {time.time()-t1:.2f}s", flush=True)

print("Step 3: Testing test encoding...", flush=True)
emb = model.encode(["CampusAI university chatbot"])
print(f"Step 3 Complete: Embedding shape {emb.shape}", flush=True)
