print("Loading test file...")

import unittest
from data_fetcher import get_user_workouts,get_user_sensor_data, get_user_profile, get_user_posts
from unittest.mock import patch, MagicMock


class TestDataFetcher(unittest.TestCase):
    def setUp(self):
        patcher = patch('google.cloud.bigquery.Client')
        self.addCleanup(patcher.stop)
        self.mock_client_class = patcher.start()

        self.mock_row_user1 = MagicMock()
        self.mock_row_user1.user_id = "user1"
        self.mock_row_user1.post_id = "post1"
        self.mock_row_user1.timestamp = "2024-07-29 12:00:00"
        self.mock_row_user1.content = "Stay consistent — every step counts!"
        self.mock_row_user1.image = "http://example.com/image1.jpg"

        self.mock_row_user2 = MagicMock()
        self.mock_row_user2.user_id = "user2"
        self.mock_row_user2.post_id = "post2"
        self.mock_row_user2.timestamp = "2024-07-29 13:00:00"
        self.mock_row_user2.content = "Hydration is key for better performance 💧"
        self.mock_row_user2.image = "http://example.com/image2.jpg"

    def test_get_user_posts_structure(self):
        self.mock_client_class.return_value.query.return_value.result.return_value = [self.mock_row_user1]
        result = get_user_posts("user1")
        self.assertIsInstance(result, list)
        for key in ["timestamp", "content", "image"]:
            self.assertIn(key, result[0])
        self.assertIsInstance(result[0]["timestamp"], str)
        self.assertTrue(result[0]["content"] is None or isinstance(result[0]["content"], str))
        self.assertTrue(result[0]["image"] is None or isinstance(result[0]["image"], str))

    def test_get_user_workouts(self):
        user_id = 'user1'
        workouts = get_user_workouts(user_id)
        self.assertIsInstance(workouts, list)
        for workout in workouts:
            self.assertIn('workout_id', workout)
            self.assertIn('start_timestamp', workout)
            self.assertIn('end_timestamp', workout)
            self.assertIn('start_lat_lng', workout)
            self.assertIn('end_lat_lng', workout)
            self.assertIn('distance', workout)
            self.assertIn('steps', workout)
            self.assertIn('calories_burned', workout)
            self.assertIsInstance(workout['workout_id'], str)
            self.assertIsInstance(workout['start_timestamp'], str)
            self.assertIsInstance(workout['end_timestamp'], str)
            self.assertIsInstance(workout['start_lat_lng'], tuple)
            self.assertIsInstance(workout['end_lat_lng'], tuple)
            self.assertIsInstance(workout['distance'], (int, float))
            self.assertIsInstance(workout['steps'], int)
            self.assertIsInstance(workout['calories_burned'], int)

    def test_get_user_sensor_data(self):
        user_id = 'user1'
        workout_id = 'workout1'
        sensor_data = get_user_sensor_data(user_id, workout_id)
        self.assertIsInstance(sensor_data, list)
        for data_point in sensor_data:
            self.assertIn('sensor_type', data_point)
            self.assertIn('timestamp', data_point)
            self.assertIn('data', data_point)
            self.assertIn('units', data_point)
            self.assertIsInstance(data_point['sensor_type'], str)
            self.assertIsInstance(data_point['timestamp'], str)
            self.assertIsInstance(data_point['data'], (int, float))
            self.assertIsInstance(data_point['units'], str)

    def test_get_user_profile(self):
        mock_user = MagicMock()
        mock_user.full_name = "Alice Johnson"
        mock_user.username = "alicej"
        mock_user.date_of_birth = "1990-01-15"
        mock_user.profile_image = "http://example.com/images/alice.jpg"
        mock_friend1 = MagicMock()
        mock_friend1.friend_id = "user2"
        mock_friend2 = MagicMock()
        mock_friend2.friend_id = "user3"
        mock_client = self.mock_client_class.return_value
        mock_query_result1 = MagicMock()
        mock_query_result1.result.return_value = [mock_user]
        mock_query_result2 = MagicMock()
        mock_query_result2.result.return_value = [mock_friend1, mock_friend2]
        mock_client.query.side_effect = [mock_query_result1, mock_query_result2]
        result = get_user_profile("user1")
        self.assertEqual(result["full_name"], "Alice Johnson")
        self.assertEqual(result["username"], "alicej")
        self.assertEqual(result["date_of_birth"], "1990-01-15")
        self.assertEqual(result["profile_image"], "http://example.com/images/alice.jpg")
        self.assertEqual(result["friends"], ["user2", "user3"])

    def test_get_user_posts(self):
        self.mock_client_class.return_value.query.return_value.result.return_value = [self.mock_row_user1]
        result = get_user_posts("user1")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["user_id"], "user1")
        self.assertEqual(result[0]["post_id"], "post1")
        self.assertEqual(result[0]["timestamp"], "2024-07-29 12:00:00")
        self.assertEqual(result[0]["content"], "Stay consistent — every step counts!")
        self.assertEqual(result[0]["image"], "http://example.com/image1.jpg")

    def test_image_appears_randomly(self):
        self.mock_client_class.return_value.query.return_value.result.return_value = [self.mock_row_user1]
        images_found = 0
        for _ in range(3):
            result = get_user_posts("user1")
            if result and result[0]["image"]:
                images_found += 1
        self.assertGreater(images_found, 0)
        self.assertLess(images_found, 30)

    def test_post_id_format(self):
        self.mock_client_class.return_value.query.return_value.result.return_value = [self.mock_row_user1]
        result = get_user_posts("user1")
        post_id = result[0].get("post_id")
        self.assertIsNotNone(post_id)
        self.assertTrue(post_id.startswith("post"))

    def test_unique_content_for_multiple_users(self):
        self.mock_client_class.return_value.query.return_value.result.side_effect = [
            [self.mock_row_user1], [self.mock_row_user2]
        ]
        post_user1 = get_user_posts("user1")
        post_user2 = get_user_posts("user2")
        self.assertTrue(
            post_user1 != post_user2 or post_user1[0]["content"] != post_user2[0]["content"]
        )

    def test_timestamp_format(self):
        self.mock_client_class.return_value.query.return_value.result.return_value = [self.mock_row_user1]
        result = get_user_posts("user1")
        pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
        self.assertRegex(result[0]["timestamp"], pattern)

    def test_content_matches_expected_list(self):
        self.mock_client_class.return_value.query.return_value.result.return_value = [self.mock_row_user1]
        allowed = [
            "Stay consistent — every step counts!",
            "Hydration is key for better performance 💧",
            "Don’t be afraid to rest. Recovery builds strength.",
            "Challenge yourself a little more each week.",
            None
        ]
        result = get_user_posts("user1")
        self.assertIn(result[0]["content"], allowed)

if __name__ == "__main__":
    unittest.main()
