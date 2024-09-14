import pandas as pd
import random

# Load quiz data from a CSV file
subject_df = pd.read_csv('quiz_data/quizes.csv', sep=',', header=None, names=['Subject', 'Question', 'Answer', 'Explanation'])

# Function to get a random question based on subject
def fetch_quiz(subject):
    # Filter the questions by subject
    subject_questions = subject_df[subject_df['Subject'] == subject]
    
    if subject_questions.empty:
        return None, None, None
    
    # Randomly select a question
    question_row = subject_questions.sample(n=1).iloc[0]
    
    return question_row['Question'], question_row['Answer'], question_row['Explanation']

# Function to verify the user's answer
def verify_answer(user_answer, correct_answer, explanation):
    if user_answer.strip().lower() == correct_answer.strip().lower():
        return "Correct!"
    else:
        return f"Incorrect. The correct answer is {correct_answer}. Explanation: {explanation}"

# Main logic to run the quiz
def run_quiz():
    # Ask the user for the subject they want to quiz on
    subject = input("Enter the subject for the quiz (e.g., Math, Science): ")
    
    # Fetch a quiz question for the given subject
    question, correct_answer, explanation = fetch_quiz(subject)
    
    if question is None:
        print("Sorry, no questions available for this subject.")
        return
    
    # Ask the user the quiz question
    print(f"Here is your question for {subject}: {question}")
    
    # Get the user's answer
    user_answer = input("Your answer: ")
    
    # Verify the answer and provide feedback
    feedback = verify_answer(user_answer, correct_answer, explanation)
    print(feedback)

# Run the quiz
run_quiz()
