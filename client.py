import pygame
import socket
import json
import threading
import ctypes

HOST = '127.0.0.1'
PORT = 65432

WIDTH, HEIGHT = 800, 800  # Увеличенное поле
GRID_SIZE = 20
WALL_THICKNESS = 5

COLORS = {"snake": (0, 255, 0), "background": (0, 0, 0), "walls": (100, 0, 0)}

class SnakeGame:
    def __init__(self, client_id):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Multiplayer Snake")
        self.clock = pygame.time.Clock()
        self.client_id = client_id
        self.snake = [(100, 100)]
        self.direction = (GRID_SIZE, 0)
        self.running = True
        self.server_state = {}
        self.move_delay = 300  # Задержка движения в мс
        self.last_move_time = pygame.time.get_ticks()
        
        # Устанавливаем окно поверх всех окон
        hwnd = pygame.display.get_wm_info()["window"]
        ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 3)

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        threading.Thread(target=self.receive_data, daemon=True).start()

    def receive_data(self):
        while True:
            try:
                data = self.sock.recv(1024).decode()
                self.server_state = json.loads(data)
            except:
                break

    def send_data(self):
        msg = json.dumps({"id": self.client_id, "position": self.snake})
        self.sock.sendall(msg.encode())

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.direction != (0, GRID_SIZE):
            self.direction = (0, -GRID_SIZE)
        if keys[pygame.K_DOWN] and self.direction != (0, -GRID_SIZE):
            self.direction = (0, GRID_SIZE)
        if keys[pygame.K_LEFT] and self.direction != (GRID_SIZE, 0):
            self.direction = (-GRID_SIZE, 0)
        if keys[pygame.K_RIGHT] and self.direction != (-GRID_SIZE, 0):
            self.direction = (GRID_SIZE, 0)

    def check_collision(self):
        head = self.snake[0]
        if head[0] < WALL_THICKNESS or head[0] >= WIDTH - WALL_THICKNESS or head[1] < WALL_THICKNESS or head[1] >= HEIGHT - WALL_THICKNESS:
            self.running = False

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time >= self.move_delay:
            self.last_move_time = current_time
            head = (self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1])
            self.snake.insert(0, head)
            self.snake.pop()
            self.check_collision()
            self.send_data()

    def draw(self):
        self.screen.fill(COLORS["background"])
        pygame.draw.rect(self.screen, COLORS["walls"], (0, 0, WIDTH, WALL_THICKNESS))
        pygame.draw.rect(self.screen, COLORS["walls"], (0, HEIGHT - WALL_THICKNESS, WIDTH, WALL_THICKNESS))
        pygame.draw.rect(self.screen, COLORS["walls"], (0, 0, WALL_THICKNESS, HEIGHT))
        pygame.draw.rect(self.screen, COLORS["walls"], (WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, HEIGHT))
        
        for player, body in self.server_state.get("players", {}).items():
            for segment in body:
                pygame.draw.rect(self.screen, COLORS["snake"], (*segment, GRID_SIZE, GRID_SIZE))
        pygame.display.flip()

    def run(self):
        self.connect()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.handle_keys()
            self.update()
            self.draw()
            self.clock.tick(60)  # Высокая частота обновления для отзывчивости
        self.sock.close()
        pygame.quit()

if __name__ == "__main__":
    client_id = input("Enter player ID: ")
    game = SnakeGame(client_id)
    game.run()
