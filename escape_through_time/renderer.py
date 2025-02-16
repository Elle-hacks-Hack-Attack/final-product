import cv2
import os
import numpy as np
import time
import config

class Renderer:
    def __init__(self):
        # Load assets
        self.bg = cv2.imread("escape_through_time/assets/path.jpg")
        self.branch = cv2.imread("escape_through_time/assets/branch.jpg", cv2.IMREAD_UNCHANGED)

        # Check if images loaded correctly
        if self.bg is None:
            raise FileNotFoundError("❌ Error: Background image not found! Check 'assets/path.jpg'")
        if self.branch is None:
            raise FileNotFoundError("❌ Error: Branch image not found! Check 'assets/branch.jpg'")

        # Resize background to actual screen size
        screen_width = config.SCREEN_WIDTH
        screen_height = config.SCREEN_HEIGHT
        self.bg = cv2.resize(self.bg, (screen_width, screen_height))
        self.bg_y = 0  # Scrolling background position

        # Resize branch to fit within the screen
        branch_width = int(screen_width * 0.3)  # 30% of screen width
        branch_height = int(screen_height * 0.2)  # 20% of screen height
        self.branch = cv2.resize(self.branch, (branch_width, branch_height))

        # Initialize branch variables
        self.branch_active = False  # Track if a branch is active
        self.branch_x = 0
        self.branch_y = config.SCREEN_HEIGHT // 4  # Top quarter of the screen
        self.branch_spawn_time = 0

        # Coin timers (store by object id)
        self.coin_spawn_times = {}

    def spawn_branch(self):
        """Randomly spawn a branch on the left or right at random intervals."""
        if not self.branch_active and np.random.rand() < 0.02:  # 2% chance per frame
            self.branch_active = True
            self.branch_on_left = np.random.rand() > 0.5  # Random side
            self.branch_x = 0 if self.branch_on_left else config.SCREEN_WIDTH - self.branch.shape[1]
            self.branch_spawn_time = time.time()

    def render(self, frame, game_state):
        # Ensure 'points' is initialized in game_state
        game_state.setdefault("points", 0)
        # Draw blue circle as player representation
        player_x = config.SCREEN_WIDTH // 2
        if game_state["position"] == "left":
            player_x = config.SCREEN_WIDTH // 4  # Move left
        elif game_state["position"] == "right":
            player_x = 3 * config.SCREEN_WIDTH // 4  # Move right
        player_y = config.SCREEN_HEIGHT - 120
        cv2.circle(frame, (player_x, player_y), 30, (255, 0, 0), -1)  # Blue circle representing player

        # Scroll background
        self.bg_y += config.SCROLL_SPEED
        if self.bg_y >= config.SCREEN_HEIGHT:
            self.bg_y = 0  # Reset for looping effect

        # Draw background properly
        frame[:config.SCREEN_HEIGHT, :config.SCREEN_WIDTH] = self.bg

        # Spawn and draw branch if active
        self.spawn_branch()
        if self.branch_active:
            branch_height, branch_width, _ = self.branch.shape
            if self.branch_y + branch_height <= frame.shape[0] and self.branch_x + branch_width <= frame.shape[1]:
                frame[self.branch_y:self.branch_y+branch_height, self.branch_x:self.branch_x+branch_width] = self.branch

            # Check if player grabbed the branch within 5 seconds
            if ((self.branch_on_left and game_state["left_hand_raised"]) or 
                (not self.branch_on_left and game_state["right_hand_raised"])):
                game_state["points"] += 1  # Increase points for grabbing the branch  # Award 1 point for grabbing the branch
                self.branch_active = False  # Hide branch once grabbed
            elif time.time() - self.branch_spawn_time > 5:
                raise SystemExit("❌ Game Over: You missed the branch!")

        # Draw coins as small circles and track their lifespan
        new_coins = []
        collected_coins = []
        for coin in game_state["coins"][:]:  # Iterate over a copy to modify the list
            x, y = coin["pos"]
            new_y = y + 50  # Move coins slightly lower
            coin_id = id(coin)  # Use id() as the key

            if coin_id not in self.coin_spawn_times:
                self.coin_spawn_times[coin_id] = time.time()  # Start timer

            if time.time() - self.coin_spawn_times[coin_id] <= 1:
                if abs(player_x - x) < 40 and abs(player_y - new_y) < 40:
                    game_state["points"] += 1  # Collect coin and increase points
                    collected_coins.append(coin_id)
                cv2.circle(frame, (x, new_y), config.COIN_SIZE // 2, (0, 255, 255), -1)
                new_coins.append(coin)  # Keep coin if still within lifespan

        game_state["coins"] = [coin for coin in new_coins if id(coin) not in collected_coins]  # Remove collected coins  # Update coin list

        # Display player's position
        color = (0, 255, 0) if game_state["position"] == "right" else (255, 0, 0) if game_state["position"] == "left" else (0, 0, 255)
        cv2.putText(frame, f"Position: {game_state['position']}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # Display hand status
        hand_status = "Left Hand Raised" if game_state["left_hand_raised"] else "Right Hand Raised" if game_state["right_hand_raised"] else "No Hand Raised"
        cv2.putText(frame, f"Hand: {hand_status}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Display coin count
        cv2.putText(frame, f"Points: {game_state['points']}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        return frame
