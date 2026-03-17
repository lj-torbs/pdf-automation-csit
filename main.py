import pandas as pd
from generators.logsheet import generate_logsheet

df = pd.read_excel("ClassList-2026-4541.xlsx")

students = df['std_name'].dropna().tolist()

generate_logsheet(students)

print("PDF generated successfully")