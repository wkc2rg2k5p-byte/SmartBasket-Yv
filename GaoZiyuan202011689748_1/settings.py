class Settings:
    """存储游戏所有设置"""

    def __init__(self):
        """初始化静态设置"""
        # 屏幕
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)

        # 飞船
        self.ship_limit = 3

        # 子弹
        self.bullet_width = 6
        self.bullet_height = 8
        self.bullet_color = (60, 60, 60)
        self.bullets_allowed = 5

        # 外星人
        self.fleet_drop_speed = 12

        # 加速比例
        self.speedup_scale = 1.1

        # 动态设置初始化
        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """初始化随游戏进行会改变的设置"""
        self.ship_speed = 1.5
        self.bullet_speed = 2.8
        self.alien_speed = 0.8
        self.fleet_direction = -1   # -1 向左，1 向右
        self.alien_points = 50

    def increase_speed(self):
        """提高速度（过关时调用）"""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.speedup_scale)