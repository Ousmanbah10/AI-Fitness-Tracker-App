#############################################################################
#Modules.py
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

from internals import create_component
import streamlit as st
from streamlit_auth0 import login_button as auth0_login_button
import streamlit.components.v1 as components
from datetime import datetime, timedelta, date
import time
import uuid
import random
from config import config
import urllib.parse
from google.cloud import bigquery  , storage 
from data_fetcher import (
    get_user_workouts, 
    create_user_post , 
    get_user_id_from_auth0_id, 
    insert_new_user, 
    upload_image_to_gcs,
    get_all_other_users,
    get_friends,
    add_friend,
    get_genai_advice,
    
    )


from challenge_fetcher import (
    get_user_points,
    log_user_activity,
    create_challenge,
    join_challenge,
   log_workout,
   )


# Access configuration values
AUTH0_DOMAIN = config["AUTH0_DOMAIN"]
AUTH0_CLIENT_ID = config["AUTH0_CLIENT_ID"]
AUTH0_CALLBACK_URL = config["AUTH0_CALLBACK_URL"]



# This one has been written for you as an example. You may change it as wanted.
def display_my_custom_component(value):
    """Displays a 'my custom component' which showcases an example of how custom
    components work.
    value: the name you'd like to be called by within the app
    """
    # Define any templated data from your HTML file. The contents of
    # 'value' will be inserted to the templated HTML file wherever '{{NAME}}'
    # occurs. You can add as many variables as you want.
    data = {
       
    'NAME': value,
 }
    # Register and display the component by providing the data and name
    # of the HTML file. HTML must be placed inside the "custom_components" folder.
    html_file_name = "my_custom_component"
    create_component(data, html_file_name)


def display_post(full_name, username, user_image, timestamp, content, post_image=None ):

    post_data = {
        "FULL_NAME": full_name,
        "USERNAME": username,
        "USER_IMAGE": user_image,
        "TIMESTAMP": timestamp,
        "CONTENT": content,
    }
    
    
    # Only add POST_IMAGE if it's not None (prevents broken image tag)
    if post_image:
        post_data["POST_IMAGE"] = post_image
        
    # Specify the HTML file to display the post
    html_file_name = "post_component"

    # Call create_component to render the post in the Streamlit app
    create_component(post_data, html_file_name, height=600)


def display_activity_summary(workouts_list):
    """
    Displays the activity summary and returns summary stats for use elsewhere.
    """
    
    workout_summary = {
        "workout_id": 0,
        "start_time": "",
        "end_time": "",
        "total_distance": 0,
        "total_steps": 0,
        "total_calories": 0,
        "start_coordinate": None,
        "end_coordinate": None,
        "total_workout_time": 0,
        "message": ""
    }
    
    recap = {'crafted_message': ""}

    if not workouts_list:
        
        recap['crafted_message'] = 'No Available Data To Display'
        create_component(recap, "Activity_Summary", height=500)
        return workout_summary  # <- Still return something

    for workout in workouts_list:
        workout_summary["workout_id"] = workout["workout_id"]
        workout_summary["total_distance"] += workout["distance"]
        workout_summary["total_steps"] += workout["steps"]
        workout_summary["total_calories"] += workout["calories_burned"]
        workout_summary["start_time"] = datetime.strptime(workout["start_timestamp"], "%Y-%m-%d %H:%M:%S")
        workout_summary["end_time"] = datetime.strptime(workout["end_timestamp"], "%Y-%m-%d %H:%M:%S")
        workout_summary["start_coordinate"] = workout["start_lat_lng"]
        workout_summary["end_coordinate"] = workout["end_lat_lng"]

        workout_duration = (workout_summary["end_time"] - workout_summary["start_time"]).total_seconds() / 60
        workout_summary["total_workout_time"] += workout_duration

    recap['crafted_message'] = f"""
        Great job! 🎉 <br><br>
        Total Workout Distances : {workout_summary['total_distance']} km <br>
        Total Workout Steps : {workout_summary['total_steps']} steps <br>
        Total Calories Burnt : {workout_summary['total_calories']} calories 🏃‍♂️🔥 <br>
        Total workout Durations : {round(workout_summary['total_workout_time'], 1)} minutes <br>
        Keep up the momentum! 🚀💪
        """

    create_component(recap, "Activity_Summary", height=500)

    return workout_summary 


def load_global_css():
    st.markdown("""
    <style>
    /* Apply to all Streamlit buttons */
    div[data-testid="stButton"] > button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 30px;
        font-weight: 600;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #388E3C;
    }
    </style>
    """, unsafe_allow_html=True) 


def display_recent_workouts(workouts_list):
    
    html_file_name = "recent_workouts"

    if not workouts_list:
        
        no_workouts_html = """
        <div class="workout-item">
            <h3>No recent workouts to display.</h3>
        </div>
        """
        create_component({"WORKOUTS_CONTENT": no_workouts_html}, html_file_name, height=200)
        return

    html_for_workouts = ""
    for i, workout in enumerate(workouts_list, start=1):
        
        start_time = workout.get("start_timestamp", "N/A")
        end_time = workout.get("end_timestamp", "N/A")
        distance = workout.get("distance", "N/A")
        steps = workout.get("steps", "N/A")
        calories = workout.get("calories_burned", "N/A")
        start_coords = workout.get("start_lat_lng", "N/A")
        end_coords = workout.get("end_lat_lng", "N/A")
        total_time = "N/A"

        workout_html = f"""
        <div class="workout-item">
          <h3>🏋️‍♂️ Workout {i}</h3>
          <p><strong>🕒 Start Time:</strong> {start_time}</p>
          <p><strong>🕒 End Time:</strong> {end_time}</p>
          <p><strong>📏 Distance:</strong> {distance} km</p>
          <p><strong>👟 Steps:</strong> {steps}</p>
          <p><strong>🔥 Calories Burned:</strong> {calories}</p>
          <p><strong>📍 Start Coords:</strong> {start_coords}</p>
          <p><strong>📍 End Coords:</strong> {end_coords}</p>
        </div>
        """
        html_for_workouts += workout_html

    create_component({"WORKOUTS_CONTENT": html_for_workouts}, html_file_name, height=400)


def display_genai_advice(user_id):
    """
    Displays GenAI-generated advice in a stylized format using Streamlit.
    """

    # Fetch advice
    advice = get_genai_advice(user_id)
    if not advice:
        st.warning("⚠️ Unable to generate advice at the moment.")
        return

    # Define headers
    headers = [
        "Stay Motivated 💪",
        "Embrace Challenges 🚀",
        "Believe in Yourself ⭐",
        "Keep Moving Forward ➡️"
    ]

    # Try to use content1–content4 keys first
    advice_list = [
        advice.get("content1"),
        advice.get("content2"),
        advice.get("content3"),
        advice.get("content4")
    ]

    # Fallback: Split a long single string if content1–4 are missing
    if not any(advice_list) and advice.get("content"):
        parts = advice["content"].split(". ")
        advice_list = [part.strip() + "." for part in parts[:4]]

    # Clean up: remove any None values
    advice_list = [a for a in advice_list if a]

    # Add custom CSS styling
    st.markdown("""
    <style>
        .motivation-container {
            margin-top: 25px;
        }
        .motivation-header {
            font-size: 22px;
            font-weight: 700;
            color: #222;
            margin-bottom: 5px;
        }
        .motivation-card {
            background-color: #f9fdf9;
            border-left: 4px solid #48bb78;
            padding: 12px 18px;
            margin-bottom: 30px;
            border-radius: 6px;
            box-shadow: 0px 4px 10px rgba(72, 187, 120, 0.15);
            font-size: 16px;
            color: #276749;
            font-weight: 500;
        }
    </style>
    """, unsafe_allow_html=True)

    # Render advice blocks
    st.markdown('<div class="motivation-container">', unsafe_allow_html=True)
    for header, text in zip(headers, advice_list):
        st.markdown(f"""
        <div class="motivation-header">{header}</div>
        <div class="motivation-card">{text}</div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

        
    



def display_my_community_page(valuee):
    
    """
    Display the community page with user's data, GenAI advice, and friends' posts.
    
    Args:
        value: A list containing [genaiadvice, friends_posts, user]
            - genaiadvice: Dictionary with GenAI advice information
            - friends_posts: List of dictionaries with friends' post information
            - user: Dictionary with user information
    """

    genaiadvice = valuee[0]
    friends_posts = valuee[1]
    user = valuee[2]
    
    image_url = "https://media.istockphoto.com/id/2153823097/photo/cheerful-athletic-couple-jogging-through-the-park.jpg?s=1024x1024&w=is&k=20&c=UF2qKPawKinDKsVYhPHSDCdmUjAtJ6SJOjAL6kBkb0Y="
    if not user or not friends_posts:
        data = {
            "message": f"""
            Welcome! 🎉 <br><br>
            You don't have any friends yet <br>
            Please add friends to view our community <br><br>
            Start connecting today! 👋
            """
        }
        html_file_name = "no_friends_community_page"
        create_component(data, html_file_name,1900)
        return

    data = {
    "USERNAME": user["full_name"],
    "GENAIADVICETIMESTAMP": genaiadvice["timestamp"],
    "GENAIADVICECONTENT": genaiadvice["content"],
    "GENAIADVICEIMAGE": image_url,
    "user_initial": user["full_name"][0].upper(),          
    "user_profile_photo": user["profile_image"],    
    
    }

    n = 0
    for i in range(10):
        
        if i < len(friends_posts):
            n += 1
            data[f"FRIENDSPOSTS{i}"] = friends_posts[i]
        else:
            data[f"FRIENDSPOSTS{i}"] = None
    
    height = (n * 350) + 1250

    html_file_name = "community_page"
    create_component(data, html_file_name,height)


def handle_auth():
    """
    Handles authentication with Auth0 and updates session state.
    """
    # The Auth0 login button doesn't support custom text, so we use it as is
    auth_result = auth0_login_button(
        client_id=AUTH0_CLIENT_ID,
        domain=AUTH0_DOMAIN,
        # redirect_uri=AUTH0_CALLBACK_URL  # Explicitly set the redirect URI
    )

    if auth_result:
        st.session_state["logged_in"] = True
        # Make sure this ID field matches what your Auth0 rule/action is returning
        st.session_state["user_id"] = auth_result["https://e3-ai-shoe-starter.com/internal_user_id"]
        st.session_state["user_email"] = auth_result.get("email")
    
        st.rerun()


def logout():
    """
    Logs out the user and redirects to the home page.
    """
    if st.sidebar.button("Logout"):
        # Clear session state
        st.session_state["logged_in"] = False
        st.session_state["user_id"] = None
        st.session_state["page"] = "login"

        # # Use localhost URL to match our callback approach
        return_url = AUTH0_CALLBACK_URL.replace('/callback', '')


        # Build full logout URL
        logout_url = (
            f"https://{AUTH0_DOMAIN}/v2/logout?"
            f"client_id={AUTH0_CLIENT_ID}&"
            f"returnTo={urllib.parse.quote(return_url)}&"
            f"federated"
        )

        # Redirect to Auth0 logout, then redirect to app
        st.markdown(f"<meta http-equiv='refresh' content='0; URL={logout_url}' />", unsafe_allow_html=True)


def display_sidebar():
    """Display the sidebar with logo and login message."""

    st.sidebar.image("custom_components/media/e3_ai_shoe.png", width=175)
    st.sidebar.markdown("---")
    
    # Display this only when not logged in
    if not st.session_state.get("logged_in", False):
        # Add some featured benefits
        st.sidebar.markdown("### App Features")
        st.sidebar.markdown("Please Login to explore Features 😊")


def handle_new_user(auth0_id, user_id=None):
    """
    Handle new user profile creation.
    """
    
    st.title("🚀 Welcome New User!")
    st.subheader("Let's complete your profile")
    
    # Form for user information
    name = st.text_input("Full Name")
    username = st.text_input("Choose a Username")
    dob = st.text_input("Date of Birth (MMDDYYYY)")
    image = st.text_input(
        "Profile Image URL (optional)", 
        value="https://thenounproject.com/icon/user-default-4154905/"
    )
    
    # Form validation message
    if not (name.strip() and username.strip() and dob.strip()):
        st.warning("Please fill in all required fields.")
    elif not (dob.isdigit() and len(dob) == 8):
        st.error("❌ Date of Birth must be exactly 8 digits (MMDDYYYY).")
    
    # Save profile button
    if st.button("Save Profile"):
        if name and username and dob and len(dob) == 8 and dob.isdigit():
            with st.spinner("Creating your profile..."):
                # Generate a user ID if none exists
                if not user_id:
                    import random
                    user_id = f"user{random.randint(1000, 9999)}"
                
                # Insert the new user
                email = st.session_state.get("user_email", "")
                result = insert_new_user(user_id, name, username, dob, image, auth0_id,email)
                
                if result:
                    st.success("✅ Profile created successfully!")
                    st.info("Please log in again to access your account.")
                    # Clear session state for clean logout
                    time.sleep(2)
                    st.session_state.clear()
                    st.rerun()
                else:
                    st.error("❌ Error creating profile. Please try again.")
        else:
            st.warning("Please fill in all fields correctly.")


def show_activity_page(user):
    
    
    # Get workout data
    workout_data = get_user_workouts(user)
    if len(workout_data) > 0:
        # Limit to 3 most recent workouts
        recent_workouts = workout_data[:3] if len(workout_data) >= 3 else workout_data
        
        # Display recent workouts
        display_recent_workouts(recent_workouts)
        
        # Display activity summary (total of those workouts)
        display_activity_summary(recent_workouts)
        display_share_stats(workout_data[0], user)
    else:    
        mock_data = [{'workout_id': 'workout1', 'start_timestamp': '2024-07-29 07:00:00', 'end_timestamp': '2024-07-29 08:00:00', 'start_lat_lng': (37.7749, -122.4194), 'end_lat_lng': (37.8049, -122.421), 'distance': 0, 'steps': 0, 'calories_burned': 0.0}]
        display_share_stats(mock_data[0], user)


def display_share_post(UserId):
    """Display a share stats section with image upload using Streamlit"""
    
    st.markdown("---")
    
    share_container = st.container()
    
    # Add green header
    share_container.markdown(
        """
        <div style="background: linear-gradient(135deg, #2e7d32 0%, #388e3c 100%); 
                    color: white; 
                    padding: 5px 5px; 
                    border-radius: 8px;">
            <h3 style="margin: 0; display: flex; align-items: center;">
                <span style="margin-right: 8px;">📣</span> Share an Image with Your Community
            </h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # User customizable text input
    with share_container:
        stat_input = st.text_area(
            label="Post Caption....",
            label_visibility="hidden"
        )
        
        # Add image upload option
        st.markdown("<strong>Add an image :</strong>", unsafe_allow_html=True)
        uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], label_visibility="hidden")
        image_url = None
        # Preview the image if one was uploaded
        if uploaded_image is not None:
            st.image(uploaded_image, caption="Image preview", use_container_width=True)
           
        value = UserId 
        if st.button("Share a photo", type="primary"):
            try:
                image_url = upload_image_to_gcs(uploaded_image)
                st.info(f"Image uploaded successfully.")
            except Exception as e:
                st.error(f"Error uploading image: {e}")

            post_id = create_user_post(
                value, 
                content=stat_input, 
                image_url=image_url  
            )
            st.success("🎉 Yourpost has been shared!")
            st.rerun()


def display_share_stats(summary, user_id="user1"):
    """Display a share stats section with image upload using Streamlit"""
    
    st.markdown("---")
    

    # Check if we have workout data
    if len(summary) > 0:
        # Create share section container with custom styling
        share_container = st.container()
        
        # Add green header
        share_container.markdown(
            """
            <div style="background: linear-gradient(135deg, #2e7d32 0%, #388e3c 100%); 
                        color: white; 
                        padding: 10px 15px; 
                        border-radius: 8px;">
                <h3 style="margin: 0; display: flex; align-items: center;">
                    <span style="margin-right: 8px;">📣</span> Share Your Progress Stats with the Community
                </h3>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Create default stat message
        
        start_time = datetime.strptime(summary['start_timestamp'], '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(summary['end_timestamp'], '%Y-%m-%d %H:%M:%S')

        # Calculate total workout time in minutes
        total_workout_time = (end_time - start_time).total_seconds() / 60
        default_stat = (
            f"I worked out for {total_workout_time} minutes, "
            f"took {summary['steps']} steps, and burned {summary['calories_burned']} calories this week! 🔥💪"
        )
        
        # Display suggested post with green styling
        share_container.markdown(
            f"""
            <div style="background-color: #f1f8e9; 
                        border-left: 4px solid #7cb342; 
                        padding: 10px 15px; 
                        margin: 15px 0; 
                        border-radius: 0 4px 4px 0;">
                <strong>Suggested post:</strong><br/>
                <em>{default_stat}</em>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # User customizable text input
        with share_container:
            stat_input = st.text_area(
                label="Enter stat here",
                label_visibility="hidden"
            )
            
            if st.button("Share this stat", type="primary"):

                post_id = create_user_post(
                    user_id, 
                    content=stat_input, 
                )
                st.success("🎉 Your workout stat has been shared!")
    else:
        # Warning message for no data
        st.warning("⚠️ No workout data available to share.")


def display_log_workout_ui():
    """
    Displays a button to log a workout and a form to fill in workout details.
    Calls the log_workout function when the form is submitted.
    """

    # Display the Log Workout button
    if not st.session_state.get("show_workout_form", False):
        if st.button("📝 Log Workout", key="log_workout_btn"):
            st.session_state["show_workout_form"] = True
            st.rerun()
    
    # If button was clicked, show the form
    if st.session_state.get("show_workout_form"):
        st.subheader("Log Your Workout 🏃‍♂️")
        
        with st.form("workout_form"):
            # Basic info
            col1, col2 = st.columns(2)
            
            with col1:
                start_date = st.date_input("Start Date", value=datetime.now().date())
                start_time_str = st.text_input("Start Time (HH:MM)", value=datetime.now().strftime("%H:%M"))
            with col2:
                end_date = st.date_input("End Date", value=datetime.now().date())
                end_time_str = st.text_input("End Time (HH:MM)", value=datetime.now().strftime("%H:%M"))
            
            # Convert to datetime objects
            try:
                start_time = datetime.combine(start_date, datetime.strptime(start_time_str, "%H:%M").time())
                end_time = datetime.combine(end_date, datetime.strptime(end_time_str, "%H:%M").time())
            except ValueError:
                st.error("Please enter time in HH:MM format")
                start_time = datetime.combine(start_date, datetime.now().time())
                end_time = datetime.combine(end_date, datetime.now().time())
            
            # Location info
            st.subheader("Starting Location")
            start_loc_col1, start_loc_col2 = st.columns(2)
            with start_loc_col1:
                start_lat = st.number_input("Starting Latitude", value=0.0, format="%.6f")
            with start_loc_col2:
                start_long = st.number_input("Starting Longitude", value=0.0, format="%.6f")
            
            st.subheader("Ending Location")
            end_loc_col1, end_loc_col2 = st.columns(2)
            with end_loc_col1:
                end_lat = st.number_input("Ending Latitude", value=0.0, format="%.6f")
            with end_loc_col2:
                end_long = st.number_input("Ending Longitude", value=0.0, format="%.6f")
            
            # Workout metrics
            st.subheader("Workout Details")
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            with metrics_col1:
                distance = st.number_input("Total Distance (miles)", min_value=0.0, step=0.1)
            with metrics_col2:
                steps = st.number_input("Total Steps", min_value=0, step=100)
            with metrics_col3:
                calories = st.number_input("Calories Burned", min_value=0, step=50)
            
            # Cancel button and submit in columns
            cancel_col, submit_col = st.columns([1, 2])
            
            with submit_col:
                submitted = st.form_submit_button("Submit Workout")
            with cancel_col:
                cancel = st.form_submit_button("Cancel")
            
            if cancel:
                st.session_state["show_workout_form"] = False
                st.rerun()
                
            if submitted:
                # Get user ID from session state
                user_id = get_user_id_from_auth0_id(st.session_state.get("user_id"))
                
                # Call the log_workout function
                result = log_workout(
                    user_id,
                    start_time, end_time,
                    start_lat, start_long,
                    end_lat, end_long,
                    distance, steps, calories
                )
                
                # Show the result message
                if "Failed" in result:
                    st.error(result)
                else:
                    st.success(result)
                    # Reset the form state
                    st.session_state["show_workout_form"] = False
                    st.rerun()

# CHALLANGES
def display_challenge(challenge):
    """
    Displays a single challenge with a Streamlit button above the HTML component
    """
    # Prepare your data as before
    goal_type = "miles" if challenge.get("goal_miles", 0) > 0 else "runs"
    completed = challenge.get("miles_completed" if goal_type == "miles" else "runs_completed", 0)
    
    # Remove the HTML button
    join_button_html = ""
    
    # Package all data for the HTML display
    data = {
        "CHALLENGE_ID": challenge["challenge_id"],
        "CHALLENGE_TITLE": challenge["title"],
        "DIFFICULTY_CLASS": challenge["difficulty"].lower(),
        "DIFFICULTY": challenge["difficulty"],
        "GOAL_VALUE": challenge["goal_miles"],
        "GOAL_TYPE": goal_type,
        "START_DATE": challenge["start_date"],
        "END_DATE": challenge["end_date"],
        "RULES": challenge["rules"],
        "STATUS_CLASS": challenge["status"],
        "STATUS": challenge["status"].capitalize(),
        "PROGRESS_PERCENTAGE": challenge.get("progress_percentage", 0),
        "PROGRESS_COMPLETED": completed,
        "HAS_PROGRESS": challenge.get("progress_percentage", 0) > 0,
        "JOIN_BUTTON_HTML": join_button_html,
        "SHOW_POINTS": challenge.get("points", 0) > 0,
        "POINTS": challenge.get("points", 0),
    }
    
    # Create a container for the entire challenge
    with st.container():
        # If challenge is active/upcoming, add Streamlit button in a small container at the top right
        if challenge["status"] in ["active", "upcoming"]:
            # Create a small container for the button
            cols = st.columns([3, 1])
            with cols[1]:
                
                button_key = f"join_{challenge['challenge_id']}"
                # Add custom CSS to style the button similar to your HTML button
                st.markdown(
                    """
                    <style>
                    div[data-testid="stButton"] > button {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 20px;
                        padding: 5px 5px;
                        font-weight: 100;
                        width: 55px%;
                    }
                    div[data-testid="stButton"] > button:hover {
                        background-color: #388E3C;
                    }
                    </style>
                    """, 
                    unsafe_allow_html=True
                )
                
                if st.button("Join Challenge", key=button_key):
                    user_id = get_user_id_from_auth0_id(st.session_state.get("user_id"))
                    msg = join_challenge(user_id, challenge["challenge_id"])
                    
                    # Set a flag so we know this challenge was joined
                    st.session_state[f"joined_{challenge['challenge_id']}"] = True
                    
                    st.success(msg)
                    st.rerun()
        
        # Get HTML template and populate it
        with open("custom_components/challenge_component.html", "r") as f:
            html_template = f.read()
        
        html = html_template
        for key, value in data.items():
            html = html.replace(f"{{{{{key}}}}}", str(value))
       
        components.html(html, height=250, scrolling=False)

# Display each challenger card via
def display_challenges(challenges_list):
    """
    Displays a list of challenges in the Streamlit app.
    
    Args:
        challenges_list (list): List of challenge dictionaries.
    """
    if not challenges_list:
        st.write("No challenges available at the moment.")
        return
        
    for challenge in challenges_list:

        # Use the custom component to display each challenge
        display_challenge(challenge)


def display_user_challenges(user_challenges_list):
    """
    Displays a user's active challenges with progress bars.
    
    Args:
        user_challenges_list (list): List of user challenge dictionaries.
    """
    # if not user_challenges_list:
    #     st.write("You haven't joined any challenges yet.")
    #     return

        
    # First, display active challenges
    active_challenges = [c for c in user_challenges_list if c['status'] == 'active']
    if active_challenges:
        st.subheader("🏃‍♂️ Active Challenges")
        for challenge in active_challenges:
            with st.container():
                # Challenge title and info
                st.markdown(f"### {challenge['title']}")
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Goal info
                    if challenge['goal_type'] == 'miles':
                        st.write(f"🎯 Goal: {challenge['miles_completed']:.1f}/{challenge['goal_value']} miles")
                    elif challenge['goal_type'] == 'runs':
                        st.write(f"🎯 Goal: {challenge['runs_completed']}/{challenge['goal_value']} runs")
                        
                    # Progress bar
                    st.progress(challenge['progress_percentage'] / 100)
                    st.write(f"Progress: {challenge['progress_percentage']}%")
                
                with col2:
                    st.write(f"**Points earned:** {challenge['points']}")
                    st.write(f"**Ends:** {challenge['end_date']}")
                    
                    # Button to see challenge details
                    if st.button("View Details", key=f"details_{challenge['challenge_id']}"):
                        st.session_state['selected_challenge'] = challenge['challenge_id']
                        st.rerun()
                
                st.markdown("---")
    
    # Then, display upcoming challenges the user has joined
    upcoming_challenges = [c for c in user_challenges_list if c['status'] == 'upcoming']
    if upcoming_challenges:
        st.subheader("🔜 Upcoming Challenges")
        for challenge in upcoming_challenges:
            with st.container():
                st.markdown(f"### {challenge['title']}")
                st.write(f"🎯 Goal: {challenge['goal_value']} {challenge['goal_type']}")
                st.write(f"📅 Starts: {challenge['start_date']}")
                st.write(f"📅 Ends: {challenge['end_date']}")
                st.markdown("---")
    
    # Finally, display completed challenges
    completed_challenges = [c for c in user_challenges_list if c['status'] == 'closed']
    if completed_challenges:
        st.subheader("✅ Completed Challenges")
        for challenge in completed_challenges:
            with st.container():
                st.markdown(f"### {challenge['title']}")
                
                # Calculate final progress and completion status
                final_progress = challenge['progress_percentage']
                completion_status = "Completed" if final_progress >= 100 else "Incomplete"
                status_color = "green" if final_progress >= 100 else "orange"
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"🎯 Goal: {challenge['goal_value']} {challenge['goal_type']}")
                    st.write(f"📊 Final Progress: {final_progress}%")
                    st.write(f"🏆 Status: <span style='color:{status_color};'>{completion_status}</span>", unsafe_allow_html=True)
                
                with col2:
                    st.write(f"**Points earned:** {challenge['points']}")
                    st.write(f"**Ended:** {challenge['end_date']}")
                
                st.markdown("---")


def display_create_challenge_ui():
    from datetime import date
    import streamlit as st
    
    # Button to show the form
    if not st.session_state.get("show_create_form", False):
        
        if st.button(" Create New Challenge For The Community"):
            st.session_state["show_create_form"] = True
            st.rerun()

    # The form only shows when this is True
    if st.session_state.get("show_create_form"):
        st.markdown("## Challenge Yourself! 🏆")
        
        # Add a back button above the form
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("← Back", key="back_button"):
                st.session_state["show_create_form"] = False
                st.rerun()
        
        with st.form("new_challenge_form"):
            title = st.text_input("🏁 Challenge Title *", max_chars=50)
            rules = st.text_area("📋 Rules / Description *")
            difficulty = st.selectbox("🔥 Difficulty *", ["Beginner", "Intermediate", "Advanced"])
            
            # Date inputs in two columns
            date_col1, date_col2 = st.columns(2)
            with date_col1:
                start_date = st.date_input("📆 Start Date *", min_value=date.today())
            with date_col2:
                end_date = st.date_input("🏁 End Date *", min_value=start_date)
            
            # Goal inputs in two columns
            goal_col1, goal_col2 = st.columns(2)
            with goal_col1:
                goal_miles = st.number_input("🏃 Goal Miles *", min_value=0.0, step=1.0)
            with goal_col2:
                goal_runs = st.number_input("🔁 Goal Runs *", min_value=0, step=1)
            
            # Points and participants in two columns
            points_col1, points_col2 = st.columns(2)
            with points_col1:
                points = st.number_input("⭐ Points Awarded *", min_value=0, step=50)
            with points_col2:
                max_participants = st.number_input("👥 Max Participants (optional)", min_value=1, step=1, value=10)
            
            # Form buttons in two columns
            button_col1, button_col2 = st.columns([3, 1])
            with button_col1:
                submitted = st.form_submit_button("✅ Submit Challenge")
            with button_col2:
                canceled = st.form_submit_button("❌ Cancel")

            if canceled:
                st.session_state["show_create_form"] = False
                st.rerun()

            if submitted:
                # Basic validation
                if (
                    not title.strip() or not rules.strip()
                    or (goal_miles <= 0 and goal_runs <= 0)
                    or points <= 0
                ):
                    st.warning("🚨 Please complete all required fields *.")
                else:
                    try:
                        challenge_id = create_challenge(
                            title=title,
                            rules=rules,
                            difficulty=difficulty,
                            start_date=start_date.strftime("%Y-%m-%d"),
                            end_date=end_date.strftime("%Y-%m-%d"),
                            goal_miles=goal_miles,
                            goal_runs=goal_runs,
                            points=points,
                            max_participants=int(max_participants)
                        )
                        st.success(f"🎉 Challenge '{title}' created successfully!")
                        st.session_state["show_create_form"] = False  # Collapse the form
                        st.rerun()
                    except Exception as e:
                        st.error(f"⚠️ Failed to create challenge: {e}")


# LEADERBOARD
def display_leaderboard():
    """
    Displays a simple overall leaderboard using the UserPoints table,
    sorted by total points (descending), using clean Streamlit formatting.
    """

    try:
        client = bigquery.Client(project="e3-ai-shoe-starter")

        # Query top 20 users with most points
        query = """
        SELECT 
            up.user_id,
            u.Name AS full_name,
            u.Username AS username,
            up.total_points AS points
        FROM `e3-ai-shoe-starter.section_e3.UserPoints` up
        JOIN `e3-ai-shoe-starter.section_e3.Users` u ON up.user_id = u.UserId
        ORDER BY up.total_points DESC
        LIMIT 20
        """

        results = client.query(query).result()

        # Render header
        current_user_id = get_user_id_from_auth0_id(st.session_state.get("user_id", ""))
        

        # Display table manually
        st.markdown("---")
        for i, row in enumerate(results, start=1):
            is_current_user = (row.user_id == current_user_id)
            name_display = f"**{row.full_name}**" if is_current_user else row.full_name
            username_display = f"`{row.username}`"
            points_display = f"**{row.points} ⭐**" if is_current_user else f"{row.points} ⭐"

            st.markdown(f"**#{i}** — {name_display} ({username_display}) — {points_display}")

            if is_current_user:
                found_current_user = True

        

        st.markdown("---")

    except Exception as e:
        st.error(f"Error loading leaderboard: {e}")

# FRIENDS
def show_friend_section(current_user_id):
    st.markdown("## 👫 Your Friends", unsafe_allow_html=True)

    friends = get_friends(current_user_id)
    if friends:
        st.markdown("<ul style='padding-left: 1.2rem;'>", unsafe_allow_html=True)
        for friend in friends:
            st.markdown(f"<li style='margin-bottom: 6px;'>{friend.friend_name}</li>", unsafe_allow_html=True)
        st.markdown("</ul>", unsafe_allow_html=True)
    else:
        st.info("You have no friends yet.")

    st.markdown("---")
    
    st.markdown("## 🔍 Add New Friends", unsafe_allow_html=True)

    users = get_all_other_users(current_user_id)

    if users:
        for user in users:
            with st.expander(f"👤 {user.Name}"):
                if st.button(f"➕ Add {user.Name}", key=user.UserId):
                    errors = add_friend(current_user_id, user.UserId)
                    if not errors:
                        st.success(f"🎉 {user.Name} added as a friend!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add friend. Maybe already added?")
    else:
        st.info("You're already friends with everyone! 🎉")




# MY CHALLANGES PAGE
def display_single_user_challenges(challenges_list, points):
    """
    Displays user challenges with a simple UI in Streamlit.
    
    Args:
        challenges_list (list): List of user challenge dictionaries from get_single_user_challenges.
    """
    # Display page header
    st.title("My Challenges 🏅")
    
    # Show total points
    total_points = points

    st.markdown(f"<h3>Total Points: {total_points} ⭐</h3>", unsafe_allow_html=True)
    
    if not challenges_list:
        st.warning("You don't have any active challenges.")
        return

    sorted_challenges = sorted(challenges_list, key=lambda c: c['challenge_status'] != 'active')

    st.subheader(f"🏆 Your Challenge(s) ")

    for challenge in sorted_challenges:
        with st.container():
            st.markdown("""
            <style>
            .challenge-card {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px 15px;
                margin-bottom: 15px;
                background-color: #eaffea;
            }
            </style>
            """, unsafe_allow_html=True)

            st.markdown('<div class="challenge-card">', unsafe_allow_html=True)

            st.markdown(f"### {challenge['title']}")
            if challenge['user_status'] == 'done':
                st.success("🎉 Congratulations! You completed this challenge. Go to *My Challenges* to join a new one.")
                
            st.write(f"🎯 Goal Type: Run {challenge['goal_miles']} Miles or Complete {challenge['goal_runs']} runs")
            st.write(f"📋 **Rules:** {challenge['rules']}")
            st.write(f"⚙️ **Difficulty:** {challenge['difficulty']}")
            st.write(f"📆 **Start:** {challenge['start_date']} — **End:** {challenge['end_date']}")
            st.write(f"📊 **Challenge Status:** `{challenge['user_status'].capitalize()}`")

            col1, col2, col3 = st.columns(3)
            col1.metric("🏃‍♂️ Miles Completed", f"{challenge['miles_completed']:.1f}")
            col2.metric("🔁 Runs Completed", challenge['runs_completed'])
            

            # Show join date if present
            if 'join_timestamp' in challenge:
                join_date = challenge['join_timestamp'].strftime("%Y-%m-%d")
                st.caption(f"📅 Joined on {join_date}")

            st.markdown(f"""
                <style>
                    div[data-testid="stButton"] button[data-testid="baseButton"][aria-label="Log Activity {challenge['challenge_id']}"] {{
                        background-color: #90ee90;
                        color: black;
                        font-weight: bold;
                    }}
                </style>
            """, unsafe_allow_html=True)

            

            if not challenge['user_status'] == 'done':
                
                # Show "Log Activity" button
                if st.button(f"Log Activity", key=f"log_btn_{challenge['challenge_id']}"):
                    st.session_state['logging_challenge'] = challenge['challenge_id']

                # ✅ Only show the form for the selected challenge
                if st.session_state.get("logging_challenge") == challenge["challenge_id"]:
                    with st.form(f"log_form_{challenge['challenge_id']}"):
                        miles_input = st.number_input("Enter miles completed", min_value=0.0, step=0.1, key=f"miles_{challenge['challenge_id']}")
                        runs_input = st.number_input("Enter runs completed", min_value=0, step=1, key=f"runs_{challenge['challenge_id']}")
                        submitted = st.form_submit_button("Submit Log")

                        if submitted:
                            user_id = st.session_state.get("user_id", challenge["user_id"])
                            user = get_user_id_from_auth0_id(user_id)
                            
                            message = log_user_activity(user_id, challenge["challenge_id"], miles_input, runs_input)
                            st.success(message)

                            # ✅ Hide the form on submission
                            st.session_state["logging_challenge"] = None
                            st.rerun()

                
            # Close card container
            st.markdown('</div>', unsafe_allow_html=True)