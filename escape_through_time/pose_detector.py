import mediapipe as mp
import cv2

class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
    
    def detect(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # Get shoulder and hand Y-coordinates
            left_shoulder_y = landmarks[11].y
            right_shoulder_y = landmarks[12].y
            right_hand_y = landmarks[15].y
            left_hand_y = landmarks[16].y

            # Determine which hand is raised
            left_hand_raised = left_hand_y < left_shoulder_y
            right_hand_raised = right_hand_y < right_shoulder_y

            return {
                "landmarks": results.pose_landmarks,
                "left_hand_raised": left_hand_raised,
                "right_hand_raised": right_hand_raised
            }
        
        return None
