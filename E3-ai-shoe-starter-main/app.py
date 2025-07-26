
import streamlit as st
import urllib.parse
import streamlit.components.v1 as components
from streamlit_auth0 import login_button as auth0_login_button 
from config import config
from internals import create_component
import time
from dotenv import load_dotenv
load_dotenv()
from datetime import date, timedelta
from modules import (
    display_my_custom_component,
    display_post,
    display_genai_advice,
    display_activity_summary,
    display_recent_workouts,
    display_my_community_page,
    display_sidebar,
    handle_auth,
    logout,
    get_user_id_from_auth0_id,
    show_activity_page,
    display_share_stats,
    display_share_post,
    handle_new_user,
    display_challenges,
    display_leaderboard,
    display_single_user_challenges,
    display_create_challenge_ui,
    display_log_workout_ui,
    load_global_css,
    show_friend_section
   
    
    
)
from data_fetcher import (
    get_user_posts,
    get_genai_advice,
    get_user_profile,
    get_user_sensor_data,
    get_user_workouts,
    get_data_for_community_page,
    create_user_post,
    insert_new_user,
   
)
from challenge_fetcher import (
    get_challenges,
    get_user_points,
    get_single_user_challenges,
    
)



# Access configuration values
AUTH0_DOMAIN = config["AUTH0_DOMAIN"]
AUTH0_CLIENT_ID = config["AUTH0_CLIENT_ID"]
AUTH0_CALLBACK_URL = config["AUTH0_CALLBACK_URL"]



# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "login"


if "selected_challenge" not in st.session_state:  
    st.session_state["selected_challenge"] = None

def check_authentication():
    """
    Simple authentication check that prevents unnecessary redirects
    """
    # If already logged in, return True
    if st.session_state.get("logged_in", False):
        return True
    
    # If not logged in, return False
    return False
    
def display_login_page():
    """
    Displays the simplified login page with the Auth0 button.
    """
    # Display the header component
    login_data = {
        "APP_TITLE": "E3 AI SHOE TRACKER",
        "LOGO_URL": "custom_components/media/e3_ai_shoe.png",
    }
    
    # Create custom login component without the button
    create_component(login_data, "login_component", height=540)
    
    # Add some space
    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
    
    # Now display the Auth0 login button
    handle_auth()

 

def display_app_content(user_id):
    """
    Displays the main app content after login.
    """
    # Navigation options
    col1, col2, col3 = st.sidebar.columns([1, 4, 0.5])
    with col2:
        page = st.radio(
            "Navigation",
            ["Home", "Post", "GenAI Advice", "Activity Summary", "Recent Workouts","Friends", "Challenges", "My Challenges", "Leaderboard"],
        )

    # Show logout button AFTER navigation
    st.sidebar.markdown("---")
    logout()
    
    # Display selected page content
    if page == "Home":
        
        mockdata = get_data_for_community_page(user_id)
        display_my_community_page(mockdata)

    elif page == "Post":
        profile = get_user_profile(user_id)

        
        if profile is None:
            st.error("User profile not found.")
            return
            
        full_name = profile["full_name"]
        username = profile["username"]
        user_image = profile["profile_image"]

        if user_image == "http://example.com/images/alice.jpg":
            user_image = "https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg"

        # Fetch user posts
        st.header("User Posts")
        user_posts = get_user_posts(user_id)
        
        if not user_posts:
            st.write("No posts to display.")
            
        else:
            for post in user_posts:
                timestamp = post.get("timestamp", "N/A")
                content = post.get("content", "No content available.")
                post_image = post.get("image", "")

                if post_image == "http://example.com/posts/post1.jpg":
                    post_image = "https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg"
                display_post(
                    full_name, username, user_image, timestamp, content, post_image
                )
        display_share_post(user_id)

    elif page == "GenAI Advice":

        profile = get_user_profile(user_id)
        if profile is None:
            st.error("User profile not found.")
            return
            
        full_name = profile["full_name"]

        st.markdown(
            "<h2 style='text-align: center;'>GenAI Advice</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='text-align: center;'>After analyzing your previous workouts, here is some tailored advice just for you, {full_name}!</p>",
            unsafe_allow_html=True,
        )
        display_genai_advice(user_id)

    
    elif page == "Activity Summary":

        st.header("Activity Summary")
        show_activity_page(user_id)
        

    elif page == "Recent Workouts":
        st.header("My Recent Workouts")
 
        workouts_list = get_user_workouts(user_id)
        display_recent_workouts(workouts_list)

        display_log_workout_ui()

    elif page == "Challenges":
            st.title("Challenge Yourself! 🏆")
            display_create_challenge_ui()
            # Display tabs for different challenge statuses
            tab1, tab2, tab3 = st.tabs(["Active Challenges", "Upcoming Challenges", "Past Challenges"])
            
            with tab1:
                st.header("Active Challenges")
                st.markdown("----------------")
                active_challenges = get_challenges(status="active")
                display_challenges(active_challenges)
                
            with tab2:
                st.header("Upcoming Challenges")
                st.markdown("----------------")
                upcoming_challenges = get_challenges(status="upcoming")
                display_challenges(upcoming_challenges)
                
            with tab3:
                st.header("Past Challenges")
                st.markdown("----------------")
                closed_challenges = get_challenges(status="closed")
                display_challenges(closed_challenges)
                
    elif page == "My Challenges":

       
        total_points = get_user_points(user_id)

        challenges_list = get_single_user_challenges(user_id)

        display_single_user_challenges(challenges_list, total_points)

    elif page == "Create Challenges":

        display_create_challenge_ui()

    elif page == "Friends":

        
        show_friend_section(user_id)

    elif page == "Leaderboard":
        st.title("Leaderboard 🏆🔄")

        display_leaderboard()



def main():
    """
    Main application function.
    """
    load_global_css()
    # Always display the sidebar with logo
    display_sidebar()
    
    if not st.session_state["logged_in"]:
        display_login_page()
    else:
        # Get Auth0 ID from session state after login
        auth0_id = st.session_state["user_id"]
        
        # Try to find the internal user ID associated with this Auth0 ID
        user_id = get_user_id_from_auth0_id(auth0_id)
    
        
        # Check if user has a profile
        profile = None
        if user_id:
            profile = get_user_profile(user_id)
            
        
        # If no profile exists, show the new user form
        if not profile:
            handle_new_user(auth0_id, user_id)
            return
        
        # If profile exists, show the main application
        display_app_content(user_id)



if __name__ == "__main__":
    main()