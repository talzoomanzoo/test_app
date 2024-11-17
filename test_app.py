from flask import Flask, jsonify, render_template, request
import json
import os

app = Flask(__name__)

# Define the path to save the JSON files
DATA_DIR = 'data' 

# Ensure the data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def parse_json_data(files):
    """Parse multiple JSON files and extract relevant fields."""
    items = []

    def format_text(text):
        """Format text by replacing \n\n with <br><br> and ** with <b> tags."""
        return text.replace("\n\n", "<br><br>").replace("**", "<b>").replace("**", "</b>", 1)

    for json_file in files:
        try:
            with open(json_file, 'r') as file:
                data = json.load(file)
                data = data["data"]

                input_data = data.get("input", {})
                evidences = input_data.get("evidences", "N/A")
                options = input_data.get("options", "N/A")

                formatted_input = f"Evidences: {format_text(evidences)}<br>Options: {format_text(options)}"

                item = {
                    "input": formatted_input,
                    "initial_response": format_text(data["output"].get("initial_response", "N/A")),
                    "label": data.get("label", "N/A"),
                    "initial_prediction": data["output"].get("initial_prediction", "N/A"),
                    "initial_feedback": format_text(
                        data["output"]["iteration"][0].get("critic_response", "N/A")
                    ) if data["output"].get("iteration") else "N/A",
                    "corrected_prediction": data["output"]["iteration"][-1].get("refiner_prediction", "N/A") if data["output"].get("iteration") else "N/A",
                    "evaluation": format_text("\n".join(data["predictions"])) if isinstance(data.get("predictions"), list) and data["predictions"] else "N/A"  # Handle list case
                }
                items.append(item)
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f"Error processing file {json_file}: {e}")
            continue
    return items

@app.route('/')
def index():
    # Render the main page
    return render_template('index.html')

@app.route('/api/table1')
def api_table1():
    json_dir = os.path.abspath("ddxplus_top_10")  # Use absolute path
    if not os.path.exists(json_dir):
        return jsonify({"error": "Directory not found"}), 404  # Handle missing directory
    ddxplus_top_10 = [os.path.join(json_dir, f) for f in os.listdir(json_dir) if f.endswith('.json')]
    items = parse_json_data(ddxplus_top_10)
    return jsonify({"items": items})

@app.route('/api/table2')
def api_table2():
    json_dir = os.path.abspath("medqa_top_10")  # Use absolute path
    if not os.path.exists(json_dir):
        return jsonify({"error": "Directory not found"}), 404  # Handle missing directory
    medqa_top_10 = [os.path.join(json_dir, f) for f in os.listdir(json_dir) if f.endswith('.json')]
    items = parse_json_data(medqa_top_10)
    return jsonify({"items": items})

@app.route('/api/table3')
def api_table3():
    json_dir = os.path.abspath("ddxplus_bottom_10")  # Use absolute path
    if not os.path.exists(json_dir):
        return jsonify({"error": "Directory not found"}), 404  # Handle missing directory
    ddxplus_bottom_10 = [os.path.join(json_dir, f) for f in os.listdir(json_dir) if f.endswith('.json')]
    items = parse_json_data(ddxplus_bottom_10)
    return jsonify({"items": items})

@app.route('/api/table4')
def api_table4():
    json_dir = os.path.abspath("medqa_bottom_10")  # Use absolute path
    if not os.path.exists(json_dir):
        return jsonify({"error": "Directory not found"}), 404  # Handle missing directory
    medqa_bottom_10 = [os.path.join(json_dir, f) for f in os.listdir(json_dir) if f.endswith('.json')]
    items = parse_json_data(medqa_bottom_10)
    return jsonify({"items": items})

@app.route('/api/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    
    # Determine the table based on the index or type
    table_name = f'table_{data["index"] // 10 + 1}'  # Example logic to determine table name
    file_path = os.path.abspath(os.path.join(DATA_DIR, f'{table_name}.json'))  # Use absolute path

    # Load existing data
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                feedback_data = json.load(f)
            except json.JSONDecodeError:
                feedback_data = []  # Start with an empty list if the file is empty or invalid
    else:
        feedback_data = []  # Start with an empty list if the file does not exist

    # Append the new feedback entry
    feedback_entry = {
        'index': data['index'],
        'likert': data['likert'],
        'feedback': data['feedback'],
        'type': data['type']
    }
    feedback_data.append(feedback_entry)

    # Save the updated data back to the JSON file
    with open(file_path, 'w') as f:
        json.dump(feedback_data, f, indent=4)

    return jsonify({'message': 'Feedback submitted successfully!'}), 200

if __name__ == '__main__':
    app.run(debug=True)
