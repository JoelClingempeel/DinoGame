import pygame

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (0, 255, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

IMAGE_DIRECTORY = 'GameImages'


class Level:
    def __init__(self, win, background, hero, end_of_level, platform_list, enemy_list):
        self.win = win
        self.background = background
        self.hero = hero
        self.end_of_level = end_of_level
        self.platform_list = platform_list
        self.enemy_list = enemy_list
        self.enemy_projectiles = []
        self.game_width = self.win.get_width()
        self.game_height = self.win.get_height()

    def draw_level(self):
        pygame.display.update()
        self.win.blit(self.background, (0, 0))
        for platform in self.platform_list:
            if (self.hero.x - int(self.game_width/2) < platform.x + platform.width or
                    self.hero.x + int(self.game_width/2) > platform.x):
                self.win.blit(platform.image, (platform.x - self.hero.x + int(self.game_width/2), platform.y))
        for enemy in self.enemy_list:
            if enemy.health > 0:
                if (self.hero.x - int(self.game_width / 2) < enemy.x + enemy.width or
                        self.hero.x + int(self.game_width / 2) > enemy.x):
                    enemy.draw_enemy(self.hero.x)
        self.hero.draw_hero()
        for projectile in self.enemy_projectiles:
            projectile.draw()

    def update_enemies(self):
        for enemy in self.enemy_list:
            if enemy.health > 0:
                enemy.update_enemy(self.hero.x, self.enemy_projectiles)
        for projectile in self.enemy_projectiles:
            projectile.update()
            if projectile.x < 0 or projectile.x > self.game_width:
                self.enemy_projectiles.remove(projectile)

    def detect_hits(self):
        for projectile in self.hero.projectile_list:
            for enemy in self.enemy_list:
                if (projectile.x + projectile.rad > enemy.x - self.hero.x + int(self.game_width/2) and
                        projectile.x - projectile.rad < enemy.x - self.hero.x + int(self.game_width/2) + enemy.width):
                    if (projectile.y + projectile.rad > enemy.y and
                            projectile.y - projectile.rad < enemy.y + enemy.height):
                        enemy.health -= 1
                        if projectile in self.hero.projectile_list:
                            self.hero.projectile_list.remove(projectile)

        if not self.hero.is_crouching:
            for projectile in self.enemy_projectiles:
                if (projectile.x + projectile.rad > int(self.game_width/2) and
                        projectile.x - projectile.rad < int(self.game_width/2) + self.hero.width):
                    if (projectile.y + projectile.rad > self.hero.y and
                            projectile.y - projectile.rad < self.hero.y + self.hero.height):
                        self.hero.health -= 1
                        if projectile in self.enemy_projectiles:
                            self.enemy_projectiles.remove(projectile)
        else:
            for projectile in self.enemy_projectiles:
                if (projectile.x + projectile.rad > int(self.game_width/2) and
                        projectile.x - projectile.rad < int(self.game_width/2) + self.hero.width):
                    if (projectile.y + projectile.rad > self.hero.y + self.hero.height - self.hero.crouching_height and
                            projectile.y - projectile.rad < self.hero.y + self.hero.height):
                        self.hero.health -= 1
                        self.enemy_projectiles.remove(projectile)

    def iterate(self):
        self.hero.update_hero(self.platform_list)
        self.update_enemies()
        self.detect_hits()
        self.draw_level()

    def restart(self):
        for enemy in self.enemy_list:
            enemy.restart()
        self.enemy_projectiles = []
        self.hero.restart()

    def status(self):
        if self.hero.health <= 0:
            return -1
        elif self.hero.x > self.end_of_level:
            return 1
        else:
            return 0


class Platform:
    def __init__(self, image, x, y):
        self.image = image
        self.x = x
        self.y = y
        self.width = image.get_width()
        self.height = image.get_height()


class Enemy:
    def __init__(self, win, left, right, steps, x_start, y, health, speed=3):
        self.win = win
        self.left = left
        self.right = right
        self.steps = steps
        self.x_start = x_start
        self.x = x_start
        self.y = y
        self.health = health
        self.max_health = health
        self.speed = speed
        self.direction = 1
        self.current_step = 0
        self.wait = 0
        self.width = left[0].get_width()
        self.height = right[0].get_height()
        self.game_width = win.get_width()
        self.game_height = win.get_height()
        self.frame_count = len(left)

    def update_enemy(self, hero_x, enemy_projectiles):
        self.current_step += 1
        if self.current_step == self.steps:
            self.current_step = 0
            self.direction *= -1
        else:
            self.x += self.direction * self.speed

        if True:
            if self.wait == 0:
                if self.direction == 1:
                    enemy_projectiles.append(Projectile(self.win,
                                                        self.x - hero_x + int(self.game_width/2) + int(self.width/2),
                                                        self.y + 50, 5, 5, BLUE))
                else:
                    enemy_projectiles.append(Projectile(self.win,
                                                        self.x - hero_x + int(self.game_width/2) + int(self.width/2),
                                                        self.y + 50, -5 , 5, BLUE))
                self.wait = 50
            else:
                self.wait -= 1

    def draw_enemy(self, hero_x):
        if self.direction == -1:
            self.win.blit(self.left[(self.current_step // 3) % self.frame_count],
                          (self.x - hero_x + int(self.game_width / 2), self.y))
        else:
            self.win.blit(self.right[(self.current_step // 3) % self.frame_count],
                          (self.x - hero_x + int(self.game_width / 2), self.y))
        health_bar(self.win, self.health, self.max_health, self.x - hero_x + int(self.game_width / 2),
                   self.y, self.width)

    def restart(self):
        self.x = self.x_start
        self.health = self.max_health
        self.direction = 1
        self.current_step = 0
        self.wait = 0


class Hero:
    def __init__(self, win, left, right, health, crouching=None, speed=3, x=0, y=420,
                 jumpiness=20, gravity=.07):
        self.win = win
        self.left = left
        self.right = right
        self.x = x
        self.y = y
        self.x_start = x
        self.y_start = y
        self.health = health
        self.max_health = health
        self.speed = speed
        self.crouching = crouching
        self.jumpiness = jumpiness
        self.gravity = gravity
        self.walk_count = 0
        self.direction = "right"
        self.is_jumping = False
        self.is_crouching = False
        self.jump_count = jumpiness
        self.falling = False
        self.fall_count = 0
        self.projectile_list = []
        self.wait = 0
        self.width = left[0].get_width()
        self.height = right[0].get_height()
        self.game_width = win.get_width()
        self.game_height = win.get_height()
        self.frame_count = len(left)
        if crouching:
            self.crouching_height = crouching[0].get_height()

    def draw_hero(self):
        if self.is_crouching:
            self.walk_count = 0
            if self.direction == "left":
                self.win.blit(self.crouching[0], (int(self.game_width / 2),
                                                  self.y + self.height - self.crouching_height))
            else:
                self.win.blit(self.crouching[1], (int(self.game_width / 2),
                                                  self.y + self.height - self.crouching_height))
        else:
            if self.walk_count >=  3*self.frame_count: # Do we need this?
                self.walk_count = 0
            if self.direction == "left":
                self.win.blit(self.left[self.walk_count//3], (int(self.game_width/2), self.y))
            else:
                self.win.blit(self.right[self.walk_count // 3], (int(self.game_width/2), self.y))
        health_bar(self.win, self.health, self.max_health, int(self.game_width / 2), self.y, 60)
        for projectile in self.projectile_list:
            projectile.draw()

    def draw_projectile(self): # Is this even used anywhere?
        for projectile in self.projectile_list:
            projectile.draw()

    def is_falling(self, platform_list):
        if self.y >= self.game_height - self.height:
            self.y = self.game_height - self.height
            return False
        for platform in platform_list:
            if platform.x < self.x + 40 and self.x < platform.x + platform.width:
                if platform.y - self.height <= self.y < platform.y + platform.height - self.height: # Verify
                    self.y = platform.y - self.height
                    return False
        return True

    def left_collision(self, platform_list):
        for platform in platform_list:
            if (self.x - self.speed) < platform.x + platform.width and (self.x - self.speed) + self.width > platform.x:
                if self.y + self.height > platform.y and self.y < platform.y + platform.height:
                    return True
        return False

    def right_collision(self, platform_list):
        for platform in platform_list:
            if (self.x + self.speed) < platform.x + platform.width and (self.x + self.speed) + self.width > platform.x:
                if self.y + self.height > platform.y and self.y < platform.y + platform.height:
                    return True
        return False

    def up_collision(self, platform_list):
        for platform in platform_list:
            if platform.x < self.x < platform.x + platform.width: # Verify
                if platform.y < self.y <= platform.y + platform.height:
                    self.y = platform.y + platform.height
                    return True
        return False

    def update_hero(self,platform_list):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            if not self.left_collision(platform_list):
                if self.x > 0:
                    self.direction = "left"
                    self.walk_count += 1
                    self.x -= self.speed

        if keys[pygame.K_RIGHT]:
            if not self.right_collision(platform_list):
                self.direction = "right"
                self.walk_count += 1
                self.x += self.speed

        if not self.is_jumping:
            if keys[pygame.K_UP]:
                self.is_jumping = True
        else:
            if self.jump_count > 0:
                if not self.up_collision(platform_list):
                    self.y -= self.gravity * (self.jump_count ** 2)
                    self.jump_count -= 1
                else:
                    self.is_jumping = False
                    self.jump_count = self.jumpiness
            else:
                self.is_jumping = False
                self.jump_count = self.jumpiness

        self.falling = self.is_falling(platform_list)
        if self.falling:
            self.y += self.gravity * (self.fall_count ** 2)
            self.fall_count += 1
        else:
            self.fall_count = 0

        if (keys[pygame.K_DOWN] and self.crouching and not self.is_jumping and not self.falling and
                not(keys[pygame.K_LEFT]) and not(keys[pygame.K_RIGHT])):
            self.is_crouching = True
        else:
            self.is_crouching = False

        if keys[pygame.K_SPACE] and not(keys[pygame.K_DOWN]):
            if self.wait == 0:
                if self.direction == "right":
                    self.projectile_list.append(Projectile(self.win, int(self.game_width/2) + 10,
                                                           self.y + 40, 5, 5, GREEN))
                else:
                    self.projectile_list.append(Projectile(self.win, int(self.game_width/2) + 10,
                                                           self.y + 40, -5 , 5, GREEN))
                self.wait = 6
            else:
                self.wait -= 1

        for projectile in self.projectile_list:
            projectile.update()
            if projectile.x < -20 or projectile.x > self.game_width + 20:
                self.projectile_list.remove(projectile)

    def restart(self):
        self.x = self.x_start
        self.y = self.y_start
        self.health = self.max_health
        self.walk_count = 0
        self.direction = "right"
        self.is_jumping = False
        self.jump_count = self.jumpiness
        self.falling = False
        self.fall_count = 0
        self.projectile_list = []
        self.wait = 0


class Projectile:
    def __init__(self, win, x, y, vel, rad, color):
        self.win = win
        self.x = x
        self.y = y
        self.vel = vel
        self.rad = rad
        self.color = color

    def draw(self):
        pygame.draw.circle(self.win, self.color, (int(self.x), int(self.y)), self.rad)

    def update(self):
        self.x += self.vel


def health_bar(win, health, max_health, x, y, length):
    if health > 0:
        green = int(length * health / max_health)
        red = length - green
        pygame.draw.rect(win, GREEN, pygame.Rect(x, y - 5, green, 5))
        pygame.draw.rect(win, RED, pygame.Rect(x + green, y - 5, red, 5))
