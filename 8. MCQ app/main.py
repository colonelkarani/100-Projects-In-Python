import pandas as pd
import random

# 1. Load MCQ data
def load_questions(file_path):
    """Load questions from CSV file"""
    return pd.read_csv(file_path)

# 2. Randomize questions and options
def randomize_quiz(df, num_questions=None):
    """Select and shuffle questions/options"""
    if num_questions:
        df = df.sample(n=num_questions)
    else:
        df = df.sample(frac=1)
    
    # Shuffle options for each question
    option_columns = ['Option A', 'Option B', 'Option C', 'Option D']
    for _, row in df.iterrows():
        options = row[option_columns].tolist()
        random.shuffle(options)
        df.loc[_, option_columns] = options
        # Update correct answer position
        correct_idx = options.index(row['Correct Answer'])
        df.at[_, 'Correct Answer'] = option_columns[correct_idx]
    
    return df.reset_index(drop=True)

# 3. Quiz runner
def run_quiz(df):
    score = 0
    for i, row in df.iterrows():
        print(f"\nQuestion {i+1}: {row['Question']}")
        for opt in ['A', 'B', 'C', 'D']:
            print(f"{opt}. {row[f'Option_{opt}']}")
        
        while True:
            user_ans = input("Your answer (A/B/C/D): ").upper()
            if user_ans in ['A', 'B', 'C', 'D']:
                break
            print("Invalid input! Please enter A, B, C, or D")
        
        if user_ans == row['Correct Answer'][-1]:  # Extract letter (A-D)
            print("✓ Correct!")
            score += 1
        else:
            print(f"✗ Incorrect! Correct answer: {row['Correct Answer']}")
    
    print(f"\nFinal Score: {score}/{len(df)} ({score/len(df)*100:.1f}%)")

# 4. Main execution
if __name__ == "__main__":
    # Load questions (replace with your CSV path)
    df = load_questions("finasteride.csv")
    
    # Randomize and run quiz
    randomized_df = randomize_quiz(df, num_questions=10)  # Quiz with 10 random Qs
    run_quiz(randomized_df)
