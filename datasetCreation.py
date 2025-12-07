import pandas as pd
import os

def create_corrected_dataset(input_file, output_file):
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: '{input_file}' not found.")
        return

    print("Reading original dataset...")
    df = pd.read_csv(input_file)

    # Function to calculate accurate calories
    def get_scientific_calories(row):
        weight = row['Weight_kg']
        height = row['Height_cm']
        age = row['Age']
        gender = row['Gender']
        activity = row['Physical_Activity_Level']

        # Calculate BMR (Basal Metabolic Rate)
        if gender == 'Male':
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        elif gender == 'Female':
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        else:
            # Fallback if gender is missing or different format
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5

        # Activity Multiplier
        # Standard mappings: Sedentary=1.2, Moderate=1.55, Active=1.725
        multipliers = {
            'Sedentary': 1.2,
            'Moderate': 1.55,
            'Active': 1.725
        }
        
        # Get multiplier, default to 1.2 if not found
        factor = multipliers.get(activity, 1.2)
        
        return int(bmr * factor)

    # Apply the calculation to every row
    print("Recalculating caloric values...")
    df['Daily_Caloric_Intake'] = df.apply(get_scientific_calories, axis=1)

    # Save to new CSV
    df.to_csv(output_file, index=False)
    print(f"Success! New dataset saved as: {output_file}")
    print("\nPreview of new values:")
    print(df[['Gender', 'Weight_kg', 'Physical_Activity_Level', 'Daily_Caloric_Intake']].head())

if __name__ == "__main__":
    input_csv = 'diet_recommendations_dataset.csv'
    output_csv = 'scientifically_corrected_diet_dataset.csv'
    
    create_corrected_dataset(input_csv, output_csv)