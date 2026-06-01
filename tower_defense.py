import pygame
import math
import random
import os

pygame.init()

# KONSTANDID JA RESSURSID

WIDTH, HEIGHT = 1400, 800
FPS = 60

GRASS = (45, 115, 45)
GRASS_DETAIL = (35, 100, 35)
ROAD = (135, 105, 75)
ROAD_BORDER = (100, 75, 50)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (220, 50, 50)
GREEN = (50, 220, 50)
GOLD = (255, 210, 40)
CYAN = (50, 200, 255)
PURPLE = (160, 60, 220)
UI_BG = (35, 38, 43)
UI_BORDER = (60, 65, 70)

FONT_NORMAL = pygame.font.SysFont("arial", 26, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 18, bold=True)
FONT_BIG = pygame.font.SysFont("arial", 65, bold=True)

# Zombide liikumistrajektoor
PATH = [
    (0, 380), (250, 380), (250, 170), (650, 170),
    (650, 580), (1050, 580), (1050, 280), (1200, 280)
]

BACKGROUND_DETAILS = []
for _ in range(120):
    rx = random.randint(0, 1180)
    ry = random.randint(80, HEIGHT)
    BACKGROUND_DETAILS.append((rx, ry, random.randint(3, 6)))

# OLEMID JA MÜRSUD

class Particle:
    # Visuaalsed efektid (plahvatused, verepritsmed)
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.dx = random.uniform(-2.5, 2.5)
        self.dy = random.uniform(-2.5, 2.5)
        self.life = random.randint(20, 40)
        self.color = color
        self.size = random.randint(2, 6)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)


class Projectile:
    # Tornide tulistatud mürsud
    def __init__(self, game, x, y, target, damage, speed, color=WHITE, is_aoe=False):
        self.game = game
        self.x, self.y = x, y
        self.target = target
        self.damage = damage
        self.speed = speed
        self.color = color
        self.is_aoe = is_aoe

    def update(self):
        if self.target not in self.game.zombies:
            return False

        dx, dy = self.target.x - self.x, self.target.y - self.y
        distance = math.hypot(dx, dy)

        if distance != 0:
            dx /= distance
            dy /= distance

        self.x += dx * self.speed
        self.y += dy * self.speed

        if distance < max(20, self.speed):
            self.hit_target()
            return False 
        return True 

    def hit_target(self):
        if self.is_aoe:
            for z in self.game.zombies:
                if math.hypot(z.x - self.x, z.y - self.y) < 110:
                    z.take_damage(self.damage)
            for _ in range(35):
                self.game.particles.append(Particle(self.x, self.y, PURPLE))
        else:
            self.target.take_damage(self.damage)
            for _ in range(8):
                self.game.particles.append(Particle(self.target.x, self.target.y, RED))

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y) + 2), 7)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 6)

# TORNID

class Tower:
    # Baasklass kõikidele tornidele
    def __init__(self, game, x, y):
        self.game = game
        self.x, self.y = x, y
        self.level = 1
        self.cooldown = 0
        self.angle = 0
        
        self.range = 100
        self.damage = 10
        self.fire_rate = 60
        self.upgrade_cost = 100
        self.base_cost = 100
        self.proj_speed = 10
        self.proj_color = WHITE
        self.is_aoe = False
        self.color = (130, 130, 130)

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

        closest = None
        closest_dist = float('inf')

        for zombie in self.game.zombies:
            dist = math.hypot(zombie.x - self.x, zombie.y - self.y)
            if dist < self.range and dist < closest_dist:
                closest = zombie
                closest_dist = dist

        if closest:
            self.angle = math.atan2(closest.y - self.y, closest.x - self.x)
            if self.cooldown == 0:
                self.shoot(closest)
                self.cooldown = self.fire_rate

    def shoot(self, target):
        self.game.projectiles.append(
            Projectile(self.game, self.x, self.y - 15, target, self.damage, self.proj_speed, self.proj_color, self.is_aoe)
        )

    def upgrade(self):
        if self.game.money >= self.upgrade_cost:
            self.game.money -= self.upgrade_cost
            self.base_cost += self.upgrade_cost // 2
            self.level += 1
            self.damage = int(self.damage * 1.6)
            self.range += 15
            self.fire_rate = max(8, self.fire_rate - 3)
            self.upgrade_cost = int(self.upgrade_cost * 1.4)

    def draw(self, screen):
        pygame.draw.circle(screen, (40, 40, 40), (self.x, self.y + 12), 28)
        pygame.draw.rect(screen, (100, 100, 105), (self.x - 22, self.y - 5, 44, 25), border_radius=4)
        pygame.draw.rect(screen, (125, 125, 130), (self.x - 22, self.y - 5, 44, 6))
        
        gun_length = 25
        end_x = self.x + math.cos(self.angle) * gun_length
        end_y = (self.y - 12) + math.sin(self.angle) * gun_length
        
        pygame.draw.line(screen, (50, 50, 50), (self.x, self.y - 12), (end_x, end_y), 7)
        pygame.draw.line(screen, self.color, (self.x, self.y - 12), (end_x, end_y), 5)
        
        pygame.draw.circle(screen, self.color, (self.x, self.y - 12), 16)
        pygame.draw.circle(screen, (30, 30, 30), (self.x, self.y - 12), 16, 2)
        
        txt = FONT_SMALL.render(str(self.level), True, GOLD)
        screen.blit(txt, (self.x - txt.get_width()//2, self.y + 22))

# Erinevad tornitüübid
class KnightTower(Tower):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.range = 140
        self.damage = 45
        self.fire_rate = 35
        self.base_cost = 100
        self.upgrade_cost = 120
        self.color = (65, 105, 225)

class ArcherTower(Tower):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.range = 240
        self.damage = 18
        self.fire_rate = 16
        self.proj_speed = 18
        self.proj_color = (240, 200, 120)
        self.base_cost = 100
        self.upgrade_cost = 90
        self.color = (46, 139, 87)

class MageTower(Tower):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.range = 190
        self.damage = 35
        self.fire_rate = 75
        self.proj_color = PURPLE
        self.is_aoe = True
        self.base_cost = 200
        self.upgrade_cost = 200
        self.color = (147, 112, 219)

class SniperTower(Tower):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.range = 480
        self.damage = 180
        self.fire_rate = 110
        self.proj_speed = 30
        self.proj_color = RED
        self.base_cost = 500
        self.upgrade_cost = 350
        self.color = (178, 34, 34)

# VAENLASED

class Zombie:
    def __init__(self, game, is_boss=False):
        self.game = game
        self.x, self.y = PATH[0]
        self.path_index = 1
        self.is_boss = is_boss
        
        if self.is_boss:
            self.type = "BOSS"
            self.speed = 0.7 + (self.game.wave * 0.03)
            self.max_health = (150 + self.game.wave * 35) * 10
            self.radius = 42
            self.color = (30, 30, 30)
            self.reward = 300 + (self.game.wave * 20)
        else:
            self.type = random.choice(["normal", "fast", "tank"])
            self.speed = 1.4 + self.game.wave * 0.07
            self.max_health = 100 + self.game.wave * 28
            self.reward = 40

            if self.type == "fast":
                self.speed *= 1.8
                self.max_health *= 0.6
                self.color = (50, 210, 50)
                self.radius = 18
            elif self.type == "tank":
                self.speed *= 0.55
                self.max_health *= 2.6
                self.color = (120, 90, 60)
                self.radius = 28
            else:
                self.color = (75, 160, 75)
                self.radius = 22

        self.health = self.max_health

    def take_damage(self, amount):
        self.health -= amount

    def update(self):
        if self.path_index >= len(PATH):
            self.game.lives -= 5 if self.is_boss else 1
            return False

        target_x, target_y = PATH[self.path_index]
        dx, dy = target_x - self.x, target_y - self.y
        distance = math.hypot(dx, dy)

        if distance != 0:
            dx /= distance
            dy /= distance

        self.x += dx * self.speed
        self.y += dy * self.speed

        if distance < 6:
            self.path_index += 1

        return True

    def die(self):
        death_color = GOLD if self.is_boss else RED
        particle_count = 50 if self.is_boss else 15
        for _ in range(particle_count):
            self.game.particles.append(Particle(self.x, self.y, death_color))
        self.game.money += self.reward

    def draw(self, screen):
        pygame.draw.ellipse(screen, (20, 40, 20, 80), (self.x - self.radius, self.y + self.radius - 8, self.radius * 2, 14))
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (20, 20, 20), (int(self.x), int(self.y)), self.radius, 2)
        
        eye_color = RED if self.is_boss else WHITE
        pygame.draw.circle(screen, eye_color, (int(self.x) + 4, int(self.y) - 4), 4)
        if self.is_boss:
            pygame.draw.circle(screen, eye_color, (int(self.x) + 14, int(self.y) - 4), 4)
        else:
            pygame.draw.circle(screen, eye_color, (int(self.x) - 4, int(self.y) - 4), 4)
        
        if self.is_boss:
            points = [
                (self.x - 25, self.y - 35), (self.x - 20, self.y - 55),
                (self.x - 5, self.y - 42), (self.x, self.y - 60), (self.x + 5, self.y - 42),
                (self.x + 20, self.y - 55), (self.x + 25, self.y - 35)
            ]
            pygame.draw.polygon(screen, GOLD, points)
            pygame.draw.polygon(screen, (180, 140, 10), points, 2)

        health_ratio = max(0, self.health / self.max_health)
        bar_width = self.radius * 1.6
        pygame.draw.rect(screen, BLACK, (self.x - bar_width//2, self.y - self.radius - 12, bar_width, 6))
        pygame.draw.rect(screen, GREEN, (self.x - bar_width//2, self.y - self.radius - 12, bar_width * health_ratio, 6))

# MÄNGU PEAKLASS

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Zombie Kingdom Defense ULTRA + BOSSES")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "MENU"
        self.selected_tower_type = KnightTower
        self.sell_mode = False
        
        self.highscore = self.load_highscore()
        self.reset_game()

    def load_highscore(self):
        if os.path.exists("highscore.txt"):
            try:
                with open("highscore.txt", "r") as f: return int(f.read().strip())
            except: return 1
        return 1

    def save_highscore(self):
        with open("highscore.txt", "w") as f: f.write(str(self.highscore))

    def reset_game(self):
        self.money = 300
        self.lives = 20
        self.wave = 1
        self.zombies = []
        self.projectiles = []
        self.towers = []
        self.particles = []
        self.spawn_timer = 0
        self.sell_mode = False
        self.start_wave()

    def start_wave(self):
        if self.wave % 5 == 0:
            self.boss_needs_spawn = True
            self.zombies_to_spawn = (6 + self.wave * 3) // 2
        else:
            self.boss_needs_spawn = False
            self.zombies_to_spawn = 6 + self.wave * 3

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "PLAYING": self.state = "PAUSED"
                    elif self.state == "PAUSED": self.state = "PLAYING"

                if self.state == "PLAYING":
                    if event.key == pygame.K_1: self.selected_tower_type = KnightTower; self.sell_mode = False
                    if event.key == pygame.K_2: self.selected_tower_type = ArcherTower; self.sell_mode = False
                    if event.key == pygame.K_3: self.selected_tower_type = MageTower; self.sell_mode = False
                    if event.key == pygame.K_4: self.selected_tower_type = SniperTower; self.sell_mode = False
                    if event.key == pygame.K_s: self.sell_mode = not self.sell_mode

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                if self.state == "MENU":
                    self.state = "PLAYING"
                elif self.state == "GAME_OVER":
                    self.reset_game()
                    self.state = "PLAYING"
                elif self.state == "PLAYING":
                    # Küljemenüü (UI) klikkimine
                    if mx >= 1200:
                        if 1210 <= mx <= 1390 and 610 <= my <= 670:
                            self.sell_mode = not self.sell_mode
                        return

                    # Mänguväljale klikkimine
                    if mx < 1200 and my > 80:
                        if self.sell_mode:
                            if event.button == 1:
                                for tower in self.towers[:]:
                                    if math.hypot(tower.x - mx, tower.y - my) < 32:
                                        refund = int(tower.base_cost * 0.75)
                                        self.money += refund
                                        for _ in range(12):
                                            self.particles.append(Particle(tower.x, tower.y, GOLD))
                                        self.towers.remove(tower)
                                        self.sell_mode = False
                                        break
                        else:
                            if event.button == 1: 
                                cost = self.selected_tower_type(self, 0, 0).base_cost
                                if self.money >= cost:
                                    overlapping = False
                                    for t in self.towers:
                                        if math.hypot(t.x - mx, t.y - my) < 45: overlapping = True
                                    if not overlapping:
                                        self.towers.append(self.selected_tower_type(self, mx, my))
                                        self.money -= cost

                            if event.button == 3:
                                for tower in self.towers:
                                    if math.hypot(tower.x - mx, tower.y - my) < 32:
                                        tower.upgrade()

    def update_playing(self):
        self.spawn_timer += 1
        
        # Vaenlaste loomine
        if self.wave % 5 == 0:
            if self.boss_needs_spawn and self.spawn_timer >= 40:
                self.zombies.append(Zombie(self, is_boss=True))
                self.boss_needs_spawn = False
                self.spawn_timer = 0
            elif not self.boss_needs_spawn and self.spawn_timer >= 65 and self.zombies_to_spawn > 0:
                self.zombies.append(Zombie(self, is_boss=False))
                self.zombies_to_spawn -= 1
                self.spawn_timer = 0
        else:
            if self.spawn_timer >= 45 and self.zombies_to_spawn > 0:
                self.zombies.append(Zombie(self, is_boss=False))
                self.zombies_to_spawn -= 1
                self.spawn_timer = 0

        for zombie in self.zombies[:]:
            if not zombie.update():
                self.zombies.remove(zombie)
            elif zombie.health <= 0:
                zombie.die()
                self.zombies.remove(zombie)

        for tower in self.towers: tower.update()

        for proj in self.projectiles[:]:
            if not proj.update():
                self.projectiles.remove(proj)

        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

        # Laine lõppemise kontroll
        if len(self.zombies) == 0 and self.zombies_to_spawn == 0 and not self.boss_needs_spawn:
            self.wave += 1
            if self.wave > self.highscore:
                self.highscore = self.wave
                self.save_highscore()
            self.start_wave()

        if self.lives <= 0:
            self.state = "GAME_OVER"

    def draw_playing(self):
        self.screen.fill(GRASS)
        
        for detail in BACKGROUND_DETAILS:
            pygame.draw.circle(self.screen, GRASS_DETAIL, (detail[0], detail[1]), detail[2])

        pygame.draw.lines(self.screen, ROAD_BORDER, False, PATH, 86)
        pygame.draw.lines(self.screen, ROAD, False, PATH, 70)
        
        for point in PATH:
            if point[0] < 1200:
                pygame.draw.circle(self.screen, (70, 50, 30), point, 8)
                pygame.draw.circle(self.screen, (110, 85, 55), point, 6)

        for tower in self.towers: tower.draw(self.screen)
        for zombie in self.zombies: zombie.draw(self.screen)
        for proj in self.projectiles: proj.draw(self.screen)
        for particle in self.particles: particle.draw(self.screen)

        # Dünaamiline kursor ja torni laskeulatus
        mx, my = pygame.mouse.get_pos()
        if mx < 1200 and my > 80:
            if self.sell_mode:
                pygame.draw.circle(self.screen, (255, 50, 50, 100), (mx, my), 25, 2)
            else:
                temp_tower = self.selected_tower_type(self, mx, my)
                range_surf = pygame.Surface((temp_tower.range * 2, temp_tower.range * 2), pygame.SRCALPHA)
                pygame.draw.circle(range_surf, (temp_tower.color[0], temp_tower.color[1], temp_tower.color[2], 50), (temp_tower.range, temp_tower.range), temp_tower.range)
                pygame.draw.circle(range_surf, (temp_tower.color[0], temp_tower.color[1], temp_tower.color[2], 160), (temp_tower.range, temp_tower.range), temp_tower.range, 2)
                self.screen.blit(range_surf, (mx - temp_tower.range, my - temp_tower.range))

        # Ülemine UI riba
        pygame.draw.rect(self.screen, (22, 24, 28), (0, 0, WIDTH, 80))
        pygame.draw.line(self.screen, UI_BORDER, (0, 80), (WIDTH, 80), 2)
        
        self.screen.blit(FONT_NORMAL.render(f"GOLD: {self.money}", True, GOLD), (25, 24))
        self.screen.blit(FONT_NORMAL.render(f"LIVES: {self.lives}", True, WHITE), (240, 24))
        
        wave_color = RED if self.wave % 5 == 0 else WHITE
        wave_label = f"WAVE: {self.wave} (BOSS + MINIONS!)" if self.wave % 5 == 0 else f"WAVE: {self.wave}"
        self.screen.blit(FONT_NORMAL.render(wave_label, True, wave_color), (460, 24))
        self.screen.blit(FONT_NORMAL.render(f"HIGH SCORE: {self.highscore}", True, GOLD), (740, 24))

        # Küljemenüü (Pood)
        pygame.draw.rect(self.screen, UI_BG, (1200, 80, 200, HEIGHT - 80))
        pygame.draw.line(self.screen, UI_BORDER, (1200, 80), (1200, HEIGHT), 4)

        shop_title = FONT_NORMAL.render("SHOP PANEL", True, WHITE)
        self.screen.blit(shop_title, (1225, 105))
        
        tower_info = [
            ("1. Knight", 100, (65, 105, 225)),
            ("2. Archer", 100, (46, 139, 87)),
            ("3. Mage", 200, (147, 112, 219)),
            ("4. Sniper", 500, (178, 34, 34))
        ]

        for i, (name, price, color) in enumerate(tower_info):
            y_pos = 165 + i * 110
            
            current_type_name = self.selected_tower_type.__name__.lower()
            if name.split(". ")[1].lower() in current_type_name and not self.sell_mode:
                pygame.draw.rect(self.screen, (50, 65, 85), (1212, y_pos - 8, 176, 95), border_radius=8)
                pygame.draw.rect(self.screen, CYAN, (1212, y_pos - 8, 176, 95), 2, border_radius=8)
            else:
                pygame.draw.rect(self.screen, (24, 26, 30), (1212, y_pos - 8, 176, 95), border_radius=8)

            pygame.draw.circle(self.screen, color, (1240, y_pos + 22), 12)
            self.screen.blit(FONT_SMALL.render(name, True, WHITE), (1265, y_pos + 10))
            self.screen.blit(FONT_SMALL.render(f"Cost: {price}", True, GOLD), (1265, y_pos + 36))

        # Müügi nupp
        if self.sell_mode:
            pygame.draw.rect(self.screen, RED, (1210, 610, 180, 60), border_radius=8)
            sell_text = FONT_NORMAL.render("CANCEL SELL", True, WHITE)
        else:
            pygame.draw.rect(self.screen, (90, 30, 30), (1210, 610, 180, 60), border_radius=8)
            pygame.draw.rect(self.screen, RED, (1210, 610, 180, 60), 2, border_radius=8)
            sell_text = FONT_NORMAL.render("SELL TOWER [S]", True, WHITE)
            
        self.screen.blit(sell_text, (1300 - sell_text.get_width()//2, 626))

        controls = FONT_SMALL.render("L-CLICK: Place/Select | R-CLICK: Upgrade | S: Sell Mode Toggle | ESC: Pause", True, WHITE)
        pygame.draw.rect(self.screen, (15, 15, 15), (0, HEIGHT - 35, 1200, 35))
        self.screen.blit(controls, (25, HEIGHT - 26))

    def draw(self):
        if self.state == "MENU":
            self.screen.fill(BLACK)
            title = FONT_BIG.render("ZOMBIE REALM DEFENSE", True, GREEN)
            prompt = FONT_NORMAL.render("Click Anywhere to Enter the Battle", True, WHITE)
            hs_text = FONT_NORMAL.render(f"Record Score: Wave {self.highscore}", True, GOLD)
            
            self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 260))
            self.screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 410))
            self.screen.blit(hs_text, (WIDTH//2 - hs_text.get_width()//2, 495))

        elif self.state == "PLAYING":
            self.draw_playing()

        elif self.state == "PAUSED":
            self.draw_playing() 
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(160)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            pause_txt = FONT_BIG.render("GAME PAUSED", True, WHITE)
            self.screen.blit(pause_txt, (WIDTH//2 - pause_txt.get_width()//2, 350))

        elif self.state == "GAME_OVER":
            self.screen.fill(BLACK)
            over_txt = FONT_BIG.render("THE KINGDOM HAS FALLEN!", True, RED)
            score_txt = FONT_NORMAL.render(f"Defeated on Wave {self.wave} | Lifetime Best: Wave {self.highscore}", True, GOLD)
            restart_txt = FONT_NORMAL.render("Click Anywhere to Try Again", True, WHITE)
            
            self.screen.blit(over_txt, (WIDTH//2 - over_txt.get_width()//2, 250))
            self.screen.blit(score_txt, (WIDTH//2 - score_txt.get_width()//2, 380))
            self.screen.blit(restart_txt, (WIDTH//2 - restart_txt.get_width()//2, 460))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            if self.state == "PLAYING":
                self.update_playing()
            self.draw()
            
        pygame.quit()

if __name__ == "__main__":
    Game().run()
