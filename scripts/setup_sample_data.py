"""
Script to create sample documents across PDF, DOCX, TXT, CSV, JSON
and mirror them into data/sample_documents/
"""

import shutil
from pathlib import Path
import docx

doc_dir = Path("data/documents")
sample_dir = Path("data/sample_documents")
doc_dir.mkdir(parents=True, exist_ok=True)
sample_dir.mkdir(parents=True, exist_ok=True)

# 1. Enrich DOCX
doc = docx.Document()
doc.add_heading("OFFICIAL UNIVERSITY CIRCULAR: MID-TERM EXAM SCHEDULE & RULES", level=1)
doc.add_paragraph("Circular Code: CIR-EXAM-2025-09")
doc.add_paragraph("Issued By: Office of the Controller of Examinations")
doc.add_paragraph(
    "All registered students are hereby notified that the Fall semester mid-term theory "
    "examinations commence promptly at 09:30 AM. Reporting time is 09:00 AM. Hall tickets "
    "must be downloaded from the university ERP portal 3 days prior. Smart watches and "
    "programmable calculators are strictly prohibited in the examination hall."
)
doc.save("data/documents/Official_University_Notice_2025.docx")

# 2. CSV
csv_content = (
    "day,meal,timing,menu_items\n"
    "Monday,Breakfast,07:30 AM - 09:00 AM,Idli Sambar Chutney Tea Coffee\n"
    "Monday,Lunch,12:30 PM - 02:00 PM,Steamed Rice Dal Tadka Paneer Butter Masala Chapati Salad\n"
    "Monday,Dinner,07:30 PM - 09:30 PM,Jeera Rice Mixed Dal Seasonal Vegetable Roti Kheer\n"
    "Sunday,Special Lunch,12:30 PM - 02:30 PM,Vegetable Biryani or Chicken Biryani Raitha Gulab Jamun\n"
)
with open("data/documents/Campus_Hostel_Mess_Menu_and_Timings.csv", "w", encoding="utf-8") as f:
    f.write(csv_content)

# 3. JSON
json_content = """{
  "academic_year": "2025-2026",
  "fee_structure": {
    "btech_tuition_per_semester": 95000,
    "hostel_occupancy_dual": 42000,
    "hostel_occupancy_single": 55000,
    "mess_annual_advance": 38000,
    "caution_deposit_refundable": 10000
  },
  "payment_modes": ["Online ERP Netbanking", "NEFT/RTGS", "UPI Portal"],
  "note": "SAMPLE DATA — FOR DEMONSTRATION ONLY"
}"""
with open("data/documents/University_Fee_Structure_2025.json", "w", encoding="utf-8") as f:
    f.write(json_content)

# Copy all to sample_documents
for f in doc_dir.glob("*.*"):
    if f.is_file():
        shutil.copy2(f, sample_dir / f.name)

print("Sample documents created and mirrored successfully!")
