import mysql.connector
import random

def connect_to_database():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="_deep0618",
        database="quizapp"
    )
    return connection

def get_questions():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT id, question_text, correct_answer FROM questions")
    questions = cursor.fetchall()
    conn.close()
    random.shuffle(questions)
    return questions

def add_participant(name):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO participants (name) VALUES (%s)", (name,))
    conn.commit()
    participant_id = cursor.lastrowid
    conn.close()
    return participant_id

def update_score(participant_id, score, level):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO scores (participant_id, score, level) VALUES (%s, %s, %s)", (participant_id, score, level))
    conn.commit()
    conn.close()

def get_scores():
    conn = connect_to_database()
    cursor = conn.cursor()
    # Get total score and highest level for each participant
    cursor.execute("""
        SELECT p.name, SUM(s.score) as total_score, MAX(s.level) as highest_level
        FROM participants p
        JOIN scores s ON p.id = s.participant_id
        GROUP BY p.id
        ORDER BY total_score DESC
    """)
    scores = cursor.fetchall()
    conn.close()
    return scores

def get_highest_score():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, SUM(s.score) as total_score
        FROM participants p
        JOIN scores s ON p.id = s.participant_id
        GROUP BY p.id
        ORDER BY total_score DESC
        LIMIT 1
    """)
    highest_score = cursor.fetchone()
    conn.close()
    return highest_score

def get_participants():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM participants")
    participants = cursor.fetchall()
    conn.close()
    return participants

def delete_participant(name):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM participants WHERE name = %s", (name,))
    participant = cursor.fetchone()
    if participant:
        participant_id = participant[0]
        cursor.execute("DELETE FROM scores WHERE participant_id = %s", (participant_id,))
        cursor.execute("DELETE FROM participants WHERE id = %s", (participant_id,))
        conn.commit()
    conn.close()

def add_question(question_text, correct_answer):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO questions (question_text, correct_answer) VALUES (%s, %s)", (question_text, correct_answer))
    conn.commit()
    conn.close()

def add_multiple_questions():
    while True:
        question_text = input("Enter the question (or type 'done' to finish): ")
        if question_text.lower() == 'done':
            break
        correct_answer = input("Enter the correct answer: ")
        add_question(question_text, correct_answer)
        print("Question added.")

def list_questions():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT id, question_text FROM questions")
    questions = cursor.fetchall()
    conn.close()
    print("\nQuestions:\n" + "-"*50)
    for q in questions:
        print(f"ID: {q[0]} | {q[1]}")
    print("-"*50)
    return questions

def remove_question():
    questions = list_questions()
    try:
        qid = int(input("Enter the ID of the question to remove: "))
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM questions WHERE id = %s", (qid,))
        conn.commit()
        conn.close()
        print("Question removed.")
    except ValueError:
        print("Invalid input. Please enter a valid question ID.")

def view_all_questions():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT id, question_text, correct_answer FROM questions")
    questions = cursor.fetchall()
    conn.close()
    print("\nQuestions and Answers:\n" + "-"*50)
    for q in questions:
        print(f"ID: {q[0]} | Q: {q[1]} | Ans: {q[2]}")
    print("-"*50)

def view_all_participants():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM participants")
    participants = cursor.fetchall()
    conn.close()
    print("\nParticipants:\n" + "-"*50)
    for p in participants:
        print(f"ID: {p[0]} | Name: {p[1]}")
    print("-"*50)

def view_all_scores():
    scores = get_scores()
    print("\nScores:\n" + "-"*50)
    print("{:<20} {:<10} {:<20}".format("Name", "Score", "Highest Level Played"))
    print("-"*50)
    for score in scores:
        print("{:<20} {:<10} {:<20}".format(score[0], score[1], score[2]))
    print("-"*50)

def view_all_data():
    view_all_questions()
    view_all_participants()
    view_all_scores()

def quiz_game(participant_id, level, used_ids=None):
    if used_ids is None:
        used_ids = set()
    questions = [q for q in get_questions() if q[0] not in used_ids]
    score = 0
    num_questions = 3 + (level - 1) * 2

    for i in range(num_questions):
        if i >= len(questions):
            print("Not enough new questions in the database to continue.")
            break
        question = questions[i]
        answer = input(f"Q{i+1}: {question[1]}\nYour answer: ").strip()
        # Flexible multi-word answer check (ignores case and spaces)
        if answer.strip().lower().replace(" ", "") == question[2].strip().lower().replace(" ", ""):
            score += 1
        used_ids.add(question[0])

    update_score(participant_id, score, level)
    print(f"Your score: {score}")

    passing_score = (num_questions + 1) // 2  # half, rounded up
    if score < passing_score:
        print(f"Sorry, you needed at least score {passing_score} to pass Level {level}. You failed. Please retry.")
        main_menu()
        return

    next_action = input("Do you want to proceed to the next level or return to the main menu? (next/main): ").strip().lower()
    if next_action == 'next':
        quiz_game(participant_id, level + 1, used_ids)
    else:
        main_menu()

def display_scores():
    scores = get_scores()
    print("\nScores:\n" + "-"*50)
    print("{:<20} {:<10} {:<20}".format("Name", "Score", "Highest Level Played"))
    print("-"*50)
    for score in scores:
        print("{:<20} {:<10} {:<20}".format(score[0], score[1], score[2]))
    print("-"*50)
    if scores:
        print(f"Highest Score: {scores[0][0]} with {scores[0][1]} points")

def delete_participant_menu():
    participants = get_participants()
    print("\nParticipants:\n" + "-"*50)
    for participant in participants:
        print(participant[0])
    print("-"*50)
    name = input("Enter the name of the participant to delete: ")
    delete_participant(name)
    print(f"Participant {name} deleted.")

def manager_menu():
    while True:
        print("\nManager Menu\n1. Add Question\n2. Add Multiple Questions\n3. Delete Participant\n4. Remove Question\n5. View All Data\n6. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            question_text = input("Enter the question: ")
            correct_answer = input("Enter the correct answer: ")
            add_question(question_text, correct_answer)
            print("Question added.")
        elif choice == '2':
            add_multiple_questions()
        elif choice == '3':
            delete_participant_menu()
        elif choice == '4':
            remove_question()
        elif choice == '5':
            view_all_data()
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please try again.")

def main_menu():
    while True:
        print("\nMain Menu\n1. Player\n2. Manager\n3. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            player_menu()
        elif choice == '2':
            password = input("Enter manager password: ")
            if password == "_deep0618":
                manager_menu()
            else:
                print("Incorrect password.")
        elif choice == '3':
            print("Exiting the quiz game.")
            break
        else:
            print("Invalid choice. Please try again.")

def player_menu():
    while True:
        print("\nPlayer Menu\n1. Play Quiz\n2. See Scores\n3. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            played_before = input("Have you played before? (yes/no): ").strip().lower()
            if played_before == 'yes':
                name = input("Enter your name: ").strip()
                participant_id, level = get_participant_info(name)
                if participant_id:
                    continue_game = input("Do you want to continue or restart? (continue/restart): ").strip().lower()
                    if continue_game == 'restart':
                        level = 1
                    quiz_game(participant_id, level)
                else:
                    print("Participant not found.")
            else:
                name = input("Enter your name: ").strip()
                participant_id = add_participant(name)
                quiz_game(participant_id, 1)
        elif choice == '2':
            display_scores()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

def get_participant_info(name):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT p.id, MAX(s.level) FROM participants p LEFT JOIN scores s ON p.id = s.participant_id WHERE p.name = %s GROUP BY p.id", (name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0], result[1] if result[1] else 1
    return None, None

if __name__ == "__main__":
    main_menu()