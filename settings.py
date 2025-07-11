import pygame
import sys
import os
from pygame.surface import Surface
from typing import Any, Optional

import config
from tools import Timer


class Settings():
    '''存储游戏里的所有设置的类'''

    def __init__(self, assets: 'AssetManager'):
        # ----------------- 基础属性初始化 -----------------
        self.assets = assets                      # 引用资源池（只做引用）
        self.screen: Optional[Surface] = None     # 屏幕 Surface 占位符
        self.screen_width = config.SCREEN_WIDTH
        self.screen_height = config.SCREEN_HEIGHT
        self.floor_height = config.FLOOR_HEIGHT
        self.score_rate = config.SCORE_RATE       # 积分系数
        self.score = 0
        self.external_score_bonus = 0
        self.bg_color = config.BG_COLOR
        self.total_clock = Timer()

        # ----------------- 游戏流程状态标志 -----------------
        self.unstart = True           # 游戏是否尚未开始
        self.game_over = False        # 游戏是否结束
        self.final_score = None       # 游戏最终得分记录
        self.change_bgm = False       # 是否切换背景音乐
        self.bgm_clock = Timer()
        self.transparent_font = 0.2   # 分数透明度

        # ------------------- 游戏结束后备份 -------------------
        self.player_instance: Any = None   # 结束前存档
        self.traps_instance: Any = None
        self.bullets_instance: Any = None
        self.items_instance: Any = None

        # ----------------- 玩家物理参数：常规形态 -----------------
        self.max_speed_y = 50.0
        self.dash_speed = 70
        self.dash_distance = 300
        self.jump_force = 30.0
        self.friction = 0.98          # 横向摩擦力
        # self.dash_freeze = 35          # 冲刺硬直
        self.gravity = pygame.Vector2(0, 2)
        self.ground_speed = 20

        # ----------------- 玩家物理参数：莫古力形态 -----------------
        self.float_speed = 17
        self.horizontal_speed = 20
        self.horizontal_friction = 0.3
        self.float_gravity = pygame.Vector2(0, 1.0)

        # ----------------- 玩家角色管理 -----------------
        self.characters_list = list(
            self.assets.images_paths['player']['sprite'].keys())[:5]
        self.now_character = self.characters_list[2]

        # ----------------- LB系统 -----------------
        self.lb_continue_time = {
            'dengdeng': 1,
            'achang': 8,
            'haita': 4,
            'juren': 8,
            'bingtang': 10,
        }
        self.lb_clock = Timer()
        self.lb_releasing_clock = Timer()
        self.lb_state = 'cooldown'         # cooldown / ready / releasing
        self.lb_cooldown_time = 10
        self.lb_charge_finished = False
        self.first_lb = False
        self.current_lb_instance = None
        
        self.haita_lb_on = False

        self.achang_lb_on = False
        self.moglin_player = None
        self.last_moglin_location = None
        
        # ----------------- 生命值与护盾 -----------------
        self.max_blood = 5
        self.now_blood = 3
        self.temp_blood = 0
        self.now_barri = 0

        # ----------------- 宝石兽 -----------------
        self.follower_skill_gap = 3
        self.fairy = None
        self.carbuncle = None
        self.carbuncle_barri = 0

        # ----------------- 子弹系统 -----------------
        self.bullet_able = False
        self.bullet_speed_factor = 25
        self.bullets_allowed = 5            # 最多同时存在

        # ----------------- 陷阱系统 -----------------
        self.trap_send_clock = Timer()           # 发射间隔计时器
        self.trap_speed_clock = Timer()     # 速度计算计时器
        self.first_trap = True

        self.trap_gap = 10                          # 间隔发射距离
        self.trap_speed_0 = 8                       # 初始速度
        self.init_trap_acc = 0.5                    # 一段加速
        self.final_trap_acc = 0.3                   # 永久加速
        self.trap_now_speed = self.trap_speed_0
        self.trap_max_speed_stage1 = 15             # 一阶段最大速度
        self.trap_final_max_speed = 24              # 最终最大速度
        self.state = "INITIAL_ACCELERATION"
        self.speed_at_state_start = 0               # 存储不同状态的开始速度
        self.subsequent_cycle_count = 0             # 加速轮数

        self.moglin_height = 300
        self.last_trap_spawn_time = 0
        self.trap_running = {}
        self.trap_border = 0                        # 陷阱左清除边界




def resource_path(relative_path):
    """PyInstaller 兼容的路径获取"""
    try:
        # PyInstaller 创建的临时文件夹路径
        base_path = sys._MEIPASS # type: ignore[attr-defined]
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class AssetManager():
    def __init__(self):
        self.images_paths = {
            'player': {
                # 玩家角色精灵图路径
                'sprite': {
                    'dengdeng':'images/player/sprite_player_SCH_dd.png',
                    'achang':'images/player/sprite_player_SMN_ac.png',
                    'haita':'images/player/sprite_player_BLM.png',
                    'juren':'images/player/sprite_player_WAR_jr.png',
                    'bingtang':'images/player/sprite_player_PLD_bt.png',
                    'moglin':'images/player/sprite_moglin_ac_lb.png',
                }, 
                # 精灵图帧数
                'frame_num': {
                    'dengdeng':7,
                    'achang':9,
                    'haita':8,
                    'juren':8,
                    'bingtang':7,
                    'moglin':2,
                },  
            },

            'items':{
                'bloodbar': {
                    'full': 'images/blood/blood_full.png',
                    'empty': 'images/blood/blood_empty.png',
                    'barri': 'images/blood/barri.png',
                },
                'limitbreak': {
                    'outline': 'images/limitbreak/lb_outline.png',
                    'ready': 'images/limitbreak/lb_ready.png',
                    'charging': 'images/limitbreak/lb_charging.png',
                },

                'trap':{
                    'moglin':'images/traps/sprite_moglin_normal.png',
                    'ice':'images/traps/ice_test.png',
                    'spike':'images/traps/spike_test.png',
                    'cfs_moglin':'images/traps/sprite_moglin_confused.png'
                },

                'ui': {
                    'arrow':'images/items/sprite_arrow_frame.png',
                    'fail': 'images/items/fail.png',
                },

                'skill':{
                    'bullet': 'images/items/bullet.png',
                },
                
                'follower': {
                    'fairy': 'images/items/sprite_fairy.png',
                    'carbuncle': 'images/items/sprite_carbuncle.png',
                    'frame_num':4,
                },
            }
        }

        self.sounds_paths = {
            'bgm': {
                'open': 'bgm_effects/openning_ppy.ogg',
                'main': 'bgm_effects/mainbgm_ppy.ogg',
                'fail': 'bgm_effects/fail_bgm.wav',
            },

            'effect': {
                # 素材出现/消失音效
                'moglin_appear': 'bgm_effects/moglin_appear.wav',
                'character_switch': 'bgm_effects/character_switch.wav',
                'ice_broke': 'bgm_effects/ice_broke.wav',
                'arrow_confirm': 'bgm_effects/arrow_confirm.wav',
                'fire_bullet': 'bgm_effects/fire_bullet.wav',
                # lb相关音效
                'lb_ready': 'bgm_effects/LB_ready.wav',
                'lb_release':'bgm_effects/LB_release.wav',
                'BLM_lb_releasing':'bgm_effects/BLM_LB.wav',
                # 宝石兽技能音效
                'SCH_healing':'bgm_effects/SCH_healing.wav',
                'SMN_barrier':'bgm_effects/SMN_barrier_new.wav',
                # 宝石兽通用音效
                'carbuncle_call':'bgm_effects/carbuncle_call.wav',
                'fairy_call':'bgm_effects/fairy_call.wav',
                'follower_leave':'bgm_effects/follower_leave.wav',
            }
        }

        self.loaded_images = {}  # 最终加载好的图像资源
        self.loaded_sounds = {}  # 最终加载好的音效资源

    def pre_load(self):
        '''预加载所有图片和音频资源'''
        def load_images_from_dict(d, prefix=''):
            for key, val in d.items():
                flat_key = f'{prefix}.{key}' if prefix else key
                if isinstance(val, str) and val.endswith(('.png', '.jpg', '.jpeg')):
                    self.loaded_images[flat_key] = pygame.image.load(resource_path(val)).convert_alpha()
                elif isinstance(val, (int, float)):
                    self.loaded_images[flat_key] = val
                elif isinstance(val, dict):
                    load_images_from_dict(val, flat_key)

        def load_sounds_from_dict(d, prefix=''):
            for key, val in d.items():
                flat_key = f'{prefix}.{key}' if prefix else key
                if isinstance(val, str) and val.endswith(('.wav', '.ogg', '.mp3')):
                    self.loaded_sounds[flat_key] = pygame.mixer.Sound(resource_path(val))
                elif isinstance(val, (int, float)):
                    self.loaded_sounds[flat_key] = val
                elif isinstance(val, dict):
                    load_sounds_from_dict(val, flat_key)

        pygame.display.set_caption("FF XIV - Great Adventure")
        pygame.mixer.music.set_volume(1.0)
        load_images_from_dict(self.images_paths)
        load_sounds_from_dict(self.sounds_paths)