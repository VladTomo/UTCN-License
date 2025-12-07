import pandas as pd
from datetime import datetime
import os

def calculate_bmi(weight, height):
    # Height in meters
    h_m = height / 100
    bmi = weight / (h_m ** 2)
    
    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 24.9:
        category = "Normal Weight"
    elif 25 <= bmi < 29.9:
        category = "Overweight"
    else:
        category = "Obese"
    return bmi, category

def calculate_macros(calories, goal):
    """
    Returns grams of Protein, Fats, Carbs based on goal.
    Protein = 4 kcal/g, Carbs = 4 kcal/g, Fat = 9 kcal/g
    """
    if goal == 'lose':
        # High Protein for satiety (40% P / 35% F / 25% C)
        p_ratio, f_ratio, c_ratio = 0.40, 0.35, 0.25
    elif goal == 'gain':
        # High Carb for energy (30% P / 20% F / 50% C)
        p_ratio, f_ratio, c_ratio = 0.30, 0.20, 0.50
    else: # Maintain
        # Balanced (30% P / 30% F / 40% C)
        p_ratio, f_ratio, c_ratio = 0.30, 0.30, 0.40

    protein_g = (calories * p_ratio) / 4
    fat_g = (calories * f_ratio) / 9
    carbs_g = (calories * c_ratio) / 4
    
    return int(protein_g), int(fat_g), int(carbs_g)

def log_patient_data(data):
    file_name = 'patient_history_log.csv'
    df = pd.DataFrame([data])
    
    # Append to CSV if exists, else create new
    if os.path.exists(file_name):
        df.to_csv(file_name, mode='a', header=False, index=False)
    else:
        df.to_csv(file_name, mode='w', header=True, index=False)
    print(f"\n[Disk] Data saved to {file_name}")

def main():
    print("="*60)
    print("   ADVANCED HEALTH & DIET PLANNER")
    print("="*60)

    try:
        # Inputs
        name = input("Patient Name: ")
        age = int(input("Age: "))
        gender = input("Gender (Male/Female): ").strip().title()
        weight = float(input("Weight (kg): "))
        height = float(input("Height (cm): "))
        
        print("\nActivity Levels: 1=Sedentary, 2=Moderate, 3=Active, 4=Very Active")
        act_map = {'1': 1.2, '2': 1.55, '3': 1.725, '4': 1.9}
        act_choice = input("Choose Level (1-4): ")
        activity_multiplier = act_map.get(act_choice, 1.2)

        print("\nGoals: 1=Lose Weight, 2=Maintain, 3=Gain Muscle")
        goal_choice = input("Choose Goal (1-3): ")
        
        # Calculations
        # BMR (Mifflin-St Jeor)
        if gender == 'Male':
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
            
        tdee = bmr * activity_multiplier # Total Daily Energy Expenditure

        # Goal Adjustment
        if goal_choice == '1':
            target_calories = tdee - 500
            goal_label = 'lose'
        elif goal_choice == '3':
            target_calories = tdee + 500
            goal_label = 'gain'
        else:
            target_calories = tdee
            goal_label = 'maintain'

        # BMI & Macros
        bmi, bmi_category = calculate_bmi(weight, height)
        protein, fats, carbs = calculate_macros(target_calories, goal_label)

        # Generate Report
        print("\n" + "="*60)
        print(f"   REPORT FOR: {name.upper()}")
        print("="*60)
        print(f" BMI Status:       {bmi:.1f} ({bmi_category})")
        print(f" Maintenance Cals: {int(tdee)} kcal")
        print(f" TARGET CALORIES:  {int(target_calories)} kcal")
        print("-" * 60)
        print(f"  MACRONUTRIENT PLAN:")
        print(f"   • Protein: {protein}g")
        print(f"   • Fats:    {fats}g")
        print(f"   • Carbs:   {carbs}g")
        print("="*60)

        # Log Data
        record = {
            'Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'Name': name,
            'Age': age,
            'Gender': gender,
            'Weight': weight,
            'Height': height,
            'BMI': round(bmi, 2),
            'Status': bmi_category,
            'Goal': goal_label,
            'Target_Calories': int(target_calories),
            'Protein_g': protein,
            'Fats_g': fats,
            'Carbs_g': carbs
        }
        log_patient_data(record)

    except ValueError:
        print("\n❌ Error: Please enter valid numbers.")

if __name__ == "__main__":
    main()