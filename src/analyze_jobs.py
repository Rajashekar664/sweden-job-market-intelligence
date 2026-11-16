
import pandas as pd
from pathlib import Path

# Find the project folder automatically
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Load cleaned job data
csv_path = PROJECT_DIR / "data" / "sweden_jobs_cleaned.csv"
df = pd.read_csv(csv_path)

print("Sweden Job Market Analysis")

# Display first 5 jobs
print(df.head())

# Display total jobs
print("Total jobs:", len(df))
