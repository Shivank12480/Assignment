from flask import Flask, request, jsonify

app = Flask(__name__)

# Constants
ROWS = 11  # 10 rows of 7 seats and 1 row of 3 seats
SEATS_PER_ROW = [7] * 10 + [3]  # Last row has 3 seats, rest have 7 seats

# Initialize seats (0 means available, 1 means booked)
seats = [[0 for _ in range(row)] for row in SEATS_PER_ROW]

def find_seats(num_seats):
    """Find and reserve the required number of seats"""
    booked_seats = []

    # Try to book all seats in the same row
    for row_idx, row in enumerate(seats):
        available_seats = [idx for idx, seat in enumerate(row) if seat == 0]
        if len(available_seats) >= num_seats:
            # Reserve seats in this row
            for i in range(num_seats):
                seats[row_idx][available_seats[i]] = 1
                booked_seats.append((row_idx + 1, available_seats[i] + 1))  # 1-based index
            return booked_seats

    # If can't book in one row, book nearby seats (try to minimize distance)
    for row_idx, row in enumerate(seats):
        available_seats = [idx for idx, seat in enumerate(row) if seat == 0]
        for i in range(min(len(available_seats), num_seats)):
            seats[row_idx][available_seats[i]] = 1
            booked_seats.append((row_idx + 1, available_seats[i] + 1))
        num_seats -= len(booked_seats)
        if num_seats <= 0:
            return booked_seats

    return booked_seats

@app.route('/book', methods=['POST'])
def book_seats():
    data = request.json
    num_seats = data.get('num_seats')

    # Validate request
    if not num_seats or not (1 <= num_seats <= 7):
        return jsonify({"error": "You can book between 1 and 7 seats at a time."}), 400

    # Check if enough seats are available
    available_seats = sum([row.count(0) for row in seats])
    if num_seats > available_seats:
        return jsonify({"error": "Not enough seats available."}), 400

    # Book seats
    booked_seats = find_seats(num_seats)
    return jsonify({
        "message": "Seats booked successfully.",
        "booked_seats": booked_seats,
        "seats_layout": seats
    })

@app.route('/seats', methods=['GET'])
def get_seats():
    """Return the current seat layout"""
    return jsonify({"seats_layout": seats})

if __name__ == '__main__':
    app.run(debug=True)
