import csv

filename = 'yourfile.csv'
new_row = ['John', 'Doe', 'john@example.com']

# Step 1: Read existing rows into a set
with open(filename, newline='') as csvfile:
    reader = csv.reader(csvfile)
    existing_rows = set(tuple(row) for row in reader)

# Step 2: Check if the new row is a duplicate
if tuple(new_row) not in existing_rows:
    # Step 3: Append the new row if it's unique
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(new_row)
    print("Row written.")
else:
    print("Duplicate row detected, not writing.")
