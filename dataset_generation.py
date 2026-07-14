import pandas as pd
import numpy as np

def _assign_workout_intensity(age, bmi, disease, activity, goal, rng):
    """Deterministic rules with 8 % label noise for realistic model variance."""
    if disease in ('Hypertension', 'Diabetes'):
        intensity = 'Light' if (bmi >= 30 or age >= 60) else 'Moderate'
    elif disease == 'Obesity':
        intensity = 'Light'
    elif bmi >= 30:
        intensity = 'Light' if activity == 'Sedentary' else 'Moderate'
    elif bmi >= 25:
        intensity = 'Moderate' if (activity == 'Active' and age < 50) else 'Light'
    else:
        if goal in ('Gain Muscle', 'Gain Weight') and activity == 'Active' and age < 55:
            intensity = 'Intense'
        elif activity == 'Active' or (activity == 'Moderate' and age < 40):
            intensity = 'Moderate'
        else:
            intensity = 'Light'

    # 8 % noise — prevents perfect determinism so model comparison is meaningful
    if rng.random() < 0.08:
        others = [x for x in ('Light', 'Moderate', 'Intense') if x != intensity]
        intensity = rng.choice(others)

    return intensity


def generate_workout_dataset(num_rows=1000, seed=99):
    print(f"Generating {num_rows} workout records...")
    rng = np.random.default_rng(seed)

    diseases   = ['None', 'None', 'None', 'Hypertension', 'Diabetes', 'Obesity']
    activities = ['Sedentary', 'Moderate', 'Active']
    goals      = ['Lose Weight', 'Maintain', 'Gain Muscle']

    rows = []
    for i in range(num_rows):
        patient_id = f"W{2000 + i}"
        age        = int(rng.integers(18, 81))
        gender     = rng.choice(['Male', 'Female'])
        height     = int(rng.normal(175, 8) if gender == 'Male' else rng.normal(162, 7))

        bmi_cat = rng.choice(['Under', 'Normal', 'Over', 'Obese'], p=[0.05, 0.40, 0.30, 0.25])
        bmi_ranges = {'Under': (16.0, 18.4), 'Normal': (18.5, 24.9),
                      'Over': (25.0, 29.9), 'Obese': (30.0, 45.0)}
        bmi    = round(float(rng.uniform(*bmi_ranges[bmi_cat])), 1)
        weight = round(bmi * (height / 100) ** 2, 1)

        disease  = rng.choice(diseases)
        activity = rng.choice(activities)
        goal     = rng.choice(goals)

        intensity = _assign_workout_intensity(age, bmi, disease, activity, goal, rng)
        rows.append([patient_id, age, gender, weight, height, bmi,
                     disease, activity, goal, intensity])

    cols = ['Patient_ID', 'Age', 'Gender', 'Weight_kg', 'Height_cm', 'BMI',
            'Disease_Type', 'Physical_Activity_Level', 'Goal', 'Workout_Intensity']
    df = pd.DataFrame(rows, columns=cols)
    filename = 'workout_dataset.csv'
    df.to_csv(filename, index=False)
    print(f"Saved: {filename}")
    print(df['Workout_Intensity'].value_counts().to_string())


if __name__ == "__main__":
    generate_workout_dataset(1000)