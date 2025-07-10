class Collision:
    def __init__(self, ai_settings, player, traps, items):
        self.ai_settings = ai_settings
        self.player = player
        self.traps = traps
        self.moglin_player = ai_settings.moglin_player
        self.items = items

    def get_current_player(self):
        return self.ai_settings.moglin_player if self.ai_settings.achang_lb_on else self.player

    def monitor_coll(self):
        current_player = self.get_current_player()
        for trap in self.traps:
            if not trap.marked:
                trap_coll_rect = trap.get_collision_rect()
                if current_player.get_collision_rect().colliderect(trap_coll_rect):
                    trap.marked = True

                    if self.ai_settings.achang_lb_on and trap.trap_type == 'moglin':
                        trap.set_marked_sprite() # 改变 moglin 陷阱的精灵图

                    return trap, self.ai_settings.trap_running[trap]
        return None, None # 没有碰撞时返回 (None, None)


    def blood_calculation(self, collided_trap, trap_type):
        current_player = self.get_current_player()
        if trap_type:
            if (trap_type == 'ice' and 
                current_player.vel.x > self.ai_settings.ground_speed
                ):
                self.traps.remove(collided_trap)
                del self.ai_settings.trap_running[collided_trap]
                self.items.flash.trigger_shake_screen()
                self.ai_settings.assets.loaded_sounds['effect.ice_broke'].set_volume(0.2)
                self.ai_settings.assets.loaded_sounds['effect.ice_broke'].play()

            else:
                if self.ai_settings.temp_blood >= 1:
                    self.ai_settings.temp_blood -= 1
                    
                elif self.ai_settings.carbuncle_barri >= 1:
                    self.ai_settings.carbuncle_barri -= 1

                elif self.ai_settings.now_barri >= 1:
                    self.ai_settings.now_barri -= 1
                    
                elif self.ai_settings.now_blood >= 1:
                    self.ai_settings.now_blood -= 1
                    self.items.flash.trigger_red_flash()

    def monitor_collision(self):
        if not self.ai_settings.unstart and self.ai_settings.lb_state != 'releasing':
            collided_trap, trap_type = self.monitor_coll()
            self.blood_calculation(collided_trap, trap_type)