#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#
# You will re-write these functions in Unit 3, and are welcome to alter the
# data returned in the meantime. We will replace this file with other data when
# testing earlier units.
#############################################################################

import random
from google.cloud import bigquery, storage
from datetime import datetime, timezone, timedelta
import uuid
import streamlit as st
import google.generativeai as genai
import os


def get_user_workouts(user_id):

    """Returns a list of user's workouts from BigQuery."""
    client = bigquery.Client(project="e3-ai-shoe-starter")
    
    query = """
    SELECT 
        WorkoutId,
        StartTimestamp,
        EndTimestamp,
        StartLocationLat,
        StartLocationLong,
        EndLocationLat,
        EndLocationLong,
        TotalDistance,
        TotalSteps,
        CaloriesBurned
    FROM `e3-ai-shoe-starter.section_e3.Workouts`
    WHERE UserId = @user_id
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
    )

    try:
        results = client.query(query, job_config=job_config).result()
        
        workouts = []
        for row in results:
            workouts.append({
                "workout_id": row.WorkoutId,
                "start_timestamp": str(row.StartTimestamp),
                "end_timestamp": str(row.EndTimestamp),
                "start_lat_lng": (row.StartLocationLat, row.StartLocationLong),
                "end_lat_lng": (row.EndLocationLat, row.EndLocationLong),
                "distance": row.TotalDistance,
                "steps": row.TotalSteps,
                "calories_burned": row.CaloriesBurned
            })
         
        return workouts
    except Exception as e:
        print(f"Error fetching workouts: {e}")
        return []


def get_user_sensor_data(user_id, workout_id):
    """Returns sensor data for a specific workout owned by the given user."""
    client = bigquery.Client(project="e3-ai-shoe-starter")

    query = """
    SELECT 
        sd.SensorId AS sensor_type,
        sd.Timestamp AS timestamp,
        sd.SensorValue AS data,
        CASE 
            WHEN sd.SensorId = 'sensor1' THEN 'bpm'
            WHEN sd.SensorId = 'sensor2' THEN 'steps'
            WHEN sd.SensorId = 'sensor3' THEN '°C'
            ELSE 'unit'
        END AS units
    FROM `e3-ai-shoe-starter.section_e3.SensorData` sd
    JOIN `e3-ai-shoe-starter.section_e3.Workouts` w
    ON sd.WorkoutID = w.WorkoutID
    WHERE w.UserId = @user_id AND sd.WorkoutID = @workout_id
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("workout_id", "STRING", workout_id)
        ]
    )

    try:
        results = client.query(query, job_config=job_config).result()
        sensor_data = []
        for row in results:
            sensor_data.append({
                "sensor_type": row.sensor_type,
                "timestamp": str(row.timestamp),
                "data": row.data,
                "units": row.units
            })
        return sensor_data
    except Exception as e:
        print(f"Error fetching sensor data: {e}")
        return []


def get_user_profile(user_id):
    """Returns information about the given user.
    """
    
    try:
        # Initialize BigQuery client
        client = bigquery.Client(project="e3-ai-shoe-starter")
        
        # Query to get user information
        user_query = """
        SELECT 
            Name as full_name, 
            Username as username, 
            FORMAT_DATE('%Y-%m-%d', DateOfBirth) as date_of_birth, 
            ImageUrl as profile_image
        FROM `e3-ai-shoe-starter.section_e3.Users`
        WHERE UserId = @user_id
        """
        
        # Set query parameters for user query
        user_params = [bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
        user_job_config = bigquery.QueryJobConfig(query_parameters=user_params)
        
        # Execute user query
        user_results = client.query(user_query, job_config=user_job_config).result()
        
        # Process user results
        user_data = None
        for row in user_results:
            user_data = {
                "full_name": row.full_name,
                "username": row.username,
                "date_of_birth": row.date_of_birth,
                "profile_image": row.profile_image,
                "friends": []  # Will be populated from a separate query
            }
            break  # We should only have one result
        
        # If no user was found, return None
        if not user_data:
            return None
        
        # Query to get user's friends
        friends_query = """
        SELECT UserId2 as friend_id
        FROM `e3-ai-shoe-starter.section_e3.Friends`
        WHERE UserId1 = @user_id
        UNION ALL
        SELECT UserId1 as friend_id
        FROM `e3-ai-shoe-starter.section_e3.Friends`
        WHERE UserId2 = @user_id
        """
        
        # Execute friends query with the same parameters
        friends_job_config = bigquery.QueryJobConfig(query_parameters=user_params)
        friends_results = client.query(friends_query, job_config=friends_job_config).result()
        
        # Add friends to user data
        for row in friends_results:
            user_data["friends"].append(row.friend_id)
        
        return user_data
        
    except Exception as e:
        print(f"Error retrieving user profile: {e}")
        return None


def get_user_posts(user_id):
    """Returns a list of a user's posts.
    """
    
    try:
        # Initialize BigQuery client
        client = bigquery.Client(project="e3-ai-shoe-starter")
        
        # Query to get user's posts
        posts_query = """
        SELECT 
            AuthorId as user_id,
            PostId as post_id,
            FORMAT_DATETIME('%Y-%m-%d %H:%M:%S', Timestamp) as timestamp,
            Content as content,
            ImageUrl as image
        FROM `e3-ai-shoe-starter.section_e3.Posts`
        WHERE AuthorId = @user_id
        ORDER BY Timestamp DESC
        """
        
        # Set query parameters
        
        query_params = [bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        
        query_job = client.query(posts_query, job_config=job_config)
        results = query_job.result()
       
        # Process posts results
        posts = []
        for row in results:
            post = {
                "user_id": row.user_id,
                "post_id": row.post_id,
                "timestamp": row.timestamp,
                "content": row.content,
                "image": row.image
            }
            posts.append(post)
            
        return posts
    except Exception as e:
        print("❌ BigQuery connection failed:", e)   
    except Exception as e:
        print(f"Error retrieving user posts: {e}")
        # If there's an error, return an empty list
        return []


def get_genai_advice(user_id):
    """
    Generate personalized advice using Google's Generative AI.
    
    Args:
        user_id (str): Unique identifier for the user
    
    Returns:
        dict: A dictionary containing advice details
    """
    try:
        # Configure Gemini API
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        
        # Initialize the generative model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prepare the prompt with personalized context
        prompt = f"Generate personalized advice for a user with ID {user_id}. "
        
        # Fetch user's workout data
        workout_data = get_user_workouts(user_id)
        
        if workout_data:
            # If workout data exists, use it to generate more specific advice
            prompt += f"\n\nWorkout History:\n{workout_data}"
            
            prompt += """
            [Generate advice based on workout history]
            [Provide insights about fitness progress]
            [Offer motivational and actionable guidance]
            
            Requirements:
            - Dont include the User
            - 2-3 sentences of advice
            - Focus on personal improvement
            - Motivational tone
            - Actionable recommendations
            """
        else:
            # Generic advice if no workout data
            prompt += """
            [Provide general life motivation]
            [Encourage personal growth]
            
            Requirements:
            - DOnt include the user 
            - 2-3 sentences of advice
            - Inspiring and constructive
            - Universal application
            """
        
        # Generate the advice
        response = model.generate_content(prompt)
        
        # Prepare the advice dictionary
        advice = {
            "advice_id": str(uuid.uuid4()),  # Generate a unique ID
            "timestamp": datetime.now().isoformat(),
            "content": response.text
        }
        
        return advice
    
    except Exception as e:
        print(f"Error generating advice: {e}")
        return None


def get_data_for_community_page(user_id):
    
    """
    Fetches data for displaying a user's community page.
    
    Returns a tuple of (gen_ai_advice, friends_posts, user_profile).
    """

    gen_ai_advice = get_genai_advice(user_id)
    
    friends = get_user_profile(user_id)['friends']
    if not friends:
        return gen_ai_advice, None , None

    friends_posts = []
    for friend in friends:
        posts = get_user_posts(friend)
       
        for post in posts:
            
            friends_posts.append(post)
    
    friends_posts.sort(key=lambda x: x['timestamp'])
    n_len = len(friends_posts)
    
    if n_len >= 9:
        friends_posts = friends_posts[:10]
    else:
        friends_posts = friends_posts[:n_len]
    user = get_user_profile(user_id)
    
    return gen_ai_advice, friends_posts , user


def create_user_post(user_id, content=None, image_url=None):
    """
    Creates a new post in BigQuery with optional content and image.
    
    Args:
        user_id (str): ID of the user creating the post
        content (str, optional): Text content of the post
        image_url (str, optional): URL of the uploaded image
    
    Returns:
        str: Generated post ID, or None if post creation fails
    """
    try:
        # Generate a unique post ID
        post_id = f'post_{str(uuid.uuid4())[:8]}'
        
        # Get current timestamp in the format specified
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Initialize BigQuery client with specific project
        client = bigquery.Client(project="e3-ai-shoe-starter")
        
        # Prepare the BigQuery insert query with full table path
        insert_query = """
        INSERT INTO `e3-ai-shoe-starter.section_e3.Posts` (PostId, AuthorId, Timestamp, ImageUrl, Content)
        VALUES (@post_id, @author_id, @timestamp, @image_url, @content)
        """
        
        # Ensure all parameters are converted to strings
        post_id = str(post_id)
        user_id = str(user_id)
        timestamp = str(timestamp)
        image_url = str(image_url) if image_url is not None else "https://cdn.statcdn.com/Statistic/635000/639015-blank-754.png"
        content = str(content) if content is not None else "My Stats"
        
        # Set query parameters (all as strings)
        query_params = [
            bigquery.ScalarQueryParameter("post_id", "STRING", post_id),
            bigquery.ScalarQueryParameter("author_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("timestamp", "STRING", timestamp),
            bigquery.ScalarQueryParameter("image_url", "STRING", image_url),
            bigquery.ScalarQueryParameter("content", "STRING", content)
        ]
        
        # Create job config
        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        
        # Run the query
        client.query(insert_query, job_config=job_config).result()
        
        st.success(f"✅ New post created: {post_id}")
        return post_id
    
    except Exception as e:
        st.error(f"❌ Error creating post: {e}")
        return None


def upload_image_to_gcs(uploaded_file):
    """
    Upload an image to Google Cloud Storage and return its public URL.
    
    Args:
        uploaded_file: File object from Streamlit file uploader
    
    Returns:
        str: Public URL of the uploaded image
    """
    try:
        # Hardcode the bucket name
        bucket_name = 'e3-ai-shoe-starter'
    
        # Initialize Google Cloud Storage client
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        # Generate a unique filename
        file_extension = uploaded_file.name.split('.')[-1]
        # Use UUID to ensure unique filename
        unique_filename = f'posts/{uuid.uuid4()}.{file_extension}'
        
        # Create a blob (cloud file) with the unique filename
        blob = bucket.blob(unique_filename)
        
        # Reset file pointer to the beginning
        uploaded_file.seek(0)
        
        # Upload the file with public access
        blob.upload_from_file(uploaded_file, content_type=f'image/{file_extension}')
        
        # Generate a signed URL that's publicly accessible for 7 days

        signed_url = blob.generate_signed_url(
            version='v4',
            # Very long expiration
            expiration=timedelta(days=7),  # 10 years
            method='GET'
            )
        
        return signed_url
    
    except Exception as e:
        st.error(f"Error uploading image to Google Cloud Storage: {e}")
        return None


def get_user_id_from_auth0_id(auth0_id):
    """Returns internal UserId (e.g., 'user1') from Auth0 user_id."""
    client = bigquery.Client(project="e3-ai-shoe-starter")

    query = """
    SELECT UserId
    FROM `e3-ai-shoe-starter.section_e3.Users`
    WHERE auth0_user_id = @auth0_id
    LIMIT 1
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("auth0_id", "STRING", auth0_id)]
    )

    try:
        results = client.query(query, job_config=job_config).result()
        for row in results:
            return row.UserId
        return None
    except Exception as e:
        print(f"Error getting UserId from auth0_user_id: {e}")
        return None


def insert_new_user(user_id, name, username, dob, image_url, auth0_id, email=None):
    """
    Insert a new user into the BigQuery database.
    """
    try:
        client = bigquery.Client(project="e3-ai-shoe-starter")
        
        # Convert MMDDYYYY → YYYY-MM-DD
        try:
            dob_iso = datetime.strptime(dob, "%m%d%Y").strftime("%Y-%m-%d")
        except ValueError as e:
            print(f"Error parsing date: {e}")
            return False
        
        # SQL query with auth0_user_id
        insert_query = """
        INSERT INTO `e3-ai-shoe-starter.section_e3.Users`
        (UserId, Name, Username, DateOfBirth, ImageUrl, auth0_user_id,Email)
        VALUES (@user_id, @name, @username, @dob, @image_url, @auth0_id,@email )
        """
        
        # Query parameters
        query_params = [
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("name", "STRING", name),
            bigquery.ScalarQueryParameter("username", "STRING", username),
            bigquery.ScalarQueryParameter("dob", "DATE", dob_iso),
            bigquery.ScalarQueryParameter("image_url", "STRING", image_url),
            bigquery.ScalarQueryParameter("auth0_id", "STRING", auth0_id),
            bigquery.ScalarQueryParameter("email", "STRING", email)
        ]
        
        # Execute query
        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        client.query(insert_query, job_config=job_config).result()
        
        print(f"✅ New user inserted: {user_id} with Auth0 ID: {auth0_id} and Email: {email}")
        return True
    except Exception as e:
        print(f"❌ Error inserting new user: {e}")
        return False

#  FRIENDS


def get_all_other_users(current_user_id):
    client = bigquery.Client()

    query = """
    SELECT U.UserId, U.Name
    FROM `e3-ai-shoe-starter.section_e3.Users` U
    WHERE U.UserId != @user_id
      AND U.UserId NOT IN (
        SELECT F.UserId2
        FROM `e3-ai-shoe-starter.section_e3.Friends` F
        WHERE F.UserId1 = @user_id
      )
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", current_user_id)
        ]
    )

    return list(client.query(query, job_config=job_config).result())


def add_friend(current_user_id, friend_user_id):
    from google.cloud import bigquery

    client = bigquery.Client()
    table_id = "e3-ai-shoe-starter.section_e3.Friends"

    # Step 1: Check if the friendship already exists
    check_query = """
    SELECT 1
    FROM `e3-ai-shoe-starter.section_e3.Friends`
    WHERE (Userid1 = @user1 AND Userid2 = @user2)
       OR (Userid1 = @user2 AND Userid2 = @user1)
    LIMIT 1
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user1", "STRING", current_user_id),
            bigquery.ScalarQueryParameter("user2", "STRING", friend_user_id),
        ]
    )

    result = list(client.query(check_query, job_config=job_config).result())

    if result:
        print(f"[INFO] Friendship between {current_user_id} and {friend_user_id} already exists.")
        return ["Already friends"]

    # Step 2: Insert both directions
    rows_to_insert = [
        {"Userid1": current_user_id, "Userid2": friend_user_id},
        {"Userid1": friend_user_id, "Userid2": current_user_id},
    ]

    errors = client.insert_rows_json(table_id, rows_to_insert)
    return errors
    

def get_friends(current_user_id):
    client = bigquery.Client()
    query = f"""
    SELECT U.Name AS friend_name
    FROM `e3-ai-shoe-starter.section_e3.Friends` F
    JOIN `e3-ai-shoe-starter.section_e3.Users` U
    ON F.Userid2 = U.UserId
    WHERE F.Userid1 = @user_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", current_user_id)
        ]
    )
    return list(client.query(query, job_config=job_config).result())
