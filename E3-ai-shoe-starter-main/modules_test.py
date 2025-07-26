#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
# You will write these tests in Unit 2.
#############################################################################

import unittest
from unittest.mock import patch, MagicMock
import modules
from modules import (
    display_my_custom_component,
    display_post,
    display_activity_summary,
    display_genai_advice,
    display_recent_workouts,
    load_global_css,
)


class TestDisplayMyCustomComponent(unittest.TestCase):
    """Test display_my_custom_component renders the right component with data."""

    @patch('modules.create_component')
    def test_display_my_custom_component(self, mock_create_component):
        display_my_custom_component('Alice')
        mock_create_component.assert_called_once_with(
            {'NAME': 'Alice'},
            'my_custom_component'
        )


class TestDisplayPost(unittest.TestCase):
    """Test display_post function with and without post_image."""

    @patch('modules.create_component')
    def test_display_post_with_image(self, mock_create_component):
        display_post(
            full_name='John Doe',
            username='user1',
            user_image='http://example.com/profile.jpg',
            timestamp='2025-03-25 10:00',
            content='This is a test post with an image.',
            post_image='http://example.com/image.jpg'
        )
        mock_create_component.assert_called_once()
        data, template = mock_create_component.call_args[0]
        self.assertEqual(data['FULL_NAME'], 'John Doe')
        self.assertEqual(data['USERNAME'], 'user1')
        self.assertEqual(data['USER_IMAGE'], 'http://example.com/profile.jpg')
        self.assertEqual(data['TIMESTAMP'], '2025-03-25 10:00')
        self.assertEqual(data['CONTENT'], 'This is a test post with an image.')
        self.assertEqual(data['POST_IMAGE'], 'http://example.com/image.jpg')
        self.assertEqual(template, 'post_component')

    @patch('modules.create_component')
    def test_display_post_without_image(self, mock_create_component):
        display_post(
            full_name='Jane Doe',
            username='user2',
            user_image='http://example.com/profile2.jpg',
            timestamp='2025-03-25 12:00',
            content='This is a test post without an image.'
        )
        mock_create_component.assert_called_once()
        data, template = mock_create_component.call_args[0]
        self.assertEqual(data['FULL_NAME'], 'Jane Doe')
        self.assertEqual(data['USERNAME'], 'user2')
        self.assertEqual(data['USER_IMAGE'], 'http://example.com/profile2.jpg')
        self.assertEqual(data['TIMESTAMP'], '2025-03-25 12:00')
        self.assertEqual(data['CONTENT'], 'This is a test post without an image.')
        self.assertNotIn('POST_IMAGE', data)
        self.assertEqual(template, 'post_component')


class TestDisplayActivitySummary(unittest.TestCase):
    """Test display_activity_summary with populated and empty data."""

    def setUp(self):
        self.mock_data = [
            {
                'workout_id': 'w1',
                'start_timestamp': '2024-01-01 10:00:00',
                'end_timestamp': '2024-01-01 10:30:00',
                'start_lat_lng': (1.0, 1.0),
                'end_lat_lng': (1.5, 1.5),
                'distance': 2.5,
                'steps': 3000,
                'calories_burned': 120,
            },
            {
                'workout_id': 'w2',
                'start_timestamp': '2024-01-02 11:00:00',
                'end_timestamp': '2024-01-02 11:45:00',
                'start_lat_lng': (2.0, 2.0),
                'end_lat_lng': (2.5, 2.5),
                'distance': 3.5,
                'steps': 4500,
                'calories_burned': 180,
            }
        ]

    @patch('modules.create_component')
    def test_with_data(self, mock_create_component):
        summary = display_activity_summary(self.mock_data)
        mock_create_component.assert_called_once()
        self.assertEqual(summary['total_distance'], 6.0)
        self.assertEqual(summary['total_steps'], 7500)
        self.assertEqual(summary['total_calories'], 300)
        self.assertAlmostEqual(summary['total_workout_time'], 75.0)

    @patch('modules.create_component')
    def test_empty(self, mock_create_component):
        summary = display_activity_summary([])
        mock_create_component.assert_called_once()
        self.assertEqual(summary, {
            'workout_id': 0,
            'start_time': '',
            'end_time': '',
            'total_distance': 0,
            'total_steps': 0,
            'total_calories': 0,
            'start_coordinate': None,
            'end_coordinate': None,
            'total_workout_time': 0,
            'message': ''
        })


class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests for display_genai_advice."""
    
    @patch('streamlit.markdown')
    @patch('streamlit.warning')
    @patch('modules.get_genai_advice')
    def test_with_content_fields(self, mock_get_genai_advice, mock_warning, mock_markdown):
        # Mock advice with content1-4 fields
        mock_get_genai_advice.return_value = {
            "content1": "Keep pushing yourself.",
            "content2": "Challenges make you stronger.",
            "content3": "You have great potential.",
            "content4": "Small steps lead to big results."
        }
        
        display_genai_advice("user123")
        
        # Check warning was not called
        mock_warning.assert_not_called()
        
        # Verify markdown was called multiple times (at least for CSS and each advice block)
        self.assertGreaterEqual(mock_markdown.call_count, 5)
    
    @patch('streamlit.markdown')
    @patch('streamlit.warning')
    @patch('modules.get_genai_advice')
    def test_with_single_content_string(self, mock_get_genai_advice, mock_warning, mock_markdown):
        # Mock advice with just a content field
        mock_get_genai_advice.return_value = {
            "content": "Keep pushing yourself. Challenges make you stronger. You have great potential. Small steps lead to big results."
        }
        
        display_genai_advice("user123")
        
        # Check warning was not called
        mock_warning.assert_not_called()
        
        # Verify markdown was called multiple times
        self.assertGreaterEqual(mock_markdown.call_count, 5)
    
    @patch('streamlit.warning')
    @patch('modules.get_genai_advice')
    def test_no_advice_available(self, mock_get_genai_advice, mock_warning):
        # Mock case where no advice is returned
        mock_get_genai_advice.return_value = None

class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests for display_recent_workouts."""

    @patch('modules.create_component')
    def test_no_workouts(self, mock_create_component):
        display_recent_workouts([])
        mock_create_component.assert_called_once()
        data, template = mock_create_component.call_args[0]
        self.assertEqual(template, 'recent_workouts')
        self.assertIn('No recent workouts to display.', data['WORKOUTS_CONTENT'])

    @patch('modules.create_component')
    def test_with_workouts(self, mock_create_component):
        workouts = [
            {
                'workout_id': 'w1',
                'start_timestamp': '2024-01-01 00:00:00',
                'end_timestamp': '2024-01-01 00:30:00',
                'distance': 5.0,
                'steps': 6000,
                'calories_burned': 300,
                'start_lat_lng': (1.45, 4.46),
                'end_lat_lng': (1.19, 4.7),
            }
        ]
        display_recent_workouts(workouts)
        mock_create_component.assert_called_once()
        data, template = mock_create_component.call_args[0]
        html = data['WORKOUTS_CONTENT']
        for snippet in [
            'Workout 1',
            '2024-01-01 00:00:00',
            '00:30:00',
            '5.0',
            '6000',
            '300',
            '(1.45, 4.46)',
            '(1.19, 4.7)',
        ]:
            self.assertIn(snippet, html)


class TestLoadGlobalCSS(unittest.TestCase):
    """Tests for load_global_css styling injection."""

    @patch('modules.st')
    def test_load_global_css_calls_markdown(self, mock_st):
        mock_st.markdown = MagicMock()
        load_global_css()
        mock_st.markdown.assert_called_once()
        args, kwargs = mock_st.markdown.call_args
        css = args[0]
        self.assertIn('div[data-testid="stButton"] > button', css)
        self.assertTrue(kwargs.get('unsafe_allow_html', False))


if __name__ == '__main__':
    unittest.main()