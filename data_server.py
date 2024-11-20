from flask import Flask, jsonify, request, render_template
import pandas as pd
from flask_cors import CORS
import os


# Load the Excel file
# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the relative path to the Excel file
excel_file_path = os.path.join(current_dir, "sampledatafoodsales_analysis.xlsx")

df = pd.read_excel(excel_file_path, sheet_name='FoodSales')

# Ensure 'Date' column is parsed as datetime with flexible formats
df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%d-%b')

# Initialize Flask app
#app = Flask(__name__, template_folder=r'C:\Users\madug\OneDrive\Desktop\Advance Database\Main project\custom_folder')

# Define the relative path to the 'custom_folder'
template_folder_path = os.path.join(current_dir, "custom_folder")


# Initialize Flask app with the relative path for templates
app = Flask(__name__, template_folder=template_folder_path)

CORS(app)  # Allow cross-origin requests

def get_public_ip():
    try:
        response = request.get('https://api.ipify.org?format=text')
        return response.text
    except Exception as e:
        return "Unable to fetch IP"

# Define the root route for testing purposes
@app.route('/')
def home():
    #return "Flask server is running!"
    #return render_template('index.html')
     if os.path.exists(os.path.join(template_folder_path, 'index.html')):
        return render_template('index.html')
    else:
        return f"Error: index.html not found in {template_folder_path}"
# Endpoint to get unique values for City and Category
@app.route('/get_initial_data', methods=['GET'])
def get_initial_data():
    cities = df['City'].dropna().unique().tolist()
    categories = df['Category'].dropna().unique().tolist()
    return jsonify({
        'cities': cities,
        'categories': categories
    })

# Endpoint to get filtered data based on query parameters
@app.route('/get_filtered_data', methods=['GET'])
def get_filtered_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    city = request.args.get('city')
    category = request.args.get('category')

    # Convert dates from string to datetime if provided
    if start_date:
        start_date = pd.to_datetime(start_date, format='%Y-%m-%d', errors='coerce')
    if end_date:
        end_date = pd.to_datetime(end_date, format='%Y-%m-%d', errors='coerce')

    # Filter the DataFrame
    filtered_df = df.copy()

    if start_date:
        filtered_df = filtered_df[filtered_df['Date'] >= start_date]
    if end_date:
        filtered_df = filtered_df[filtered_df['Date'] <= end_date]
    if city:
        filtered_df = filtered_df[filtered_df['City'] == city]
    if category:
        filtered_df = filtered_df[filtered_df['Category'] == category]

    # Convert DataFrame to list of dictionaries for JSON response
    result = filtered_df.to_dict(orient='records')
    return jsonify(result)

if __name__ == '__main__':
    # Run the Flask app and allow external connections (0.0.0.0)
    app.run(host='0.0.0.0', port=5000, debug=True)
