import pygame
import random
from tools import AnimatedSprite as Sp

class Items:
    def __init__(self, ai_settings):
        '''存储管理零碎美术素材'''
        self.ai_settings = ai_settings

        self.blood_bar = self.BloodBar(ai_settings)
        self.lb_bar = self.LBBar(ai_settings)
        self.opening = self.Opening(ai_settings)
        self.score = self.Score(ai_settings)
        self.flash = self.Flash(ai_settings)

    @staticmethod
    def draw_progress_image(screen, image, pos, progress):
        """
        在指定位置 pos 处绘制部分显示的图片。
        progress: 显示进度(0.0~1.0)
        """
        # 限制进度在 0.0 到 1.0 之间
        progress = max(0.0, min(1.0, progress))
        # 计算显示区域的宽度（从左开始）
        width = int((image.get_width() - 16) * progress)
        # 定义需要显示的区域
        display_rect = pygame.Rect(16, 0, width, image.get_height())
        # 在屏幕上绘制部分图片
        screen.blit(image, pos, display_rect)

    @staticmethod
    def draw_releasing_image(screen, image, pos, progress):
        '''lb释放期间的倒数条动画(从右向左减少)'''
        # 限制进度在 0.0 到 1.0 之间
        progress = max(0.0, min(1.0, progress))

        total_width = image.get_width() - 16  # 可用宽度（排除左边的16像素）
        visible_width = int(total_width * (1.0 - progress))  # 随着进度减少而减少

        # 从右侧开始裁剪（注意x坐标变化）
        display_rect = pygame.Rect(16, 0, visible_width, image.get_height())
        display_pos = (pos[0], pos[1])  # 不偏移x轴，让裁剪“从右缩短”

        screen.blit(image, display_pos, display_rect)

        
    class BloodBar:
        def __init__(self, ai_settings):
            self.ai_settings = ai_settings

            self.blood_gap = 80      # px 血条元素间横向间距
            self.blood_height = -60  # 血条显示高度
            self.blood_space = -50   # 血条与屏幕左侧的距离

        def blood_display(self, target_surface):
            '''(gf-update screen)管血条显示的'''
            if self.ai_settings.unstart:
                return
            
            for i in range(self.ai_settings.now_blood):
                '''显示当前血量'''
                full_blood_pos = pygame.Vector2(
                    self.blood_gap * i + self.blood_space, self.blood_height
                    )
                target_surface.blit(self.ai_settings.assets.loaded_images['items.bloodbar.full'], 
                                full_blood_pos)
                
            for y in range(
                self.ai_settings.now_barri + self.ai_settings.carbuncle_barri
                ):
                '''画盾'''
                barri_start_pos = pygame.Vector2(
                    self.blood_gap * (self.ai_settings.now_blood + y) + self.blood_space,
                    self.blood_height
                )
                target_surface.blit(
                    self.ai_settings.assets.loaded_images['items.bloodbar.barri'],
                    barri_start_pos
                )

    class LBBar:
        def __init__(self, ai_settings):
            self.ai_settings = ai_settings

            self.lb_height = 60      # lb条显示高度
            self.lb_space = 1100     # lb条与屏幕左侧的距离
            self.lb_outline_pos = pygame.Vector2(self.lb_space, self.lb_height)
            self.lb_charging_pos = pygame.Vector2(self.lb_space + 16, self.lb_height)

        def update_lb_state(self):
            '''(gf-update screen)更新 lb 状态进度，不负责绘制'''
            if self.ai_settings.unstart:
                return

            if self.ai_settings.lb_state == 'cooldown':
                now_time = self.ai_settings.lb_clock.get_elapsed()
                now_time = min(now_time, self.ai_settings.lb_cooldown_time)
                self.ai_settings.lb_progress = now_time / self.ai_settings.lb_cooldown_time

            elif self.ai_settings.lb_state == 'releasing':
                now_time = self.ai_settings.lb_releasing_clock.get_elapsed()
                duration = self.ai_settings.lb_continue_time[self.ai_settings.now_character]
                self.ai_settings.lb_progress = now_time / duration
            else:
                self.ai_settings.lb_progress = 0  # 其他状态时不显示进度

        def lb_bar_display(self, target_surface):
            '''(gf-update screen)绘制 lb UI 元素'''
            if self.ai_settings.unstart:
                return

            state = self.ai_settings.lb_state
            progress = self.ai_settings.lb_progress

            if state == 'cooldown':
                Items.draw_progress_image(
                    self.ai_settings.screen,
                    self.ai_settings.assets.loaded_images['items.limitbreak.charging'],
                    self.lb_charging_pos,
                    progress
                )
            elif state == 'releasing':
                Items.draw_releasing_image(
                    self.ai_settings.screen,
                    self.ai_settings.assets.loaded_images['items.limitbreak.charging'],
                    self.lb_charging_pos,
                    progress
                )


            # 始终绘制外框
            target_surface.blit(
                self.ai_settings.assets.loaded_images['items.limitbreak.outline'], 
                self.lb_outline_pos
                )

            if state == 'ready':
                target_surface.blit(
                    self.ai_settings.assets.loaded_images['items.limitbreak.ready'], 
                    self.lb_outline_pos
                    )
    
    class Score:
        def __init__(self, ai_settings):
            self.ai_settings = ai_settings
            self.font_large = pygame.font.Font("font/Marker Felt.ttf", 300)

        def calculate_score(self):
            if self.ai_settings.final_score is not None:
                return self.ai_settings.final_score
            
            else:
                # 计算基于时间的得分
                current_time = self.ai_settings.total_clock.get_elapsed()
                time_based_score = int(current_time * self.ai_settings.score_rate)
                
                # 将基于时间的得分加到 ai_settings.score 中
                self.ai_settings.score = time_based_score + self.ai_settings.external_score_bonus
                return self.ai_settings.score


        def build_score_surface(self):
            score = self.calculate_score()
            score_text = str(score)

            char_width = 180
            char_height = 400
            total_width = len(score_text) * char_width
            total_height = char_height

            score_surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)

            for i, char in enumerate(score_text):
                char_surface = self.font_large.render(char, True, (0, 0, 0))
                char_surface = char_surface.convert_alpha()
                char_surface.set_alpha(int(255 * self.ai_settings.transparent_font))

                char_rect = char_surface.get_rect()
                char_rect.center = (
                    i * char_width + char_width // 2,
                    total_height // 2
                )
                score_surface.blit(char_surface, char_rect)

            final_rect = score_surface.get_rect()
            final_rect.center = (
                self.ai_settings.screen_width // 2,
                self.ai_settings.screen_height // 2 - 50
            )

            return score_surface, final_rect
        
        def score_display(self, target_surface):
            if self.ai_settings.unstart:
                return
            surface, rect = self.build_score_surface()
            target_surface.blit(surface, rect)

    class Opening:
        def __init__(self, ai_settings):
            self.screen = ai_settings.screen
            self.ai_settings = ai_settings

            self.start_player_coord = [250, 500, 750, 1000, 1250]
            self.opening_char_sprite_list = Sp.batch_for_opening(
                self.ai_settings.characters_list, self.ai_settings,
                )
            
            self.selected_index = 2     # 当前索引，初始选择最中间的 
            self.arrow_height = 350     # 箭头显示高度
            
            self.arrow_sprite = Sp(
                sprite_filename = ai_settings.assets.loaded_images['items.ui.arrow'],
                frame_width = 300,
                frame_height = 300,
                total_frames = 9,
                )

        def all_char_display(self):
            '''在开始界面显示所有角色'''
            for i in range(len(self.opening_char_sprite_list)):
                character = self.opening_char_sprite_list[i]
                character.pos = pygame.Vector2(
                    self.start_player_coord[i],
                    self.ai_settings.floor_height)
                
                character.rect.center = character.pos   # 同步rect
                character.update()      # 更新新的帧
                character.blit(self.ai_settings.screen)        # 绘制
  
        def draw_opening_arrow(self):
            '''画箭头，纯画'''
            self.arrow_position = self.start_player_coord[self.selected_index] 
            self.arrow_sprite.rect.center = (self.arrow_position, self.arrow_height)
            self.arrow_sprite.update() # 这是更新帧数的，没有更新位置
            self.arrow_sprite.blit(self.ai_settings.screen)
            # 这里就不用再判定一遍是否开始了，扔到最后的函数里判定
        
        def opening_char_choose(self):
            '''改变now_char'''
            self.ai_settings.now_character = \
                self.ai_settings.characters_list[self.selected_index]
            self.ai_settings.assets.loaded_sounds['effect.arrow_confirm'].play()

        def opening_display(self):
            '''(gf-update screen)管理整个开始界面的函数'''
            if self.ai_settings.unstart:
                self.all_char_display()
                self.draw_opening_arrow()

    class Flash:
        def __init__(self, ai_settings):
            self.ai_settings = ai_settings

            # =========== 扣血红屏 ===========
            self.flash_alpha_max = 150 # 闪红时最大透明度 (0-255)，可以调高一点，如 180
            self.flash_duration_ms = 500 # 闪红动画总持续时间 (毫秒)，例如 500ms (0.5秒)

            self.current_alpha = 0  # 当前红色层的透明度
            self.is_active = False  # 闪红效果是否正在进行中
            self.start_time = 0     # 闪红开始的时间戳 (毫秒)
            # 不需要单独的 clock 对象，直接使用 pygame.time.get_ticks() 即可

            # =========== 撞碎冰块震屏 ===========
            self.shake_duration_ms = 200 # 震动持续时间 (毫秒)，例如 200ms
            self.shake_intensity = 8    # 震动最大强度 (像素偏移量)，例如 10 像素
            self.ai_settings.current_shake_offset = (0, 0) # 存储当前帧的震动偏移量
            self.is_shaking = False # 控制屏幕震动动画
            self.start_shake_time = 0 # 震动开始的时间戳

            # =========== LB技能动画相关参数 ===========
            self.lb_flash_duration = self.ai_settings.lb_continue_time['haita'] # LB技能总持续时间 (毫秒)
            self.lb_animation_peak_offset = 1 # 动画达到最大效果的时间偏移量 (秒)，即在结束前1秒达到最大
            self.lb_fade_out_duration = 1 # 动画最后1秒的淡出时间 (秒)


            # 暗屏动画参数
            self.current_alpha = 0
            self.darkscreen_start_time = 0
            self.darkscreen_max_alpha = 240 # 暗屏最大透明度 (0-255)
            self.is_darkscreen_active = False

        # -------------- 扣血屏幕变红 --------------
        def trigger_red_flash(self):
            '''
            外部调用此方法来触发屏幕闪红效果。
            例如：在碰撞检测并扣血后调用 items.flash.trigger_red_flash()
            '''
            self.is_active = True
            self.current_alpha = self.flash_alpha_max 
            self.start_time = pygame.time.get_ticks() # 记录动画开始的时间

        def update_and_draw_red_flash(self):
            '''
            在主游戏循环的绘制阶段调用此方法。
            它负责更新闪红动画状态并绘制红色层。
            '''
            if not self.is_active:
                return 

            # 计算动画已经进行了多长时间
            elapsed_time = pygame.time.get_ticks() - self.start_time

            # 进度 (0.0 到 1.0) = elapsed_time / flash_duration_ms
            # current_alpha = max_alpha * (1.0 - progress)

            if elapsed_time < self.flash_duration_ms:
                # 动画还在进行中
                progress = elapsed_time / self.flash_duration_ms
                # 线性递减透明度，从 max_alpha 到 0
                self.current_alpha = self.flash_alpha_max * (1.0 - progress)
            else:
                # 动画结束
                self.current_alpha = 0
                self.is_active = False
                
            # 确保 alpha 值在有效范围内 (0-255)
            self.current_alpha = max(0, min(255, self.current_alpha))


            # 绘制红色层（这部分基本不变）
            red_surface = pygame.Surface(
                (self.ai_settings.screen_width, self.ai_settings.screen_height), 
                pygame.SRCALPHA 
            )
            red_surface.fill((74, 30, 9, int(self.current_alpha)))
            self.ai_settings.screen.blit(red_surface, (0, 0))

        # -------------- 撞碎冰块震屏 --------------
        def trigger_shake_screen(self):
            '''
            外部调用此方法来触发屏幕震动效果。
            例如：玩家撞碎冰块后调用 items.flash.trigger_shake_screen()
            '''
            self.is_shaking = True
            self.start_shake_time = pygame.time.get_ticks() # 记录震动开始的时间
            self.ai_settings.current_shake_offset = (0, 0) # 重置偏移量

        def update_shake_screen(self):
            '''
            在主游戏循环的更新阶段（或绘制阶段之前）调用此方法。
            它负责计算当前帧的震动偏移量。
            '''
            if not self.is_shaking:
                self.ai_settings.current_shake_offset = (0, 0) # 确保不震动时偏移量为0
                return

            elapsed_time = pygame.time.get_ticks() - self.start_shake_time

            if elapsed_time < self.shake_duration_ms:
                strength_factor = 1.0 - (elapsed_time / self.shake_duration_ms)
                current_intensity = self.shake_intensity * strength_factor       
                # current_intensity = self.shake_intensity

                shake_x = random.randint(-int(current_intensity), int(current_intensity))
                shake_y = random.randint(-int(current_intensity), int(current_intensity))
                
                self.ai_settings.current_shake_offset = (shake_x, shake_y)
            else:
                # 震动结束
                self.is_shaking = False
                self.ai_settings.current_shake_offset = (0, 0) # 震动结束后，偏移量归零

        # -------------- LB技能动画触发 --------------
        def trigger_lb_flash(self):
            '''
            外部调用此方法来触发LB技能的暗屏效果。
            '''
            self.is_darkscreen_active = True
            self.darkscreen_start_time = pygame.time.get_ticks()


        # -------------- LB技能暗屏动画 --------------
        def blm_lb_darkscreen(self, targetsurface):
            '''
            绘制LB技能期间的屏幕变暗动画。
            屏幕整体随着阴影变大而变暗，在LB持续时间结束前一秒达到最黑，
            最后一秒由最黑渐变到完全透明。
            '''
            if not self.is_darkscreen_active:
                return
            elapsed_time = (pygame.time.get_ticks() - self.darkscreen_start_time) / 1000
            # print(elapsed_time)
            
            # 动画达到峰值的时间点
            peak_time = self.lb_flash_duration - self.lb_animation_peak_offset
            
            if elapsed_time < peak_time:
                # 屏幕变暗阶段
                progress = elapsed_time / peak_time
                self.current_alpha = self.darkscreen_max_alpha * progress
                # print(f'current_alpha_darkin {self.current_alpha}')
            elif elapsed_time < self.lb_flash_duration:
                # 屏幕淡出阶段 (最后1秒)
                fade_progress = (elapsed_time - peak_time) / self.lb_fade_out_duration
                self.current_alpha = self.darkscreen_max_alpha * (1.0 - fade_progress)
                # print(f'current_alpha_fadeout {self.current_alpha}')
            elif elapsed_time >= self.lb_flash_duration:
                # 动画结束
                self.is_darkscreen_active = False
                return

            # 确保alpha值在有效范围内
            self.current_alpha = max(0, min(255, int(self.current_alpha)))

            # 创建一个纯黑的Surface，并设置其透明度
            dark_surface = pygame.Surface(
                (self.ai_settings.screen_width, self.ai_settings.screen_height),
                pygame.SRCALPHA
            )
            dark_surface.fill((10, 10, 10, self.current_alpha))

            # 绘制到目标Surface
            targetsurface.blit(dark_surface, (0, 0))


class EndPlay:
    @staticmethod
    def last_score(ai_settings):
        if ai_settings.final_score is None:
            ai_settings.final_score = ai_settings.score

    @staticmethod
    def slide_in_fail_image(ai_settings):
        """让失败提示图片从左侧滑入并在右边停下"""
        # 初始化一次
        if not hasattr(ai_settings, "fail_image_state"):
            image = ai_settings.assets.loaded_images['items.ui.fail']  # 你的素材
            ai_settings.fail_image = image
            ai_settings.fail_image_state = {
                "x": -image.get_width(),  # 从屏幕左侧之外开始
                "y": ai_settings.floor_height,  # 贴地
                "vx": 5.0,
                "max_vx": 20.0,
                "ax": 0.3,
                "arrived": False
            }

        state = ai_settings.fail_image_state
        image = ai_settings.fail_image

        # 如果还没停下就继续推进
        if not state["arrived"]:
            if state["vx"] < state["max_vx"]:
                state["vx"] += state["ax"]

            target_x = ai_settings.screen_width - image.get_width() - 100
            distance = target_x - state["x"]

            if distance < 200:
                state["vx"] *= 0.85  # 减速

            # 如果已经非常接近终点，就钉住不再移动
            if distance <= 0 or (distance < 15 and state["vx"] < 1.5):
                state["x"] = target_x
                state["vx"] = 0
                state["arrived"] = True
            else:
                state["x"] += state["vx"]


        ai_settings.screen.blit(image, (int(state["x"]), int(state["y"])))
