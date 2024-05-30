import binascii
import streamlit as st
import pandas as pd
from functions.github_contents import GithubContents
import bcrypt
from datetime import timedelta
import datetime

# Set constants
DATA_FILE_LOGIN = "MyLoginTable.csv"
DATA_COLUMNS = ['username', 'name', 'password']
DATA_FILE_EXERCISE = "exercise_final.csv"
USER_PLAN_COLUMNS = ['username', 'date', 'day', 'exercise_name', 'level', 'primaryMuscles', 'instructions']
DATA_FILE_USER_PLANS = "user_training_plans.csv"
DATA_FILE_COMPLETED_PLANS = "completed_training_plans.csv"
DATA_FILE_TRAINING_LOGS = "training_logs.csv"
TRAINING_LOG_COLUMNS = ['username', 'start_date', 'end_date', 'training_plan']

muscle_images = {
    "biceps": "images/arms.png",
    "quadriceps": "images/arms.png",
    "triceps": "images/arms.png",
    "shoulders": "images/Shoulders.png",
    "chest": "images/chest.png",
    "glutes": "images/booty.png",
    "lower back": "images/back.png",
    "abdominals": "images/abdominal.png",
    "abductors": "images/Legs.png",
    "hamstrings": "images/Legs.png"
}

def init_dataframe():
    """Initialize or load the exercises dataframe."""
    if 'df_exercises' not in st.session_state:
        st.session_state.df_exercises = st.session_state.github.read_df(DATA_FILE_EXERCISE)
    
    if 'df_user_plans' not in st.session_state:
        if st.session_state.github.file_exists(DATA_FILE_USER_PLANS):
            st.session_state.df_user_plans = st.session_state.github.read_df(DATA_FILE_USER_PLANS)
        else:
            st.session_state.df_user_plans = pd.DataFrame(columns=USER_PLAN_COLUMNS)

    if 'df_completed_plans' not in st.session_state:
        if st.session_state.github.file_exists(DATA_FILE_COMPLETED_PLANS):
            st.session_state.df_completed_plans = st.session_state.github.read_df(DATA_FILE_COMPLETED_PLANS)
        else:
            st.session_state.df_completed_plans = pd.DataFrame(columns=USER_PLAN_COLUMNS)

    if 'df_training_logs' not in st.session_state:
        if st.session_state.github.file_exists(DATA_FILE_TRAINING_LOGS):
            st.session_state.df_training_logs = st.session_state.github.read_df(DATA_FILE_TRAINING_LOGS)
        else:
            st.session_state.df_training_logs = pd.DataFrame(columns=['username', 'start_date', 'end_date', 'training_plan'])

import pandas as pd
from datetime import timedelta

def create_training_plan(filtered_df, selected_days, start_date):
    """Create a training plan with 5 random exercises for each selected day and save it to GitHub."""
    training_plan = pd.DataFrame(columns=USER_PLAN_COLUMNS)
    
    for day in selected_days:
        day_exercises = filtered_df.sample(n=5)
        day_plan = pd.DataFrame({
            'username': st.session_state['username'],
            'date': [start_date] * len(day_exercises),
            'day': [day] * len(day_exercises),
            'exercise_name': day_exercises["name"],
            'level': day_exercises['level'],
            'primaryMuscles': day_exercises['primaryMuscles'],
            'instructions': day_exercises['instructions']
        })
        training_plan = pd.concat([training_plan, day_plan], ignore_index=True)
        start_date += timedelta(days=1)

    # Display the training plan
    #st.markdown(f"<h2 style='color: #ff5733;'><b>Training Plan</b></h2>", unsafe_allow_html=True)

    # for day in selected_days:
    #     st.markdown(f"<h3>{day}</h3>", unsafe_allow_html=True)
    #     day_exercises = training_plan[training_plan['day'] == day]
    #     for _, exercise in day_exercises.iterrows():
    #         st.markdown(f"<p style='font-size:16px;'><strong>Exercise:</strong> <em>{exercise['exercise_name']}</em></p>", unsafe_allow_html=True)
    #         st.markdown(f"<p style='font-size:16px;'><strong>Level:</strong> {exercise['level']}</p>", unsafe_allow_html=True)
    #         st.markdown(f"<p style='font-size:16px;'><strong>Muscles:</strong> {exercise['primaryMuscles']}</p>", unsafe_allow_html=True)

    #         muscles = exercise['primaryMuscles'].split(',')
    #         for muscle in muscles:
    #             muscle = muscle.strip()
    #             if muscle in muscle_images:
    #                 st.image(muscle_images[muscle], width=100)

    #         st.markdown(f"<p style='font-size:16px;'><strong>Instructions:</strong> {exercise['instructions']}</p>", unsafe_allow_html=True)            
    #         st.write("")

    # Save the training plan to the user's plan DataFrame
    st.session_state.df_user_plans = pd.concat([st.session_state.df_user_plans, training_plan], ignore_index=True)
    
    # Save the updated user plans to GitHub
    st.session_state.github.write_df(DATA_FILE_USER_PLANS, st.session_state.df_user_plans, "Updated user training plans")
    
    return training_plan


def save_training_plan_to_logs(user_training_plan):
    """
    Speichert den gesamten Trainingsplan für den ausgewählten Zeitraum im Training Logs Tab.
    """
    start_date = user_training_plan['date'].min()
    end_date = user_training_plan['date'].max()
    
    # Erstelle einen Eintrag für den gesamten Trainingszeitraum
    training_logs_entry = {
        'username': st.session_state['username'],
        'start_date': start_date,
        'end_date': end_date,
        'training_plan': user_training_plan.to_dict(orient='records')
    }
    
    # Füge den Eintrag zu den Training Logs hinzu
    st.session_state.df_training_logs = st.session_state.df_training_logs.append(training_logs_entry, ignore_index=True)
    
    # Speichere die aktualisierten Training Logs im GitHub
    st.session_state.github.write_df(DATA_FILE_TRAINING_LOGS, st.session_state.df_training_logs, "Updated training logs")

def current_training_plan():
    st.markdown("<h2 style='color: #ff5733;'> <b>Current Training Plan</b> </h2>", unsafe_allow_html=True)
    user_plans = st.session_state.df_user_plans
    user_plans = user_plans[user_plans['username'] == st.session_state['username']]

    if not user_plans.empty:
        # Find the start date
        start_date = user_plans.iloc[0]['date']
        # Convert to datetime if necessary
        if not isinstance(start_date, datetime.datetime):
            start_date = pd.to_datetime(start_date)
        # Find the end date of the training plan (start date + 6 days)
        end_date = start_date + timedelta(days=6)
        st.markdown(f"<h5 style='color: #ff5733'> {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}</h5>", unsafe_allow_html=True)
        
        for _, row in user_plans.iterrows():
            st.markdown(f"<h3>{row['day']}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:18px;'><strong>Exercise:</strong> {row['exercise_name']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:16px;'><strong>Level:</strong> {row['level']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:16px;'><strong>Muscles:</strong> {row['primaryMuscles']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:16px;'><strong>Instructions:</strong> {row['instructions']}</p>", unsafe_allow_html=True)

            muscle = row['primaryMuscles']
            if muscle in muscle_images:
                st.image(muscle_images[muscle], width=100)

            st.write("")
        if st.button("Training Plan Completed", key= f"complete_training1"):
            complete_training_plan()
    else:
        st.write("No current training plans available.")

    
def complete_training_plan():
    """Move the current training plan to the completed plans and clear it from the active plans."""
    user_plans = st.session_state.df_user_plans
    username = st.session_state['username']
    
    # Filter out the plans for the current user
    user_plans = user_plans[user_plans['username'] == username]
    #st.dataframe(user_plans)
    if not user_plans.empty:
        # Convert 'date' column to datetime
        user_plans['date'] = pd.to_datetime(user_plans['date'])

        # Append the user's current plan to the completed plans
        st.session_state.df_completed_plans = pd.concat([st.session_state.df_completed_plans, user_plans], ignore_index=True)
        
        # Save the completed plans to GitHub
        st.session_state.github.write_df(DATA_FILE_COMPLETED_PLANS, st.session_state.df_completed_plans, "Updated completed training plans")
        
        # Remove the user's current plan from the active plans
        st.session_state.df_user_plans = st.session_state.df_user_plans[st.session_state.df_user_plans['username'] != username]
        
        # Save the updated user plans to GitHub
        st.session_state.github.write_df(DATA_FILE_USER_PLANS, st.session_state.df_user_plans, "Updated user training plans")
        
        # Create a new subtab for the completed training plan
        create_completed_training_plan_subtab(user_plans)
        
        st.success("Training plan completed and moved to the Completed Training Plans tab.")
    else:
        st.warning("No current training plans available.")


def create_completed_training_plan_subtab(user_plans):
    """Create a subtab for the completed training plan."""
    start_date = user_plans['date'].min()
    end_date = user_plans['date'].max() + timedelta(days=6)
    tab_label = f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}"

    # Check if the subtab already exists
    existing_subtabs = st.session_state.get('completed_training_plan_subtabs', [])
    for subtab in existing_subtabs:
        if subtab['label'] == tab_label:
            # If subtab already exists, return
            return

    # If subtab doesn't exist, create a new subtab
    new_subtab = {
        'label': tab_label,
        'user_plans': user_plans
    }
    existing_subtabs.append(new_subtab)
    st.session_state['completed_training_plan_subtabs'] = existing_subtabs

def completed_training_plans_page():
    st.markdown("<h2 style='color: #ff5733;'> <b>Completed Training Plans</b> </h2>", unsafe_allow_html=True)
    completed_plans = st.session_state.df_completed_plans
    completed_plans = completed_plans[completed_plans['username'] == st.session_state['username']]

    if not completed_plans.empty:
        # Display the subtabs only if there are completed training plans available
        display_completed_training_plan_subtabs()

    else:
        st.write("No completed training plans available.")

def display_completed_training_plan_subtabs():
    """Display subtabs for completed training plans."""
    subtabs = st.session_state.get('completed_training_plan_subtabs', [])
    
    if subtabs:
        # Create a selectbox to choose the subtab
        selected_subtab_label = st.selectbox("Training Plan:", [subtab['label'] for subtab in subtabs], key="select_training_plan_subtab")

        # Find the selected subtab
        selected_subtab = None
        for subtab in subtabs:
            if subtab['label'] == selected_subtab_label:
                selected_subtab = subtab
                break
        
        # Display the selected subtab
        if selected_subtab:
            user_plans = selected_subtab['user_plans']
            for _, row in user_plans.iterrows():
                st.markdown(f"<p style='font-size:20px;'><strong>{row['day']}</strong></p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:18px;'><strong>Exercise:</strong> {row['exercise_name']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:16px;'><strong>Level:</strong> {row['level']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:16px;'><strong>Muscles:</strong> {row['primaryMuscles']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:16px;'><strong>Instructions:</strong> {row['instructions']}</p>", unsafe_allow_html=True)
                
                muscle = row['primaryMuscles']
                if muscle in muscle_images:
                    st.image(muscle_images[muscle], width=100)
            st.write("")

    else:
        st.write("No completed training plans available.")

def display_completed_training_plan():
    """Display the completed training plan."""
    subtabs = st.session_state.get('completed_training_plan_subtabs', [])

    if subtabs:
        # Create a selectbox to choose the subtab
        selected_subtab_label = st.selectbox("Select Training Plan:", [subtab['label'] for subtab in subtabs])

        # Find the selected subtab
        selected_subtab = None
        for subtab in subtabs:
            if subtab['label'] == selected_subtab_label:
                selected_subtab = subtab
                break

        # Display the selected subtab
        if selected_subtab:
            user_plans = selected_subtab['user_plans']
            st.write("Completed Training Plans:")
            for _, row in user_plans.iterrows():
                st.write(f"Date: {row['date']}")
                st.write(f"Day: {row['day']}")
                st.write(f"Exercise: {row['exercise_name']}")
                st.write(f"Level: {row['level']}")
                st.write(f"Muscles: {row['primaryMuscles']}")
                st.write(f"Instructions: {row['instructions']}")
                st.write("")
    else:
        st.write("No completed training plans available.")

def main_fitness():
    # Initial setup
    if 'authentication' not in st.session_state:
        st.session_state['authentication'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = ""
    if 'completed_training_plan_subtabs' not in st.session_state:
        st.session_state['completed_training_plan_subtabs'] = []

    # Check authentication status
    if not st.session_state['authentication']:
        login_page()
    else:
        init_dataframe()
        cols = st.columns(3)
        with cols[1]:
            st.image("Logo_Idee2 copy.png", width=300)
        st.markdown("<h2 style='color: #ff5733;'> <b>Fit through College🏋️</b> </h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: grey;'> <b>Your individual training plan that keeps you fit through college</b> </h4>", unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["*Create Training Plan*", "*Current Training Plan*", "*Completed Training Plans*"])

        with tab1:
            st.write("To create a new training plan, please open the sidebar by clicking on the arrow on the top left and fill in the required details.")
            fitness_levels = st.session_state.df_exercises['level'].unique()
            muscles = st.session_state.df_exercises["primaryMuscles"].unique()
            
            st.sidebar.markdown('<p style="color: #ff5733; font-weight: bold; font-size: 20px;">Plan your fitness routine💪</p>', unsafe_allow_html=True)
            st.sidebar.markdown("__*Fitness Level*__")
            level = st.sidebar.selectbox("How would you rate your fitness level?", fitness_levels, key="fitness_level_selectbox")
            
            st.sidebar.markdown("__*Muscles*__")
            muscles = st.sidebar.multiselect("Which muscles do you want to train?", muscles, key="muscles_multiselect")
            
            st.sidebar.markdown("__*Week*__")
            selected_week = st.sidebar.date_input("When does your training week start?", value=None, min_value=None, max_value=None, key=None)
            
            st.sidebar.markdown("__*Training Days*__")
            selected_days = st.sidebar.multiselect("On which days do you want to train?", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], key="training_days_multiselect")
            
            st.sidebar.markdown("__*Time of Training*__")
            training_time = st.sidebar.time_input("At what time do you want to train?", value=None, key="training_time_input")
            
            filter_button = st.sidebar.button("Create Weekly Training Plan", key="create_training_plan_button")
            
            if filter_button:
                if selected_week:
                    start_week = selected_week
                    end_week = start_week + timedelta(days=6)
                    
                    filtered_df = st.session_state.df_exercises[st.session_state.df_exercises['level'] == level]
                    if muscles:
                        filtered_df = filtered_df[filtered_df["primaryMuscles"].isin(muscles)]

                    st.subheader(f"{start_week.strftime('%d.%m.%Y')} - {end_week.strftime('%d.%m.%Y')}")
                    
                    user_training_plan = create_training_plan(filtered_df, selected_days, start_week)
                    st.session_state.df_user_plans = user_training_plan
                    
                    for day, exercises in user_training_plan.groupby('day'):
                        st.subheader(f"{day} - {training_time}")
                        for _, exercise in exercises.iterrows():
                            st.markdown(f"<h3><em>{exercise['exercise_name']}</em></h3>", unsafe_allow_html=True)
                            st.write(f"**Level**: {exercise['level']}")
                            st.write(f"**Muscles**: {exercise['primaryMuscles']}")
                            st.write(f"**Instructions**: {exercise['instructions']}")
                           
                            muscle = exercise['primaryMuscles']
                            if muscle in muscle_images:
                                st.image(muscle_images[muscle], width=100)
        with tab2:
            current_training_plan()
        
        with tab3:
            completed_training_plans_page()

        # Logout button
        if st.sidebar.button("Logout", key="logout_button", help="Click here to logout"):
            st.session_state['authentication'] = False
            st.session_state['username'] = ""

def login_page():
    """ Login an existing user. """
    cols = st.columns(3)
    with cols[1]:
        st.image("Logo_Idee2 copy.png", width=300)
    st.markdown("<h2 style='color: #ff5733;'> <b>Login</b>📝 </h2>", unsafe_allow_html=True)
    with st.form(key='login_form'):
        st.session_state['username'] = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            authenticate(st.session_state.username, password)

def register_page():
    """ Register a new user. """
    cols = st.columns(3)
    with cols[1]:
        st.image("Logo_Idee2 copy.png", width=300)
    st.markdown("<h2 style='color: #ff5733;'> <b>Register</b>📝 </h2>", unsafe_allow_html=True)
    with st.form(key='register_form'):
        new_username = st.text_input("New Username")
        new_name = st.text_input("Name")
        new_password = st.text_input("New Password", type="password")
        if st.form_submit_button("Register"):
            hashed_password = bcrypt.hashpw(new_password.encode('utf8'), bcrypt.gensalt()) # Hash the password
            hashed_password_hex = binascii.hexlify(hashed_password).decode() # Convert hash to hexadecimal string
            
            # Check if the username already exists
            if new_username in st.session_state.df_users['username'].values:
                st.error("Username already exists. Please choose a different one.")
                return
            else:
                new_user = pd.DataFrame([[new_username, new_name, hashed_password_hex]], columns=DATA_COLUMNS)
                st.session_state.df_users = pd.concat([st.session_state.df_users, new_user], ignore_index=True)
                
                # Writes the updated dataframe to GitHub data repository
                st.session_state.github.write_df(DATA_FILE_LOGIN, st.session_state.df_users, "added new user")
                st.success("Registration successful! You can now log in.")

def authenticate(username, password):
    """ 
    Initialize the authentication status.

    Parameters:
    username (str): The username to authenticate.
    password (str): The password to authenticate.    
    """
    login_df = st.session_state.df_users
    login_df['username'] = login_df['username'].astype(str)

    if username in login_df['username'].values:
        stored_hashed_password = login_df.loc[login_df['username'] == username, 'password'].values[0]
        stored_hashed_password_bytes = binascii.unhexlify(stored_hashed_password) # convert hex to bytes
        
        # Check the input password
        if bcrypt.checkpw(password.encode('utf8'), stored_hashed_password_bytes): 
            st.session_state['authentication'] = True
            st.success('Login successful')
            st.rerun()
        else:
            st.error('Incorrect password')
    else:
        st.error('Username not found')

def init_github():
    """Initialize the GithubContents object."""
    if 'github' not in st.session_state:
        st.session_state.github = GithubContents(
            st.secrets["github"]["owner"],
            st.secrets["github"]["repo"],
            st.secrets["github"]["token"])
        print("github initialized")

def init_credentials():
    """Initialize or load the dataframe."""
    if 'df_users' in st.session_state:
        pass

    if st.session_state.github.file_exists(DATA_FILE_LOGIN):
        st.session_state.df_users = st.session_state.github.read_df(DATA_FILE_LOGIN)
    else:
        st.session_state.df_users = pd.DataFrame(columns=DATA_COLUMNS)

def main():
    init_github() # Initialize the GithubContents object
    init_credentials() # Loads the credentials from the Github data repository

    if 'authentication' not in st.session_state:
        st.session_state['authentication'] = False

    if not st.session_state['authentication']:
        options = st.sidebar.selectbox("Select a page", ["Login", "Register"])
        if options == "Login":
            login_page()
        elif options == "Register":
            register_page()

    else:
        main_fitness()

if __name__ == "__main__":
    main()

