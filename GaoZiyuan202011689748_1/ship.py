import pygame
from pygame.sprite import Sprite

class Ship(Sprite):
    def __init__(self, ai_game):
        super().__init__()
        self.screen      = ai_game.screen
        self.settings    = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        self.image = pygame.image.load('images/ship.bmp')
        self.rect  = self.image.get_rect()

        # 固定在左侧中央
        self.rect.left = 10
        self.rect.centery = self.screen_rect.centery

        self.y = float(self.rect.y)
        self.moving_up   = False
        self.moving_down = False

    def update(self):
        if self.moving_up and self.rect.top > 0:
            self.y -= self.settings.ship_speed
        if self.moving_down and self.rect.bottom < self.screen_rect.bottom:
            self.y += self.settings.ship_speed
        self.rect.y = self.y

    def center_ship(self):
        self.rect.centery = self.screen_rect.centery
        self.y = float(self.rect.y)

    def blitme(self):
        self.screen.blit(self.image, self.rect)