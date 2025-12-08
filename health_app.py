import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import os

# THE AI BRAIN
class DietRecommenderAI:
    def __init__(self, csv_file):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.encoders = {}
        if os.path.exists(csv_file):
            self.train_model(csv_file)
        else:
            print(f"Error: {csv_file} not found. Run the generator script first.")

    def train_model(self, file_path):
        df = pd.read_csv(file_path)
        # Robust Training: Force text format and handle missing values
        for col in ['Disease_Type', 'Diet_Recommendation']:
            df[col] = df[col].fillna('None').astype(str)
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            self.encoders[col] = le
            
        X = df[['Age', 'Weight_kg', 'BMI', 'Disease_Type']]
        y = df['Diet_Recommendation']
        self.model.fit(X, y)

    def predict(self, age, weight, height, disease):
        bmi = weight / ((height/100) ** 2)
        disease = str(disease).strip()
        
        # Safe encoding
        le = self.encoders['Disease_Type']
        if disease in le.classes_:
            disease_code = le.transform([disease])[0]
        else:
            disease_code = le.transform(['None'])[0] # Default to healthy
            
        pred = self.model.predict([[age, weight, bmi, disease_code]])[0]
        return self.encoders['Diet_Recommendation'].inverse_transform([pred])[0]

# THE NUTRITIONIST ENGINE (New Features)
def calculate_macros(calories, diet_type):
    """
    Returns grams of Protein, Fat, Carbs based on the specific diet.
    """
    if diet_type == 'Low_Carb':
        # 30% Protein, 50% Fat, 20% Carbs
        ratios = (0.30, 0.50, 0.20)
    elif diet_type == 'Low_Sodium':
        # Standard Balanced: 30% P, 30% F, 40% C
        ratios = (0.30, 0.30, 0.40)
    else: # Balanced
        # Standard: 30% P, 30% F, 40% C
        ratios = (0.30, 0.30, 0.40)
        
    protein = int((calories * ratios[0]) / 4)
    fat = int((calories * ratios[1]) / 9)
    carbs = int((calories * ratios[2]) / 4)
    
    return {'Protein': protein, 'Fats': fat, 'Carbs': carbs}

def get_meal_plan(diet_type):
    """
    Returns a sample daily menu based on the diet.
    """
    menus = {
        'Low_Carb': {
            'Breakfast': 'Omelet with Spinach & Avocado',
            'Lunch': 'Grilled Chicken Caesar Salad (No Croutons)',
            'Dinner': 'Baked Salmon with Asparagus & Butter',
            'Snack': 'Almonds or Cheese Stick'
        },
        'Low_Sodium': {
            'Breakfast': 'Oatmeal with Fresh Berries (No Salt)',
            'Lunch': 'Quinoa Bowl with Roasted Veggies',
            'Dinner': 'Lemon Herb Chicken with Steamed Broccoli',
            'Snack': 'Apple Slices with Unsalted Peanut Butter'
        },
        'Balanced': {
            'Breakfast': 'Greek Yogurt with Granola & Honey',
            'Lunch': 'Turkey & Avocado Sandwich on Whole Wheat',
            'Dinner': 'Lean Beef Stir-fry with Brown Rice',
            'Snack': 'Banana or Protein Bar'
        }
    }
    return menus.get(diet_type, menus['Balanced'])

def draw_bmi_bar(bmi):
    """
    Visualizes BMI on a simple text bar.
    """
    # Scale: 15 (min) to 40 (max)
    categories = ["Under", "Normal", "Over", "Obese"]
    pointer = min(max(int(bmi - 15), 0), 25) # Clamp visualization range
    bar = ["-"] * 26
    bar[pointer] = "▲" # The user's position
    
    print("\n   BMI SCALE:")
    print("   15 [ " + "".join(bar) + " ] 40")
    print("      |      |      |      |")
    print("     Undr   Norm   Over   Obes")

# MAIN APP
def main():
    print("\n" + "="*60)
    print("COMPLETE AI HEALTH COACH")
    print("="*60)
    
    dataset_file = 'realistic_diet_dataset.csv'
    ai = DietRecommenderAI(dataset_file)
    
    try:
        # User Input
        name = input("Name: ")
        age = int(input("Age: "))
        gender = input("Gender (Male/Female): ").strip()
        weight = float(input("Weight (kg): "))
        height = float(input("Height (cm): "))
        
        # Show options
        if hasattr(ai, 'encoders'):
             opts = [str(x) for x in ai.encoders['Disease_Type'].classes_]
             print(f"\nConditions: {', '.join(opts)}")
        disease = input("Condition (or 'None'): ").strip()
        
        print("\nActivity: Sedentary, Moderate, Active")
        activity = input("Activity: ").strip()
        print("\nGoal: Lose Weight, Maintain, Gain Muscle")
        goal = input("Goal: ").strip()

        # Calculations
        # Calories (Mifflin-St Jeor)
        if gender.lower() == 'male':
            bmr = (10*weight) + (6.25*height) - (5*age) + 5
        else:
            bmr = (10*weight) + (6.25*height) - (5*age) - 161
        
        mults = {'sedentary': 1.2, 'moderate': 1.55, 'active': 1.725}
        tdee = bmr * mults.get(activity.lower(), 1.2)
        
        if goal == 'Lose Weight': target_cals = int(tdee - 500)
        elif goal == 'Gain Muscle': target_cals = int(tdee + 500)
        else: target_cals = int(tdee)
        target_cals = max(target_cals, 1200)

        # AI Prediction
        diet_type = ai.predict(age, weight, height, disease)
        
        # Nutrition Breakdown
        macros = calculate_macros(target_cals, diet_type)
        menu = get_meal_plan(diet_type)
        
        # FINAL REPORT
        print("\n" + "="*60)
        print(f"PERSONALIZED PLAN: {name.upper()}")
        print("="*60)
        
        # Visual BMI
        bmi = weight / ((height/100)**2)
        print(f"🔹 BMI Score: {bmi:.1f}")
        draw_bmi_bar(bmi)
        
        print(f"\n🔹 RECOMMENDED DIET: {diet_type} Diet")
        if diet_type == 'Low_Carb': print("   (Focus on high protein and healthy fats to manage insulin)")
        elif diet_type == 'Low_Sodium': print("   (Focus on fresh foods to lower blood pressure)")
        
        print("-" * 60)
        print(f"DAILY NUTRITION TARGETS ({target_cals} kcal)")
        print(f" Protein: {macros['Protein']}g")
        print(f" Fats:    {macros['Fats']}g")
        print(f" Carbs:   {macros['Carbs']}g")
        
        print("-" * 60)
        print(f"SAMPLE MEAL PLAN ({diet_type})")
        print(f"Breakfast: {menu['Breakfast']}")
        print(f" Lunch:     {menu['Lunch']}")
        print(f" Dinner:    {menu['Dinner']}")
        print(f" Snack:     {menu['Snack']}")
        print("="*60)

    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()