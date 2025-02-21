import csv

# Define the headers corresponding to the CSV columns.
headers = [
    "NLOC", "CCN", "token", "PARAM", "length",
    "location_full"
]

functions = []

with open('lizard_report.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if not row:
            continue
        # Create a dictionary by zipping our headers with the row.
        row_dict = dict(zip(headers, row))
        try:
            nloc = int(row_dict["NLOC"])
        except ValueError:
            nloc = 0
        try:
            ccn = int(row_dict["CCN"])
        except ValueError:
            ccn = 0
        
        # We can use the provided filename and function name.
        location_full = row_dict["location_full"]
        
        
        functions.append({
            "nloc": nloc,
            "ccn": ccn,
            "filename": location_full, 
        })

# Sort functions by NLOC (length) in descending order.
longest_functions = sorted(functions, key=lambda f: f['nloc'], reverse=True)[:10]

# Sort functions by cyclomatic complexity (CCN) in descending order.
most_complex_functions = sorted(functions, key=lambda f: f['ccn'], reverse=True)[:10]

print("Top 5 Longest Functions:")
for func in longest_functions:
    print(f"Function '{func['filename']}  - {func['nloc']} lines")

print("\nTop 5 Most Complex Functions:")
for func in most_complex_functions:
    print(f"Function  '{func['filename']} - Cyclomatic Complexity: {func['ccn']}")
