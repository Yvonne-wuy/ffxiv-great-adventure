import pygame
from tools import AnimatedSprite as Sp, clamp
from move_logic import BaseMove, FloatMove

class Player:
    def __init__(self, ai_settings):
        '''初始化基础信息'''
        self.screen = ai_settings.screen
        self.ai_settings = ai_settings
        self.screen_rect = self.screen.get_rect()

        # 设置玩家的初始位置（使用浮点坐标）
        self.pos = pygame.Vector2(
            self.screen_rect.centerx,
            ai_settings.floor_height)   
        # 初始化当前速度 速度是矢量
        self.vel = pygame.Vector2(0,0)
        self.base_move_logic = BaseMove(ai_settings, self)

        # 精灵图实例
        self.now_character = self.ai_settings.now_character # 当前角色
        self.player_sprite = Sp(
            sprite_filename = self.ai_settings.assets.loaded_images[f'player.sprite.{self.now_character}'],
            frame_width = 300,
            frame_height = 300,
            total_frames = self.ai_settings.assets.loaded_images[f'player.frame_num.{self.now_character}'],
            )
        self.rect = self.player_sprite.return_rect()
        # 碰撞矩形尺寸
        self.collision_width = 150
        self.collision_height = 150

    def load_sprite_for_character(self):
        '''根据当前角色重载精灵图信息'''
        self.now_character = self.ai_settings.now_character
        self.player_sprite = Sp(
            sprite_filename = self.ai_settings.assets.loaded_images[f'player.sprite.{self.now_character}'],
            frame_width = 300,
            frame_height = 300,
            total_frames = self.ai_settings.assets.loaded_images[f'player.frame_num.{self.now_character}'],
        )
        self.rect = self.player_sprite.return_rect()
        
    def update_move(self):
        self.base_move_logic.move()

    def update_sprite(self):
        '''更新玩家动画和位置'''
        self.player_sprite.update()

    def blit_player(self):
        '''在指定位置绘制玩家'''
        if self.ai_settings.last_moglin_location:
            self.rect.center = self.ai_settings.last_moglin_location
            self.ai_settings.last_moglin_location = None
        self.player_sprite.blit(self.ai_settings.screen)

    def get_collision_rect(self):
        """返回以角色中心为基准、尺寸较小的碰撞矩形。"""
        center = self.rect.center
        return pygame.Rect(center[0] - self.collision_width // 2,
                           center[1] - self.collision_height // 2,
                           self.collision_width,
                           self.collision_height)

class MoglinPlayer(Player):
    '''lb变成莫古力'''
    
    def __init__(self, ai_settings, player):
        super().__init__(ai_settings)
        self.screen = ai_settings.screen
        self.ai_settings = ai_settings
        self.screen_rect = self.screen.get_rect()
        self.float_move_logic = FloatMove(ai_settings, self)

        # 复制位置，初始化速度
        self.pos = pygame.Vector2(player.pos)
        self.vel = pygame.Vector2(0, 0)

        # 加载精灵图
        self.player_sprite = Sp(
            sprite_filename = self.ai_settings.assets.loaded_images['player.sprite.moglin'],
            frame_width=300,
            frame_height=300,
            total_frames=2
        )
        self.rect = self.player_sprite.return_rect()
    
    def update_move(self):
        self.float_move_logic.move()

    def update_sprite(self):
        '''更新玩家动画'''
        self.player_sprite.update()
    
    def blit_mg_player(self):
        self.player_sprite.blit(self.ai_settings.screen)