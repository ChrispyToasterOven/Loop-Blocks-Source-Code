import sys
import pygame
import math
import intime
import random
import level_list
from pygame.locals import *

pygame.init()

mainclock = pygame.time.Clock()

windowwidth = 1920
windowheight = 1080
windowsurface = pygame.display.set_mode((windowwidth, windowheight), 1, 16)

pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)

basicfont = pygame.font.SysFont("Sans", 30)
bigfont = pygame.font.SysFont("Sans", 50)
smallfont = pygame.font.SysFont("Sans", 18)

black = (0, 0, 0)
white = (255, 255, 255)
l_grey = (200, 200, 200)
red = (255, 0, 0)
magenta = (240, 62, 233)
pink = (255, 110, 249)


# ======== save/load =========================


def save(values):
    with open('score.txt', 'w') as f:
        for value in values:
            f.write(str(value) + '\n')


def load():
    with open('score.txt', 'r') as f:
        load_data = []
        for line in f.readlines():
            load_data.append(int(line))
        return load_data


# ============================================


def move_x(angle, dist):
    return math.cos(angle) * dist


def move_y(angle, dist):
    return math.sin(angle) * dist


def point(x, y, point_x, point_y):
    return math.atan2(y - point_y, point_x - x)


# ================= sprites =====================


class Player(pygame.sprite.Sprite):
    def __init__(self):
        self._layer = 20
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(0, 0, 50, 50)
        self.float = [0, 0]
        self.image1 = pygame.image.load('images/player.png').convert_alpha()
        self.image1 = pygame.transform.scale(self.image1, (240, 60)).convert_alpha()
        self.image1.fill((30, 30, 10), None, special_flags=pygame.BLEND_RGB_SUB)

        self.numimages = 4
        self.cImage = 0
        self.float_image = 0
        self.width = 60
        self.height = 60
        self.area = None

        self.offset = [0, 0]
        self.special_flags = 0

        self.angle = 0
        self.angle1 = 0
        self.speed = 300
        self.x_vel = 0
        self.y_vel = 0

        self.atk_timer = 1

    def update(self):
        keystate = pygame.key.get_pressed()
        mouse_x = pygame.mouse.get_pos()[0]
        mouse_y = pygame.mouse.get_pos()[1]

        if playing:
            if keystate[K_w] or keystate[K_a] or keystate[K_s] or keystate[K_d]:
                if keystate[K_w]:
                    if 270 < math.degrees(self.angle) < 360:
                        self.angle1 = 450
                    else:
                        self.angle1 = 90
                if keystate[K_a]:
                    self.angle1 = 180
                if keystate[K_s]:
                    if 0 < math.degrees(self.angle) < 90:
                        self.angle1 = -90
                    else:
                        self.angle1 = 270
                if keystate[K_d]:
                    if 0 < math.degrees(self.angle) < 180 or math.degrees(self.angle) < 1:
                        self.angle1 = 0
                    else:
                        self.angle1 = 360

                if math.degrees(self.angle) - 10 < self.angle1 < math.degrees(self.angle) + 10:
                    self.angle = math.radians(self.angle1)

                if self.angle < math.radians(self.angle1):
                    self.angle += intime.change(math.radians(400), dt, gamespeed)
                    if math.degrees(self.angle) >= 360:
                        self.angle = self.angle - math.radians(360)

                if self.angle > math.radians(self.angle1):
                    self.angle -= intime.change(math.radians(400), dt, gamespeed)
                    if math.degrees(self.angle) < 0:
                        self.angle = self.angle + math.radians(360)

                # x movement
                self.x_vel = intime.change(move_x(self.angle, self.speed), dt, gamespeed)
                self.float[0] += self.x_vel
                self.rect.x = int(self.float[0])

                spritecollide = pygame.sprite.spritecollide(self, walls, False)

                if spritecollide:
                    self.float[0] -= self.x_vel
                    self.rect.x = int(self.float[0])
                    spritecollide = pygame.sprite.spritecollide(self, walls, False)
                    if self.x_vel > 0:
                        for block in spritecollide:
                            self.float[0] = block.rect.x - self.rect.width
                    else:
                        for block in spritecollide:
                            self.float[0] = block.rect.right + 0.1

                # y movement
                self.y_vel = intime.change(move_y(self.angle, -self.speed), dt, gamespeed)
                self.float[1] += self.y_vel
                self.rect.y = int(self.float[1])

                spritecollide = pygame.sprite.spritecollide(self, walls, False)

                if spritecollide:
                    self.float[1] -= self.y_vel
                    self.rect.y = int(self.float[1])
                    spritecollide = pygame.sprite.spritecollide(self, walls, False)
                    if self.y_vel > 0:
                        for block in spritecollide:
                            self.float[1] = block.rect.y - self.rect.height
                    else:
                        for block in spritecollide:
                            self.float[1] = block.rect.bottom + 0.1

            # if keystate[K_SPACE] and self.atk_timer <= 0:
            #     self.atk_timer = 0.5
            #     h = Hitring(self.rect.centerx, self.rect.centery)
            #     hitrings.add(h)
            #     allsprites.add(h)
            # else:
            #     self.atk_timer -= intime.change(1, dt, gamespeed)

            self.float_image += intime.change(11, dt, gamespeed)
            if self.float_image > self.numimages - 1:
                self.float_image = 0

        self.cImage = int(self.float_image)
        self.image = pygame.Surface.subsurface(self.image1,
                                               (self.cImage * self.width, 0, self.width, self.height)).convert_alpha()
        self.image = pygame.transform.rotate(self.image, math.degrees(self.angle) + 90).convert_alpha()
        self.offset = [-int(self.image.get_width() / 2) + (self.rect.width / 2),
                       -int(self.image.get_height() / 2) + (self.rect.width / 2)]

        # if pygame.mouse.get_pressed()[0]:
        #     self.float = [mouse_x, mouse_y]
        #     self.rect.topleft = self.float


class Asset(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self._layer = 20
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x, y, 60, 60)
        self.image = pygame.image.load('images/block.png').convert()
        self.image = pygame.transform.scale(self.image, (60, 60)).convert()

        self.offset = [0, 0]
        self.area = None
        self.special_flags = 0


class LoopBlock(pygame.sprite.Sprite):
    def __init__(self, x, y, n):
        self._layer = 20
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x, y, 60, 60)
        self.image = pygame.image.load('images/loop_block.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60)).convert_alpha()

        self.gate_num = n
        self.gate_num_text = bigfont.render(str(n), True, white)
        self.image.blit(self.gate_num_text, (19, 2))
        self.image.fill((60, 10, 0), special_flags=pygame.BLEND_RGB_SUB)

        self.offset = [0, 0]
        self.area = None
        self.special_flags = 0

        self.tick = True
        self.tick2 = False

    def update(self):
        if loop_box[int(box_sel)] - 1 == self.gate_num:
            if self in walls:
                walls.remove(self)
                self.tick2 = True
                if self.tick:
                    self.tick = False
                    self.image.set_alpha(100)
        else:
            if self not in walls:
                walls.add(self)
                self.tick = True
                if self.tick2:
                    self.tick2 = False
                    self.image.set_alpha(255)
                    if pygame.Rect.colliderect(self.rect, player.rect):
                        player.float = [-200000, -200000]
                        player.rect.topleft = (-200000, -200000)
                        global screenshake
                        screenshake = 0.3


class Hitring(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self._layer = 21
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(0, 0, 160, 160)
        self.rect.center = (x, y)
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.rad = 80
        pygame.draw.circle(self.image, black, (self.image.get_width() / 2, self.image.get_height() / 2), self.rad, 4)
        self.offset = [0, 0]
        self.special_flags = 0
        self.area = None
        self.damage = 1

    def update(self):
        pygame.draw.rect(windowsurface, red, self.rect, 2)
        spritecollide = pygame.sprite.spritecollide(self, mobs, False)
        for mob in spritecollide:
            x_dist = mob.rect.centerx - self.rect.centerx
            y_dist = mob.rect.centery - self.rect.centery
            distance = math.sqrt((x_dist ** 2) + (y_dist ** 2))
            if distance <= self.rad:
                mob.hp -= self.damage
        self.kill()


class Mob(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self._layer = 20
        pygame.sprite.Sprite.__init__(self)
        self.float = [x, y]
        self.rect = pygame.Rect(x, y, 40, 40)
        self.image = pygame.Surface((40, 40))
        self.hp = 2

        self.area = None
        self.offset = [0, 0]
        self.special_flags = 0

    def update(self):
        if self.hp <= 0:
            self.kill()


class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self)
        self.float = [x, y]
        self.rect = pygame.Rect(x, y, 60, 60)
        self.image = pygame.image.load('images/goal.png')
        self.time = 0

        self.area = (0, 0, 60, 60)
        self.offset = [0, 0]
        self.special_flags = 0

    def update(self):
        self.time += intime.change(2, dt, gamespeed)
        if self.time >= 2:
            self.time = 0
        self.area = (int(self.time) * 60, 0, 60, 60)
        if pygame.Rect.colliderect(self.rect, player.rect):
            global level
            global loop_box
            global playing
            global current_level
            playing = False
            if level == current_level:
                current_level += 1
                save([current_level, doTutorial])
            level += 1
            load_level(level)
            loop_box = []
            for i in range(10):
                loop_box.append(0)


class LoopUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self)
        self.float = [x, y]
        self.rect = pygame.Rect(x, y, 60, 60)
        self.image = pygame.image.load('images/loop_up.png')

        self.area = None
        self.offset = [0, 0]
        self.special_flags = 0

    def update(self):
        if pygame.Rect.colliderect(self.rect, player.rect):
            global loopsLeft
            loopsLeft += 1
            self.kill()


# ===============================================


tickspeed = 0
gamespeed = 1
dt = 0

allsprites = pygame.sprite.LayeredUpdates()
walls = pygame.sprite.Group()
loop_blocks = pygame.sprite.Group()
draw_shadows = pygame.sprite.Group()
hitrings = pygame.sprite.Group()
mobs = pygame.sprite.Group()
goals = pygame.sprite.Group()
items = pygame.sprite.Group()

player = Player()
allsprites.add(player)
draw_shadows.add(player)

blit = windowsurface.blit

camera_rect = pygame.Rect(0, 0, 1920, 1080)

screenshake = 0

shadow_img = pygame.image.load('images/shadow.png').convert_alpha()
shadow_img = pygame.transform.scale(shadow_img, (56, 56)).convert_alpha()

box_size = 40
box_sel = 0
loop_box = []
for i in range(10):
    loop_box.append(0)

click_buffer = True

playing = False

play_img = pygame.image.load('images/play.png').convert_alpha()

box_surface = pygame.Surface((box_size, box_size))
box_surface.fill(magenta)
box_surface.set_alpha(50)

box_surface_sel = pygame.Surface((box_size, box_size))
box_surface_sel.fill(pink)
box_surface_sel.set_alpha(125)

floor_surface = pygame.Surface((0, 0))
gates = []

level_time = 6
levels_amount = level_list.total_levels()

level_sel = pygame.image.load('images/level_sel.png').convert_alpha()

loopsLeft = 1
deathTick = True

menu = 1

title = pygame.image.load('images/title.png').convert_alpha()
title_rect = pygame.Rect(0, 0, title.get_width(), title.get_height())

title_block_surface = pygame.Surface((windowwidth, windowheight))
title_lb = pygame.image.load('images/loop_block.png').convert_alpha()
title_lb = pygame.transform.scale(title_lb, (60, 60)).convert_alpha()
title_lb.fill((60, 10, 0), special_flags=pygame.BLEND_RGB_SUB)

crown = pygame.image.load('images/crown.png').convert_alpha()

title_timer = 0

for y in range(18):
    for x in range(32):
        title_block_surface.blit(title_lb, (x * 60, y * 60))

level = 0
current_level = load()[0]
doTutorial = 0
tut_arrow = pygame.image.load('images/arrow.png').convert_alpha()
tut_arrow = pygame.transform.scale(tut_arrow, (46, 98)).convert_alpha()
tut_arrow_pos = [windowwidth - 280, windowheight - 150]
arrow_bounce = 1


# ================= buttons ===============================================================
def button_draw(menu_num):
    global click_buffer
    global level
    global doTutorial
    global menu
    global current_level

    if menu_num == 1:
        for button in menubuttons[menu_num]:
            button_rect = button[1]
            if button[0] == 'play':
                button_rect.center = (windowwidth/2, windowheight/2)
                textBox('PLAY', button_rect, True, 71)
            if pygame.mouse.get_pressed()[0] and click_buffer:
                mouse_x, mouse_y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                if pygame.Rect.colliderect(button_rect, pygame.Rect(mouse_x, mouse_y, 1, 1)):
                    if button[0] == 'play':
                        level = load()[0]
                        current_level = level
                        print(current_level)
                        print(levels_amount)
                        if current_level >= levels_amount:
                            level = 0
                        doTutorial = load()[1]
                        print('level: ' + str(level))
                        print('do tutorial: ' + str(doTutorial))
                        menu = 0
                        load_level(level)

            # blit(button_images[button[0]], button_rect)


menubuttons = [[],
               [('play', pygame.Rect(0, 0, 256, 60)), ],
               ]

inv_buttons = [('Exit', 'Exit Game')]

button_images = {
    # 'play': pygame.transform.scale(pygame.image.load('images/button_small.png').convert(), (256, 60)).convert()
}
# ===============================================================================================================


# ========= text box ===================================
def textBox(text, tb_rect, big=False, offset=0):
    tb_width = (tb_rect.width/6) - 2
    text = text.split()
    line_len = 0
    lines = ['']
    for word in text:
        line_len += len(word) + 1
        if line_len > tb_width:
            lines.append('')
            line_len = len(word) + 1
        lines[-1] += word + ' '

    line_y = 0
    for line in lines:
        if big:
            line_text = bigfont.render(line, True, white)
        else:
            line_text = smallfont.render(line, True, white)

        blit(line_text, (tb_rect.x + 6 + offset, tb_rect.y + line_y * 20))
        line_y += 1

    pygame.draw.rect(windowsurface, white, tb_rect, 3)
# =========================================================


def gate_sort(i):
    return i[4]


# ========= generate level ===============================
def load_level(num):
    global floor_surface
    global gates
    global loopsLeft
    global doTutorial
    global menu
    global current_level
    global level_time
    loopsLeft = 1
    gates = [-1]

    level_time = 6

    if num > 0:
        doTutorial = 0

    for b in loop_blocks:
        b.kill()
    for w in walls:
        w.kill()
    for g in goals:
        g.kill()
    for i in items:
        i.kill()

    floor_surface = pygame.Surface((windowwidth, windowheight))
    shadow_surface = pygame.Surface((windowwidth, windowheight), pygame.SRCALPHA)
    shadow_surface.fill((0, 0, 0, 0))

    shadow = pygame.image.load('images/drop_shadow.png').convert_alpha()
    shadow = pygame.transform.scale(shadow, (96, 96)).convert_alpha()

    floor_tile = pygame.image.load('images/floor.png').convert()
    floor_tile = pygame.transform.scale(floor_tile, (60, 60)).convert()

    if num < levels_amount:
        level_load = level_list.load(num)

        for y in range(18):
            for x in range(32):
                floor_surface.blit(floor_tile, (x * 60, y * 60))

                if level_load[0][y][x] == 1:
                    a = Asset(x * 60, y * 60)
                    walls.add(a)
                    allsprites.add(a)

        for asset in level_load[1]:
            if asset[2] == 'player':
                player.float = [asset[0], asset[1]]
                player.rect.topleft = (asset[0], asset[1])
                player.angle = math.radians(asset[4])
            if asset[2] == 'loop_block':
                lb = LoopBlock(asset[0], asset[1], asset[4])
                loop_blocks.add(lb)
                walls.add(lb)
                allsprites.add(lb)
                if asset[4] not in gates:
                    gates.append(asset[4])
            if asset[2] == 'loops':
                loopsLeft = asset[4]
            if asset[2] == 'goal':
                g = Goal(asset[0], asset[1])
                goals.add(g)
                allsprites.add(g)
            if asset[2] == 'loop_up':
                lu = LoopUp(asset[0], asset[1])
                items.add(lu)
                allsprites.add(lu)
            if asset[2] == 'level_time':
                level_time = asset[4]

        gates.sort()
        print(gates)

        for block in walls:
            shadow_surface.blit(shadow, (block.rect.x - 36, block.rect.y))

        shadow_surface.set_alpha(100)
        floor_surface.blit(shadow_surface, (0, 0))

    else:
        menu = 1


# =========================================================


# ===============================================================
for i in range(0):
    m = Mob(random.randint(0, windowwidth), random.randint(0, windowheight))
    mobs.add(m)
    allsprites.add(m)
# ===============================================================

# ============= game loop ========================
while True:
    mouse_rect = pygame.Rect(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], 1, 1)
    if not pygame.mouse.get_pressed()[0]:
        click_buffer = True
    windowsurface.fill(black)
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                save([current_level, doTutorial])
                pygame.quit()
                sys.exit()
        if event.type == QUIT:
            save([current_level, doTutorial])
            pygame.quit()
            sys.exit()

    if pygame.key.get_pressed()[K_m] and pygame.mouse.get_pressed()[0] and click_buffer:
        print(pygame.mouse.get_pos())

    if menu > 0:
        if menu == 1:
            title_timer += intime.change(1, dt, gamespeed)
            if title_timer >= 8:
                title_timer = 0
            title_block_surface.set_alpha(100 + (((0.25 * title_timer - 1) ** 2) - 1) * 50)
            blit(title_block_surface, (0, 0))
            title_rect.center = windowwidth/2, 260
            blit(title, title_rect)
            if current_level >= levels_amount:
                blit(crown, (title_rect.centerx + 430, title_rect.y - 30))
        button_draw(menu)
    else:
        allsprites.update()

        if loopsLeft <= 0:
            if deathTick:
                deathTick = False
                player.float = [-200000, -200000]
                player.rect.topleft = (-200000, -200000)
                screenshake = 0.3
        else:
            deathTick = True
        if screenshake > 0:
            screenshake -= intime.change(1, dt, gamespeed)
            camera_rect.y = math.sin(screenshake * 70) * 5

        blit(floor_surface, (-camera_rect.x, -camera_rect.y))
        # draw sprites =========================================================================
        for sprite in allsprites:
            if sprite in draw_shadows:
                shadow_rect = shadow_img.get_rect()
                shadow_rect.center = sprite.rect.center
                blit(shadow_img, (shadow_rect[0] - camera_rect.x, shadow_rect[1] - camera_rect.y))
            draw_x = sprite.rect.x + sprite.offset[0] - camera_rect.x
            draw_y = sprite.rect.y + sprite.offset[1] - camera_rect.y
            blit(sprite.image, (draw_x, draw_y), sprite.area, special_flags=sprite.special_flags)
        # ======================================================================================

        # ======== tutorial =========================
        if doTutorial == 1:
            arrow_bounce -= intime.change(1, dt, gamespeed)
            if arrow_bounce <= 0:
                arrow_bounce = 1
            blit(tut_arrow, (tut_arrow_pos[0], tut_arrow_pos[1] + math.sin(arrow_bounce * math.pi * 4) * 8))

            if tut_arrow_pos == [2000, 2000]:
                tutorial_tb = pygame.Rect(windowwidth - 340, windowheight - 180, 200, 100)
                textBox('When the timeline lands on a number, it will open all gates with the same number.', tutorial_tb)

                tutorial_tb = pygame.Rect(144, 384, 150, 30)
                textBox('Move with: W, A, S, D', tutorial_tb)

                tutorial_tb = pygame.Rect(windowwidth - 740, windowheight - 130, 200, 80)
                textBox('The Timeline can only loop a set amount of times, so be resourceful.', tutorial_tb)

                tutorial_tb = pygame.Rect(1593, 137, 135, 30)
                textBox('Reach the Goal.', tutorial_tb)
        if level == 2:
            tutorial_tb = pygame.Rect(1510, 501, 160, 30)
            textBox('Increases loops by 1 ->', tutorial_tb)
        # ===========================================

        # ========== level select ==============================
        if level > 0:
            level_text = bigfont.render('LEVEL ' + str(level) + '/' + str(levels_amount - 1), True, white)
        else:
            level_text = bigfont.render('TUTORIAL', True, white)
        level_rect = level_text.get_rect()
        level_rect.center = windowwidth/2, 30
        blit(level_text, level_rect)

        level_fwd = pygame.Rect(0, 0, 60, 60)
        level_fwd.x = level_rect.right

        level_bwd = pygame.Rect(0, 0, 60, 60)
        level_bwd.right = level_rect.x

        blit(level_sel, level_fwd, (0, 0, 60, 60))
        blit(level_sel, level_bwd, (60, 0, 60, 60))

        if pygame.Rect.colliderect(level_fwd, mouse_rect):
            if pygame.mouse.get_pressed()[0] and click_buffer:
                if level + 1 <= current_level:
                    loop_box = []
                    for i in range(10):
                        loop_box.append(0)
                    level += 1
                    load_level(level)
        if pygame.Rect.colliderect(level_bwd, mouse_rect):
            if pygame.mouse.get_pressed()[0] and click_buffer:
                if level - 1 > -1:
                    loop_box = []
                    for i in range(10):
                        loop_box.append(0)
                    level -= 1
                    load_level(level)
        # ======================================================

        # ============= loop box ==============================================
        if playing:
            box_sel += intime.change(1, dt, gamespeed)
            if box_sel >= level_time:
                box_sel = 0
                if loopsLeft > 0:
                    loopsLeft -= 1
        else:
            box_sel = -1

        if loopsLeft > 1:
            loop_remain = basicfont.render("LOOPS REMAINING: " + str(loopsLeft), True, white)
        else:
            loop_remain = basicfont.render("LOOPS REMAINING: " + str(loopsLeft), True, red)
        blit(loop_remain, (windowwidth - 750, windowheight - 40))

        loop_box_text = basicfont.render("TIMELINE", True, white)
        blit(loop_box_text, (windowwidth - 400, windowheight - 72))

        play_rect = pygame.Rect(windowwidth - 475, windowheight - 60, 60, 60)
        if pygame.Rect.colliderect(play_rect, mouse_rect):
            if pygame.mouse.get_pressed()[0] and click_buffer:
                playing = not playing
                load_level(level)
                if playing:
                    box_sel = 0
                if doTutorial == 1 and tut_arrow_pos == [windowwidth - 465, windowheight - 180]:
                    tut_arrow_pos = [2000, 2000]

        pygame.draw.rect(windowsurface, white, play_rect, 6)
        if playing:
            play_area = (60, 0, 60, 60)
            stop_text = basicfont.render('STOP/RESTART', True, white)
            blit(stop_text, (play_rect.x - 60, play_rect.y - 40))
        else:
            play_area = (0, 0, 60, 60)
        blit(play_img, play_rect, play_area)

        for box in range(level_time):
            box_rect = pygame.Rect((box * box_size) + windowwidth - (box_size * 10), windowheight - box_size, box_size, box_size)

            if not playing:
                if pygame.Rect.colliderect(box_rect, mouse_rect):
                    box_sel = box
                    if pygame.mouse.get_pressed()[0] and click_buffer:
                        loop_box[box] += 1
                        if len(gates) - 1 < loop_box[box]:
                            loop_box[box] = 0
                        if doTutorial and tut_arrow_pos == [windowwidth - 280, windowheight - 150]:
                            tut_arrow_pos = [windowwidth - 465, windowheight - 180]
            if box_sel == box and not playing:
                for gate in gates:
                    drop_rect = pygame.Rect(box_rect.x, box_rect.y - ((gate + 2) * box_size), box_size, box_size)
                    if loop_box[box] - 1 == gate:
                        blit(box_surface_sel, drop_rect)
                        pygame.draw.rect(windowsurface, white, drop_rect, 6)
                    else:
                        blit(box_surface, drop_rect)
                        pygame.draw.rect(windowsurface, white, drop_rect, 1)

                    if gate != -1:
                        gate_text = basicfont.render(str(gate), True, white)
                        blit(gate_text, (drop_rect.x + 13, drop_rect.y + 1))

            if int(box_sel) == box:
                blit(box_surface_sel, box_rect)
                pygame.draw.rect(windowsurface, white, box_rect, 6)
            else:
                blit(box_surface, box_rect)
                pygame.draw.rect(windowsurface, white, box_rect, 1)

            if gates[loop_box[box]] != -1:
                box_text = basicfont.render(str(gates[loop_box[box]]), True, white)
                blit(box_text, (box_rect.x + 13, box_rect.y + 1))

        # =====================================================================

    fps = mainclock.get_fps()

    # ==== text =========
    # angle_font = basicfont.render('a: ' + str(math.degrees(player.angle)), True, white)
    # angle1_font = basicfont.render('a1: ' + str(player.angle1), True, white)
    # blit(angle_font, (10, 10))
    # blit(angle1_font, (10, 60))

    exit_font = basicfont.render('press ESC to exit game', True, white)
    blit(exit_font, (0, 0))
    fps_text = basicfont.render(str(int(fps)), True, white)
    back_fps_text = basicfont.render(str(int(fps)), True, l_grey)
    blit(fps_text, (10, windowheight - 40))
    blit(back_fps_text, (12, windowheight - 38))
    # ==================

    if pygame.mouse.get_pressed()[0]:
        click_buffer = False

    pygame.display.update()
    dt = mainclock.tick(tickspeed) / 1000
