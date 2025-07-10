from player import MoglinPlayer

class LimitBreak:
    '''LB大类'''
    # 技能实现归这个类管，lb条动画见items
    
    def __init__(self, ai_settings):
        self.ai_settings = ai_settings

    @staticmethod
    def charging(ai_settings):
        '''充能'''
        if not ai_settings.lb_charge_finished:
            nowtime = ai_settings.lb_clock.get_elapsed()
            if nowtime >= ai_settings.lb_cooldown_time:
                ai_settings.lb_state = 'ready'
                ai_settings.assets.loaded_sounds['effect.lb_ready'].play()
                ai_settings.lb_clock.stop()
                ai_settings.lb_charge_finished = True
            

    def use_lb(self):
        '''放LB'''
        self.ai_settings.assets.loaded_sounds['effect.lb_release'].play()
        self.ai_settings.lb_state = 'releasing'
        self.ai_settings.lb_releasing_clock.start()
        
    def recharge(self):
        '''结束LB'''
        self.ai_settings.lb_state = 'cooldown'
        self.ai_settings.lb_clock.start()
        self.ai_settings.lb_charge_finished = False
        LimitBreak.charging(self.ai_settings)


    @staticmethod
    def monitor_lb_continue(collision_detector, ai_settings):
        '''监测lb进程'''
        if ai_settings.first_lb:
            LimitBreak.charging(ai_settings)
            
        if ai_settings.lb_state == 'releasing' and ai_settings.lb_instance:
            collided_trap, trap_type = collision_detector.monitor_coll()
            ai_settings.lb_instance.update(trap_type)
            collision_detector.blood_calculation(collided_trap, trap_type)


class HealBloodPoint:
    '''小技能-回血（有数字接口）'''
    
    def __init__(self, heal_num, ai_settings):
        self.heal_num = heal_num
        self.ai_settings = ai_settings

    def apply(self):
        if self.ai_settings.now_blood < self.ai_settings.max_blood:
            self.ai_settings.now_blood = min(
                self.ai_settings.now_blood + self.heal_num,
                self.ai_settings.max_blood)

class HealBarrier:
    '''小技能-上盾(有数字接口)'''
    
    def __init__(self, barri_num, ai_settings):
        self.barri_num = barri_num
        self.ai_settings = ai_settings

    def apply(self):
        self.ai_settings.now_barri += self.barri_num



class DengDengLB(LimitBreak):
    '''上1层盾,回2滴血'''
    
    def __init__(self, ai_settings):
        super().__init__(ai_settings)
        self.duration = self.ai_settings.lb_continue_time['dengdeng']

    def apply(self, traps, ai_settings, player, items):
        self.use_lb()
        self.ai_settings.now_barri = min(3, self.ai_settings.now_barri + 1)
        self.ai_settings.now_blood = min(self.ai_settings.now_blood + 2, 
                                         self.ai_settings.max_blood)
        print('dengdeng lb applying')

    def update(self, trap_type):
        now_time = self.ai_settings.lb_releasing_clock.get_elapsed()
        if now_time >= self.duration:
            self.recharge()
            self.ai_settings.current_lb_instance = None
            print('dengdeng lb finished')


class JuRenLB(LimitBreak):
    '''无敌，撞击回血'''
    
    def __init__(self, ai_settings):
        super().__init__(ai_settings)
        self.duration = self.ai_settings.lb_continue_time['juren']

    def apply(self, traps, ai_settings, player, items):
        self.use_lb()
        print('juren lb applying')
    
    def update(self, trap_type):
        # 无敌+撞击回血
        if trap_type:
            self.ai_settings.temp_blood += 1
            HealBloodPoint(1, self.ai_settings).apply()
            
        now_time = self.ai_settings.lb_releasing_clock.get_elapsed()
        if now_time >= self.duration:
            self.recharge()
            self.ai_settings.current_lb_instance = None
            print('juren lb finished')


class BingTangLB(LimitBreak):
    '''可以发射子弹'''
    
    def __init__(self, ai_settings):
        super().__init__(ai_settings)
        self.duration = self.ai_settings.lb_continue_time['bingtang']

    def apply(self, traps, ai_settings, player, items):
        self.use_lb()
        self.ai_settings.bullet_able = True
        print('bingtang lb applying')

    def update(self, trap_type):
        now_time = self.ai_settings.lb_releasing_clock.get_elapsed()
        if now_time >= self.duration:
            self.ai_settings.bullet_able = False
            self.recharge()
            self.ai_settings.current_lb_instance = None
            print('bingtang lb finished')


class HaiTaLB(LimitBreak):
    '''无敌,清屏'''
    
    def __init__(self, ai_settings):
        super().__init__(ai_settings)
        self.duration = self.ai_settings.lb_continue_time['haita']

    def apply(self, traps, ai_settings, player, items):
        self.use_lb()
        self.ai_settings.haita_lb_on = True
        items.flash.trigger_lb_flash()
        self.ai_settings.trap_border = self.ai_settings.screen_width + 300
        self.ai_settings.assets.loaded_sounds['effect.moglin_appear'].set_volume(0)
        self.ai_settings.assets.loaded_sounds['effect.BLM_lb_releasing'].play()
        print('haita lb applying')

    def update(self, trap_type):
        # 无敌
        if trap_type:
            self.ai_settings.temp_blood += 1
            
        now_time = self.ai_settings.lb_releasing_clock.get_elapsed()
        if now_time >= self.duration:
            self.ai_settings.trap_border = 0 # 复原边界
            self.ai_settings.haita_lb_on = False
            self.recharge()
            self.ai_settings.current_lb_instance = None
            self.ai_settings.assets.loaded_sounds['effect.moglin_appear'].set_volume(1.0)
            print('haita lb finished')


class AChangLB(LimitBreak):
    '''改变精灵图，对莫古力箱子无敌'''
    
    def __init__(self, ai_settings):
        super().__init__(ai_settings)
        self.duration = self.ai_settings.lb_continue_time['achang']
        self.moglin_player = None

    def apply(self, traps, ai_settings, player, items):
        self.ai_settings.achang_lb_on = True
        self.use_lb()
        self.ai_settings.last_moglin_location = None
        self.ai_settings.moglin_player = MoglinPlayer(ai_settings, player)
        print('achang lb apply')

    def update(self, trap_type):
        # 变身莫古力后运动
        if self.ai_settings.moglin_player:
            self.ai_settings.moglin_player.update_move()

        # 对特定陷阱无敌
        if trap_type and (trap_type == 'spike' or trap_type == 'moglin'):
            self.ai_settings.temp_blood += 1

        now_time = self.ai_settings.lb_releasing_clock.get_elapsed()
        if now_time >= self.duration:
            self.recharge()
            self.ai_settings.last_moglin_location = self.ai_settings.moglin_player.rect.center
            self.ai_settings.moglin_player = None
            self.ai_settings.current_lb_instance = None
            self.ai_settings.achang_lb_on = False
            print('achang lb finished')

lb_list = {
    'haita':HaiTaLB,
    'dengdeng':DengDengLB,
    'bingtang':BingTangLB,
    'achang':AChangLB,
    'juren':JuRenLB,
    }
