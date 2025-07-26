import unittest
from unittest.mock import patch, MagicMock
from google.cloud import bigquery
from challenge_fetcher import (
    get_challenges,
    create_challenge,
    log_user_activity,
    get_single_user_challenges,
    get_user_points,
    get_challenge_by_id,
    calculate_progress_percentage,
    join_challenge,
    log_workout,
)
from datetime import datetime, date


class TestChallengeFetcher(unittest.TestCase):
    @patch("challenge_fetcher.bigquery.Client")
    def test_get_challenges_no_filter(self, mock_bigquery_client):
        # Mock the BigQuery client and its query method
        mock_client = MagicMock()
        mock_bigquery_client.return_value = mock_client
        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job
        mock_result = [
            MagicMock(
                challenge_id="challenge1",
                title="Challenge 1",
                rules="Rule 1",
                difficulty="Beginner",
                start_date="2024-01-01",
                end_date="2024-01-31",
                max_participants=100,
                status="active",
                goal_miles=10.0,
                goal_runs=5,
                points=100,
            ),
            MagicMock(
                challenge_id="challenge2",
                title="Challenge 2",
                rules="Rule 2",
                difficulty="Advanced",
                start_date="2024-02-01",
                end_date="2024-02-28",
                max_participants=50,
                status="upcoming",
                goal_miles=20.0,
                goal_runs=10,
                points=200,
            ),
        ]
        mock_query_job.result.return_value = mock_result

        # Call the function
        challenges = get_challenges()

        # Assertions
        self.assertEqual(len(challenges), 2)
        self.assertEqual(challenges[0]["challenge_id"], "challenge1")
        self.assertEqual(challenges[0]["title"], "Challenge 1")
        self.assertEqual(challenges[0]["rules"], "Rule 1")
        self.assertEqual(challenges[0]["difficulty"], "Beginner")
        self.assertEqual(challenges[0]["start_date"], "2024-01-01")
        self.assertEqual(challenges[0]["end_date"], "2024-01-31")
        self.assertEqual(challenges[0]["max_participants"], 100)
        self.assertEqual(challenges[0]["status"], "active")
        self.assertEqual(challenges[0]["goal_miles"], 10.0)
        self.assertEqual(challenges[0]["goal_runs"], 5)
        self.assertEqual(challenges[0]["points"], 100)

        self.assertEqual(challenges[1]["challenge_id"], "challenge2")
        self.assertEqual(challenges[1]["title"], "Challenge 2")
        self.assertEqual(challenges[1]["rules"], "Rule 2")
        self.assertEqual(challenges[1]["difficulty"], "Advanced")
        self.assertEqual(challenges[1]["start_date"], "2024-02-01")
        self.assertEqual(challenges[1]["end_date"], "2024-02-28")
        self.assertEqual(challenges[1]["max_participants"], 50)
        self.assertEqual(challenges[1]["status"], "upcoming")
        self.assertEqual(challenges[1]["goal_miles"], 20.0)
        self.assertEqual(challenges[1]["goal_runs"], 10)
        self.assertEqual(challenges[1]["points"], 200)

        mock_client.query.assert_called_once()

    @patch("challenge_fetcher.bigquery.Client")
    def test_get_challenges_with_filter(self, mock_bigquery_client):
        # Mock the BigQuery client and its query method
        mock_client = MagicMock()
        mock_bigquery_client.return_value = mock_client
        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job
        mock_result = [
            MagicMock(
                challenge_id="challenge1",
                title="Challenge 1",
                rules="Rule 1",
                difficulty="Beginner",
                start_date="2024-01-01",
                end_date="2024-01-31",
                max_participants=100,
                status="active",
                goal_miles=10.0,
                goal_runs=5,
                points=100,
            )
        ]
        mock_query_job.result.return_value = mock_result

        # Call the function
        challenges = get_challenges(status="active")

        # Assertions
        self.assertEqual(len(challenges), 1)
        self.assertEqual(challenges[0]["challenge_id"], "challenge1")
        self.assertEqual(challenges[0]["status"], "active")
        mock_client.query.assert_called_once()

    @patch("challenge_fetcher.bigquery.Client")
    def test_get_challenges_exception(self, mock_bigquery_client):
        # Mock the BigQuery client to raise an exception
        mock_client = MagicMock()
        mock_bigquery_client.return_value = mock_client
        mock_client.query.side_effect = Exception("BigQuery error")

        # Call the function
        challenges = get_challenges()

        # Assertions
        self.assertEqual(challenges, [])

    @patch("challenge_fetcher.bigquery.Client")
    def test_create_challenge(self, mock_bigquery_client):
        # Mock the BigQuery client and its query method
        mock_client = MagicMock()
        mock_bigquery_client.return_value = mock_client
        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job
        mock_query_job.result.return_value = None

        # Call the function
        challenge_id = create_challenge(
            title="New Challenge",
            rules="New Rule",
            difficulty="Intermediate",
            start_date="2024-03-01",
            end_date="2024-03-31",
            goal_miles=15.0,
            goal_runs=8,
            points=150,
            max_participants=75,
        )

        # Assertions
        self.assertIsNotNone(challenge_id)
        mock_client.query.assert_called_once()

    @patch("challenge_fetcher.bigquery.Client")
    def test_log_user_activity_update_activity(self, mock_bigquery_client):
        # Mock the BigQuery client and its query method
        mock_client = MagicMock()
        mock_bigquery_client.return_value = mock_client
        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job
        mock_result = [
            MagicMock(
                miles_completed=5.0,
                runs_completed=3,
                goal_miles=10.0,
                goal_runs=5,
                points=100,
            )
        ]
        mock_query_job.result.side_effect = [
            None,  # Mock result for the first query (update)
            mock_result,  # Mock result for the second query (fetch)
        ]

        # Call the function
        message = log_user_activity(
            user_id="user1",
            challenge_id="challenge1",
            miles_logged=2.0,
            runs_logged=1,
        )

        # Assertions
        self.assertEqual(message, "✅ Logged 2.0 miles and 1 runs.")
        self.assertEqual(mock_client.query.call_count, 2)

    @patch("challenge_fetcher.bigquery.Client")
    def test_log_user_activity_complete_challenge(self, mock_bigquery_client):
        # Mock the BigQuery client and its query method
        mock_client = MagicMock()
        mock_bigquery_client.return_value = mock_client
        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job
        mock_result = [
            MagicMock(
                miles_completed=10.0,
                runs_completed=5,
                goal_miles=10.0,
                goal_runs=5,
                points=100,
            )
        ]
        mock_query_job.result.side_effect = [
            None,  # Mock result for the first query (update)
            mock_result,  # Mock result for the second query (fetch)
            None,  # Mock result for the third query (mark as done)
            None # Mock result for the fourth query (update points)
        ]

        # Call the function
        message = log_user_activity(
            user_id="user1",
            challenge_id="challenge1",
            miles_logged=5.0,
            runs_logged=2,
        )

        # Assertions
        self.assertEqual(message, "✅ Challenge completed! 100 points awarded.")
        self.assertEqual(mock_client.query.call_count, 4)

    @patch("challenge_fetcher.bigquery.Client")
    def test_get_single_user_challenges(self, mock_bigquery_client):
        # Mock the BigQuery client and its query method
        mock_client = MagicMock()
        mock_bigquery_client.return_value = mock_client
        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job
        mock_result = [
            MagicMock(
                user_id="user1",
                challenge_id="challenge1",
                miles_completed=5.0,
                runs_completed=3,
                user_status="active",
                join_timestamp=datetime(2024, 1, 1),
                title="Challenge 1",
                goal_miles=10.0,
                goal_runs=5,
                rules="Rule 1",
                difficulty="Beginner",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
                challenge_status="active",
            )
        ]
        mock_query_job.result.return_value = mock_result

        # Call the function
        challenges = get_single_user_challenges(user_id="user1")

        # Assertions
        self.assertEqual(len(challenges), 1)
        self.assertEqual(challenges[0]["user_id"], "user1")
        self.assertEqual(challenges[0]["challenge_id"], "challenge1")
        self.assertEqual(challenges[0]["miles_completed"], 5.0)
        self.assertEqual(challenges[0]["runs_completed"], 3)
        self.assertEqual(challenges[0]["user_status"], "active")
        self.assertEqual(challenges[0]["join_timestamp"], datetime(2024, 1, 1))
        self.assertEqual(challenges[0]["title"], "Challenge 1")
        self.assertEqual(challenges[0]["goal_miles"], 10.0)
        self.assertEqual(challenges[0]["goal_runs"], 5)
        self.assertEqual(challenges[0]["rules"], "Rule 1")
        self.assertEqual(challenges[0]["difficulty"], "Beginner")
        self.assertEqual(challenges[0]["start_date"], date(2024, 1, 1))
        self.assertEqual(challenges[0]["end_date"], date(2024, 1, 31))
        self.assertEqual(challenges[0]["challenge_status"], "active")
        mock_client.query.assert_called_once()

    @patch("challenge_fetcher.bigquery.Client")
    def test_get_user_points(self, mock_bigquery_client):
        # Mock the BigQuery client and its query method
        mock_client = MagicMock()
        mock_bigquery_client.return_value = mock_client
        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job
        mock_result = [MagicMock(total_points=150)]
        mock_query_job.result.return_value = mock_result

        # Call the function
        points = get_user_points(user_id="user1")

        # Assertions
        self.assertEqual(points, 150)
        mock_client.query.assert_called_once()

    @patch("challenge_fetcher.bigquery.Client")
    def test_get_user_points_exception(self, mock_bigquery_client):
        # Mock the BigQuery client to raise an exception
        mock_client = MagicMock()
        mock_bigquery_client.return_value = mock_client
        mock_client.query.side_effect = Exception("BigQuery error")

        # Call the function
        points = get_user_points(user_id="user1")

        # Assertions
        self.assertEqual(points, 0)

    @patch("challenge_fetcher.bigquery.Client")
    def test_get_challenge_by_id(self, mock_bigquery_client):
        # Mock the BigQuery client and its query method
        mock_client = MagicMock()
        mock_bigquery_client.return_value = mock_client
        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job
        mock_result = [
            MagicMock(
                challenge_id="challenge1",
                title="Challenge 1",
                goal_type="miles",
                goal_value=10,
                rules="Rule 1",
                difficulty="Beginner",
                start_date="2024-01-01",
                end_date="2024-01-31",
                max_participants=100,
                status="active",
            )
        ]
        mock_query_job.result.return_value = mock_result

        # Call the function
        challenge = get_challenge_by_id(challenge_id="challenge1")

        # Assertions
        self.assertEqual(challenge["challenge_id"], "challenge1")
        self.assertEqual(challenge["title"], "Challenge 1")
        self.assertEqual(challenge["goal_type"], "miles")
        self.assertEqual(challenge["goal_value"], 10)
        self.assertEqual(challenge["rules"], "Rule 1")
        self.assertEqual(challenge["difficulty"], "Beginner")
        self.assertEqual(challenge["start_date"], "2024-01-01")
        self.assertEqual(challenge["end_date"], "2024-01-31")
        self.assertEqual(challenge["max_participants"], 100)
        self.assertEqual(challenge["status"], "active")
        mock_client.query.assert_called_once()

    @patch("challenge_fetcher.bigquery.Client")
    def test_get_challenge_by_id_exception(self, mock_bigquery_client):
        # Mock the BigQuery client to raise an exception
        mock_client = MagicMock()
        mock_bigquery_client.return_value = mock_client
        mock_client.query.side_effect = Exception("BigQuery error")

        # Call the function
        challenge = get_challenge_by_id(challenge_id="challenge1")

        # Assertions
        self.assertIsNone(challenge)

    def test_calculate_progress_percentage_miles(self):
        # Call the function
        percentage = calculate_progress_percentage(
            goal_type="miles", goal_value=10, miles_completed=5, runs_completed=0
        )

        # Assertions
        self.assertEqual(percentage, 50)

    def test_calculate_progress_percentage_runs(self):
        # Call the function
        percentage = calculate_progress_percentage(
            goal_type="runs", goal_value=5, miles_completed=0, runs_completed=3
        )

        # Assertions
        self.assertEqual(percentage, 60)

    def test_calculate_progress_percentage_invalid_goal_type(self):
        # Call the function
        percentage = calculate_progress_percentage(
            goal_type="invalid", goal_value=5, miles_completed=0, runs_completed=3
        )

        # Assertions
        self.assertEqual(percentage, 0)

    def test_calculate_progress_percentage_goal_value_zero(self):
        # Call the function
        percentage = calculate_progress_percentage(
            goal_type="miles", goal_value=0, miles_completed=5, runs_completed=0
        )

        # Assertions
        self.assertEqual(percentage, 0)

    def test_calculate_progress_percentage_completed(self):
        # Call the function
        percentage = calculate_progress_percentage(
            goal_type="miles", goal_value=10, miles_completed=15, runs_completed=0
        )

        # Assertions
        self.assertEqual(percentage, 100)

    @patch("challenge_fetcher.bigquery.Client")
    def test_join_challenge_new_user(self, mock_bigquery_client):
        # Mock the BigQuery client and its query method
        mock_client = MagicMock()
        mock_bigquery_client.return_value = mock_client
        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job
        mock_query_job.result.return_value = []

        # Call the function
        message = join_challenge(user_id="user1", challenge_id="challenge1")

        # Assertions
        self.assertEqual(message, "✅ Successfully joined the challenge!")
        self.assertEqual(mock_client.query.call_count, 2)

    @patch("challenge_fetcher.bigquery.Client")
    def test_join_challenge_existing_user(self, mock_bigquery_client):
        # Mock the BigQuery client and its query method
        mock_client = MagicMock()
        mock_bigquery_client.return_value = mock_client
        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job
        mock_query_job.result.return_value = [MagicMock()]

        # Call the function
        message = join_challenge(user_id="user1", challenge_id="challenge1")

        # Assertions
        self.assertEqual(message, "⚠️ You’ve already joined this challenge.")
        self.assertEqual(mock_client.query.call_count, 1)

    @patch("challenge_fetcher.bigquery.Client")
    def test_log_workout_success(self, mock_bigquery_client):
        # Mock the BigQuery client and its query method
        mock_client = MagicMock()
        mock_bigquery_client.return_value = mock_client
        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job
        mock_query_job.result.return_value = []

        # Call the function
        message = log_workout(
            user_id="user1",
            start_time=datetime(2024, 1, 1, 10, 0, 0),
            end_time=datetime(2024, 1, 1, 11, 0, 0),
            start_lat=37.7749,
            start_long=-122.4194,
            end_lat=37.7849,
            end_long=-122.4294,
            distance=5.0,
            steps=6000,
            calories=300,
        )

        # Assertions
        self.assertEqual(message, "🎉 Workout logged successfully!")
        mock_client.query.assert_called_once()

    @patch("challenge_fetcher.bigquery.Client")
    def test_log_workout_exception(self, mock_bigquery_client):
        # Mock the BigQuery client to raise an exception
        mock_client = MagicMock()
        mock_bigquery_client.return_value = mock_client
        mock_client.query.side_effect = Exception("BigQuery error")

        # Call the function
        message = log_workout(
            user_id="user1",
            start_time=datetime(2024, 1, 1, 10, 0, 0),
            end_time=datetime(2024, 1, 1, 11, 0, 0),
            start_lat=37.7749,
            start_long=-122.4194,
            end_lat=37.7849,
            end_long=-122.4294,
            distance=5.0,
            steps=6000,
            calories=300,
        )

        # Assertions
        self.assertIn("⚠️ Failed to log workout", message)


if __name__ == "__main__":
    unittest.main()
