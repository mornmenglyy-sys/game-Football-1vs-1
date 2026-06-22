import sys
import math
import random

from PyQt6.QtCore import Qt, QRectF, QTimer
from PyQt6.QtGui import QPainter, QFont, QPixmap, QColor
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton


WIDTH = 1000
HEIGHT = 500
GROUND = 400


class Game(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Head Soccer VS Smart AI")
        self.setFixedSize(WIDTH, HEIGHT)

        # Images
        self.bg_img = QPixmap("bg.jpg")
        self.player_img = QPixmap("sticker.webp")
        self.ai_img = QPixmap("played3.webp")
        self.ball_img = QPixmap("1.webp")

        self.keys = set()

        # Player
        self.player_x = 150
        self.player_y = GROUND
        self.player_vy = 0

        # AI
        self.ai_x = 850
        self.ai_y = GROUND
        self.ai_vy = 0

        # Ball
        self.ball_x = WIDTH // 2
        self.ball_y = 150
        self.ball_vx = 5
        self.ball_vy = 0

        self.ball_trail = []

        # Score
        self.player_score = 0
        self.ai_score = 0

        # Goal
        self.goal_W = 60
        self.goal_H = 130
        self.goal_y = GROUND - self.goal_H

        # Match
        self.match_time = 90
        self.time_left = self.match_time
        self.game_running = False
        self.result = ""

        # AI
        self.ai_message = "Let's Play!"

        # Timers
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)

        self.match_timer = QTimer()
        self.match_timer.timeout.connect(self.update_time)

        # Buttons
        self.start_btn = QPushButton("Start", self)
        self.start_btn.setGeometry(820, 10, 60, 30)
        self.start_btn.clicked.connect(self.start_game)

        self.stop_btn = QPushButton("Stop", self)
        self.stop_btn.setGeometry(890, 10, 60, 30)
        self.stop_btn.clicked.connect(self.stop_game)

        self.reset_btn = QPushButton("Reset", self)
        self.reset_btn.setGeometry(750, 10, 60, 30)
        self.reset_btn.clicked.connect(self.reset_game)

    # ================= RESET =================
    def reset_positions(self):
        self.player_x = 150
        self.player_y = GROUND
        self.player_vy = 0

        self.ai_x = 850
        self.ai_y = GROUND
        self.ai_vy = 0

        self.reset_ball()

    def reset_ball(self):
        self.ball_x = WIDTH // 2
        self.ball_y = 150
        self.ball_vx = 0
        self.ball_vy = 0
        self.ball_trail.clear()

    # ================= CONTROL =================
    def start_game(self):
        self.game_running = True
        self.timer.start(16)
        self.match_timer.start(1000)

    def stop_game(self):
        self.game_running = False
        self.timer.stop()
        self.match_timer.stop()

    def reset_game(self):
        self.stop_game()
        self.reset_positions()
        self.player_score = 0
        self.ai_score = 0
        self.time_left = self.match_time
        self.result = ""
        self.update()

    # ================= TIMER =================
    def update_time(self):
        if not self.game_running:
            return

        self.time_left -= 1
        if self.time_left <= 0:
            self.time_left = 0
            self.end_game()

    def end_game(self):
        self.stop_game()

        if self.player_score > self.ai_score:
            self.result = "YOU WIN 🏆"
        elif self.player_score < self.ai_score:
            self.result = "YOU LOSE 💀"
        else:
            self.result = "DRAW ⚖️"

    # ================= INPUT =================
    def keyPressEvent(self, event):
        self.keys.add(event.key())

    def keyReleaseEvent(self, event):
        self.keys.discard(event.key())

    # ================= AI =================
    def update_ai(self):

        speed = 6
        if self.ai_score < self.player_score:
            speed = 8

        predicted_x = self.ball_x + self.ball_vx * 10

        target_x = self.ball_x if self.ball_x > WIDTH * 0.6 else predicted_x

        if target_x < self.ai_x:
            self.ai_x -= speed
        else:
            self.ai_x += speed

        self.ai_x = max(WIDTH // 2, min(WIDTH - 40, self.ai_x))

        if abs(self.ball_x - self.ai_x) < 80 and self.ball_y < self.ai_y:
            self.ai_vy = -13

        self.ai_vy += 0.75
        self.ai_y += self.ai_vy

        if self.ai_y > GROUND:
            self.ai_y = GROUND
            self.ai_vy = 0

    # ================= COLLISION =================
    def check_collision(self, px, py, is_ai=False):
        dx = self.ball_x - px
        dy = self.ball_y - py
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 50:
            if dist == 0:
                dist = 1

            nx = dx / dist
            ny = dy / dist

            if is_ai:
                self.ball_vx = -10
                self.ball_vy = ny * 8 - 5
            else:
                self.ball_vx = nx * 10
                self.ball_vy = ny * 10

    # ================= GAME LOOP =================
    def update_game(self):
        if not self.game_running:
            return

        # PLAYER
        if Qt.Key.Key_A in self.keys:
            self.player_x -= 6
        if Qt.Key.Key_D in self.keys:
            self.player_x += 6
        if Qt.Key.Key_W in self.keys and self.player_y >= GROUND:
            self.player_vy = -14

        self.player_vy += 0.7
        self.player_y += self.player_vy

        if self.player_y > GROUND:
            self.player_y = GROUND
            self.player_vy = 0

        self.player_x = max(40, min(WIDTH // 2, self.player_x))

        # AI
        self.update_ai()

        # BALL PHYSICS
        self.ball_vy += 0.3
        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy

        self.ball_trail.append((self.ball_x, self.ball_y))
        if len(self.ball_trail) > 10:
            self.ball_trail.pop(0)

        if self.ball_y > GROUND:
            self.ball_y = GROUND
            self.ball_vy *= -0.4

        self.ball_vx *= 0.995

        # GOALS
        if 10 < self.ball_x < 10 + self.goal_W and self.ball_y > self.goal_y:
            self.ai_score += 1
            # self.ai_message = random.choice(["Haha!", "Easy!", "Oops!"])
            self.reset_positions()

        if WIDTH - 70 < self.ball_x < WIDTH - 10 and self.ball_y > self.goal_y:
            self.player_score += 1
            # self.ai_message = random.choice(["Nooo!", "Lucky!", "Wait!"])
            self.reset_positions()

        # WALLS
        if self.ball_x < 15 or self.ball_x > WIDTH - 15:
            self.ball_vx *= -1

        # COLLISIONS
        self.check_collision(self.player_x, self.player_y)
        self.check_collision(self.ai_x, self.ai_y, True)

        self.update()

    # ================= DRAW =================
    def paintEvent(self, event):
        painter = QPainter(self)

        painter.drawPixmap(self.rect(), self.bg_img)

        # HUD
        painter.fillRect(0, 0, WIDTH, 80, QColor(0, 0, 0, 150))

        painter.setFont(QFont("Arial", 26, QFont.Weight.Bold))
        painter.setPen(Qt.GlobalColor.white)

        painter.drawText(
            QRectF(0, 10, WIDTH, 40),
            Qt.AlignmentFlag.AlignCenter,
            f"{self.player_score}  :  {self.ai_score}"
        )

        painter.drawText(
            QRectF(0, 40, WIDTH, 40),
            Qt.AlignmentFlag.AlignCenter,
            f"Time: {self.time_left}"
        )

        # TRAIL
        for i, (x, y) in enumerate(self.ball_trail):
            painter.setOpacity(i / 10)
            painter.drawPixmap(int(x - 10), int(y - 10), 20, 20, self.ball_img)

        painter.setOpacity(1)

        # PLAYER
        painter.drawPixmap(int(self.player_x - 40), int(self.player_y - 80), 80, 80, self.player_img)

        # AI
        painter.drawPixmap(int(self.ai_x - 40), int(self.ai_y - 80), 80, 80, self.ai_img)

        # BALL
        painter.drawPixmap(int(self.ball_x - 15), int(self.ball_y - 15), 30, 30, self.ball_img)

        # AI BUBBLE
        painter.setBrush(Qt.GlobalColor.white)
        painter.drawRoundedRect(int(self.ai_x - 50), int(self.ai_y - 120), 100, 30, 10, 10)
        painter.drawText(QRectF(self.ai_x - 50, self.ai_y - 120, 100, 30),
                         Qt.AlignmentFlag.AlignCenter,
                         self.ai_message)

        # RESULT
        if self.time_left == 0:
            painter.fillRect(self.rect(), QColor(0, 0, 0, 180))
            painter.setFont(QFont("Impact", 50))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.result)


app = QApplication(sys.argv)
window = Game()
window.show()
sys.exit(app.exec())