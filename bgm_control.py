def play_welcome_bgm(ai_settings):
    '''播放开始界面的bgm'''
    ai_settings.assets.loaded_sounds['bgm.open'].set_volume(1.0)
    ai_settings.assets.loaded_sounds['bgm.open'].play(loops=-1)
    
def play_main_bgm(ai_settings):
    '''bgm切换'''
    now_time = ai_settings.bgm_clock.get_elapsed()
    if 0 < now_time <= 0.25:
        ai_settings.assets.loaded_sounds['bgm.main'].set_volume(0.25)
        ai_settings.assets.loaded_sounds['bgm.open'].set_volume(0.75)
    elif 0.25 < now_time <= 0.5:
        ai_settings.assets.loaded_sounds['bgm.main'].set_volume(0.5)
        ai_settings.assets.loaded_sounds['bgm.open'].set_volume(0.5)
    elif 0.5 < now_time <= 0.75:
        ai_settings.assets.loaded_sounds['bgm.main'].set_volume(0.75)
        ai_settings.assets.loaded_sounds['bgm.open'].set_volume(0.25)
    elif 0.75 < now_time <= 1.0:
        ai_settings.assets.loaded_sounds['bgm.main'].set_volume(1.0)
        ai_settings.assets.loaded_sounds['bgm.open'].set_volume(0.0)
    elif now_time > 1.0:
        print('bgm change finished')
        ai_settings.assets.loaded_sounds['bgm.open'].stop()
        ai_settings.bgm_clock.stop()
        ai_settings.change_bgm = False


def play_fail_bgm(ai_settings):
    '''播放失败时的BGM'''
    ai_settings.assets.loaded_sounds['bgm.main'].stop()
    ai_settings.assets.loaded_sounds['bgm.fail'].set_volume(0.7)
    ai_settings.assets.loaded_sounds['bgm.fail'].play(loops=0)
