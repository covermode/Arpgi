# GUI client for debug.    @LatypovIlya


import pygame
from client import ArpgiClient


def throw_and_run(func, args=None, kwargs=None):
    args = () if args is None else args
    kwargs = {} if kwargs is None else kwargs
    from threading import Thread
    t = Thread(target=func, args=args, kwargs=kwargs)
    t.start()


class Camera:
    def __init__(self, screen_size):
        self.ss_x, self.ss_y = screen_size
        self.target = None

    def set_target(self, target):
        self.target = target

    def calc(self, pos):
        return pos[0] - (self.target.x + self.target.w // 2 - self.ss_x // 2), \
               pos[1] - (self.target.y + self.target.h // 2 - self.ss_y // 2)

    def decalc(self, screen_pos):
        return screen_pos[0] + (self.target.x + self.target.w // 2 - self.ss_x // 2), \
               screen_pos[1] + (self.target.y + self.target.h // 2 - self.ss_y // 2)


class GUIClient(ArpgiClient):
    def __init__(self, host, port):
        super(GUIClient, self).__init__(host, port)

        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 10)
        self.screen_size = self.screen_width, self.screen_height = 800, 600
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Arpgi GUI Client")

        self.camera = Camera(self.screen_size)
        self.clock = pygame.time.Clock()

    def draw_entity(self, on: pygame.Surface, model):
        pos = self.camera.calc((model.x, model.y))
        pygame.draw.rect(on, (255, 255, 255),
                         (pos[0], pos[1], model.w, model.h), 2)
        on.blit(self.font.render(str(model.name),
                                 False, (255, 255, 255)), (pos[0] + 5, pos[1] + 5))
        on.blit(self.font.render(str((model.x, model.y)),
                                 False, (255, 255, 255)), (pos[0] + 5, pos[1] + 20))
        on.blit(self.font.render(str((model.delta_pos_x, model.delta_pos_y)),
                                 False, (255, 255, 255)), (pos[0] + 5, pos[1] + 35))

    def draw_static(self, on: pygame.Surface, model):
        pos = self.camera.calc((model.x, model.y))
        pygame.draw.rect(on, (255, 255, 255),
                         (pos[0], pos[1], model.w, model.h), 2)
        on.blit(self.font.render(str(model.name),
                                 False, (255, 255, 255)), (pos[0] + 5, pos[1] + 5))
        on.blit(self.font.render(str((model.x, model.y)),
                                 False, (255, 255, 255)), (pos[0] + 5, pos[1] + 20))

    def draw_models(self, on: pygame.Surface):
        for _, model in self.statics.items():
            self.draw_static(on, model)
        for _, model in self.entities.items():
            self.draw_entity(on, model)

    def ui_cycle(self):
        self.clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = self.camera.decalc(event.pos)
                print(pos)
                throw_and_run(self.move_at, args=(
                    [pos[0] - self.entities[self.name].x,
                     pos[1] - self.entities[self.name].y],))

        self.screen.fill((0, 0, 0))
        self.camera.set_target(self.entities[self.name])
        pygame.draw.rect(self.screen, pygame.Color("white"), (
            *(self.camera.calc((0, 0))), *self.map_size
        ), 2)
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
