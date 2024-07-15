from flask import Flask, jsonify, request
import requests
import time

app = Flask(__name__)


WINDOW_SIZE = 10
TIMEOUT = 0.5  


THIRD_PARTY_SERVER = "http://localhost:8000/"  


numbers = []


def is_unique(number):
    """Checks if a number is already present in the storage."""
    return number not in numbers


def get_numbers(number_type):
    """Fetches numbers from the third-party server based on type."""
    url = THIRD_PARTY_SERVER + number_type
    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()  
        return response.json()["numbers"]
    except (requests.exceptions.RequestException, TimeoutError):
        return []


@app.route("/numbers/<number_id>")
def calculate_average(number_id):
    """Processes request based on number_id and responds with average."""
    start_time = time.time()

  
    if number_id not in ("p", "f", "e", "r"):
        return jsonify({"error": "Invalid number type"}), 400

    
    new_numbers = get_numbers(number_id)

   
    for number in new_numbers:
        if is_unique(number) and len(numbers) < WINDOW_SIZE:
            numbers.append(number)
        elif len(numbers) == WINDOW_SIZE:
            numbers.pop(0)  
            numbers.append(number)

  
    average = sum(numbers) / len(numbers) if len(numbers) == WINDOW_SIZE else None

    
    response = {
        "windowPrevState": numbers.copy()[:-len(new_numbers)],
        "windowCurrState": numbers,
        "numbers": new_numbers,
        "avg": average,
    }

    
    if time.time() - start_time > TIMEOUT:
        return jsonify({"error": "Request timed out"}), 500

    return jsonify(response)


if __name__ == "__main__":
    app.run(host="localhost", port=9876)
