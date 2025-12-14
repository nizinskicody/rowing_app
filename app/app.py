from flask import (
    Flask,
    render_template,
    request, 
    jsonify
)
from generator import (
    WORKOUT_TYPES, DIFFICULTIES,
    generate_rowing_workout,
    convert_for_frontend
)

app = Flask(__name__)

# --- Configuration ---
# Set the desired interval time in minutes

# ---------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    # Placeholder data for the dropdown menus
    dropdown_options = {
        'task_type': WORKOUT_TYPES,
        'difficulty': DIFFICULTIES
    }

    initial_message = "Set your task details and total time, then press 'Set Timer'."
    initial_interval_message = "Interval insructions will be displayed here."

    if request.method == 'POST':
        # Get the data from the form
        task_type = request.form.get('task_type')
        difficulty = request.form.get('difficulty')
        total_time_minutes = request.form.get('total_time')

        # Logic for generating intervals called here

        # Simple validation
        try:
            total_time_minutes = int(total_time_minutes)
            if total_time_minutes < 15:
                raise ValueError("Minimum workout time of 15 minutes.")
            if total_time_minutes > 240:
                total_time_minutes = 240
        except (ValueError, TypeError) as e:
            error_message = f"Error: {e}. Please enter a valid positive number for 'Total Time'."
            return jsonify({'success': False, 'message': error_message})

        # Success message
        success_message = (
            f"Timer set for {total_time_minutes} minutes "
            f"for a **{difficulty} {task_type}** workout. "
            "Press 'Start' to begin."
        )

        workout_intervals = generate_rowing_workout(
            task_type, difficulty, total_time_minutes
        )
        workout_details = convert_for_frontend(workout_intervals)

        # We return all necessary data to the frontend
        return jsonify({
            'success': True,
            'message': success_message,
            'total_time_seconds': total_time_minutes * 60,
            'intervals_data': workout_details
        })

    # This block handles the initial GET request to load the page
    return render_template(
        'index.html', 
        options=dropdown_options, 
        message=initial_message,
        interval_message=initial_interval_message
    )

if __name__ == '__main__':
    app.run(debug=True, port=5001)