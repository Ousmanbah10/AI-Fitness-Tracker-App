A personalized fitness tracking web app built with Streamlit, Python, Google BigQuery, Auth0, and Gemini. This platform allows users to join fitness challenges, log their progress, and receive AI-powered insights to stay motivated and consistent.A personalized fitness tracking web app built with Streamlit, Python, Google BigQuery, Auth0, and Gemini. Designed to help users join fitness challenges, track progress, and receive AI-powered insights to stay motivated and consistent. This project was developed as part of the Google Tech Exchange 2025 program, with a strong focus on cloud development, databases, and real-world AI integration.

🚀 Features

📈 Track Progress: Join fitness challenges and log miles or workouts daily.
🥇 Real-Time Leaderboards: Compete with other users and view up-to-date rankings.
🔐 Secure Login: Auth0-powered authentication with personalized dashboards.
📸 Social Feed: Share milestone photos and updates with others in the community.
🤖 AI Insights: Receive intelligent tips and feedback based on your performance using Gemini.
🧠 Tech Stack

Frontend: Streamlit (Python-based web framework)
Backend: Python, Google BigQuery (data storage & analytics)
Authentication: Auth0
AI Integration: Gemini (for personalized tips and insights)
📂 Folder Structure

AI-Fitness-Tracker-App/
│
├── app.py # Main Streamlit app
├── components/ # Custom Streamlit components
├── services/ # Auth0 & BigQuery integration
├── utils/ # Helper functions
├── assets/ # Images, icons, etc.
├── .env # Environment variables (DO NOT COMMIT)
├── requirements.txt # Python dependencies
└── README.md # Project overview
🛠 Setup Instructions

Clone the repository:
git clone https://github.com/your-username/AI-Fitness-Tracker-App.git
cd AI-Fitness-Tracker-App
Create a virtual environment and install dependencies:
python -m venv venv
source venv/bin/activate # or venv\Scripts\activate on Windows
pip install -r requirements.txt

Set up environment variables:
Create a .env file and add:

AUTH0_DOMAIN=your-auth0-domain
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
BIGQUERY_PROJECT=your-gcp-project-id
GEMINI_API_KEY=your-gemini-key
Run the app:
streamlit run app.py
📌 Project Highlights

Built during the Google Tech Exchange 2025 program
Combines data science, user authentication, and AI/ML workflows
Designed for scalability and ease of use
📬 Contact

Created by Ousman Bah
LinkedIn • GitHub
