import pygame
from tools import clamp

class BaseMove:
    def __init__(self, ai_settings, entity):
        self.screen = ai_settings.screen
        self.ai_settings = ai_settings
        self.screen_rect = self.screen.get_rect()
        self.en = entity

        # 地面平移的运动标记
        self.ground_move_right = False
        self.ground_move_left = False
        # 明确的地面状态标志
        self.is_grounded = True

        # 冲刺
        self.dash_state = 'ready' # 冲刺状态机：ready / dashing / cooldown
        self.dash_timer = 0 # 硬直计时器
        self.dash_target = 0

        self.DIR = {
            "right": (self.ai_settings.dash_speed, 0),
            "left":  (-self.ai_settings.dash_speed, 0),
        }
        self.GROUND_FLAG = {
            "right": "ground_move_right",
            "left":  "ground_move_left",
        }

    def update_dash_target(self, ai_settings):
        if self.en.vel.x > 0:
            self.dash_target = min(
            (self.en.pos.x + ai_settings.dash_distance),
            (ai_settings.screen_width - 1))
        elif self.en.vel.x < 0:
            self.dash_target = max(
            (self.en.pos.x - ai_settings.dash_distance),1)

    def update_ground_state(self, ai_settings):
        self.is_grounded = (self.en.pos.y >= (ai_settings.floor_height - 1))

    def _handle_dashing(self, ai_settings):
        '''处理冲刺阶段'''
        if (self.en.vel.x > 0 and self.en.pos.x >= self.dash_target) or \
            (self.en.vel.x < 0 and self.en.pos.x <= self.dash_target):
            self.en.pos.x = self.dash_target
            self.en.vel.update(0, 0)
            # self.dash_timer = pygame.time.get_ticks() # 开始硬直计时
            self.dash_state = 'cooldown'
        else:
            self.en.vel.x *= ai_settings.friction # 轻微空气阻力

    def _handle_cooldown(self):
        '''处理硬直阶段'''
        # if pygame.time.get_ticks() - self.dash_timer > self.ai_settings.dash_freeze: # 硬直
        self.dash_state = 'ready'
        self.en.vel += self.ai_settings.gravity # 启用重力

    def move(self):
        '''统一使用向量self.pos控制位置(物理模拟和地面平移都基于pos)'''
        # 更新地面状态
        self.update_ground_state(self.ai_settings)
        if self.dash_state == 'dashing':
            self._handle_dashing(self.ai_settings)
        elif self.dash_state == 'cooldown':
            self._handle_cooldown()
            pass
        elif self.dash_state == 'ready':
            if self.is_grounded:
                self.en.vel.y = max(min(self.en.vel.y, self.ai_settings.max_speed_y),
                    -self.ai_settings.max_speed_y) # 限制起跳速度
                self.en.pos.y += self.en.vel.y # 允许并应用平地起跳
                if self.ground_move_right:
                    self.en.pos.x += self.ai_settings.ground_speed # 右平移
                elif self.ground_move_left:
                    self.en.pos.x -= self.ai_settings.ground_speed # 左平移
            # elif not self.is_grounded:
            #     self.en.vel += self.ai_settings.gravity # 空中重力
            self.en.vel += self.ai_settings.gravity # 空中重力

        self.en.pos += self.en.vel
        # 边界约束
        self.en.pos.x = clamp(self.en.pos.x, 0, self.ai_settings.screen_width)
        self.en.pos.y = clamp(self.en.pos.y, 0, self.ai_settings.floor_height)

        self.en.rect.center = (int(self.en.pos.x), int(self.en.pos.y))
    
    def down_key_ad(self, dir_name: str):
        if not self.is_grounded:
            if self.dash_state == 'ready':
                self.dash_state = 'dashing'
                self.en.vel.update(self.DIR[dir_name])
                self.update_dash_target(self.ai_settings)
        setattr(self, self.GROUND_FLAG[dir_name], True)
    
    def down_key_w(self):
        self.is_grounded = False
        self.en.vel.y = -self.ai_settings.jump_force

    def continuous_key_ad(self):
        '''持续检测是否按住A/D键,用于持续移动控制'''
        keys = pygame.key.get_pressed()
        self.ground_move_left = keys[pygame.K_a]
        self.ground_move_right = keys[pygame.K_d]

    def up_key_ad(self, dir_name: str):
        if self.is_grounded and dir_name:
            setattr(self, self.GROUND_FLAG[dir_name], False)

    def up_key_w(self):
        self.is_grounded = False
        self.ground_move_right = False
        self.ground_move_left = False




class FloatMove:
    def __init__(self, ai_settings, entity):
        self.screen = ai_settings.screen
        self.ai_settings = ai_settings
        self.screen_rect = self.screen.get_rect()
        
        self.en = entity

        # 控制参数
        self.float_speed = ai_settings.float_speed             # 垂直漂浮速度
        self.horizontal_speed = ai_settings.horizontal_speed   # 横向移动速度
        self.horizontal_friction = ai_settings.horizontal_friction
        self.float_gravity = ai_settings.float_gravity         # 使用已有重力向量

    def _handle_vertical_movement(self, keys):
        """处理垂直方向的移动逻辑。"""
        if keys[pygame.K_w]:
            self.en.vel.y = -self.float_speed
        else:
            self.en.vel += self.float_gravity

    def _handle_horizontal_movement(self, keys):
        """处理水平方向的移动逻辑。"""
        if keys[pygame.K_d]:
            self.en.vel.x = self.horizontal_speed
        elif keys[pygame.K_a]:
            self.en.vel.x = -self.horizontal_speed
        else:
            # 模拟摩擦：逐渐衰减至 0
            self.en.vel.x *= (1 - self.horizontal_friction)
            if abs(self.en.vel.x) < 0.1:
                self.en.vel.x = 0  # 防止无限趋近

    def move(self):
        keys = pygame.key.get_pressed()

        self._handle_vertical_movement(keys)
        self._handle_horizontal_movement(keys)

        # 应用速度
        self.en.pos += self.en.vel

        # 边界约束
        self.en.pos.x = clamp(self.en.pos.x, 0, self.ai_settings.screen_width)
        self.en.pos.y = clamp(self.en.pos.y, 0, self.ai_settings.floor_height - 100)

        self.en.rect.center = (int(self.en.pos.x), int(self.en.pos.y))