import pygame

def clamp(value, min_val, max_val):
    '''限制数值范围'''
    return max(min_val, min(value, max_val))

class Timer():
    '''计时器小工具'''
    
    def __init__(self):
        self.start_time = None
        self.elapsed_time = 0

    def start(self):
        self.start_time = pygame.time.get_ticks()

    def stop(self):
        if self.start_time is not None:
            self.elapsed_time = pygame.time.get_ticks() - self.start_time
        else:
            self.elapsed_time = 0

    def update(self):
        if self.start_time is not None:
            self.elapsed_time = pygame.time.get_ticks() - self.start_time

    def get_elapsed(self):
        if self.start_time is None:
            return 0
        # 返回经过的秒数
        self.elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000.0
        return self.elapsed_time



class AnimatedSprite(pygame.sprite.Sprite):
    '''精灵图调用'''
    
    def __init__(
        self, sprite_filename, frame_width, frame_height, total_frames):
        super().__init__()
        # 加载精灵表
        self.sprite_sheet = sprite_filename
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.total_frames = total_frames
        self.frame_rate = 17  # 每秒切换多少帧
        self.last_update = pygame.time.get_ticks()
        
        # 从精灵表中切割出各帧
        self.frames = []
        for i in range(total_frames):
            rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
            frame = self.sprite_sheet.subsurface(rect)
            self.frames.append(frame)
        
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.frames[0].get_rect()
        self.pos = self.rect.copy()

    def return_rect(self):
        return self.rect
        
    def update(self):
        '''更新精灵图动画'''
        # 计算时间差
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > 1000 / self.frame_rate:
            # 如果到了更新帧的时间，切换到下一个帧
            self.current_frame = (self.current_frame + 1) % self.total_frames
            self.last_update = current_time

    def blit(self, target_surface):
        '''绘制到屏幕上'''
        target_surface.blit(self.frames[self.current_frame],self.rect)


    @classmethod
    def batch_for_opening(cls, name_list, ai_settings):
        opening_char_list = []
        for player_name in name_list:
            sprite_filename = ai_settings.assets.loaded_images[f'player.sprite.{player_name}']
            frame_width = 300
            frame_height = 300
            total_frames = ai_settings.assets.loaded_images[f'player.frame_num.{player_name}']
            instance = cls( 
                sprite_filename, 
                frame_width, 
                frame_height, 
                total_frames)
            
            opening_char_list.append(instance)
        return opening_char_list