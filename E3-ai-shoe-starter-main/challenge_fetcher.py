from google.cloud import bigquery
import uuid
from datetime import datetime, timezone, date



def get_challenges(status=None):
    """
    Fetches all challenges from BigQuery, optionally filtered by status.
    
    Args:
        status (str, optional): Challenge status to filter by (e.g., 'active', 'closed')
    
    Returns:
        list: List of challenge dictionaries
    """
    try:
        client = bigquery.Client(project="e3-ai-shoe-starter")

        query = """
        SELECT 
            challenge_id,
            title,
            rules,
            difficulty,
            FORMAT_DATE('%Y-%m-%d', start_date) as start_date,
            FORMAT_DATE('%Y-%m-%d', end_date) as end_date,
            max_participants,
            status,
            goal_miles,
            goal_runs,
            points
        FROM `e3-ai-shoe-starter.section_e3.Challenges`
        """

        if status:
            query += " WHERE status = @status"
            query_params = [bigquery.ScalarQueryParameter("status", "STRING", status)]
            job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        else:
            job_config = bigquery.QueryJobConfig()

        query_job = client.query(query, job_config=job_config)
        results = query_job.result()

        challenges = []
        for row in results:
            challenges.append({
                "challenge_id": row.challenge_id,
                "title": row.title,
                "rules": row.rules,
                "difficulty": row.difficulty,
                "start_date": row.start_date,
                "end_date": row.end_date,
                "max_participants": row.max_participants,
                "status": row.status,
                "goal_miles": row.goal_miles,
                "goal_runs": row.goal_runs,
                "points": row.points
            })

        return challenges

    except Exception as e:
        print(f"❌ Error retrieving challenges: {e}")
        return []


def create_challenge(title, rules, difficulty, start_date, end_date,
                     goal_miles, goal_runs, points, max_participants=None):
    client = bigquery.Client(project="e3-ai-shoe-starter")

    challenge_id = str(uuid.uuid4())
    status = "upcoming"

    query = """
    INSERT INTO `e3-ai-shoe-starter.section_e3.Challenges` (
        challenge_id, title, rules, difficulty,
        start_date, end_date, goal_miles, goal_runs,
        points, status, max_participants
    )
    VALUES (
        @challenge_id, @title, @rules, @difficulty,
        @start_date, @end_date, @goal_miles, @goal_runs,
        @points, @status, @max_participants
    )
    """

    params = [
        bigquery.ScalarQueryParameter("challenge_id", "STRING", challenge_id),
        bigquery.ScalarQueryParameter("title", "STRING", title),
        bigquery.ScalarQueryParameter("rules", "STRING", rules),
        bigquery.ScalarQueryParameter("difficulty", "STRING", difficulty),
        bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
        bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
        bigquery.ScalarQueryParameter("goal_miles", "FLOAT", goal_miles),
        bigquery.ScalarQueryParameter("goal_runs", "INT64", goal_runs),
        bigquery.ScalarQueryParameter("points", "INT64", points),
        bigquery.ScalarQueryParameter("status", "STRING", status),
        bigquery.ScalarQueryParameter("max_participants", "INT64", max_participants if max_participants is not None else None),
    ]

    job_config = bigquery.QueryJobConfig(query_parameters=params)
    client.query(query, job_config=job_config).result()

    return challenge_id


def log_user_activity(user_id, challenge_id, miles_logged, runs_logged):
    

    client = bigquery.Client(project="e3-ai-shoe-starter")
    user_id = str(user_id).strip()
    challenge_id = str(challenge_id).strip()

    try:
        print(f"[INFO] Starting activity logging for user: {user_id}, challenge: {challenge_id}")
        print(f"[INFO] Miles: {miles_logged}, Runs: {runs_logged}")

        # Step 1: Update activity
        update_activity_query = """
        UPDATE `e3-ai-shoe-starter.section_e3.UserChallenges`
        SET 
            miles_completed = miles_completed + @miles_logged,
            runs_completed = runs_completed + @runs_logged
        WHERE 
            TRIM(user_id) = TRIM(@user_id)
            AND TRIM(challenge_id) = TRIM(@challenge_id)
            AND status = 'active'
        """
        update_params = [
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("challenge_id", "STRING", challenge_id),
            bigquery.ScalarQueryParameter("miles_logged", "FLOAT", miles_logged),
            bigquery.ScalarQueryParameter("runs_logged", "INT64", runs_logged),
        ]
        job_config = bigquery.QueryJobConfig(query_parameters=update_params)
        print("[INFO] Running update_activity_query...")
        client.query(update_activity_query, job_config=job_config).result()

        # Step 2: Fetch progress
        fetch_query = """
        SELECT 
            uc.miles_completed,
            uc.runs_completed,
            c.goal_miles,
            c.goal_runs,
            c.points
        FROM `e3-ai-shoe-starter.section_e3.UserChallenges` uc
        JOIN `e3-ai-shoe-starter.section_e3.Challenges` c
        ON TRIM(uc.challenge_id) = TRIM(c.challenge_id)
        WHERE TRIM(uc.user_id) = TRIM(@user_id) AND TRIM(uc.challenge_id) = TRIM(@challenge_id)
        LIMIT 1
        """
        fetch_job_config = bigquery.QueryJobConfig(query_parameters=update_params[:2])
        print("[INFO] Running fetch_query...")
        results = client.query(fetch_query, job_config=fetch_job_config).result()

        for row in results:
            goal_miles = row.goal_miles or 0
            goal_runs = row.goal_runs or 0
            points = row.points
            miles_completed = row.miles_completed
            runs_completed = row.runs_completed

            print(f"[DEBUG] Progress: {miles_completed}/{goal_miles} miles, {runs_completed}/{goal_runs} runs")

            if miles_completed >= goal_miles and runs_completed >= goal_runs:
                print("[INFO] Challenge is complete. Marking as done and awarding points.")

                # Step 4: Mark challenge as done
                mark_done_query = """
                UPDATE `e3-ai-shoe-starter.section_e3.UserChallenges`
                SET status = 'done'
                WHERE TRIM(user_id) = TRIM(@user_id) AND TRIM(challenge_id) = TRIM(@challenge_id)
                """
                client.query(mark_done_query, job_config=fetch_job_config).result()

                # Step 5: Upsert points
                merge_points_query = """
                MERGE `e3-ai-shoe-starter.section_e3.UserPoints` T
                USING (SELECT @user_id AS user_id, @points AS points) S
                ON T.user_id = S.user_id
                WHEN MATCHED THEN
                  UPDATE SET total_points = T.total_points + S.points
                WHEN NOT MATCHED THEN
                  INSERT (user_id, total_points) VALUES (S.user_id, S.points)
                """
                merge_points_config = bigquery.QueryJobConfig(query_parameters=[
                    bigquery.ScalarQueryParameter("points", "INT64", points),
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                ])
                print("[INFO] Running merge_points_query...")
                client.query(merge_points_query, job_config=merge_points_config).result()

                return f"✅ Challenge completed! {points} points awarded."

        return f"✅ Logged {miles_logged} miles and {runs_logged} runs."

    except Exception as e:
        print("[ERROR] An error occurred during log_user_activity:")
        
        return f"❌ Error logging activity: {e}"


def get_single_user_challenges(user_id):
    try:
        client = bigquery.Client(project="e3-ai-shoe-starter")
        
        query = """
        SELECT 
            uc.user_id,
            uc.challenge_id,
            uc.miles_completed,
            uc.runs_completed,
            uc.status AS user_status,
            uc.join_timestamp,
            c.title,
            c.goal_miles,
            c.goal_runs,
            c.rules,
            c.difficulty,
            c.start_date,
            c.end_date,
            c.status AS challenge_status
        FROM `e3-ai-shoe-starter.section_e3.UserChallenges` uc
        JOIN `e3-ai-shoe-starter.section_e3.Challenges` c
        ON TRIM(uc.challenge_id) = TRIM(c.challenge_id)
        WHERE uc.user_id = @user_id
        """
        
        query_params = [bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()

        detailed_challenges = []
        for row in results:
            challenge = {
                "user_id": row.user_id,
                "challenge_id": row.challenge_id,
                "title": row.title,
                "goal_miles": row.goal_miles,
                "goal_runs": row.goal_runs,
                "rules": row.rules,
                "difficulty": row.difficulty,
                "start_date": row.start_date,
                "end_date": row.end_date,
                "challenge_status": row.challenge_status,
                "user_status": row.user_status,
                "miles_completed": row.miles_completed,
                "runs_completed": row.runs_completed,
                "join_timestamp": row.join_timestamp
            }
            detailed_challenges.append(challenge)
        
        return detailed_challenges

    except Exception as e:
        print(f"Error retrieving challenge details: {e}")
        return []


def get_user_points(user_id):
    """
    Fetches the total points for a user.
    
    Args:
        user_id (str): The ID of the user.
        
    Returns:
        int: The total points or 0 if not found.
    """
    try:

        client = bigquery.Client(project="e3-ai-shoe-starter")
        user_id = str(user_id).strip()

        print(f"[INFO] Fetching points for user: {user_id}")

        query = """
        SELECT total_points
        FROM `e3-ai-shoe-starter.section_e3.UserPoints`
        WHERE TRIM(user_id) = TRIM(@user_id)
        LIMIT 1
        """

        query_params = [bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
        job_config = bigquery.QueryJobConfig(query_parameters=query_params)

        query_job = client.query(query, job_config=job_config)
        results = query_job.result()

        for row in results:
            print(f"[INFO] User found. Points: {row.total_points}")
            return row.total_points

        print("[INFO] User not found. Returning 0 points.")
        return 0

    except Exception as e:
        print(f"[ERROR] Error retrieving user points: {e}")
        return 0


def get_challenge_by_id(challenge_id):
    """
    Fetches a specific challenge by ID.
    
    Args:
        challenge_id (str): The ID of the challenge to retrieve.
        
    Returns:
        dict: Challenge data or None if not found.
    """
    try:
        # Initialize BigQuery client
        client = bigquery.Client(project="e3-ai-shoe-starter")
        
        # Query to get the challenge
        challenge_query = """
        SELECT 
            challenge_id,
            title,
            goal_type,
            goal_value,
            rules,
            difficulty,
            FORMAT_DATE('%Y-%m-%d', start_date) as start_date,
            FORMAT_DATE('%Y-%m-%d', end_date) as end_date,
            max_participants,
            status
        FROM `e3-ai-shoe-starter.section_e3.Challenges`
        WHERE challenge_id = @challenge_id
        """
        
        # Set query parameters
        query_params = [bigquery.ScalarQueryParameter("challenge_id", "STRING", challenge_id)]
        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        
        # Execute query
        query_job = client.query(challenge_query, job_config=job_config)
        results = query_job.result()
        
        # Process results
        challenge = None
        for row in results:
            challenge = {
                "challenge_id": row.challenge_id,
                "title": row.title,
                "goal_type": row.goal_type,
                "goal_value": row.goal_value,
                "rules": row.rules,
                "difficulty": row.difficulty,
                "start_date": row.start_date,
                "end_date": row.end_date,
                "max_participants": row.max_participants,
                "status": row.status
            }
            break  # We should only have one result
            
        return challenge
    except Exception as e:
        print(f"Error retrieving challenge: {e}")
        return None


def calculate_progress_percentage(goal_type, goal_value, miles_completed, runs_completed):
    """
    Calculates the progress percentage for a challenge.
    
    Args:
        goal_type (str): Type of goal (e.g., "miles", "runs").
        goal_value (int): Target value for the goal.
        miles_completed (float): Miles completed by the user.
        runs_completed (int): Runs completed by the user.
        
    Returns:
        int: Progress percentage (0-100).
    """
    if goal_type == "miles" and goal_value > 0:
        return min(int((miles_completed / goal_value) * 100), 100)
    elif goal_type == "runs" and goal_value > 0:
        return min(int((runs_completed / goal_value) * 100), 100)
    else:
        return 0


def join_challenge(user_id, challenge_id):
    
    """
    Adds a new row to the UserChallenges table when a user joins a challenge.
    If the user already joined, do nothing.
    """
    client = bigquery.Client(project="e3-ai-shoe-starter")

    # Step 1: Check if user already joined this challenge
    check_query = """
    SELECT 1
    FROM `e3-ai-shoe-starter.section_e3.UserChallenges`
    WHERE user_id = @user_id AND challenge_id = @challenge_id
    LIMIT 1
    """
    check_config = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
        bigquery.ScalarQueryParameter("challenge_id", "STRING", challenge_id),
    ])
    existing = client.query(check_query, job_config=check_config).result()

    if any(existing):  # Already joined
        return f"⚠️ You’ve already joined this challenge."

    # Step 2: Insert the new row
    insert_query = """
    INSERT INTO `e3-ai-shoe-starter.section_e3.UserChallenges`
    (user_id, challenge_id, miles_completed, runs_completed, join_timestamp, status)
    VALUES (@user_id, @challenge_id, 0.0, 0, CURRENT_TIMESTAMP(), "active")
    """
    insert_config = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
        bigquery.ScalarQueryParameter("challenge_id", "STRING", challenge_id),
    ])
    client.query(insert_query, job_config=insert_config).result()
    
    return f"✅ Successfully joined the challenge!"


def log_workout(user_id, start_time, end_time, start_lat, start_long, 
               end_lat, end_long, distance, steps, calories):
    """
    Records a workout in the database and updates challenge progress.
    
    Args:
        user_id (str): User ID
        start_time (datetime): Workout start time
        end_time (datetime): Workout end time
        start_lat (float): Starting latitude
        start_long (float): Starting longitude
        end_lat (float): Ending latitude
        end_long (float): Ending longitude
        distance (float): Total distance in miles
        steps (int): Total steps
        calories (float): Calories burned
        
    Returns:
        str: Success message or error
    """

    
    try:
        # Generate workout ID
        workout_id = str(uuid.uuid4())
        
        # Create BigQuery client
        client = bigquery.Client(project="e3-ai-shoe-starter")
        
        # Create the query
        query = """
        INSERT INTO `e3-ai-shoe-starter.section_e3.Workouts` (
            WorkoutId, UserId, StartTimestamp, EndTimestamp,
            StartLocationLat, StartLocationLong, EndLocationLat, EndLocationLong,
            TotalDistance, TotalSteps, CaloriesBurned
        )
        VALUES (
            @workout_id, @user_id, @start_timestamp, @end_timestamp,
            @start_lat, @start_long, @end_lat, @end_long,
            @total_distance, @total_steps, @calories_burned
        )
        """
        
        # Set up parameters
        params = [
            bigquery.ScalarQueryParameter("workout_id", "STRING", workout_id),
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("start_timestamp", "DATETIME", start_time.isoformat()),
            bigquery.ScalarQueryParameter("end_timestamp", "DATETIME", end_time.isoformat()),
            bigquery.ScalarQueryParameter("start_lat", "FLOAT", start_lat),
            bigquery.ScalarQueryParameter("start_long", "FLOAT", start_long),
            bigquery.ScalarQueryParameter("end_lat", "FLOAT", end_lat),
            bigquery.ScalarQueryParameter("end_long", "FLOAT", end_long),
            bigquery.ScalarQueryParameter("total_distance", "FLOAT", distance),
            bigquery.ScalarQueryParameter("total_steps", "INT64", steps),
            bigquery.ScalarQueryParameter("calories_burned", "FLOAT", calories)
        ]
        
        # Execute the query
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        client.query(query, job_config=job_config).result()
        
        return "🎉 Workout logged successfully!"
    
    except Exception as e:
        return f"⚠️ Failed to log workout: {e}"