import os
import random
import pandas as pd
from flask import Flask, render_template, request
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

app = Flask(__name__)

# Ensure datasets exist
exercise_file = 'new_cleaned_exercise_dataset.csv'
nutrition_file = 'neutritionData1.csv'

if not os.path.exists(exercise_file) or not os.path.exists(nutrition_file):
    raise FileNotFoundError("Dataset files are missing. Please upload them.")

# Load datasets
exercise_df = pd.read_csv(exercise_file)
nutrition_df = pd.read_csv(nutrition_file)

# Train a regression model to predict calorie intake
X_nutrition = nutrition_df[['Protein (g)', 'Carbs (g)', 'Fat (g)']]
y_nutrition = nutrition_df['Total Calories']
X_train, X_test, y_train, y_test = train_test_split(X_nutrition, y_nutrition, test_size=0.2, random_state=42)

rf_regressor = RandomForestRegressor(n_estimators=100, random_state=42)
rf_regressor.fit(X_train, y_train)

# Activity level mapping
activity_level_mapping = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very active": 1.9
}
muscle_groups = {
    'Push': ['Chest', 'Shoulders', 'Triceps'],
    'Pull': ['Back', 'Biceps', 'Forearms'],
    'Legs': ['Quads', 'Hamstrings', 'Glutes', 'Calves'],
    'Core': ['Abs', 'Lower Back']
}


def generate_workout_plan(workout_type, difficulty, num_weeks):
    workout_plan = []
    for week in range(1, num_weeks + 1):
        for day in range(1, 8):
            exercises = exercise_df[exercise_df['Difficulty Level'] == difficulty]
            
            if exercises.empty:
                continue  # Skip if no exercises match difficulty level
            

            if "push pull legs" in workout_type:
                if day % 7 == 1 or day % 7 == 4:  # Push day
                    workout_selection = exercises[(exercises['Force'] == 'Push') & (exercises['Targeted Muscle'].isin(['Chest', 'Triceps', 'Shoulders']))]
                    targeted_muscles = ['Chest', 'Shoulders', 'Triceps']
                elif day % 7 == 2 or day % 7 == 5:  # Pull day
                    workout_selection = exercises[(exercises['Force'] == 'Pull') & (exercises['Targeted Muscle'].isin(['Back', 'Biceps']))]
                    targeted_muscles = ['Back', 'Biceps']
                elif day % 7 == 3 or day % 7 == 6:  # Leg day
                    workout_selection = exercises[exercises['Targeted Muscle'].isin(['Legs', 'Glutes', 'Hamstrings', 'Quads'])]
                    targeted_muscles = ['Legs']
                else:  # Rest day
                    workout_plan.append({'week': week, 'day': day, 'workout': ['Rest Day'], 'muscle_group': "Rest"})
                    continue
            elif "single" in workout_type:
                if day % 7 == 1 :  
                    workout_selection = exercises[(exercises['Mechanics'] == 'Single') & (exercises['Targeted Muscle'].isin(['Chest']))]
                    targeted_muscles = ['Chest']
                elif day % 7 == 2 :  
                    workout_selection = exercises[(exercises['Mechanics'] == 'Single') & (exercises['Targeted Muscle'].isin(['Back']))]
                    targeted_muscles = ['Back']
                
                elif day % 7 == 3:  
                    workout_selection = exercises[(exercises['Mechanics'] == 'Single') & (exercises['Targeted Muscle'].isin(['Shoulder']))]
                    targeted_muscles = ['Shoulder']
                elif day % 7 == 4 :  
                    workout_selection = exercises[(exercises['Mechanics'] == 'Single') & (exercises['Targeted Muscle'].isin(['Triceps' ,'Biceps']))]
                    targeted_muscles= ['Triceps' , 'Biceps']
                elif day % 7 == 5 :  
                    workout_selection = exercises[(exercises['Mechanics'] == 'Single') & (exercises['Targeted Muscle'].isin(['Abs', 'Core']))]
                    targeted_muscles = ['Abs',' Core']
                elif day % 7 == 6 :  
                    workout_selection = exercises[exercises['Targeted Muscle'].isin(['Legs', 'Glutes', 'Hamstrings', 'Quads'])]
                    targeted_muscles = ['Legs ']                
                else:  # Rest day
                    workout_plan.append({'week': week, 'day': day, 'workout': ['Rest Day'], 'muscle_group': "Rest"})
                    continue

            else:
                if day % 7 == 1 or day % 7 == 4:  # Push day
                    workout_selection = exercises[(exercises['Mechanics'] == 'Compound') & (exercises['Targeted Muscle'].isin(['Back', 'Chest']))]
                    targeted_muscles =  ['Chest','Back']
                elif day % 7 == 2 or day % 7 == 5:
                    workout_selection = exercises[(exercises['Force'] == 'Push') & (exercises['Targeted Muscle'].isin(['Biceps', 'Triceps', 'Shoulders']))]
                    targeted_muscles = ['Shoulders','Arms']
                
                elif day % 7 == 3 or day % 7 == 6:  # Leg day
                    workout_selection = exercises[exercises['Targeted Muscle'].isin(['Legs', 'Glutes', 'Hamstrings', 'Quads'])]
                    targeted_muscles = ['Legs'] 
                else:  # Rest day
                    workout_plan.append({'week': week, 'day': day, 'workout': ['Rest Day'], 'muscle_group': "Rest"})
                    continue

            workout_selection = workout_selection.sample(min(3, len(workout_selection)), replace=False)
            reps = max(6, min(15, difficulty * 2 + 4))

            workout_plan.append({
                'week': week,
                'day': day,
                'muscles': targeted_muscles,
                'workout': [f"{exercise} - 3 sets x {reps} reps" for exercise in workout_selection['Exercise Name']]
            })
    return workout_plan

def generate_meal_plan(diet_type, num_weeks):
    meal_plan = []
    for week in range(1, num_weeks + 1):
        for day in range(1, 8):
            filtered_nutrition = nutrition_df if diet_type == "non-veg" else nutrition_df[~nutrition_df['Recipe Name'].str.contains("Chicken|Eggs|Shrimp|Egg|Turkey|Beef|Salmon|Bacon|Fish|Pork", na=False)]
            
            if filtered_nutrition.empty:
                continue  # Skip if no meals match the criteria
            
            meals = {
                "Breakfast": filtered_nutrition[filtered_nutrition['Time of Day'] == 'Breakfast'].sample(1),
                "Lunch": filtered_nutrition[filtered_nutrition['Time of Day'] == 'Lunch'].sample(1),
                "Dinner": filtered_nutrition[filtered_nutrition['Time of Day'] == 'Dinner'].sample(1),
                "Snack": filtered_nutrition[filtered_nutrition['Time of Day'] == 'Snack'].sample(1)
            }
            
            meal_plan.append({
                'week': week,
                'day': day,
                
                'diet': [f"{meal}: {meals[meal]['Recipe Name'].values[0]} - {meals[meal]['Total Calories'].values[0]} kcal" for meal in meals]
            })
    return meal_plan

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        name = request.form['name']
        height_cm = float(request.form['height'])
        weight_kg = float(request.form['weight'])
        age = int(request.form['age'])
        gender = request.form['gender'].lower()
        goal = request.form['goal'].lower()
        activity_level_str = request.form['activity_level'].lower()
        difficulty = int(request.form['difficulty'])
        num_weeks = int(request.form['num_weeks'])
        diet_type = request.form['diet_type'].lower()
        workout_type = request.form['workout_type'].lower()

        activity_level = activity_level_mapping.get(activity_level_str, 1.2)
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + (5 if gender == 'male' else -161)
        tdee = bmr * activity_level
        daily_calories = tdee * (1.2 if goal == "bulking" else 0.8 if goal == "cutting" else 1.0)

        protein = round((daily_calories * 0.3) / 4, 1)
        carbs = round((daily_calories * 0.4) / 4, 1)
        fats = round((daily_calories * 0.3) / 9, 1)

        workout_plan = generate_workout_plan(workout_type, difficulty, num_weeks)
        meal_plan = generate_meal_plan(diet_type, num_weeks)

        full_plan = []
        for i in range(len(workout_plan)):
            plan_item = {
                'week': workout_plan[i]['week'],
                'day': workout_plan[i]['day'],
                'muscles': workout_plan[i].get('muscles', ['No Muscles Defined']),  # Explicit muscles key
                'workout': workout_plan[i]['workout'],
                'diet': meal_plan[i]['diet'] if i < len(meal_plan) else ['No Meal Plan']
            }
            full_plan.append(plan_item)

        return render_template('result.html', name=name, daily_calories=round(daily_calories, 2), protein=protein, carbs=carbs, fats=fats, plan=full_plan)

    except ValueError:
        return "Invalid input. Please enter valid numerical values for height, weight, and age.", 400

if __name__ == '__main__':
    app.run(port=5001, debug=True)
