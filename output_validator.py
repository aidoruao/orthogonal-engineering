import pandas as pd
def validate_output():
    df = pd.read_csv("refined_inventory.csv")
    if "verified_invariant" in df.columns:
        density = df["verified_invariant"].mean()
        print(f"Invariant Density: {density:.2%}")
    else:
        print("Column 'verified_invariant' missing from CSV.")
validate_output()
