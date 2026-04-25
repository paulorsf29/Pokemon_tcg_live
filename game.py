import sys
import pygame
from settings import WIDTH, HEIGHT, FPS, TITLE
from scenes.splash_scene import SplashScene

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.selected_deck = "Deck Pikachu EX"
        self.scene = SplashScene(self)

    def change_scene(self, new_scene):
        self.scene = new_scene

    def quit(self):
        self.running = False

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                self.scene.handle_event(event)

            self.scene.update(dt)
            self.scene.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit()