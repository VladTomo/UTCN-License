import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import os

# The AI Model
class DietRecommenderAI:
    _FEATURE_COLS     = ['Age', 'Gender', 'Weight_kg', 'Height_cm', 'BMI',
                         'Disease_Type', 'Severity', 'Physical_Activity_Level',
                         'Cholesterol_mg/dL', 'Blood_Pressure_mmHg',
                         'Glucose_mg/dL', 'Weekly_Exercise_Hours']
    _CATEGORICAL_COLS = ['Gender', 'Disease_Type', 'Severity', 'Physical_Activity_Level']

    def __init__(self, csv_file):
        self.model    = RandomForestClassifier(n_estimators=100, random_state=42)
        self.encoders = {}
        if os.path.exists(csv_file):
            self.train_model(csv_file)
        else:
            print(f"Error: {csv_file} not found.")

    def train_model(self, file_path):
        df = pd.read_csv(file_path)
        df['Disease_Type'] = df['Disease_Type'].fillna('None')

        for col in self._CATEGORICAL_COLS:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            self.encoders[col] = le

        le_target = LabelEncoder()
        df['Diet_Recommendation'] = le_target.fit_transform(
            df['Diet_Recommendation'].astype(str))
        self.encoders['Diet_Recommendation'] = le_target

        X = df[self._FEATURE_COLS].values
        y = df['Diet_Recommendation'].values
        self.model.fit(X, y)

    def _safe_encode(self, col: str, value: str) -> int:
        le    = self.encoders[col]
        value = str(value).strip()
        if value in le.classes_:
            return int(le.transform([value])[0])
        return int(le.transform([le.classes_[0]])[0])

    def _build_features(self, age, weight, height, disease, gender,
                        activity_level, severity, cholesterol,
                        blood_pressure, glucose, weekly_exercise):
        bmi      = weight / ((height / 100) ** 2)
        activity = _ACTIVITY_MAP.get(activity_level, 'Moderate')
        return [[
            age,
            self._safe_encode('Gender', gender),
            weight, height, bmi,
            self._safe_encode('Disease_Type', disease),
            self._safe_encode('Severity', severity),
            self._safe_encode('Physical_Activity_Level', activity),
            cholesterol, blood_pressure, glucose, weekly_exercise,
        ]]

    def predict(self, age, weight, height, disease,
                gender='Female', activity_level='Moderate', severity='Mild',
                cholesterol=180.0, blood_pressure=120, glucose=90.0,
                weekly_exercise=3.0):
        features = self._build_features(age, weight, height, disease, gender,
                                        activity_level, severity, cholesterol,
                                        blood_pressure, glucose, weekly_exercise)
        pred = self.model.predict(features)[0]
        return self.encoders['Diet_Recommendation'].inverse_transform([pred])[0]

    def predict_with_confidence(self, age, weight, height, disease,
                                gender='Female', activity_level='Moderate',
                                severity='Mild', cholesterol=180.0,
                                blood_pressure=120, glucose=90.0,
                                weekly_exercise=3.0):
        """Returns (diet_type, confidence) where confidence is 0.0-1.0."""
        features   = self._build_features(age, weight, height, disease, gender,
                                          activity_level, severity, cholesterol,
                                          blood_pressure, glucose, weekly_exercise)
        pred       = self.model.predict(features)[0]
        proba      = self.model.predict_proba(features)[0]
        diet_type  = self.encoders['Diet_Recommendation'].inverse_transform([pred])[0]
        return diet_type, float(proba.max())


# ── Diet Info ────────────────────────────────────────────────────────────────

DIET_INFO = {
    'Balanced': {
        'title':       'Balanced Diet',
        'color':       '#06b6d4',
        'description': 'A well-rounded eating pattern that distributes calories evenly '
                       'across all three macronutrients, supporting overall health and '
                       'sustainable weight management.',
        'rationale':   'Recommended for generally healthy individuals whose primary goal '
                       'is weight maintenance, gradual loss, or general wellness.',
        'eat':   ['Whole grains (oats, brown rice, quinoa)',
                  'Lean proteins (chicken, turkey, fish)',
                  'Fruits & colourful vegetables',
                  'Healthy fats (olive oil, avocado)',
                  'Low-fat dairy or plant alternatives'],
        'avoid': ['Ultra-processed snack foods',
                  'Refined sugars & sugary drinks',
                  'Trans fats (margarine, fast food)',
                  'Excessive alcohol',
                  'Large portions of saturated fat'],
        'tips':  ['Eat 3 balanced meals + 1 planned snack per day',
                  'Fill half your plate with vegetables at each meal',
                  'Aim for 2 L of water daily',
                  'Practice mindful eating -- eat slowly and without screens'],
    },
    'Low_Carb': {
        'title':       'Low Carb Diet',
        'color':       '#f59e0b',
        'description': 'Significantly reduces carbohydrate intake and replaces those '
                       'calories with protein and healthy fats, helping stabilise blood '
                       'sugar and promote fat burning.',
        'rationale':   'Recommended due to a Diabetes diagnosis. Lowering carb intake '
                       'reduces glucose spikes and improves insulin sensitivity.',
        'eat':   ['Meat, poultry & fatty fish (salmon, mackerel)',
                  'Eggs (all preparations)',
                  'Non-starchy vegetables (spinach, broccoli, zucchini)',
                  'Nuts & seeds (almonds, walnuts, chia)',
                  'Avocado & olive oil'],
        'avoid': ['Bread, pasta & white rice',
                  'Sugary drinks & fruit juices',
                  'Starchy vegetables (potatoes, corn)',
                  'Most fruits (except berries in moderation)',
                  'Sweets, cakes & pastries'],
        'tips':  ['Keep net carbs under 50 g / day',
                  'Prioritise fibre-rich low-carb vegetables',
                  'Check blood glucose regularly when changing diet',
                  'Stay well hydrated -- low-carb diets can be diuretic'],
    },
    'Low_Sodium': {
        'title':       'Low Sodium Diet',
        'color':       '#a78bfa',
        'description': 'Limits daily sodium intake to protect cardiovascular health, '
                       'reduce fluid retention, and lower blood pressure.',
        'rationale':   'Recommended due to a Hypertension diagnosis. Reducing sodium '
                       'intake is one of the most effective dietary interventions for '
                       'managing blood pressure.',
        'eat':   ['Fresh fruits & vegetables (unprocessed)',
                  'Unsalted nuts & seeds',
                  'Fresh meats & fish (not cured or smoked)',
                  'Herbs & spices as flavour substitutes',
                  'Low-sodium canned or frozen goods'],
        'avoid': ['Processed & cured meats (bacon, salami, ham)',
                  'Canned soups & ready meals',
                  'Fast food & restaurant meals',
                  'Table salt & seasoning blends',
                  'Pickled foods & soy sauce'],
        'tips':  ['Target < 1 500 mg of sodium per day',
                  'Read nutrition labels -- sodium hides in unexpected foods',
                  'Cook at home to control exactly what goes in your food',
                  'Use lemon juice, garlic, and herbs instead of salt'],
    },
}


# ── Workout Recommender ───────────────────────────────────────────────────────

# Maps GUI labels → dataset labels for activity and goal
_ACTIVITY_MAP = {
    "Sedentary":         "Sedentary",
    "Lightly Active":    "Sedentary",
    "Moderately Active": "Moderate",
    "Very Active":       "Active",
    "Extra Active":      "Active",
}
_GOAL_MAP = {
    "Lose Weight":    "Lose Weight",
    "Maintain Weight":"Maintain",
    "Gain Weight":    "Gain Muscle",
}

WORKOUT_PLANS = {
    "Light": {
        "label":       "Light Intensity",
        "description": "Safe, low-impact movement to build a healthy habit.",
        "duration":    "30-40 min / session",
        "frequency":   "4-5 days / week",
        "exercises": [
            ("Walking",        "Flat terrain, comfortable pace"),
            ("Gentle Yoga",    "Focus on flexibility and breathing"),
            ("Stretching",     "Full-body, 15-20 min"),
            ("Water Aerobics", "Low joint stress, great for beginners"),
        ],
    },
    "Moderate": {
        "label":       "Moderate Intensity",
        "description": "Cardio and strength to improve fitness and burn calories.",
        "duration":    "40-55 min / session",
        "frequency":   "4-5 days / week",
        "exercises": [
            ("Brisk Walking / Jog", "Heart rate 50-70% of max"),
            ("Cycling",             "Steady pace, flat or light hills"),
            ("Bodyweight Circuit",  "Push-ups, squats, lunges - 3 sets"),
            ("Swimming Laps",       "30 min continuous"),
        ],
    },
    "Intense": {
        "label":       "High Intensity",
        "description": "Max-effort training for performance and muscle building.",
        "duration":    "50-75 min / session",
        "frequency":   "5-6 days / week",
        "exercises": [
            ("HIIT Intervals",   "20s on / 10s off, 8 rounds"),
            ("Weight Training",  "Compound lifts - 4 sets x 8-12 reps"),
            ("Running",          "5-10 km at a challenging pace"),
            ("CrossFit Circuit", "Mixed functional movements, timed"),
        ],
    },
}


class WorkoutRecommenderAI:
    _FEATURE_COLS     = ['Age', 'Gender', 'Weight_kg', 'Height_cm', 'BMI',
                         'Disease_Type', 'Physical_Activity_Level', 'Goal']
    _CATEGORICAL_COLS = ['Gender', 'Disease_Type', 'Physical_Activity_Level', 'Goal']

    def __init__(self, csv_file):
        self.model    = RandomForestClassifier(n_estimators=100, random_state=42)
        self.encoders = {}
        if os.path.exists(csv_file):
            self.train_model(csv_file)
        else:
            print(f"Error: {csv_file} not found. Run dataset_generation.py first.")

    def train_model(self, file_path):
        df = pd.read_csv(file_path)
        for col in self._CATEGORICAL_COLS:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].fillna('None').astype(str))
            self.encoders[col] = le
        le_target = LabelEncoder()
        df['Workout_Intensity'] = le_target.fit_transform(df['Workout_Intensity'].astype(str))
        self.encoders['Workout_Intensity'] = le_target
        X = df[self._FEATURE_COLS].values
        y = df['Workout_Intensity'].values
        self.model.fit(X, y)

    def _safe_encode(self, col: str, value: str) -> int:
        le    = self.encoders[col]
        value = str(value).strip()
        if value in le.classes_:
            return int(le.transform([value])[0])
        return int(le.transform([le.classes_[0]])[0])

    def predict(self, age, weight, height, disease,
                gender='Female', activity_level='Moderately Active', goal='Maintain Weight'):
        """Returns (intensity_label, confidence) where confidence is 0.0-1.0."""
        bmi         = weight / ((height / 100) ** 2)
        activity    = _ACTIVITY_MAP.get(activity_level, 'Moderate')
        mapped_goal = _GOAL_MAP.get(goal, 'Maintain')
        features = [[
            age,
            self._safe_encode('Gender', gender),
            weight, height, bmi,
            self._safe_encode('Disease_Type', disease),
            self._safe_encode('Physical_Activity_Level', activity),
            self._safe_encode('Goal', mapped_goal),
        ]]
        pred      = self.model.predict(features)[0]
        proba     = self.model.predict_proba(features)[0]
        intensity = self.encoders['Workout_Intensity'].inverse_transform([pred])[0]
        return intensity, float(proba.max())


# ── Macros Calculator ─────────────────────────────────────────────────────────

# Macros Calculator
def calculate_macros(calories, diet_type):
    # Returns grams of Protein, Fat, Carbs based on the specific diet.

    if diet_type == 'Low_Carb':
        # Ratio tuple: (Protein %, Fat %, Carbs %)
        ratios = (0.30, 0.50, 0.20)
    elif diet_type == 'Low_Sodium':
        # Standard Balanced: 30% P, 30% F, 40% C
        ratios = (0.30, 0.30, 0.40)
    else: # Balanced
        ratios = (0.30, 0.30, 0.40)
        
    # Calculate grams: Protein/Carbs = 4 kcal/g, Fat = 9 kcal/g
    protein = int((calories * ratios[0]) / 4)
    fat = int((calories * ratios[1]) / 9)
    carbs = int((calories * ratios[2]) / 4)
    
    return {'Protein': protein, 'Fats': fat, 'Carbs': carbs}

def get_meal_plan(diet_type):
    # Returns a sample daily menu based on the diet.

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
    # Visualizes BMI on a simple text bar.

    # Clamp the pointer value so it doesn't go off the chart
    # We subtract 15 because the chart starts at BMI 15
    pointer_position = min(max(int(bmi - 15), 0), 25) 
    
    # Create a list of dashes representing the scale
    bar = ["-"] * 26
    bar[pointer_position] = "|" # This marker shows the user's BMI
    
    print("\n   BMI SCALE:")
    print("   15 [ " + "".join(bar) + " ] 40")
    print("      |      |      |      |")
    print("     Undr   Norm   Over   Obes")

# Main App
def main():
    print("\n" + "="*60)
    print("   COMPLETE AI HEALTH COACH")
    print("="*60)
    
    dataset_file = 'diet_recommendations_dataset.csv'
    ai = DietRecommenderAI(dataset_file)
    
    try:
        # User Input
        name = input("Name: ")
        age = int(input("Age: "))
        gender = input("Gender (Male/Female): ").strip()
        weight = float(input("Weight (kg): "))
        height = float(input("Height (cm): "))
        
        # Show options safely
        if hasattr(ai, 'encoders'):
             # opts = options
             opts = [str(x) for x in ai.encoders['Disease_Type'].classes_]
             print(f"\nConditions: {', '.join(opts)}")
             
        disease = input("Condition (or 'None'): ").strip()
        
        print("\nActivity: Sedentary, Moderate, Active")
        activity = input("Activity: ").strip()
        print("\nGoal: Lose Weight, Maintain, Gain Muscle")
        goal = input("Goal: ").strip()

        # Calculations
        # BMR (Basal Metabolic Rate): Calories burned at complete rest
        if gender.lower() == 'male':
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        
        # Activity Multipliers
        mults = {'sedentary': 1.2, 'moderate': 1.55, 'active': 1.725}
        
        # Total Daily Energy Expenditure (Maintenance Calories)
        tdee = bmr * mults.get(activity.lower(), 1.2)
        
        if goal == 'Lose Weight': target_cals = int(tdee - 500)
        elif goal == 'Gain Muscle': target_cals = int(tdee + 500)
        else: target_cals = int(tdee)
        
        # Ensure calories don't drop below safe minimum (1200)
        target_cals = max(target_cals, 1200)

        # AI Prediction
        diet_type = ai.predict(age, weight, height, disease)
        
        # Nutrition Breakdown
        macros = calculate_macros(target_cals, diet_type)
        menu = get_meal_plan(diet_type)
        
        # Report
        print("\n" + "="*60)
        print(f"   PERSONALIZED PLAN: {name.upper()}")
        print("="*60)
        
        # Visual BMI
        bmi = weight / ((height/100)**2)
        print(f"BMI Score: {bmi:.1f}")
        draw_bmi_bar(bmi)
        
        print(f"\nRECOMMENDED DIET: {diet_type} Diet")
        if diet_type == 'Low_Carb': 
            print("   (Focus on high protein and healthy fats to manage insulin)")
        elif diet_type == 'Low_Sodium': 
            print("   (Focus on fresh foods to lower blood pressure)")
        
        print("-" * 60)
        print(f"DAILY NUTRITION TARGETS ({target_cals} kcal)")
        print(f"   * Protein: {macros['Protein']}g")
        print(f"   * Fats:    {macros['Fats']}g")
        print(f"   * Carbs:   {macros['Carbs']}g")
        
        print("-" * 60)
        print(f"SAMPLE MEAL PLAN ({diet_type})")
        print(f"   * Breakfast: {menu['Breakfast']}")
        print(f"   * Lunch:     {menu['Lunch']}")
        print(f"   * Dinner:    {menu['Dinner']}")
        print(f"   * Snack:     {menu['Snack']}")
        print("="*60)

    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()