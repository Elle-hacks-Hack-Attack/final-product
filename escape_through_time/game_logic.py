import random
import config

class GameLogic:
    def __init__(self):
        self.player_position = "center"
        self.left_hand_raised = False
        self.right_hand_raised = False
        self.obstacles = []
        self.coins = []  # Store active coins
        self.coin_count = 0  # Player's score

    def spawn_obstacle(self):
        """ Randomly generates obstacles """
        obs_type = random.choice(["left_block", "right_block", "vine_left", "vine_right", "fallen_tree"])
        
        if obs_type == "left_block":
            return {"type": "left_block", "pos": (0, 300), "size": (config.SCREEN_WIDTH // 2, 50), "color": (0, 0, 255)}
        elif obs_type == "right_block":
            return {"type": "right_block", "pos": (config.SCREEN_WIDTH // 2, 300), "size": (config.SCREEN_WIDTH // 2, 50), "color": (0, 0, 255)}
        elif obs_type == "vine_left":
            return {"type": "vine", "pos": (50, 100), "size": (30, 100), "color": (0, 255, 0)}
        elif obs_type == "vine_right":
            return {"type": "vine", "pos": (config.SCREEN_WIDTH - 80, 100), "size": (30, 100), "color": (0, 255, 0)}
        elif obs_type == "fallen_tree":
            return {"type": "fallen_tree", "pos": (100, 400), "size": (config.SCREEN_WIDTH - 200, 30), "color": (139, 69, 19)}

    def spawn_coins(self):
        """ Randomly generates a row of 3 coins """
        if random.randint(1, config.COIN_SPAWN_RATE) > 98:
            lane = random.choice(["left", "center", "right"])
            y_pos = random.randint(250, 350)  # Random height

            if lane == "left":
                x_start = 100
            elif lane == "right":
                x_start = config.SCREEN_WIDTH - 200
            else:
                x_start = (config.SCREEN_WIDTH // 2) - 50

            return [{"type": "coin", "pos": (x_start + i * 40, y_pos), "size": (config.COIN_SIZE, config.COIN_SIZE), "color": (0, 255, 255)} for i in range(3)]
        return []

    def check_coin_collection(self):
        """ Checks if player collects coins based on their position """
        collected_coins = []
        for coin in self.coins:
            x, y = coin["pos"]
            if (self.player_position == "left" and x < config.SCREEN_WIDTH // 3) or \
               (self.player_position == "right" and x > 2 * (config.SCREEN_WIDTH // 3)) or \
               (self.player_position == "center" and config.SCREEN_WIDTH // 3 < x < 2 * (config.SCREEN_WIDTH // 3)):
                collected_coins.append(coin)

        for coin in collected_coins:
            self.coins.remove(coin)
            self.coin_count += 1  # Increase player’s coin count

    def update(self, pose_data):
        if pose_data:
            landmarks = pose_data["landmarks"]
            self.left_hand_raised = pose_data["left_hand_raised"]
            self.right_hand_raised = pose_data["right_hand_raised"]

            # Detect left/right movement
            left_hand_x = landmarks.landmark[15].x
            right_hand_x = landmarks.landmark[16].x

            if left_hand_x < 0.4:
                self.player_position = "left"
            elif right_hand_x > 0.6:
                self.player_position = "right"
            else:
                self.player_position = "center"

        # Spawn obstacles & coins
        if random.randint(1, 100) > 98:
            self.obstacles.append(self.spawn_obstacle())

        new_coins = self.spawn_coins()
        if new_coins:
            self.coins.extend(new_coins)

        # Check for coin collection
        self.check_coin_collection()

        return {
            "position": self.player_position,
            "left_hand_raised": self.left_hand_raised,
            "right_hand_raised": self.right_hand_raised,
            "obstacles": self.obstacles,
            "coins": self.coins,
            "coin_count": self.coin_count
        }
