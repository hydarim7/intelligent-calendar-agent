
# Personal AI Assistant Agent

A sophisticated personal assistant agent built using the **Google Agent Development Kit (ADK)** and **Vertex AI**. This agent is designed to streamline daily life management by autonomously organizing appointments, coordinating multi-attendee meetings via Google Calendar, and providing context-aware weather insights.

## 📋 Table of Contents
- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [Architecture & Directory Structure](#-architecture--directory-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Deployment](#-deployment)

---

## 🧠 Project Overview

This project implements an intelligent agent capable of managing complex scheduling tasks and acting as a daily planner. It leverages Large Language Models (LLMs) to understand natural language requests and executes actions through specific tool integrations.

The agent is designed to:
* **Optimize Scheduling:** Prioritize tasks and organize daily agendas based on urgency and user preferences.
* **Automate Coordination:** Seamlessly book events and manage invites for multiple attendees.
* **Contextualize Planning:** Integrate real-time weather data to inform outfit recommendations and event timing.

## ✨ Key Features

### ✔ Smart Scheduling
* **Automated Organization:** Automatically structures appointments and creates daily agendas.
* **Priority Management:** Ranks tasks and events based on importance and deadlines.
* **Conflict Resolution:** actively checks for free/busy status to prevent double-booking.

### ✔ Meeting Management (Google Calendar)
* **Event Booking:** Creates, edits, and manages calendar events directly.
* **Multi-Attendee Support:** Checks availability for multiple participants and sends invites.
* **Dynamic Updates:** Allows adding or removing guests and modifying times for existing events.

### ✔ Weather Assistant
* **Real-time Lookup:** Retrieves accurate local weather conditions.
* **Proactive Reminders:** Provides morning weather briefings.
* **Lifestyle Recommendations:** Suggests appropriate attire and optimal times for outdoor activities.

---

## 📂 Architecture & Directory Structure

The project follows a modular structure where the core agent logic is separated from tool definitions and deployment scripts.

```text
kaggle_agent/
├── agent/
│   ├── agent.py               # Core agent logic and definition
│   ├── prompt.py              # System instructions and behavioral prompts
│   ├── tools/                 # Integration tools
│   │   ├── calendar_tools.py  # Google Calendar API logic
│   │   ├── weather_tools.py   # Weather API logic
│   │   ├── prompt_tools.py    # Utilities for dynamic prompting
│   │   └── __init__.py
│   └── __init__.py
├── deployment/                # Scripts for Vertex AI Agent Engine (e.g., deploy.py)
├── client_secret.json         # OAuth credentials (user-provided)
├── token.json                 # Auto-generated OAuth token (after first run)
├── run_agent.py               # Optional entry point script
├── pyproject.toml             # Poetry dependencies and project metadata
├── poetry.lock                # Locked dependency versions
├── .env                       # Environment variables
└── README.md                  # Project documentation


```


## 🛠 Prerequisites
Before running the agent, ensure you have the following installed and configured:

Python 3.9+

Poetry (Dependency Manager)

Google Cloud Platform Project:

Access to Vertex AI.

A Gemini API Key (or Vertex AI credentials).

Python Agent Development Kit: Refer to the ADK Quickstart Guide for base installation.

 ## 🚀 Installation & Setup
1. Clone and Navigate
Clone the repository and navigate to the agent's directory:
cd kaggle_agent

2. Install Dependencies
Install the required Python packages using Poetry:
poetry install



3. Google Calendar Authentication
To enable calendar scheduling, you must authenticate via OAuth 2.0.
Download your OAuth 2.0 Client ID JSON file from the Google Cloud Console.
Rename it to client_secret.json and place it in the root directory (kaggle_agent/).

Note: Upon the first execution of the agent, a browser window will open prompting you to log in. Once authenticated, a token.json file will be generated automatically for future non-interactive runs.

## ⚙️ Configuration
Environment Variables
Create a .env file in the root directory by copying the example file (if available) or creating a new one. Populate it with the necessary keys:

 .env example
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_CLOUD_PROJECT=your_project_id
WEATHER_API_KEY=your_weather_provider_key



## 💻 Usage
You can run the agent using the command line or the recommended Visual Developer UI.

Option A: ADK Developer UI (Recommended)
This provides a web interface to interact with the agent visually:
adk web 

After running the command, open the local URL provided in the terminal to chat with the agent.

Option B: CLI Interaction
Run the agent directly in your terminal:
adk run

Example Interaction Workflows
Scheduling & Planning:
"Plan my day for me." "I have these tasks — help me prioritize them." "Find a 2-hour slot to study today."

Meeting Management:
"Schedule a meeting with alice@example.com and mark@example.com." "Add another guest to my meeting at 3 PM." "Am I free tomorrow at 4 PM?"

Weather & Lifestyle:
"What’s the weather today in Amsterdam?" "Remind me of the weather every morning." "What should I wear today based on the forecast?"


## ☁️ Deployment
This agent is architected for deployment to the Vertex AI Agent Engine.

Deployment Requirements
A Google Cloud Project with Vertex AI APIs enabled.
IAM Roles: Vertex AI User, Storage Admin, Service Account User.
A staging Google Cloud Storage (GCS) bucket.

Deployment scripts and specific instructions regarding the deployment/ directory will be added in future updates.