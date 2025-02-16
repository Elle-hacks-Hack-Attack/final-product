import streamlit as st
import cv2
import numpy as np
import time
import mediapipe as mp
import sys
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import random  # For heart rate generation

# Add the escape-through-time folder to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), "escape_through_time"))

from escape_through_time.renderer import Renderer  # Import game renderer
import escape_through_time.config as config

SCORES_FILE = "scores.json"

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Initialize the game renderer
renderer = Renderer()

def generate_heart_rate():
    """Generate a random heart rate between 60 and 100 bpm (elderly range)."""
    return random.randint(60, 100)

def save_score(points, heart_rate):
    """Save the player's score and heart rate to a JSON file."""
    try:
        if os.path.exists(SCORES_FILE):
            with open(SCORES_FILE, "r") as file:
                data = file.read().strip()
                if data:
                    scores = json.loads(data)
                else:
                    scores = []
        else:
            scores = []

        # Append new game result
        new_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "points": points,
            "heart_rate": heart_rate
        }
        scores.append(new_entry)

        with open(SCORES_FILE, "w") as file:
            json.dump(scores, file, indent=4)

        print("✅ Score saved:", new_entry)  # Debugging statement
        print("🔄 Full Score Data:", scores)  # Debugging statement

    except Exception as e:
        st.error(f"Error saving score: {e}")

def load_scores():
    """Load player scores from the JSON file, handling empty or corrupt files."""
    if os.path.exists(SCORES_FILE):
        try:
            with open(SCORES_FILE, "r") as file:
                data = file.read().strip()  # Remove any empty spaces
                if not data:  # If the file is empty, return an empty list
                    return []
                return json.loads(data)  # Load JSON if valid
        except json.JSONDecodeError:
            return []  # If the file is corrupted, return an empty list
    return []

def show_score_graph():
    """Display score and heart rate history as a graph."""
    scores = load_scores()
    if not scores:
        st.write("No game data available yet.")
        return

    df = pd.DataFrame(scores)

    fig, ax1 = plt.subplots()

    # Plot points
    ax1.set_xlabel("Game Date")
    ax1.set_ylabel("Points", color="blue")
    ax1.plot(df["timestamp"], df["points"], marker="o", linestyle="-", color="blue", label="Points")
    ax1.tick_params(axis="y", labelcolor="blue")

    # Create second y-axis for heart rate
    ax2 = ax1.twinx()
    ax2.set_ylabel("Heart Rate (bpm)", color="red")
    ax2.plot(df["timestamp"], df["heart_rate"], marker="s", linestyle="--", color="red", label="Heart Rate")
    ax2.tick_params(axis="y", labelcolor="red")

    plt.xticks(rotation=45)
    plt.title("Player Score & Heart Rate Progress")

    st.pyplot(fig)

def run_game():
    stframe = st.empty()  # Streamlit frame for displaying video
    
    cap = cv2.VideoCapture(0)  # Open webcam
    if not cap.isOpened():
        st.error("Error: Could not open webcam.")
        return

    game_state = {
        "position": "center",
        "left_hand_raised": False,
        "right_hand_raised": False,
        "coins": [],
        "points": 0
    }

    heart_rate = generate_heart_rate()  # Generate random heart rate

    if "stop_game" not in st.session_state:
        st.session_state.stop_game = False

    stop_button = st.button("Stop Game", key="stop_game_button")

    while cap.isOpened() and not st.session_state.stop_game:
        ret, frame = cap.read()
        if not ret:
            st.write("Error: Unable to read from camera")
            break

        frame = cv2.flip(frame, 1)  # Flip horizontally for natural movement
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = pose.process(rgb_frame)
        if results.pose_landmarks:
            left_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]

            game_state["left_hand_raised"] = left_wrist.y < results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y
            game_state["right_hand_raised"] = right_wrist.y < results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y

        game_frame = renderer.render(frame, game_state)

        stframe.image(cv2.cvtColor(game_frame, cv2.COLOR_BGR2RGB), channels="RGB")

        if stop_button:
            st.session_state.stop_game = True

    cap.release()
    cv2.destroyAllWindows()

    save_score(game_state["points"], heart_rate)

    st.write(f"### Final Score: {game_state['points']} points")
    st.write(f"### Heart Rate During Game: {heart_rate} bpm")
    st.write("### Score Progress:")
    show_score_graph()

# Sidebar layout
st.sidebar.header('App Name')
st.sidebar.markdown('<h1 style="font-size: 50px;">User Profile</h1>', unsafe_allow_html=True)
profile_image = "https://th.bing.com/th/id/OIP.0zxk_tJUgh4DVrqXYyT-SgHaFj?rs=1&pid=ImgDetMain"
st.sidebar.image(profile_image, width=300)
st.sidebar.markdown('<h2 style="font-size: 45px;">Hello, Jane Doe</h2>', unsafe_allow_html=True)

# Load last recorded heart rate
scores = load_scores()
last_heart_rate = scores[-1]["heart_rate"] if scores else "N/A"
st.sidebar.write(f"**Heart Rate**: {last_heart_rate} bpm")
st.sidebar.write("**Step Count**: 2 steps")

st.sidebar.write("### Navigation")
tabs = ["Game", "Health Dashboard"]
tab_selection = st.sidebar.radio("Go to", tabs)

if tab_selection == "Game":
    st.title("'Escape Through Time' Game")
    st.write("Welcome to the Game! Use your hands to interact!")

    if st.button("Start Game", key="start_game_button"):
        run_game()

    # Load data from scores.json
    with open("scores.json", "r") as file:
        session_data = json.load(file)

    df = pd.DataFrame(session_data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date

    # Calculate game session frequency
    daily_sessions = df.groupby("date").size()

    st.title("Game Performance Analysis")

    # Bar graph: Frequency of game sessions per day
    st.subheader("Game Sessions Per Day")
    fig, ax = plt.subplots()
    daily_sessions.plot(kind="bar", ax=ax)
    ax.set_ylabel("Number of Sessions")
    st.pyplot(fig)

    # Line graph: Points progression
    df_sorted = df.sort_values("timestamp")
    st.subheader("Points Progression")
    fig, ax = plt.subplots()
    ax.plot(df_sorted["timestamp"], df_sorted["points"], marker='o', linestyle='-')
    ax.set_xlabel("Time")
    ax.set_ylabel("Points")
    st.pyplot(fig)

    # Line graph: Heart rate progression
    st.subheader("Heart Rate Progression")
    fig, ax = plt.subplots()
    ax.plot(df_sorted["timestamp"], df_sorted["heart_rate"], marker='o', linestyle='-', color='r')
    ax.set_xlabel("Time")
    ax.set_ylabel("Heart Rate (BPM)")
    st.pyplot(fig)

elif tab_selection == "Health Dashboard":
    st.title("Health Dashboard")
    st.write("Welcome to your Health Dashboard!")
    st.write("Here you can track your health data and monitor your progress.")
    show_score_graph()
