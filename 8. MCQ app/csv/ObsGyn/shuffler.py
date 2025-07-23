import os
import csv
import random

def clean_cell(row, key):
    val = row.get(key)
    if val is None:
        return ''
    return val.strip()

def shuffle_answers_in_file(filepath):
    temp_filepath = filepath + '.tmp'
    print(f"Processing file: {filepath}")

    with open(filepath, 'r', newline='', encoding='utf-8') as infile, \
         open(temp_filepath, 'w', newline='', encoding='utf-8') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        
        if not fieldnames or any(f is None for f in fieldnames):
            raise ValueError(f"File {filepath} has invalid headers: {fieldnames}")

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row_num, row in enumerate(reader, start=2):
            # Remove any unexpected None keys (malformed rows)
            if None in row:
                print(f"Warning: Row {row_num} has unexpected None key; skipping those fields.")
                del row[None]

            options = [clean_cell(row, k) for k in ['Option A', 'Option B', 'Option C', 'Option D']]
            correct_answer = clean_cell(row, 'Correct Answer')

            # If correct answer not in options (case insensitive), skip shuffling for the row
            try:
                correct_index = next(
                    i for i, opt in enumerate(options) if opt.lower() == correct_answer.lower()
                )
            except StopIteration:
                print(f"Warning: Correct answer '{correct_answer}' not found in options at row {row_num}. Skipping shuffle for this row.")
                writer.writerow(row)
                continue

            # Shuffle options
            shuffled_options = options[:]
            random.shuffle(shuffled_options)

            # Find new index of correct answer in shuffled options
            new_correct_index = next(
                i for i, opt in enumerate(shuffled_options) if opt.lower() == correct_answer.lower()
            )

            # Update row with shuffled options
            row['Option A'] = shuffled_options[0]
            row['Option B'] = shuffled_options[1]
            row['Option C'] = shuffled_options[2]
            row['Option D'] = shuffled_options[3]

            # Update correct answer to the shuffled correct answer text
            row['Correct Answer'] = shuffled_options[new_correct_index]

            writer.writerow(row)

    # Replace original file with the shuffled one
    os.remove(filepath)
    os.rename(temp_filepath, filepath)
    print(f"Finished shuffling and updated: {filepath}")

def shuffle_all_csv_in_directory(directory='.'):
    for filename in os.listdir(directory):
        if filename.lower().endswith('.csv'):
            full_path = os.path.join(directory, filename)
            if os.path.isfile(full_path):
                shuffle_answers_in_file(full_path)
    print("All CSV files processed.")

# Run the script on current directory
if __name__ == "__main__":
    shuffle_all_csv_in_directory()
