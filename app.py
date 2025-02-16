import streamlit as st
import cv2
import numpy as np
import time
import mediapipe as mp
import sys
import os

# Add the escape-through-time folder to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), "escape_through_time"))

from escape_through_time.renderer import Renderer  # Import game renderer
import escape_through_time.config as config

# Sidebar layout
st.sidebar.header('App Name')
st.sidebar.markdown('<h1 style="font-size: 50px;">User Profile</h1>', unsafe_allow_html=True)
profile_image = "https://th.bing.com/th/id/OIP.0zxk_tJUgh4DVrqXYyT-SgHaFj?rs=1&pid=ImgDetMain"  # Profile picture
st.sidebar.image(profile_image, width=300)
st.sidebar.markdown('<h2 style="font-size: 45px;">Hello, Jane Doe</h2>', unsafe_allow_html=True)
st.sidebar.write("**Heart Rate**: 75 bpm")
st.sidebar.write("**Step Count**: 2 steps")

# Navigation tabs
st.sidebar.write("### Navigation")
tabs = ["Game", "Health Dashboard"]
tab_selection = st.sidebar.radio("Go to", tabs)

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Initialize the game renderer
renderer = Renderer()

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

    # Use session state to track the stop game button
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

        # Detect player's pose using MediaPipe
        results = pose.process(rgb_frame)
        if results.pose_landmarks:
            left_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]

            game_state["left_hand_raised"] = left_wrist.y < results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y
            game_state["right_hand_raised"] = right_wrist.y < results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y

        # Update and render the game frame
        game_frame = renderer.render(frame, game_state)

        # Display game frame in Streamlit
        stframe.image(game_frame, channels="RGB")

        # If the stop button is clicked, update session state to exit loop
        if stop_button:
            st.session_state.stop_game = True

    cap.release()
    cv2.destroyAllWindows()

# Tab content
if tab_selection == "Game":
    st.title("'Escape Through Time' Game")
    st.write("Welcome to the Game! Use your hands to interact!")

    if st.button("Start Game", key="start_game_button"):
        run_game()

elif tab_selection == "Health Dashboard":
    st.title("Health Dashboard")
    st.write("Welcome to your Health Dashboard!")
    st.write("Here you can track your health data and monitor your progress.")
    st.write("Your health data will be displayed here.")
