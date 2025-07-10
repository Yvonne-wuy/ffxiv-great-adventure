import pygame
import random

from tools import AnimatedSprite as Sp, Timer
        
class Trap(pygame.sprite.Sprite):
    '''表示单个陷阱的类'''

    # 定义类变量，所有陷阱共享
    possible_traps = ['moglin','ice','spike','moglin','spike']
    moglin_avaliable_centery = [150, 280]

    def __init__(self, ai_settings, trap_type):
        super().__init__()
        self.ai_settings = ai_settings
        self.trap_type = trap_type
        self.marked = False     # 是否被碰撞

        # 根据陷阱类型选择不同的精灵图
        if self.trap_type == 'moglin':
            unmark_sprite_filename = ai_settings.assets.loaded_images['items.trap.moglin']
            self.marked_sprite_filename = ai_settings.assets.loaded_images['items.trap.cfs_moglin']
            frame_width = 300
            frame_height = 300
            total_frames = 2
        elif self.trap_type == 'ice':
            unmark_sprite_filename = ai_settings.assets.loaded_images['items.trap.ice']
            self.marked_sprite_filename = None
            frame_width = 90
            frame_height = 300
            total_frames = 1
        elif self.trap_type == 'spike':
            unmark_sprite_filename = ai_settings.assets.loaded_images['items.trap.spike']
            self.marked_sprite_filename = None
            frame_width = 216
            frame_height = 252
            total_frames = 1

        # 初始化精灵图对象
        self.trap_sprite = Sp(
            sprite_filename = unmark_sprite_filename,
            frame_width = frame_width,
            frame_height = frame_height,
            total_frames = total_frames
        )
        self.rect = self.trap_sprite.return_rect()
        
        # 定位：初始位置在屏幕右侧
        self.rect.right = ai_settings.screen_width + 400
        self.rect.top = 0

       # 运动设置
        self.initial_speed = self.ai_settings.trap_speed_0  # 初始速度
        self.init_speed_rate = self.ai_settings.init_trap_acc  # 第一段加速的加速度
        self.final_speed_rate = self.ai_settings.final_trap_acc  # 后续加速的加速度
        self.trap_max_speed_stage1 = self.ai_settings.trap_max_speed_stage1


    def update(self, traps):
        '''更新陷阱的动画和运动'''
        self.trap_sprite.update()  # 刷新精灵图动画
        self.move_trap()
        for trap in traps.copy():
            if trap.rect.centerx <= self.ai_settings.trap_border:
                    traps.remove(trap) # 删除已消失的陷阱
                    del self.ai_settings.trap_running[trap]

    def move_trap(self):
        '''根据计时器与加速度更新陷阱的位置'''
        # --- 状态机逻辑 ---
        # 1. 第一次加速 (INITIAL_ACCELERATION)
        if self.ai_settings.state == "INITIAL_ACCELERATION":
            now_time = self.ai_settings.total_clock.get_elapsed()
            self.ai_settings.trap_now_speed = self.initial_speed + self.init_speed_rate * now_time
            #print(f'已加速{now_time}当前速度{self.ai_settings.trap_now_speed}')
            # 检测是否达到最大一阶段速度
            if self.ai_settings.trap_now_speed >= self.trap_max_speed_stage1:
                self.ai_settings.trap_now_speed = self.trap_max_speed_stage1 # 确保速度不超过上限
                # 切换到第一次保持状态
                self.ai_settings.state = "FIRST_HOLD"
                self.ai_settings.trap_speed_clock.start()
                #self.speed_at_state_start = self.current_speed # 保存当前速度作为下一阶段的保持速度
                #print(f"DEBUG: state{self.ai_settings.state}速度: {self.ai_settings.trap_now_speed:.2f}")

        # 2. 第一次保持 (FIRST_HOLD)
        if self.ai_settings.state == "FIRST_HOLD":
            self.ai_settings.trap_now_speed = self.trap_max_speed_stage1
            now_time = self.ai_settings.trap_speed_clock.get_elapsed()
            #print(f'正在保持{now_time}，当前速度{self.ai_settings.trap_now_speed}')
            # 计时直到过完20秒
            if now_time >= 20.0:
                # 切换到之后的加速状态
                self.ai_settings.trap_speed_clock.start()
                self.ai_settings.speed_at_state_start = self.ai_settings.trap_now_speed # 保存当前速度作为下一个加速阶段的起始速度
                #print(f"DEBUG: 切换到 SUBSEQUENT_ACCELERATION (首次)") # 调试信息
                self.ai_settings.state = "SUBSEQUENT_ACCELERATION"

        # 3. 之后的加速 (SUBSEQUENT_ACCELERATION)
        if self.ai_settings.state == "SUBSEQUENT_ACCELERATION" \
                and self.ai_settings.trap_now_speed <= self.ai_settings.trap_final_max_speed:
            now_time = self.ai_settings.trap_speed_clock.get_elapsed()
            self.ai_settings.trap_now_speed = self.ai_settings.speed_at_state_start + self.final_speed_rate * now_time
            #print(f'已加速{now_time}当前速度{self.ai_settings.trap_now_speed}')
            # 计时直到时间到达6s
            if now_time >= 6.0:
                # 切换到之后的保持状态
                self.ai_settings.subsequent_cycle_count += 1
                self.ai_settings.state = "SUBSEQUENT_HOLD"
                self.ai_settings.trap_speed_clock.start()
                self.ai_settings.speed_at_state_start = self.ai_settings.trap_now_speed # 保存当前速度作为下一个保持阶段的起始速度
                #print(f"DEBUG: 正在执行第{self.ai_settings.subsequent_cycle_count}次加速，切换到 SUBSEQUENT_ACC，当前速度: {self.ai_settings.trap_now_speed:.2f}")

        # 4. 之后的保持 (SUBSEQUENT_HOLD)
        if self.ai_settings.state == "SUBSEQUENT_HOLD":
            self.ai_settings.trap_now_speed = self.ai_settings.speed_at_state_start # 保持上一个状态结束时的速度
            now_time = self.ai_settings.trap_speed_clock.get_elapsed()

            if now_time >= 15.0 * self.ai_settings.subsequent_cycle_count:
                # 15s * 循环次数后，切换回之后的加速状态
                self.ai_settings.state = "SUBSEQUENT_ACCELERATION"
                self.ai_settings.trap_speed_clock.start()
                self.ai_settings.speed_at_state_start = self.ai_settings.trap_now_speed # 保存当前速度作为下一个加速阶段的起始速度
                #print(f"DEBUG: 已加速{self.ai_settings.subsequent_cycle_count}次，切换到 SUBSEQUENT_HOLD，保持速度: {self.ai_settings.trap_now_speed:.2f}")

        # --- 更新陷阱位置 ---
        self.rect.x -= self.ai_settings.trap_now_speed

    def blit_trap(self, target_surface):
        '''在屏幕上绘制陷阱'''
        self.trap_sprite.blit(target_surface)

    def get_collision_rect(self):
        # 根据 trap_type 决定用哪个碰撞矩形
        if self.trap_type == 'moglin':
            center = self.rect.center
            collision_width = 90
            collision_height = 180
            return pygame.Rect(center[0] - collision_width // 2,
                               center[1] - collision_height // 2,
                               collision_width,
                               collision_height)
        else:
            # 对于其他陷阱直接用 rect 作为碰撞检测区域
            return self.rect
        
    def set_marked_sprite(self):
        """当陷阱被标记时，改变其精灵图并保持原有位置"""
        if self.marked_sprite_filename and self.trap_type == 'moglin':
            # 保存旧的 rect 位置，因为新的 Sp 对象会创建一个新的 rect
            old_rect_center = self.rect.center

            # 创建一个新的 Sp 精灵图对象来替换当前的
            self.trap_sprite = Sp(
                sprite_filename=self.marked_sprite_filename,
                frame_width=self.trap_sprite.frame_width,
                frame_height=self.trap_sprite.frame_height,
                total_frames=self.trap_sprite.total_frames
            )
            # 更新 Trap 实例的 rect 为新精灵图的 rect
            self.rect = self.trap_sprite.return_rect()
            # 将新的 rect 的中心点设置为旧 rect 的中心点，实现位置继承
            self.rect.center = old_rect_center

    @classmethod
    def create_trap(cls, ai_settings, traps):
        '''创建一个新的陷阱并设置其垂直位置'''
        # 如果列表空了，重置 possible_traps
        if not cls.possible_traps:
            cls.possible_traps = ['moglin','ice','spike','moglin','ice','spike']
            random.shuffle(cls.possible_traps)
        # 弹出一个陷阱类型
        trap_type = cls.possible_traps.pop(0)
        # 创建陷阱时传入类型
        trap = Trap(ai_settings, trap_type)
        # 根据类型设置不同的垂直位置
        if trap_type == 'moglin':
            trap.rect.centery = random.choice(cls.moglin_avaliable_centery)
            ai_settings.trap_running[trap] = 'moglin'
            ai_settings.assets.loaded_sounds['effect.moglin_appear'].play()
        elif trap_type == 'ice':
            trap.rect.centery = 430     # 稍微抬高了一点鼓励玩家起跳
            ai_settings.trap_running[trap] = 'ice'
        elif trap_type == 'spike':
            trap.rect.centery = 584
            ai_settings.trap_running[trap] = 'spike'
        traps.add(trap)

    @staticmethod
    def monitor_trap_build(ai_settings, traps):
        '''监测持续生成新陷阱'''
        if not ai_settings.unstart:
            if ai_settings.first_trap:
                Trap.create_trap(ai_settings, traps)
                ai_settings.first_trap = False
            else:
                current_elapsed = ai_settings.trap_send_clock.get_elapsed()
                # 计算当前移动速度（像素/秒）
                spaced_time = ai_settings.trap_gap / ai_settings.trap_now_speed
                if current_elapsed - ai_settings.last_trap_spawn_time >= spaced_time:
                    Trap.create_trap(ai_settings, traps)
                    ai_settings.last_trap_spawn_time = current_elapsed