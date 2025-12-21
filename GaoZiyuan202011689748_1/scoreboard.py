import pygame.font

class Scoreboard:
    def __init__(self, ai_game):
        self.screen   = ai_game.screen
        self.stats    = ai_game.stats
        self.text_color = (30, 30, 30)
        self.font     = pygame.font.SysFont(None, 36)
        self.prep_score()

    def prep_score(self):
        score_str = f"Score: {self.stats.score}"
        self.score_image = self.font.render(score_str, True,
                                            self.text_color, (230,230,230))
        self.score_rect  = self.score_image.get_rect()
        self.score_rect.right = self.screen.get_rect().right - 20
        self.score_rect.top   = 10

    def show_score(self):
        self.prep_score()
        self.screen.blit(self.score_image, self.score_rect)