import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

# ========== 第三方库 ==========
import pygame
from pygame.sprite import Group

# ========== 游戏对象 & 模型类 ==========
from follower import FollowerManager as FollowerMgr
from player import Player
from bullet import Bullet
from collision import Collision
from trap import Trap

# ========== UI & 功能模块 ==========
from ui_items import Items
from settings import Settings
from lb_skill import LimitBreak
from settings import AssetManager
import bgm_control as bgm
import game_functions as gf

    
def run_game():
    # 初始化游戏&设置和屏幕对象
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.init()
    pygame.font.init()
    pygame.display.init()

    assets = AssetManager()
    ai_settings = Settings(assets)
    screen = pygame.display.set_mode(
        (ai_settings.screen_width, ai_settings.screen_height))

    ai_settings.screen = screen
    ai_settings.assets.pre_load()         # 预加载资源和标题

    items = Items(ai_settings)
    player = Player(ai_settings)    # 玩家实例
    bullets = Group()   # 创建一个用于存储子弹的编组
    traps = Group()     # 创建一个用于存储陷阱的编组
    collision_detector = Collision(ai_settings, player, traps, items)  # 碰撞实例

    ai_settings.player_instance = player # 存储引用
    ai_settings.traps_instance = traps
    ai_settings.bullets_instance = bullets
    ai_settings.items_instance = items
    
    clock = pygame.time.Clock()         # 创建计时器锁帧用
    bgm.play_welcome_bgm(ai_settings)   # 播放bgm

    # 开始游戏的主循环
    while not ai_settings.game_over:
        clock.tick(100)   # 锁定帧数
        gf.check_events(ai_settings, player, bullets, traps, items)    # 监视键盘和鼠标事件
        player.update_move()    # 刷新玩家显示的位置
        Bullet.update_bullets(ai_settings, traps, bullets)      # 刷新子弹显示的位置
        Trap.monitor_trap_build(ai_settings, traps)     # 生成并刷新陷阱位置
        collision_detector.monitor_collision()    # 碰撞监测
        LimitBreak.monitor_lb_continue(collision_detector, ai_settings)     # 监测lb是否应该结束了
        FollowerMgr.monitor_follower(ai_settings, player)    # 监控宝石兽状态
        gf.update_screen(ai_settings, player, traps, bullets, items)   # 更新屏幕
        gf.monitor_game_over(ai_settings)  # 检测游戏是否结束

    return ai_settings


# ==================== 游戏主入口 ====================

if __name__ == '__main__':
    restart_game = True # 初始时，先运行一次游戏

    while restart_game:
        # 运行一局游戏，并获取ai_settings的最终状态
        final_ai_settings = run_game()

        # 游戏结束后，进入一个循环等待用户选择重启或退出
        restart_game = False # 假设默认不重启，除非用户选择
        while final_ai_settings.game_over: # 停留在游戏结束界面
            # 持续更新屏幕以显示结束画面
            gf.pin_last_frame(final_ai_settings, 
                               final_ai_settings.player_instance, 
                               final_ai_settings.traps_instance, 
                               final_ai_settings.bullets_instance, 
                               final_ai_settings.items_instance)
            
            # 监听事件，看玩家是否选择重启
            if gf.handle_game_over_events(final_ai_settings):
                restart_game = True # 设置为True，外部循环将再次运行 run_game()
                # 关键：这里需要 break 掉当前循环，以便外部循环能再次调用 run_game()
                break 
