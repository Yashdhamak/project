from flask import Flask, jsonify, request
from datetime import datetime, timedelta

app = Flask(__name__)

# Sample data (replace with database implementation)
doctors = [
    {"id": 1, "name": "Dr. John Doe", "max_patients": 5},
    {"id": 2, "name": "Dr. Jane Smith", "max_patients": 7}
]

appointments = []

# Get list of doctors
@app.route('/doctors', methods=['GET'])
def get_doctors():
    return jsonify(doctors)

# Get doctor details
@app.route('/doctors/<int:doctor_id>', methods=['GET'])
def get_doctor(doctor_id):
    doctor = next((doc for doc in doctors if doc["id"] == doctor_id), None)
    if doctor:
        return jsonify(doctor)
    else:
        return jsonify({"message": "Doctor not found"}), 404

# Get doctor availability for a specific date
@app.route('/doctors/<int:doctor_id>/availability', methods=['GET'])
def get_availability(doctor_id):
    date_str = request.args.get('date')
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({"message": "Invalid date format"}), 400

    doctor = next((doc for doc in doctors if doc["id"] == doctor_id), None)
    if not doctor:
        return jsonify({"message": "Doctor not found"}), 404

    # Assuming doctors work only on weekdays (Mon-Fri)
    if date.weekday() >= 5:
        return jsonify({"message": "Doctor not available on weekends"}), 400

    # Assuming doctors work only in the evenings
    start_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=17)
    end_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=20)

    # Check existing appointments for the doctor on the given date
    appointments_on_date = [apt for apt in appointments if apt['doctor_id'] == doctor_id and apt['date'] == date]
    slots_available = doctor['max_patients'] - len(appointments_on_date)

    return jsonify({
        "doctor_id": doctor_id,
        "date": date_str,
        "start_time": start_time.strftime('%H:%M'),
        "end_time": end_time.strftime('%H:%M'),
        "slots_available": slots_available
    })

# Book appointment
@app.route('/appointments', methods=['POST'])
def book_appointment():
    data = request.json
    doctor_id = data.get('doctor_id')
    patient_name = data.get('patient_name')
    date_str = data.get('date')

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({"message": "Invalid date format"}), 400

    doctor = next((doc for doc in doctors if doc["id"] == doctor_id), None)
    if not doctor:
        return jsonify({"message": "Doctor not found"}), 404

    # Check doctor availability
    availability = get_availability(doctor_id).json()
    if availability['slots_available'] <= 0:
        return jsonify({"message": "No available slots for the selected date"}), 400

    # Book appointment
    appointments.append({
        "doctor_id": doctor_id,
        "patient_name": patient_name,
        "date": date
    })

    return jsonify({"message": "Appointment booked successfully"}), 201

if __name__ == '__main__':
    app.run(debug=True)