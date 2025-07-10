from pygame.sprite import Sprite

class Bullet(Sprite):
    '''一个对发射的子弹进行管理的类'''

    def __init__(self, ai_settings, player):
        '''在玩家所处位置创建一个子弹对象'''
        super().__init__()
        self.ai_settings = ai_settings
         # 加载子弹图像
        self.image = ai_settings.assets.loaded_images['items.skill.bullet']
        self.rect = self.image.get_rect()

        # 设置初始位置（以玩家位置为准）
        self.rect.centerx = player.rect.centerx
        self.rect.centery = player.rect.centery
        self.rect.right = player.rect.right     # 从玩家右边飞出


        # 存储用小数表示的子弹位置
        self.x = float(self.rect.x)# 横向射出子弹

        self.speed_factor = ai_settings.bullet_speed_factor

    def update(self):
        '''向右移动子弹'''
        # 更新表示子弹位置的小数值
        self.x += self.speed_factor
        # 更新表示子弹的rect的位置
        self.rect.x = self.x

    def blit_bullet(self, target_surface):
        '''在屏幕上绘制子弹'''
        target_surface.blit(self.image, self.rect)

    @staticmethod
    def update_bullets(ai_settings, traps, bullets):
        '''更新子弹的位置，并删除已消失的子弹'''
        bullets.update() # 更新子弹的位置
        
        for bullet in bullets.copy():
            if bullet.rect.right >= ai_settings.screen_width:
                    bullets.remove(bullet) # 删除已消失的子弹
            # 检查是否有子弹击中了陷阱，如果有，就删除陷阱和子弹
            for trap in traps:
                if bullet.rect.colliderect(trap.get_collision_rect()):
                    traps.remove(trap)
                    ai_settings.external_score_bonus += 300

    @staticmethod
    def fire_bullet(ai_settings, player, bullets):
        '''如果还没有到达限制，就发射一颗子弹'''
        # 创建新子弹，并将其加入到编组bullets中
        if len(bullets) < ai_settings.bullets_allowed:
            new_bullet = Bullet(ai_settings, player)
            bullets.add(new_bullet) # 把新的子弹加入到编组里
            ai_settings.assets.loaded_sounds['effect.fire_bullet'].play()
            
        
