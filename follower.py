import pygame

from tools import AnimatedSprite as Sp, Timer
from lb_skill import HealBloodPoint

class Follower:
    """通用跟随宝石兽基类"""
    
    def __init__(self, ai_settings, image_path):
        self.ai_settings = ai_settings
        
        # 加载宝石兽精灵图
        self.follower_sprite = Sp(
            sprite_filename = image_path,
            frame_width = 300,
            frame_height = 300,
            total_frames = self.ai_settings.assets.loaded_images['items.follower.frame_num']
            )
        self.rect = self.follower_sprite.return_rect()

        # 宝石兽的位置（浮点向量）
        self.pos = pygame.Vector2(-300, ai_settings.floor_height)
        # 是否处于召唤状态
        self.active = False
        # 技能计时器
        self.follower_skill_clock = Timer()

    def follow(self, player):
        """跟随玩家，具体行为由子类实现"""
        raise NotImplementedError("子类必须实现 follow 方法")

    def call(self):
        """召唤宝石兽，让宝石兽出现"""
        raise NotImplementedError("子类必须实现 call 方法")

    def blit_follower(self):
        """绘制宝石兽到屏幕上"""
        if self.active:
            self.follower_sprite.blit(self.ai_settings.screen)

    def update(self):
        '''更新宝石兽精灵图动画'''
        if self.active:
            self.follower_sprite.update()



class Carbuncle(Follower):
    """宝石兽:一直在地面跟随,x跟随玩家身后,y保持恒定(地面高度)"""
    
    def __init__(self, ai_settings):
        image_path = ai_settings.assets.loaded_images['items.follower.carbuncle']
        super().__init__(ai_settings, image_path)

    def follow(self, player):
        # 目标位置：相对于玩家的位置
        target_x = player.pos.x - 200  # 稍微跟在后面
        target_y = self.ai_settings.floor_height + 70

        # 差值向量（追踪距离）
        dx = target_x - self.pos.x
        dy = target_y - self.pos.y

        # 计算距离和角度
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance > 20:  # 如果差得不多就别动了，避免抖动
            # 控制最大速度
            max_speed = 20  # 像素/秒
            # 加速度因子，离得越远越快，越近越慢（缓动）
            speed = min(distance * 5, max_speed)

            # 单位向量方向乘以速度和平滑系数
            self.pos.x += (dx / distance) * speed * 0.5
            self.pos.y += (dy / distance) * speed * 0.5

        # 更新位置
        self.rect.center = (int(self.pos.x), int(self.pos.y))


    def skill(self):
        '''黄宝石兽，没盾上一个盾'''
        if not self.ai_settings.unstart:
            now_time = self.follower_skill_clock.get_elapsed()
            if now_time >= self.ai_settings.follower_skill_gap:
                if self.ai_settings.carbuncle_barri < 1 and self.ai_settings.now_blood >= 1:
                    self.ai_settings.carbuncle_barri += 1
                    self.ai_settings.assets.loaded_sounds['effect.SMN_barrier'].play()
                    self.follower_skill_clock.start()

    def call(self):
        """召唤宝石兽，让宝石兽出现"""
        self.active = True
        self.ai_settings.assets.loaded_sounds['effect.carbuncle_call'].play()
        # 此处可以添加动画
        self.follower_skill_clock.start()
        print("宝石兽已召唤")

    def leave(self):
        """宝石兽离开，隐藏宝石兽"""
        self.ai_settings.carbuncle = None
        self.active = False
        self.ai_settings.assets.loaded_sounds['effect.follower_leave'].play()
        self.follower_skill_clock.stop()
        # 此处可以添加离场动画
        print("宝石兽已离开")



class Fairy(Follower):
    """小仙女：保持在玩家身后偏上的位置"""
    
    def __init__(self, ai_settings):
        image_path = ai_settings.assets.loaded_images['items.follower.fairy']
        super().__init__(ai_settings, image_path)

    def follow(self, player):
        # 目标位置：相对于玩家的位置
        target_x = player.pos.x - 200  # 稍微跟在后面
        target_y = player.pos.y - 100

        # 差值向量（追踪距离）
        dx = target_x - self.pos.x
        dy = target_y - self.pos.y

        # 计算距离和角度
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance > 20:  # 如果差得不多就别动了，避免抖动
            # 控制最大速度
            max_speed = 20  # 像素/秒
            # 加速度因子，离得越远越快，越近越慢（缓动）
            speed = min(distance * 5, max_speed)

            # 单位向量方向乘以速度和平滑系数
            self.pos.x += (dx / distance) * speed * 0.5
            self.pos.y += (dy / distance) * speed * 0.5

        # 更新位置
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def skill(self):
        '''小仙女，回一口血'''
        if not self.ai_settings.unstart:
            now_time = self.follower_skill_clock.get_elapsed()
            if now_time >= self.ai_settings.follower_skill_gap:
                if self.ai_settings.now_blood < 3:
                    HealBloodPoint(1, self.ai_settings).apply()
                    self.ai_settings.assets.loaded_sounds['effect.SCH_healing'].play()
                    self.follower_skill_clock.start()

    def call(self):
        """召唤小仙女，让小仙女出现"""
        self.active = True
        self.ai_settings.assets.loaded_sounds['effect.fairy_call'].play()
        # 此处可以添加动画
        self.follower_skill_clock.start()
        print("小仙女已召唤")

    def leave(self):
        """小仙女离开，隐藏小仙女"""
        self.ai_settings.fairy = None
        self.active = False
        self.ai_settings.assets.loaded_sounds['effect.follower_leave'].play()
        self.follower_skill_clock.stop()
        # 此处可以添加离场动画
        print("小仙女已离开")



class FollowerManager:
    '''宝石兽运行'''
    
    @staticmethod
    def follower_call(ai_settings):
        '''监测是否要召唤宝石兽，创建实例+召唤'''
        # 并未进主循环
        if not ai_settings.unstart:
            if ai_settings.now_character == 'dengdeng' \
                and not ai_settings.fairy:
                ai_settings.fairy = Fairy(ai_settings)
                ai_settings.fairy.call()
                ai_settings.fairy.follower_skill_clock.start()
                
            if ai_settings.now_character == 'achang' \
                and not ai_settings.carbuncle:
                ai_settings.carbuncle = Carbuncle(ai_settings)
                ai_settings.carbuncle.call()
                ai_settings.carbuncle.follower_skill_clock.start()

    @staticmethod
    def follow_player(ai_settings, player):
        '''管理宝石兽跟随'''
        # 并未直接进主循环
        if ai_settings.carbuncle:
            ai_settings.carbuncle.skill()
            ai_settings.carbuncle.follow(player)
        elif ai_settings.fairy:
            ai_settings.fairy.skill()
            ai_settings.fairy.follow(player)

    @staticmethod
    def del_follower(ai_settings):
        '''非秘术师删除宝石兽'''
        # 并未直接进主循环
        current = ai_settings.now_character

        # 如果当前不是 achang，删掉 carbuncle
        if current != 'achang' and ai_settings.carbuncle:
            ai_settings.carbuncle.leave()
            ai_settings.carbuncle = None

        # 如果当前不是 dengdeng，删掉 fairy
        if current != 'dengdeng' and ai_settings.fairy:
            ai_settings.fairy.leave()
            ai_settings.fairy = None

    @staticmethod
    def monitor_follower(ai_settings, player):
        '''监测宝石兽状态'''
        FollowerManager.follower_call(ai_settings)
        FollowerManager.follow_player(ai_settings, player)
        FollowerManager.del_follower(ai_settings)
        # 此函数进主循环