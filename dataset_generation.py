import pandas as pd
import numpy as np
import random

def generate_realistic_dataset(num_rows=100):
    print(f"Generating {num_rows} realistic patient records...")
    
    data = []
    
    for i in range(num_rows):
        # Generate Physical Stats
        patient_id = f"P{1000+i}"
        age = random.randint(18, 80)
        gender = random.choice(['Male', 'Female'])
        
        # Height: Normal distribution around average (Male: 175cm, Female: 162cm)
        if gender == 'Male':
            height = int(np.random.normal(175, 8))
        else:
            height = int(np.random.normal(162, 7))
            
        # Weight: Derived from a random Target BMI to ensure realism
        # (5% Underweight, 40% Normal, 30% Overweight, 25% Obese)
        bmi_category = np.random.choice(['Under', 'Normal', 'Over', 'Obese'], 
                                        p=[0.05, 0.40, 0.30, 0.25])
        
        if bmi_category == 'Under':
            target_bmi = random.uniform(16.0, 18.4)
        elif bmi_category == 'Normal':
            target_bmi = random.uniform(18.5, 24.9)
        elif bmi_category == 'Over':
            target_bmi = random.uniform(25.0, 29.9)
        else: # Obese
            target_bmi = random.uniform(30.0, 45.0)
            
        # Calculate Weight from BMI formula: Weight = BMI * (Height_m)^2
        weight = round(target_bmi * ((height/100) ** 2), 1)
        actual_bmi = round(weight / ((height/100) ** 2), 1)
        
        # Determine Health Status
        # Disease is often correlated with BMI and Age
        disease = "None"
        rand_chance = random.random()
        
        if actual_bmi >= 30: # Obese range
            if rand_chance < 0.30: disease = "Diabetes"
            elif rand_chance < 0.60: disease = "Hypertension"
            else: disease = "Obesity" # The condition itself
        elif actual_bmi >= 25: # Overweight
            if rand_chance < 0.15: disease = "Hypertension"
            elif rand_chance < 0.25: disease = "Diabetes"
        else:
            # Even healthy weight people can have issues as they age
            if age > 50 and rand_chance < 0.10: disease = "Hypertension"

        # Determine Goal
        if actual_bmi >= 25:
            goal = "Lose Weight"
        elif actual_bmi < 18.5:
            goal = "Gain Muscle"
        else:
            goal = "Maintain"

        # Activity Level
        activity = np.random.choice(['Sedentary', 'Moderate', 'Active'], p=[0.4, 0.4, 0.2])

        # Calculate Exact Calories (Mifflin-St Jeor)
        if gender == 'Male':
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
            
        activity_multipliers = {'Sedentary': 1.2, 'Moderate': 1.55, 'Active': 1.725}
        tdee = bmr * activity_multipliers[activity]
        
        # Apply Goal Adjustment
        if goal == 'Lose Weight':
            final_calories = tdee - 500
        elif goal == 'Gain Muscle':
            final_calories = tdee + 500
        else:
            final_calories = tdee
            
        # Safety: Don't recommend starvation
        if final_calories < 1200: final_calories = 1200

        # Assign Diet Recommendation (Logic for AI to Learn)
        if disease == 'Diabetes':
            diet_rec = 'Low_Carb'
        elif disease == 'Hypertension':
            diet_rec = 'Low_Sodium'
        elif disease == 'Obesity':
            diet_rec = 'Balanced' # Calorie deficit is the main "treatment" here
        else:
            diet_rec = 'Balanced'

        # Append Row
        data.append([patient_id, age, gender, weight, height, actual_bmi, 
                     disease, activity, goal, int(final_calories), diet_rec])
    
    # Create DataFrame
    columns = ['Patient_ID', 'Age', 'Gender', 'Weight_kg', 'Height_cm', 'BMI', 
               'Disease_Type', 'Physical_Activity_Level', 'Goal', 
               'Daily_Caloric_Intake', 'Diet_Recommendation']
    
    df = pd.DataFrame(data, columns=columns)
    
    # Save to CSV
    filename = 'realistic_diet_dataset.csv'
    df.to_csv(filename, index=False)
    print(f"Success! File saved as: {filename}")
    print(df.head())

if __name__ == "__main__":
    generate_realistic_dataset(1000)