import pygame
import socket
import json
import threading

HOST = '127.0.0.1'
PORT = 65432

WIDTH, HEIGHT = 500, 500
GRID_SIZE = 20

COLORS = {"snake": (0, 255, 0), "background": (0, 0, 0)}

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
        if keys[pygame.K_UP]: self.direction = (0, -GRID_SIZE)
        if keys[pygame.K_DOWN]: self.direction = (0, GRID_SIZE)
        if keys[pygame.K_LEFT]: self.direction = (-GRID_SIZE, 0)
        if keys[pygame.K_RIGHT]: self.direction = (GRID_SIZE, 0)

    def update(self):
        head = (self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1])
        self.snake.insert(0, head)
        self.snake.pop()
        self.send_data()

    def draw(self):
        self.screen.fill(COLORS["background"])
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
            self.clock.tick(10)
        self.sock.close()
        pygame.quit()

if __name__ == "__main__":
    client_id = input("Enter player ID: ")
    game = SnakeGame(client_id)
    game.run()