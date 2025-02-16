import cv2
import mediapipe as mp
import numpy as np
from pose_detector import PoseDetector
from game_logic import GameLogic
from renderer import Renderer
import config

def main():
    cap = cv2.VideoCapture(0)  # Start video capture
    pose_detector = PoseDetector()
    game_logic = GameLogic()
    renderer = Renderer()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # Flip for a mirrored effect
        pose_landmarks = pose_detector.detect(frame)
        game_state = game_logic.update(pose_landmarks)
        frame = renderer.render(frame, game_state)
        
        cv2.imshow("Temple Run Game", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
