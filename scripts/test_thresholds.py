import sys
from pathlib import Path

# Add root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from vector_database import search_similar_chunks

df = pd.read_csv("data/evaluation_questions.csv")
print("Evaluating question distances against ChromaDB:")
answerable_dists = []
unanswerable_dists = []

for idx, row in df.iterrows():
    q_id = row["question_id"]
    ans = str(row["answerable"]).lower() == "true"
    q = row["question"]
    res = search_similar_chunks(q, top_k=1)
    dist = res[0]["distance"] if res else 1.0

    if ans:
        answerable_dists.append(dist)
    else:
        unanswerable_dists.append(dist)

    print(f"{q_id:8s} | Ans: {str(ans):5s} | Dist: {dist:.3f} | {q[:45]}")

print("\n--- Summary Statistics ---")
print(f"Answerable max distance:    {max(answerable_dists):.3f}")
print(f"Answerable mean distance:   {sum(answerable_dists)/len(answerable_dists):.3f}")
print(f"Unanswerable min distance:  {min(unanswerable_dists):.3f}")
print(f"Unanswerable mean distance: {sum(unanswerable_dists)/len(unanswerable_dists):.3f}")
