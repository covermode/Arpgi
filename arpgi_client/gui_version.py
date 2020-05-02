import pygame
from client import ArpgiClient


class GUIClient(ArpgiClient):
    def __init__(self, host, port):
        super(GUIClient, self).__init__(host, port)

        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 10)
        self.screen_size = self.screen_width, self.screen_height = 800, 600
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Arpgi GUI Client")

        self.clock = pygame.time.Clock()

    def draw_model(self, on: pygame.Surface, model):
        pygame.draw.rect(on, (255, 255, 255) if model.alive else (100, 100, 100),
                         model.rect, 2)
        on.blit(self.font.render(str(model.rect), False, (255, 255, 255)),
                (model.rect[0], model.rect[1]))
        on.blit(self.font.render(str(model.d_pos), False, (255, 255, 255)),
                (model.rect[0], model.rect[1] + 15))

    def draw_models(self, on: pygame.Surface):
        for _, model in self.models.items():
            self.draw_model(on, model)

    def ui_cycle(self):
        self.clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.move_at([event.pos[0] - self.models[self.name].rect[0],
                              event.pos[1] - self.models[self.name].rect[1]])

        self.screen.fill((0, 0, 0))
        self.draw_models(self.screen)
        pygame.display.flip()

    def main(self):
        self.run = True
        self.start()
        while self.run:
            self.ui_cycle()
        self.quit()

    def quit(self):
        super(GUIClient, self).quit()
        pygame.quit()


if __name__ == '__main__':
    client = GUIClient("localhost", 5000)
    client.main()

    import threading
    assert threading.active_count() == 1
