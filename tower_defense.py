import pygame
import math
import random
import os

pygame.init()

# ==========================================
# CONSTANTS & ASSETS
# ==========================================

WIDTH, HEIGHT = 1400, 800
FPS = 60

GRASS = (55, 125, 55)
ROAD = (120, 90, 60)
DARK_ROAD = (90, 65, 40)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (220, 50, 50)
GREEN = (50, 220, 50)
GOLD = (255, 210, 40)
CYAN = (50, 200, 255)
PURPLE = (150, 50, 200)
UI_BG = (40, 45, 50)      # Külgmenüü taustavärv
UI_BORDER = (70, 75, 80)  # Külgmenüü äärejoone värv

FONT_NORMAL = pygame.font.SysFont("arial", 28, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 20, bold=True)
FONT_BIG = pygame.font.SysFont("arial", 70, bold=True)

PATH = [
    (0, 380), (250, 380), (250, 170), (650, 170),
    (650, 580), (1050, 580), (1050, 280), (1200, 280) # Lühendatud poeala jaoks (1200)
]

def load_image(filename, scale):
    if os.path.exists(filename):
        img = pygame.image.load(filename).convert_alpha()
        return pygame.transform.scale(img, scale)
    return None

IMAGES = {
    "zombie": None,
    "tank": None,
    "fast": None,
    "tower_base": None,
}

# ==========================================
# ENTITIES & PROJECTILES
# ==========================================

class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.dx = random.uniform(-2, 2)
        self.dy = random.uniform(-2, 2)
        self.life = 30
        self.color = color
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)


class Projectile:
    def __init__(self, game, x, y, target, damage, speed, color=WHITE, is_aoe=False):
        self.game = game
        self.x, self.y = x, y
        self.target = target
        self.damage = damage
        self.speed = speed
        self.color = color
        self.is_aoe = is_aoe

    def update(self):
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
                if math.hypot(z.x - self.x, z.y - self.y) < 100:
                    z.take_damage(self.damage)
            for _ in range(30):
                self.game.particles.append(Particle(self.x, self.y, PURPLE))
        else:
            self.target.take_damage(self.damage)
            for _ in range(6):
                self.game.particles.append(Particle(self.target.x, self.target.y, RED))

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 6)

# ==========================================
# TOWERS (INHERITANCE)
# ==========================================

class Tower:
    def __init__(self, game, x, y):
        self.game = game
        self.x, self.y = x, y
        self.level = 1
        self.cooldown = 0
        
        self.range = 100
        self.damage = 10
        self.fire_rate = 60
        self.upgrade_cost = 100
        self.proj_speed = 10
        self.proj_color = WHITE
        self.is_aoe = False
        self.color = (130, 130, 130)

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        closest = None
        closest_dist = float('inf')

        for zombie in self.game.zombies:
            dist = math.hypot(zombie.x - self.x, zombie.y - self.y)
            if dist < self.range and dist < closest_dist:
                closest = zombie
                closest_dist = dist

        if closest:
            self.shoot(closest)
            self.cooldown = self.fire_rate

    def shoot(self, target):
        self.game.projectiles.append(
            Projectile(self.game, self.x, self.y, target, self.damage, self.proj_speed, self.proj_color, self.is_aoe)
        )

    def upgrade(self):
        if self.game.money >= self.upgrade_cost:
            self.game.money -= self.upgrade_cost
            self.level += 1
            self.damage = int(self.damage * 1.5)
            self.range += 12
            self.fire_rate = max(10, self.fire_rate - 2)
            self.upgrade_cost += 50

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 0, 100), (self.x, self.y + 10), 30)
        
        if IMAGES["tower_base"]:
            screen.blit(IMAGES["tower_base"], (self.x - 30, self.y - 30))
        else:
            pygame.draw.circle(screen, (100, 100, 100), (self.x, self.y), 30)

        pygame.draw.circle(screen, self.color, (self.x, self.y - 10), 15)
        
        txt = FONT_SMALL.render(str(self.level), True, GOLD)
        screen.blit(txt, (self.x - 5, self.y + 5))


class KnightTower(Tower):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.range = 150
        self.damage = 40
        self.fire_rate = 40
        self.upgrade_cost = 150
        self.color = (70, 100, 255)

class ArcherTower(Tower):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.range = 250
        self.damage = 15
        self.fire_rate = 15
        self.proj_speed = 20
        self.upgrade_cost = 100
        self.color = (50, 200, 50)

class MageTower(Tower):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.range = 180
        self.damage = 30
        self.fire_rate = 80
        self.proj_color = PURPLE
        self.is_aoe = True
        self.upgrade_cost = 250
        self.color = (180, 50, 180)

class SniperTower(Tower):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.range = 500
        self.damage = 150
        self.fire_rate = 120
        self.proj_speed = 35
        self.proj_color = RED
        self.upgrade_cost = 300
        self.color = (200, 50, 50)

# ==========================================
# ZOMBIE
# ==========================================

class Zombie:
    def __init__(self, game):
        self.game = game
        self.x, self.y = PATH[0]
        self.path_index = 1
        
        self.type = random.choice(["normal", "fast", "tank"])
        self.speed = 1.4 + self.game.wave * 0.08
        self.max_health = 120 + self.game.wave * 30

        if self.type == "fast":
            self.speed *= 2
            self.max_health *= 0.6
            self.color = (100, 255, 100)
            self.img = IMAGES["fast"]
            self.radius = 20
        elif self.type == "tank":
            self.speed *= 0.5
            self.max_health *= 2.5
            self.color = (90, 70, 50)
            self.img = IMAGES["tank"]
            self.radius = 32
        else:
            self.color = (70, 190, 70)
            self.img = IMAGES["zombie"]
            self.radius = 24

        self.health = self.max_health

    def take_damage(self, amount):
        self.health -= amount

    def update(self):
        if self.path_index >= len(PATH):
            self.game.lives -= 1
            return False

        target_x, target_y = PATH[self.path_index]
        dx, dy = target_x - self.x, target_y - self.y
        distance = math.hypot(dx, dy)

        if distance != 0:
            dx /= distance
            dy /= distance

        self.x += dx * self.speed
        self.y += dy * self.speed

        if distance < 5:
            self.path_index += 1

        return True

    def die(self):
        for _ in range(15):
            self.game.particles.append(Particle(self.x, self.y, RED))
        self.game.money += 40

    def draw(self, screen):
        pygame.draw.ellipse(screen, (0, 0, 0, 100), (self.x - 20, self.y + self.radius - 5, 40, 12))
        
        if self.img:
            rect = self.img.get_rect(center=(self.x, self.y))
            screen.blit(self.img, rect)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

        health_ratio = max(0, self.health / self.max_health)
        pygame.draw.rect(screen, RED, (self.x - 20, self.y - self.radius - 10, 40, 5))
        pygame.draw.rect(screen, GREEN, (self.x - 20, self.y - self.radius - 10, 40 * health_ratio, 5))

# ==========================================
# GAME MANAGER
# ==========================================

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Zombie Kingdom Defense ULTRA")
        
        global IMAGES
        IMAGES["zombie"] = load_image("zombie.png", (48, 48))
        IMAGES["tank"] = load_image("tank_zombie.png", (64, 64))
        IMAGES["fast"] = load_image("fast_zombie.png", (40, 40))
        IMAGES["tower_base"] = load_image("tower_base.png", (60, 60))

        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "MENU" 
        self.selected_tower_type = KnightTower
        
        # 4. PUNKT: Rekordi laadimine failist
        self.highscore = self.load_highscore()
        
        self.reset_game()

    def load_highscore(self):
        if os.path.exists("highscore.txt"):
            try:
                with open("highscore.txt", "r") as f:
                    return int(f.read().strip())
            except:
                return 1
        return 1

    def save_highscore(self):
        with open("highscore.txt", "w") as f:
            f.write(str(self.highscore))

    def reset_game(self):
        self.money = 500
        self.lives = 20
        self.wave = 1
        self.zombies = []
        self.projectiles = []
        self.towers = []
        self.particles = []
        self.spawn_timer = 0
        self.start_wave()

    def start_wave(self):
        self.zombies_to_spawn = 8 + self.wave * 3

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "PLAYING": self.state = "PAUSED"
                    elif self.state == "PAUSED": self.state = "PLAYING"

                if self.state == "PLAYING":
                    if event.key == pygame.K_1: self.selected_tower_type = KnightTower
                    if event.key == pygame.K_2: self.selected_tower_type = ArcherTower
                    if event.key == pygame.K_3: self.selected_tower_type = MageTower
                    if event.key == pygame.K_4: self.selected_tower_type = SniperTower

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                if self.state == "MENU":
                    self.state = "PLAYING"
                
                elif self.state == "GAME_OVER":
                    self.reset_game()
                    self.state = "PLAYING"

                elif self.state == "PLAYING":
                    # Ei luba ehitada poepaneeli (X > 1200) peale
                    if mx < 1200:
                        if event.button == 1: 
                            cost = self.selected_tower_type(self, 0, 0).upgrade_cost - 50 
                            if self.money >= cost:
                                self.towers.append(self.selected_tower_type(self, mx, my))
                                self.money -= cost

                        if event.button == 3: 
                            for tower in self.towers:
                                if math.hypot(tower.x - mx, tower.y - my) < 35:
                                    tower.upgrade()

    def update_playing(self):
        self.spawn_timer += 1
        if self.spawn_timer >= 40 and self.zombies_to_spawn > 0:
            self.zombies.append(Zombie(self))
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

        if len(self.zombies) == 0 and self.zombies_to_spawn == 0:
            self.wave += 1
            # 4. PUNKT: Rekordi uuendamine reaalajas
            if self.wave > self.highscore:
                self.highscore = self.wave
                self.save_highscore()
            self.start_wave()

        if self.lives <= 0:
            self.state = "GAME_OVER"

    def draw_playing(self):
        self.screen.fill(GRASS)
        pygame.draw.lines(self.screen, DARK_ROAD, False, PATH, 90)
        pygame.draw.lines(self.screen, ROAD, False, PATH, 70)
        
        for tower in self.towers: tower.draw(self.screen)
        for zombie in self.zombies: zombie.draw(self.screen)
        for proj in self.projectiles: proj.draw(self.screen)
        for particle in self.particles: particle.draw(self.screen)

        # 2. PUNKT: Torni ehituse leviala joonistamine (Range Preview)
        mx, my = pygame.mouse.get_pos()
        if mx < 1200 and my > 80:
            # Loome ajutise torni, et teada selle ulatust ja värvi
            temp_tower = self.selected_tower_type(self, mx, my)
            
            # Poolläbipaistva ringi joonistamine Pygame pinna (Surface) abil
            range_surf = pygame.Surface((temp_tower.range * 2, temp_tower.range * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surf, (temp_tower.color[0], temp_tower.color[1], temp_tower.color[2], 60), (temp_tower.range, temp_tower.range), temp_tower.range)
            pygame.draw.circle(range_surf, (temp_tower.color[0], temp_tower.color[1], temp_tower.color[2], 180), (temp_tower.range, temp_tower.range), temp_tower.range, 2)
            self.screen.blit(range_surf, (mx - temp_tower.range, my - temp_tower.range))

        # Ülemine staatuse riba
        pygame.draw.rect(self.screen, (25, 25, 25), (0, 0, WIDTH, 80))
        self.screen.blit(FONT_NORMAL.render(f"GOLD: {self.money}", True, GOLD), (20, 20))
        self.screen.blit(FONT_NORMAL.render(f"LIVES: {self.lives}", True, WHITE), (250, 20))
        self.screen.blit(FONT_NORMAL.render(f"WAVE: {self.wave}", True, WHITE), (480, 20))
        self.screen.blit(FONT_NORMAL.render(f"HIGH SCORE: {self.highscore}", True, GOLD), (680, 20))

        # 3. PUNKT: Külgmenüü (Shop UI) joonistamine
        pygame.draw.rect(self.screen, UI_BG, (1200, 80, 200, HEIGHT - 80))
        pygame.draw.line(self.screen, UI_BORDER, (1200, 80), (1200, HEIGHT), 4)

        shop_title = FONT_NORMAL.render("TOWERS SHOP", True, WHITE)
        self.screen.blit(shop_title, (1215, 100))
        
        # Info poodi nimekirja kuvamiseks
        tower_info = [
            ("1. Knight", 100, (70, 100, 255)),
            ("2. Archer", 50, (50, 200, 50)),
            ("3. Mage", 200, (180, 50, 180)),
            ("4. Sniper", 250, (200, 50, 50))
        ]

        # Joonistame poe valikud
        for i, (name, price, color) in enumerate(tower_info):
            y_pos = 160 + i * 110
            
            # Kui see tüüp on parajasti valitud, joonistame ümber esiletõstmise kasti
            current_type_name = self.selected_tower_type.__name__.lower()
            if name.split(". ")[1].lower() in current_type_name:
                pygame.draw.rect(self.screen, (60, 80, 100), (1210, y_pos - 10, 180, 95), border_radius=8)
                pygame.draw.rect(self.screen, CYAN, (1210, y_pos - 10, 180, 95), 2, border_radius=8)
            else:
                pygame.draw.rect(self.screen, (30, 33, 35), (1210, y_pos - 10, 180, 95), border_radius=8)

            pygame.draw.circle(self.screen, color, (1235, y_pos + 20), 12)
            self.screen.blit(FONT_SMALL.render(name, True, WHITE), (1260, y_pos + 8))
            self.screen.blit(FONT_SMALL.render(f"Cost: {price} Gold", True, GOLD), (1260, y_pos + 32))

        controls = FONT_SMALL.render("L-CLICK = BUILD | R-CLICK = UPGRADE TOWER | ESC = PAUSE", True, WHITE)
        self.screen.blit(controls, (20, HEIGHT - 35))

    def draw(self):
        if self.state == "MENU":
            self.screen.fill(BLACK)
            title = FONT_BIG.render("ZOMBIE KINGDOM DEFENSE", True, GREEN)
            prompt = FONT_NORMAL.render("Click Anywhere to Start", True, WHITE)
            hs_text = FONT_NORMAL.render(f"Current High Score: Wave {self.highscore}", True, GOLD)
            
            self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 260))
            self.screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 400))
            self.screen.blit(hs_text, (WIDTH//2 - hs_text.get_width()//2, 480))

        elif self.state == "PLAYING":
            self.draw_playing()

        elif self.state == "PAUSED":
            self.draw_playing() 
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            pause_txt = FONT_BIG.render("PAUSED", True, WHITE)
            self.screen.blit(pause_txt, (WIDTH//2 - pause_txt.get_width()//2, 350))

        elif self.state == "GAME_OVER":
            self.screen.fill(BLACK)
            over_txt = FONT_BIG.render("THE KINGDOM HAS FALLEN", True, RED)
            score_txt = FONT_NORMAL.render(f"You reached Wave {self.wave} | High Score: Wave {self.highscore}", True, GOLD)
            restart_txt = FONT_NORMAL.render("Click Anywhere to Restart", True, WHITE)
            
            self.screen.blit(over_txt, (WIDTH//2 - over_txt.get_width()//2, 260))
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