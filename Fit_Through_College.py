import streamlit as st
import pandas as pd
from github_contents import GithubContents
import random
from datetime import datetime, timedelta

# Read the CSV file containing fitness exercises
DATA_FILE = "exercise_final.csv"

def init_github():
    """Initialize the GithubContents object."""
    if 'github' not in st.session_state:
        st.session_state.github = GithubContents(
            st.secrets["github"]["owner"],
            st.secrets["github"]["repo"],
            st.secrets["github"]["token"])

def init_dataframe():
    """Initialize or load the dataframe."""
    if 'df_exercises' not in st.session_state:
        st.session_state.df_exercises = st.session_state.github.read_df(DATA_FILE)

def create_training_plan(filtered_df, selected_days):
    """Create a training plan with 5 random exercises for each selected day."""
    training_plan = {}
    for day in selected_days:
        day_exercises = filtered_df.sample(n=5)
        training_plan[day] = day_exercises
    return training_plan

def main():
    st.title("Fit Through College")
    init_github()
    init_dataframe()
    fitness_levels = st.session_state.df_exercises['level'].unique()
    muscles = st.session_state.df_exercises["primaryMuscles"].unique()
    
    st.sidebar.markdown("Fitness Level")
    level = st.sidebar.selectbox("How would you rate your fitness level?", fitness_levels, key="fitness_level_selectbox")
    
    st.sidebar.markdown("Muscles")
    muscles = st.sidebar.multiselect("Which muscles do you want to train?",muscles, key="muscles_multiselect")
    
    st.sidebar.markdown("Week")
    selected_week = st.sidebar.date_input("When does your training week start?", value=None, min_value=None, max_value=None, key=None)

    
    st.sidebar.markdown("Training Days")
    selected_days = st.sidebar.multiselect("On which days do you want to train?", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], key="training_days_multiselect")
    
    st.sidebar.markdown("Time of Training")
    training_time = st.sidebar.time_input("At what time do you want to train?", value=None, key="training_time_input")
   

    filter_button = st.sidebar.button("Create Weekly Training Plan", key="create_training_plan_button")
    if filter_button:
        if selected_week:
            start_week = selected_week
            end_week = start_week + timedelta(days=6)
            
            filtered_df = st.session_state.df_exercises[st.session_state.df_exercises['level'] == level]
            if muscles:
                filtered_df = filtered_df[filtered_df["primaryMuscles"].isin(muscles)]

            st.write(f"Week: {start_week.strftime('%d.%m.%Y')} - {end_week.strftime('%d.%m.%Y')}")

            training_plan = create_training_plan(filtered_df, selected_days)

            for day, exercises in training_plan.items():
                st.subheader(f"{day} - {training_time}")
                for index, exercise in exercises.iterrows():
                    st.subheader(exercise["name"])
                    st.write(f"Level: {exercise['level']}")
                    st.write(f"Muscles: {exercise['primaryMuscles']}")
                    st.write(f"Instructions: {exercise['instructions']}")
        else:
            st.sidebar.error("Please select a week.")

if __name__ == "__main__":
    main()

