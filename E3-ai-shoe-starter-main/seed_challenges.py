"""
seed_challenges.py

This script populates the BigQuery dataset with sample data for the Challenges feature.
It creates tables for Challenges, UserChallenges, UserPoints, ChallengeMilestones, and UserMilestones.
"""

from google.cloud import bigquery
from google.oauth2 import service_account
import uuid
from datetime import datetime, timedelta, timezone
import random
import time
import os

# Explicitly set up credentials
def get_bigquery_client():
    """Get a properly authenticated BigQuery client."""
    try:
        # Try using explicit credentials if available
        credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=["https://www.googleapis.com/auth/bigquery"]
            )
            return bigquery.Client(credentials=credentials, project="e3-ai-shoe-starter")
        else:
            # Fall back to application default credentials
            return bigquery.Client(project="e3-ai-shoe-starter")
    except Exception as e:
        print(f"Error setting up BigQuery client: {e}")
        raise

def create_tables():
    """Creates the necessary tables in BigQuery."""
    client = get_bigquery_client()
    
    # Check if dataset exists
    try:
        dataset_ref = client.dataset("section_e3")
        client.get_dataset(dataset_ref)
        print("Dataset exists: section_e3")
    except Exception as e:
        print(f"Dataset error: {e}")
        print("Creating dataset section_e3...")
        dataset = bigquery.Dataset(f"e3-ai-shoe-starter.section_e3")
        dataset.location = "US"
        client.create_dataset(dataset)
    
    # Create Challenges table
    challenges_schema = [
        bigquery.SchemaField("challenge_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("goal_type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("goal_value", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("rules", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("difficulty", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("start_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("end_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("max_participants", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
    ]
    
    challenges_table_id = "e3-ai-shoe-starter.section_e3.Challenges"
    
    try:
        client.get_table(challenges_table_id)
        print("Challenges table already exists.")
    except Exception as e:
        print(f"Will create Challenges table: {e}")
        challenges_table = bigquery.Table(challenges_table_id, schema=challenges_schema)
        challenges_table = client.create_table(challenges_table)
        print(f"Created Challenges table: {challenges_table.table_id}")
    
    # Create UserChallenges table
    user_challenges_schema = [
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("challenge_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("miles_completed", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("runs_completed", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("points", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("join_timestamp", "TIMESTAMP", mode="REQUIRED"),
    ]
    
    user_challenges_table_id = "e3-ai-shoe-starter.section_e3.UserChallenges"
    
    try:
        client.get_table(user_challenges_table_id)
        print("UserChallenges table already exists.")
    except Exception as e:
        print(f"Will create UserChallenges table: {e}")
        user_challenges_table = bigquery.Table(user_challenges_table_id, schema=user_challenges_schema)
        user_challenges_table = client.create_table(user_challenges_table)
        print(f"Created UserChallenges table: {user_challenges_table.table_id}")
    
    # Create UserPoints table
    user_points_schema = [
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("total_points", "INTEGER", mode="REQUIRED"),
    ]
    
    user_points_table_id = "e3-ai-shoe-starter.section_e3.UserPoints"
    
    try:
        client.get_table(user_points_table_id)
        print("UserPoints table already exists.")
    except Exception as e:
        print(f"Will create UserPoints table: {e}")
        user_points_table = bigquery.Table(user_points_table_id, schema=user_points_schema)
        user_points_table = client.create_table(user_points_table)
        print(f"Created UserPoints table: {user_points_table.table_id}")
    
    # Create ChallengeMilestones table
    challenge_milestones_schema = [
        bigquery.SchemaField("milestone_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("challenge_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("milestone_percentage", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("description", "STRING", mode="REQUIRED"),
    ]
    
    challenge_milestones_table_id = "e3-ai-shoe-starter.section_e3.ChallengeMilestones"
    
    try:
        client.get_table(challenge_milestones_table_id)
        print("ChallengeMilestones table already exists.")
    except Exception as e:
        print(f"Will create ChallengeMilestones table: {e}")
        challenge_milestones_table = bigquery.Table(challenge_milestones_table_id, schema=challenge_milestones_schema)
        challenge_milestones_table = client.create_table(challenge_milestones_table)
        print(f"Created ChallengeMilestones table: {challenge_milestones_table.table_id}")
    
    # Create UserMilestones table
    user_milestones_schema = [
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("milestone_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("achieved_timestamp", "TIMESTAMP", mode="REQUIRED"),
    ]
    
    user_milestones_table_id = "e3-ai-shoe-starter.section_e3.UserMilestones"
    
    try:
        client.get_table(user_milestones_table_id)
        print("UserMilestones table already exists.")
    except Exception as e:
        print(f"Will create UserMilestones table: {e}")
        user_milestones_table = bigquery.Table(user_milestones_table_id, schema=user_milestones_schema)
        user_milestones_table = client.create_table(user_milestones_table)
        print(f"Created UserMilestones table: {user_milestones_table.table_id}")

def seed_challenges():
    """Seeds the Challenges table with sample data."""
    client = get_bigquery_client()
    
    # Get current date
    today = datetime.now(timezone.utc).date()
    
    # Sample challenges
    sample_challenges = [
        {
            "challenge_id": str(uuid.uuid4()),
            "title": "Spring Marathon Prep",
            "goal_type": "miles",
            "goal_value": 50,
            "rules": "Complete 50 miles within the challenge period. Indoor and outdoor runs count.",
            "difficulty": "Intermediate",
            "start_date": (today - timedelta(days=15)).isoformat(),  # Active challenge (started 15 days ago)
            "end_date": (today + timedelta(days=15)).isoformat(),    # Ends in 15 days
            "max_participants": 100,
            "status": "active"
        },
        {
            "challenge_id": str(uuid.uuid4()),
            "title": "Weekend Warrior",
            "goal_type": "runs",
            "goal_value": 8,
            "rules": "Complete 8 runs on weekends (Saturday/Sunday) during the challenge period.",
            "difficulty": "Beginner",
            "start_date": (today - timedelta(days=10)).isoformat(),  # Active challenge (started 10 days ago)
            "end_date": (today + timedelta(days=20)).isoformat(),    # Ends in 20 days
            "max_participants": None,
            "status": "active"
        },
        {
            "challenge_id": str(uuid.uuid4()),
            "title": "Summer Distance Challenge",
            "goal_type": "miles",
            "goal_value": 100,
            "rules": "Run 100 miles during the summer months. Track your progress and earn badges.",
            "difficulty": "Advanced",
            "start_date": (today + timedelta(days=15)).isoformat(),  # Upcoming challenge (starts in 15 days)
            "end_date": (today + timedelta(days=75)).isoformat(),    # Ends in 75 days
            "max_participants": 50,
            "status": "upcoming"
        },
        {
            "challenge_id": str(uuid.uuid4()),
            "title": "10K Training Plan",
            "goal_type": "miles",
            "goal_value": 30,
            "rules": "Follow the guided training plan to prepare for a 10K race.",
            "difficulty": "Beginner",
            "start_date": (today + timedelta(days=7)).isoformat(),   # Upcoming challenge (starts in 7 days)
            "end_date": (today + timedelta(days=37)).isoformat(),    # Ends in 37 days
            "max_participants": None,
            "status": "upcoming"
        },
        {
            "challenge_id": str(uuid.uuid4()),
            "title": "Winter Challenge",
            "goal_type": "runs",
            "goal_value": 15,
            "rules": "Complete 15 runs during the winter season. Indoor runs count too!",
            "difficulty": "Intermediate",
            "start_date": (today - timedelta(days=45)).isoformat(),  # Closed challenge (started 45 days ago)
            "end_date": (today - timedelta(days=5)).isoformat(),     # Ended 5 days ago
            "max_participants": 200,
            "status": "closed"
        }
    ]
    
    # Insert challenges
    challenge_ids = []
    for challenge in sample_challenges:
        try:
            query = f"""
            INSERT INTO `e3-ai-shoe-starter.section_e3.Challenges`
            (challenge_id, title, goal_type, goal_value, rules, difficulty, start_date, end_date, max_participants, status)
            VALUES(
                '{challenge["challenge_id"]}', 
                '{challenge["title"]}', 
                '{challenge["goal_type"]}', 
                {challenge["goal_value"]}, 
                '{challenge["rules"]}', 
                '{challenge["difficulty"]}', 
                PARSE_DATE('%Y-%m-%d', '{challenge["start_date"]}'), 
                PARSE_DATE('%Y-%m-%d', '{challenge["end_date"]}'), 
                {challenge["max_participants"] if challenge["max_participants"] is not None else 'NULL'}, 
                '{challenge["status"]}'
            )
            """
            
            query_job = client.query(query)
            query_job.result()
            print(f"Inserted challenge: {challenge['title']}")
            challenge_ids.append(challenge["challenge_id"])
        except Exception as e:
            print(f"Error inserting challenge {challenge['title']}: {e}")
    
    # Return the challenge IDs for further seeding
    return challenge_ids

def seed_challenge_milestones(challenge_ids):
    """Seeds the ChallengeMilestones table with sample data."""
    client = get_bigquery_client()
    
    milestones_created = 0
    
    # Create milestones for each challenge
    for challenge_id in challenge_ids:
        # Default milestones at 25%, 50%, 75%, and 100%
        milestone_percentages = [25, 50, 75, 100]
        milestone_descriptions = [
            "25% Complete! You're off to a great start!",
            "Halfway there! Keep pushing!",
            "75% Complete! The finish line is in sight!",
            "Challenge Completed! Congratulations!"
        ]
        
        for percentage, description in zip(milestone_percentages, milestone_descriptions):
            milestone_id = str(uuid.uuid4())
            
            try:
                query = f"""
                INSERT INTO `e3-ai-shoe-starter.section_e3.ChallengeMilestones`
                (milestone_id, challenge_id, milestone_percentage, description)
                VALUES('{milestone_id}', '{challenge_id}', {percentage}, '{description}')
                """
                
                query_job = client.query(query)
                query_job.result()
                milestones_created += 1
            except Exception as e:
                print(f"Error inserting milestone: {e}")
    
    print(f"Created {milestones_created} challenge milestones.")

if __name__ == "__main__":
    print("Creating tables...")
    create_tables()
    
    print("\nSeeding challenges...")
    challenge_ids = seed_challenges()
    
    print("\nSeeding challenge milestones...")
    seed_challenge_milestones(challenge_ids)
    
    print("\nDone! The Challenges feature data has been successfully seeded.")
    print("You can now run your Streamlit app to see the challenges in action.")