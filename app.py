import lightgbm as lgb
import pandas as pd
from flask import Flask, request, jsonify, render_template_string

# Initialize Flask app
app = Flask(__name__)

# Load the saved LightGBM model using LightGBM's built-in function
try:
    model = lgb.Booster(model_file='lightgbm_healthcare_model.txt')
except FileNotFoundError:
    model = None
    print("Model file not found. Please ensure 'lightgbm_healthcare_model.txt' is in the correct directory.")

# Load the important features list
with open('important_features.txt', 'r') as f:
    important_features = [line.strip() for line in f]

# HTML form for user input
HTML_FORM = """
<!doctype html>
<title>Predict Healthcare Cost</title>
<h1>Enter Patient Information</h1>
<form method="POST" action="/">
    Age: <input type="text" name="age"><br>
    BMI: <input type="text" name="bmi"><br>
    Number of Children: <input type="text" name="children"><br>
    Smoker: <input type="radio" name="smoker" value="yes"> Yes
            <input type="radio" name="smoker" value="no"> No<br>
    Sex: <input type="radio" name="sex" value="male"> Male
         <input type="radio" name="sex" value="female"> Female<br>
    Region: <select name="region">
                <option value="northeast">Northeast</option>
                <option value="northwest">Northwest</option>
                <option value="southeast">Southeast</option>
                <option value="southwest">Southwest</option>
            </select><br>
    <input type="submit" value="Predict">
</form>
<h2>{{ prediction }}</h2>
"""

@app.route('/', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            # Get form data
            age = int(request.form['age'])
            bmi = float(request.form['bmi'])
            children = int(request.form['children'])
            smoker = request.form['smoker']
            sex = request.form['sex']
            region = request.form['region']

            # Create the input data in the same format as training
            input_data = {
                'age': [age],
                'bmi': [bmi],
                'children': [children],
                'smoker_no': [1 if smoker == 'no' else 0],
                'smoker_yes': [1 if smoker == 'yes' else 0],
                'sex_female': [1 if sex == 'female' else 0],
                'sex_male': [1 if sex == 'male' else 0],
                'region_northeast': [1 if region == 'northeast' else 0],
                'region_northwest': [1 if region == 'northwest' else 0],
                'region_southeast': [1 if region == 'southeast' else 0],
                'region_southwest': [1 if region == 'southwest' else 0]
            }

            # Convert input data to DataFrame
            input_df = pd.DataFrame(input_data)

            # Use only the important features for prediction
            input_df_important = input_df[important_features]

            # Make prediction
            if model:
                prediction = model.predict(input_df_important)[0]
                return render_template_string(HTML_FORM, prediction=f"Predicted Healthcare Cost: ${prediction:.2f}")
            else:
                return render_template_string(HTML_FORM, prediction="Model not found. Please check server setup.")
        
        except ValueError as ve:
            # Handle incorrect data types
            return render_template_string(HTML_FORM, prediction=f"Error: Invalid input. Please enter correct values. Details: {ve}")
        
        except Exception as e:
            # Handle other exceptions
            return render_template_string(HTML_FORM, prediction=f"An unexpected error occurred: {e}")

    # Render the HTML form on GET request
    return render_template_string(HTML_FORM, prediction=None)

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
