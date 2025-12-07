import pandas as pd
import numpy as np
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import os

def predict_daily_calories(csv_file_path):
    # Load the Dataset
    if not os.path.exists(csv_file_path):
        print(f"Error: The file '{csv_file_path}' was not found in the current directory.")
        return

    print("Loading dataset and training model... Please wait.")
    df = pd.read_csv(csv_file_path)

    # Data Preprocessing
    # We need to turn text (Male/Female, Sedentary/Active) into numbers
    le_gender = LabelEncoder()
    le_activity = LabelEncoder()

    # The dataset uses Title Case (e.g., 'Male', 'Moderate'), so we ensure our data is consistent
    df['Gender'] = le_gender.fit_transform(df['Gender'])
    df['Physical_Activity_Level'] = le_activity.fit_transform(df['Physical_Activity_Level'])

    # Define the inputs (features) and the output (target)
    features = ['Age', 'Gender', 'Weight_kg', 'Height_cm', 'Physical_Activity_Level']
    target = 'Daily_Caloric_Intake'

    X = df[features]
    y = df[target]

    # Model training
    # We use a Random Forest Regressor which is good for finding patterns in complex data
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    print("Model trained successfully!\n")

    # User Input
    print("="*40)
    print("   DAILY CALORIE PREDICTOR")
    print("="*40)

    try:
        # Get Age
        age = int(input("Enter Age: "))

        # Get Gender (Handle case sensitivity)
        valid_genders = list(le_gender.classes_)
        print(f"Options: {', '.join(valid_genders)}")
        gender_input = input("Enter Gender: ").strip().title()
        
        if gender_input not in valid_genders:
            print(f"❌ Invalid gender. Please enter exactly: {valid_genders}")
            return
        gender_encoded = le_gender.transform([gender_input])[0]

        # Get Weight and Height
        weight = float(input("Enter Weight (kg): "))
        height = float(input("Enter Height (cm): "))

        # Get Activity Level
        valid_activities = list(le_activity.classes_)
        print(f"Options: {', '.join(valid_activities)}")
        activity_input = input("Enter Activity Level: ").strip().title()

        if activity_input not in valid_activities:
            print(f"❌ Invalid activity level. Please enter exactly: {valid_activities}")
            return
        activity_encoded = le_activity.transform([activity_input])[0]

        # Prediction
        # Create a single row of data with the user's inputs
        input_data = np.array([[age, gender_encoded, weight, height, activity_encoded]])
        
        # Predict
        predicted_calories = model.predict(input_data)[0]

        print("-" * 40)
        print(f"Recommended Daily Caloric Intake: {predicted_calories:.0f} kcal")
        print("-" * 40)

    except ValueError:
        print("\n❌ Error: Please enter valid numbers for Age, Weight, and Height.")

if __name__ == "__main__":
    # Ensure this matches the exact name of your uploaded file
    file_name = 'scientifically_corrected_diet_dataset.csv'
    predict_daily_calories(file_name)