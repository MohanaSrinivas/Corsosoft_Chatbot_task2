from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

chat_history = []
numbers_list = []
command_count = {}
awaiting_prime_range = False  

def validate_list(input_str):

    parts = input_str.split(",")

    
    if awaiting_prime_range:
        return False

    return all(part.strip().isdigit() for part in parts)


def generate_primes(start, end):

    primes = []
    for num in range(start, end + 1):
        if num > 1:
            is_prime = True
            for i in range(2, int(num ** 0.5) + 1):
                if num % i == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.append(num)
    return primes


def update_command_count(command):

    if command in command_count:
        command_count[command] += 1
    else:
        command_count[command] = 1


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    global numbers_list, awaiting_prime_range

    user_message = request.json.get("message", "").strip().lower()
    chat_history.append(f"User: {user_message}")

    responses = {
        "hello": "Hi there! How can I help you today?",
        "hi": "Hi there! How can I help you today?",
        "todays date/time": datetime.now().strftime("%d %B %Y, %I:%M %p"),
        "bye": "Goodbye! Have a great day!"
    }

    if user_message in responses:
        reply = responses[user_message]
        update_command_count(user_message)

    elif user_message == "list operations":
        reply = "Please enter a list of integers (comma-separated):"
        update_command_count("list operations")

    elif validate_list(user_message):
        try:
            numbers_list = list(map(int, user_message.split(",")))
            reply = (
                f"Sum: {sum(numbers_list)}<br>"
                f"Maximum: {max(numbers_list)}<br>"
                f"Reversed List: {list(reversed(numbers_list))}<br>"
                f"Sorted List: {sorted(numbers_list)}<br>"
                "Would you like to remove duplicates? (yes/no)"
            )
            update_command_count("list operations")
        except ValueError:
            reply = "Error: Please enter a valid comma-separated list of integers."

    elif user_message == "yes" and "Would you like to remove duplicates?" in chat_history[-2]:
        if numbers_list:
            numbers_list = list(set(numbers_list))
            reply = (
                f"Updated List: {sorted(numbers_list)}<br>"
                f"Sum: {sum(numbers_list)}<br>"
                f"Maximum: {max(numbers_list)}<br>"
                f"Reversed List: {list(reversed(numbers_list))}<br>"
                "How else can I assist you?"
            )
        else:
            reply = "Error: No numbers stored. Please enter a list of integers first."

    elif user_message == "generate primes":
        awaiting_prime_range = True 
        reply = "Please enter the range for prime generation in the format 'start, end':"

    elif awaiting_prime_range:
        try:
            start, end = map(int, user_message.split(","))
            if start > end:
                reply = "Error: Start value must be less than or equal to end value."
            else:
                primes = generate_primes(start, end)
                reply = f"Prime numbers between {start} and {end}: " + (", ".join(map(str, primes)) if primes else "None found.")
                update_command_count("generate prime")
        except ValueError:
            reply = "Error: Please enter a valid numeric range (start, end)."

        awaiting_prime_range = False  

    elif user_message == "bye":
        most_frequent_command = max(command_count, key=command_count.get, default="No commands used")
        reply = (
            f"Here’s a summary of your session:<br>"
            f"- Commands Used: {len(command_count)}<br>"
            f"- Most Frequent Command: {most_frequent_command}<br>"
            "Do you want to save this summary? (yes/no)"
        )
        update_command_count("bye")

    else:
        reply = "Enter correct keyword."

    chat_history.append(f"Chatbot: {reply}")
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)
