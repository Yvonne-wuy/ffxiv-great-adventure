import sys
import pygame

import lb_skill
import bgm_control as bgm
from ui_items import EndPlay
from bullet import Bullet as blt

# =================== 输入检测 ===================
def check_events(ai_settings, player, bullets, traps, items):
    '''响应按键和鼠标事件'''
    if ai_settings.change_bgm == True: # 监听按下开始切换bgm
            ai_settings.bgm_clock.update() # 更新定时器
            bgm.play_main_bgm(ai_settings)

    player.base_move_logic.continuous_key_ad() # 按住ad持续移动

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            check_bullets_events(event, ai_settings, player, bullets)
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, player, traps, items)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, player)

def check_keydown_events(event, ai_settings, player, traps, items):
    '''响应KeyDown按下'''
    if event.key == pygame.K_d:
        player.base_move_logic.down_key_ad('right')
            
    elif event.key == pygame.K_a:
        player.base_move_logic.down_key_ad('left')
            
    elif event.key == pygame.K_w:
        player.base_move_logic.down_key_w()
        

    elif event.key == pygame.K_s:
        print(ai_settings.moglin_player)
        pass

    elif event.key == pygame.K_q:
        switch_character(ai_settings, player)
        
    elif event.key == pygame.K_e:
        if not ai_settings.unstart and ai_settings.lb_state == 'ready':
            current_lb_key = ai_settings.now_character
            lb_class = lb_skill.lb_list[current_lb_key]
            if lb_class:
                ai_settings.lb_instance = lb_class(ai_settings)
                ai_settings.lb_instance.apply(traps, ai_settings, player, items)
        
    elif event.key == pygame.K_RETURN:
        game_start_prepare(ai_settings, player)

    elif event.key == pygame.K_LEFT:
        if items.opening.selected_index > 0 and ai_settings.unstart:
            items.opening.selected_index -= 1
            items.opening.opening_char_choose()

    elif event.key == pygame.K_RIGHT:
        if items.opening.selected_index < len(items.opening.start_player_coord) - 1 and ai_settings.unstart:
            items.opening.selected_index += 1
            items.opening.opening_char_choose()


def check_bullets_events(event, ai_settings, player, bullets):
    '''响应鼠标按下子弹发射'''
    if event.type == pygame.MOUSEBUTTONDOWN and ai_settings.bullet_able:
        blt.fire_bullet(ai_settings, player, bullets)

def check_keyup_events(event, player):
    '''响应KeyUp松开'''
    if event.key == pygame.K_d:
        player.base_move_logic.up_key_ad('right')
    elif event.key == pygame.K_a:
        player.base_move_logic.up_key_ad('left')
    elif event.key == pygame.K_w:
        player.base_move_logic.up_key_w()

def game_start_prepare(ai_settings, player):
    '''按下开始绑定的东西'''
    if ai_settings.unstart == True:
        ai_settings.unstart = False
        player.load_sprite_for_character()
        
        ai_settings.change_bgm = True # 打开切换bgm标志
        ai_settings.assets.loaded_sounds['bgm.main'].set_volume(1.0)
        ai_settings.assets.loaded_sounds['bgm.main'].play(loops=-1)
        
        ai_settings.total_clock.start() # 开启总计时器
        ai_settings.bgm_clock.start() # 启动bgm切换计时器
        ai_settings.trap_send_clock.start() # 启动陷阱生成计时器
        ai_settings.lb_clock.start() # 启动lb条计时器
        ai_settings.first_lb = True
    


# =================== 绘制屏幕 ===================
def update_screen(ai_settings, player, traps, bullets, items):
    '''
    更新屏幕上的图像，并且切换到新屏幕
    '''
    # 绘制背景填充
    ai_settings.screen.fill(ai_settings.bg_color)

    # --------------- surface图层开始 ---------------
    items.flash.update_shake_screen()   # 获取偏移量
    offset_x, offset_y = ai_settings.current_shake_offset

    target_surface = pygame.Surface(
        (ai_settings.screen_width, ai_settings.screen_height),
        pygame.SRCALPHA # 添加这个标志，表示 Surface 带有 Alpha (透明) 通道
    )

    # 绘制分数
    items.score.score_display(target_surface)     # 会动的都是blit_name,不会动的都是name_display

    # 重绘所有子弹
    for bullet in bullets.sprites():
        bullet.blit_bullet(target_surface)
    
    # 绘制陷阱
    for trap in traps.sprites():
        trap.update(traps)
        trap.blit_trap(target_surface)

    # 绘制血条和lb
    items.blood_bar.blood_display(target_surface)
    items.lb_bar.update_lb_state()
    items.lb_bar.lb_bar_display(target_surface)

    ai_settings.screen.blit(target_surface, (offset_x, offset_y))
    # --------------- surface图层结束 ---------------

    # 绘制宝石兽（如果有）
    if ai_settings.fairy:
        ai_settings.fairy.update()
        ai_settings.fairy.blit_follower()
    if ai_settings.carbuncle:
        ai_settings.carbuncle.update()
        ai_settings.carbuncle.blit_follower()

    # 绘制开场
    items.opening.opening_display()

    # 绘制掉血变红特效
    items.flash.update_and_draw_red_flash()

    # 绘制玩家（最上面的图层）
    if not ai_settings.achang_lb_on and not ai_settings.unstart:
        player.update_sprite()
        player.blit_player()

    # 绘制lb莫古力
    if ai_settings.moglin_player:
        ai_settings.moglin_player.update_sprite()
        ai_settings.moglin_player.blit_mg_player()

    # 黑魔lb阴影
    items.flash.blm_lb_darkscreen(ai_settings.screen)
    
    # 让最近绘制的屏幕可见
    pygame.display.flip()



# =================== 角色切换 ===================
def switch_character(ai_settings, player):
    '''切换角色'''
    if ai_settings.lb_state == 'releasing' or ai_settings.unstart:
        return
    # 找到当前角色在键列表中的索引
    current_index = ai_settings.characters_list.index(ai_settings.now_character)
    next_index = (current_index + 1) % len(ai_settings.characters_list)
    
    ai_settings.now_character = ai_settings.characters_list[next_index]
    ai_settings.assets.loaded_sounds['effect.character_switch'].play()
    player.load_sprite_for_character()



# =================== 结束游戏 ===================
def monitor_game_over(ai_settings):
    '''监测是否应该结束游戏了'''
    if not ai_settings.unstart and ai_settings.now_blood < 1:
        ai_settings.game_over = True
        bgm.play_fail_bgm(ai_settings)

def pin_last_frame(ai_settings, player, traps, bullets, items):
    '''结束后主循环'''
    # quit_and_restart()
    EndPlay.last_score(ai_settings)
    last_frame(ai_settings, player, traps, bullets, items)

def last_frame(ai_settings, player, traps, bullets, items):
    # 重绘背景屏幕
    ai_settings.screen.fill(ai_settings.bg_color)

    # 绘制分数
    text_surface, text_rect = items.score.build_score_surface() # 预制分数
    ai_settings.screen.blit(text_surface, text_rect)

    # 重绘所有子弹
    for bullet in bullets.sprites():
        bullet.draw_bullet(ai_settings.screen)

    # 绘制陷阱
    for trap in traps.sprites():
        trap.blit_trap(ai_settings.screen)

    # 绘制血条和lb
    items.blood_bar.blood_display(ai_settings.screen)
    items.lb_bar.lb_bar_display(ai_settings.screen)

    # 绘制宝石兽（如果有）
    if ai_settings.fairy:
        ai_settings.fairy.blit_follower()
    if ai_settings.carbuncle:
        ai_settings.carbuncle.blit_follower()

    # 绘制玩家（最上面的图层）
    if not ai_settings.achang_lb_on:
        player.blit_player()

    # 绘制lb莫古力
    if ai_settings.moglin_player:
        ai_settings.moglin_player.blit_mg_player()

    EndPlay.slide_in_fail_image(ai_settings)

    # 让最近绘制的屏幕可见
    pygame.display.flip()


def handle_game_over_events(ai_settings):
    '''在游戏结束后，监听玩家输入以决定是退出还是重启'''
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        # 假设你设置了 'R' 键为重启，或者点击一个“重新开始”按钮
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: # 按下 'R' 键重启
                ai_settings.assets.loaded_sounds['bgm.fail'].stop()
                return True # 返回True表示需要重启
    return False # 返回False表示不需要重启或继续等待