from random import randint
from time import time as timer
from pygame import *
mixer.init()
init()
font.init()


class GameSprite(sprite.Sprite):
    def __init__(self, player_image, x, y, width, height, speed):
        super().__init__()
        self.image = transform.scale(image.load(player_image), (width, height))
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        virtual_surface.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
    def __init__(self, x, y):
        global clip_group

        self.fire_time = 0
        self.hp = 3
        self.max_resistance = 25
        self.resistance_frames = self.max_resistance
        self.resistance = False
        self.clip = 10
        self.reload = False
        self.start_reload = 0
        self.interface_clip = clip_group
        super().__init__("image/rocket.png", x, y, 100, 150, 10)

    def update(self):
        global text_hp
        global clip_group

        key_pressed = key.get_pressed()
        if key_pressed[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if key_pressed[K_d] and self.rect.x < WIDTH - self.rect.width:
            self.rect.x += self.speed

        if not self.reload:
            if key_pressed[K_SPACE]:
                current_time = timer()
                if current_time - self.fire_time >= 0.2:
                    self.fire()
                    self.interface_clip = self.interface_clip[:-1]
                    if self.clip <= 0:
                        self.reload = True
                        self.start_reload = timer()
        else:
            current_time = timer()
            if current_time - self.start_reload > 2:
                self.reload = False
                self.clip = 10
                self.interface_clip = clip_group

        if self.resistance:
            self.resistance_frames -= 1
            if self.resistance_frames <= 0:
                self.resistance = False
                self.resistance_frames = self.max_resistance

        text_hp = font_finish.render(f"{self.hp}", True, (50, 255, 55))

    def fire(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        bullet_group.add(bullet)
        fire_sound.play()
        self.fire_time = timer()
        self.clip -= 1


class Ufo(GameSprite):
    def __init__(self):
        super().__init__("image/ufo/ufo.png", randint(0, WIDTH - 150), randint(-HEIGHT, - 150), 150, 75, 2)
        self.wait = 0
        self.is_dead = False
        self.dead_frame = 0

    def update(self):
        global text_lost
        global lost_count

        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            self.respawn()
            lost_count += 1
            text_lost = font_interface.render(f"Пропущено: {lost_count}", True, (255, 255, 255))

        if self.is_dead:
            if self.dead_frame < 6:
                if self.wait <= 0:
                    self.change_image(animation_list[self.dead_frame])
                    self.wait = 3
                    self.dead_frame += 1
                else:
                    self.wait -= 1
            else:
                self.respawn()

    def respawn(self):
        self.rect.x = randint(0, WIDTH - 150)
        self.rect.y = randint(-HEIGHT, - 150)
        self.image = transform.scale(image.load("image/ufo/ufo.png"), (self.rect.width, self.rect.height))
        self.is_dead = False
        self.dead_frame = 0

    def death(self):
        global score
        global text_score

        if not self.is_dead:
            score += 1
            text_score = font_interface.render(f"Рахунок: {score}", True, (255, 255, 255))
            self.is_dead = True

    def change_image(self, sprite_animation):
        self.image = transform.scale(sprite_animation, (self.rect.width, self.rect.height))


class BossUfo(GameSprite):
    def __init__(self):
        self.hp = 5
        self.wait = 0
        self.is_dead = False
        self.dead_frame = 0
        super().__init__("image/ufo.png", randint(0, WIDTH - 250), -170, 250, 125, 1)

    def update(self):
        global text_lost
        global lost_count

        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            lost_count += 3
            text_lost = font_interface.render(f"Пропущено: {lost_count}", True, (255, 255, 255))
            self.kill()

        if self.is_dead:
            if self.dead_frame < 6:
                if self.wait <= 0:
                    self.change_image(animation_list[self.dead_frame])
                    self.wait = 3
                    self.dead_frame += 1
                else:
                    self.wait -= 1
            else:
                self.kill()

    def death(self):
        global score
        global text_score

        if not self.is_dead:
            score += 5
            text_score = font_interface.render(f"Рахунок: {score}", True, (255, 255, 255))
            self.is_dead = True

    def change_image(self, sprite_image):
        self.image = transform.scale(sprite_image, (self.rect.width, self.rect.height))


class Bullet(GameSprite):
    def __init__(self, x, y):
        super().__init__("image/bullet.png", x, y, 20, 40, 14)
        self.rect.centerx = x

    def update(self):
        self.rect.y -= self.speed
        if self.rect.y <= -self.rect.width:
            self.kill()


class Asteroid(GameSprite):
    def __init__(self):
        self.width = randint(40, 80)
        super().__init__("image/asteroid.png",
                         randint(0, WIDTH - 75), randint(- HEIGHT, - 150),
                         self.width, self.width, 3)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            self.respawn()

    def respawn(self):
        self.width = randint(40, 80)
        self.image = transform.scale(image.load("image/asteroid.png"), (self.width, self.width))
        self.rect = self.image.get_rect()
        self.rect.x = randint(0, WIDTH - 75)
        self.rect.y = randint(-HEIGHT, -150)


WIDTH = 1280
HEIGHT = 720

ASPECT_RATIO = WIDTH / HEIGHT

window = display.set_mode((WIDTH, HEIGHT), RESIZABLE)
display.set_caption("Shooter")
background = transform.scale(image.load("image/galaxy.jpg"), (WIDTH, HEIGHT))
clock = time.Clock()

virtual_surface = Surface((WIDTH, HEIGHT))
current_size = window.get_size()

mixer.music.load("sounds/space.ogg")
mixer.music.set_volume(0.1)
mixer.music.play(-1)

fire_sound = mixer.Sound("sounds/fire.ogg")
fire_sound.set_volume(0.1)


score = 0
lost_count = 0

font_interface = font.Font(None, 30)
text_lost = font_interface.render(f"Пропущено: {lost_count}", True, (255, 255, 255))
text_score = font_interface.render(f"Рахунок: {score}", True, (255, 255, 255))

font_finish = font.Font(None, 150)
text_win = font_finish.render("YOU WIN", True, (50, 255, 55))
text_lose = font_finish.render("YOU LOSE", True, (250, 50, 50))

text_hp = font_finish.render("1", True, (50, 255, 55))

animation_list = []
for i in range(1, 7):
    temp = image.load(f"image/ufo/ufo_{i}-removebg-preview.png")
    animation_list.append(temp)

cartridge_x = 30
clip_group = []
for i in range(10):
    cartridge = GameSprite("image/bullet.png", cartridge_x, HEIGHT - 80, 20, 40, 0)
    cartridge_x += 20
    clip_group.append(cartridge)

ufo_group = sprite.Group()
for i in range(10):
    ufo = Ufo()
    ufo_group.add(ufo)

player = Player(590, 560)

boss_group = sprite.Group()
boss_is_ready = True
bullet_group = sprite.Group()

asteroids_group = sprite.Group()
for i in range(3):
    asteroid = Asteroid()
    asteroids_group.add(asteroid)

finish = False
game = True
while game:
    for e in event.get():
        if e.type == QUIT:
            exit()
        if e.type == KEYDOWN:
            if e.type == K_ESCAPE:
                exit()
            if e.key == K_p:
                if finish:
                    finish = False
                if not finish:
                    finish = True
        if e.type == VIDEORESIZE:
            new_width = e.w
            new_height = int(new_width / ASPECT_RATIO)
            window = display.set_mode((new_width, new_height), RESIZABLE)
            current_size = window.get_size()

    if not finish:
        virtual_surface.blit(background, (0, 0))

        if not player.resistance:
            dead_list = sprite.spritecollide(player, ufo_group, False)
            for enemy in dead_list:
                player.hp -= 1
                enemy.death()
                player.resistance = True

            boss_dead_list = sprite.spritecollide(player, boss_group, False)
            for enemy in boss_dead_list:
                player.hp -= 2
                enemy.death()
                player.resistance = True

            asteroid_collide_list = sprite.spritecollide(player, asteroids_group, False)
            for asteroid in asteroid_collide_list:
                player.hp -= 1
                asteroid.respawn()
                player.resistance = True

        asteroid_hit_list = sprite.groupcollide(asteroids_group, bullet_group, False, True)

        hit_list = sprite.groupcollide(ufo_group, bullet_group, False, True)
        for enemy in hit_list:
            enemy.death()

        boss_hit_list = sprite.groupcollide(boss_group, bullet_group, False, True)
        for enemy in boss_hit_list:
            enemy.hp -= 1
            if enemy.hp <= 0:
                enemy.death()
                score += 3
                text_score = font_interface.render(f"Рахунок: {score}", True, (255, 255, 255))
                boss_is_ready = True
                player.hp += 1

        if score % 20 == 0 and score != 0 and boss_is_ready:
            boss = BossUfo()
            boss_is_ready = False
            boss_group.add(boss)

        player.update()
        player.reset()

        ufo_group.update()
        ufo_group.draw(virtual_surface)

        boss_group.update()
        boss_group.draw(virtual_surface)

        bullet_group.update()
        bullet_group.draw(virtual_surface)

        asteroids_group.update()
        asteroids_group.draw(virtual_surface)

        for cartridge in player.interface_clip:
            cartridge.reset()

        virtual_surface.blit(text_hp, (WIDTH - 100, 30))

        virtual_surface.blit(text_lost, (30, 30))
        virtual_surface.blit(text_score, (30, 60))

        if player.hp <= 0 or lost_count >= 10:
            finish = True
            virtual_surface.blit(text_lose, (375, 325))

        if score >= 100:
            finish = True
            virtual_surface.blit(text_win, (400, 325))

    scaled_surface = transform.scale(virtual_surface, current_size)
    window.blit(scaled_surface, (0, 0))
    clock.tick(60)
    display.update()
