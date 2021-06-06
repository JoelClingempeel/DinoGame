from sidescroller_engine import *
import os
import yaml

GAME_WINDOW_SIZE = (800, 500)
GAME_FONT = "comicsansms"
GAME_FONT_SIZE = 24
CLOCK_SPEED = 27

pygame.init()
win = pygame.display.set_mode(GAME_WINDOW_SIZE)
pygame.display.set_caption("Dino Visits the Museum")
clock = pygame.time.Clock()
font = pygame.font.SysFont(GAME_FONT, GAME_FONT_SIZE)


def get_image(image_name, mask=False):
    image = pygame.image.load(os.path.join(IMAGE_DIRECTORY, image_name))
    if mask:
        image.set_colorkey(WHITE)
    return image


def get_character_sprites(file_prefix, num_sprites, image_type='bmp'):
    return [get_image('%s%d.%s' % (file_prefix, index, image_type), mask=True)
            for index in range(1, num_sprites + 1)]


def create_level(config, hero):
    with open(config) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    platform_list = []
    for platform_type, x, y in zip(config['platform_types'],
                                   config['platform_x_coords'],
                                   config['platform_y_coords']):
        platform_list.append(Platform(images[platform_type], x, y))
    enemy_list = []
    for left, right, steps, x_start, y, health in zip(config['enemy_left'],
                                                      config['enemy_right'],
                                                      config['enemy_steps'],
                                                      config['enemy_x_start'],
                                                      config['enemy_y'],
                                                      config['enemy_health']):
        enemy_list.append(Enemy(win, sprites[left], sprites[right], steps, x_start, y, health))
    return Level(win, images[config['background']], hero, config['end_of_level'], platform_list, enemy_list)


# Load images, and make white backgrounds transparent.
DinoLeft = get_character_sprites('DinoL', 7, image_type='png')
DinoRight = get_character_sprites('DinoR', 7, image_type='png')
crouchingDino = [get_image('CrouchingDinoL.bmp', mask=True),
                 get_image('CrouchingDinoR.bmp', mask=True)]
dino = Hero(win, DinoLeft, DinoRight, 8, crouchingDino, 3)
splashScreen = get_image('DinoSplashScreen.png')
dinoEnding = get_image('DinoEnding.png', mask=True)

images = {'steelBar': get_image('SteelBar.png'),
          'brickWall': get_image('BrickWall.bmp'),
          'woodPlank': get_image('woodPlank.png'),
          'crackedStone': get_image('crackedStone.png'),
          'dinoFriend': get_image('dinoFriend.bmp', mask=True),
          'background1': get_image('DinoGameLevel1.png'),
          'background2': get_image('DinoGameLevel2.png'),
          'background3': get_image('DinoGameLevel3.png')}

sprites = {'BadGuyLeft': get_character_sprites('BadGuyL', 7),
           'BadGuyRight': get_character_sprites('BadGuyR', 7),
           'AltBadGuyLeft': get_character_sprites('AltBadGuyL', 7),
           'AltBadGuyRight': get_character_sprites('AltBadGuyR', 7),
           'jellyfish': get_character_sprites('Jellyfish', 5)}

level1 = create_level('level1_config.yaml', dino)
level2 = create_level('level2_config.yaml', dino)
level3 = create_level('level3_config.yaml', dino)


def splash():
    global run
    while run:
        for game_event in pygame.event.get():
            if game_event.type == pygame.QUIT:
                run = False
        win.blit(splashScreen, (0, 0))
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_SPACE]:
            return 0
        pygame.display.flip()


def game_end():
    global run
    while run:
        for game_event in pygame.event.get():
            if game_event.type == pygame.QUIT:
                run = False
        win.blit(dinoEnding, (0, 0))
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_SPACE]:
            return 0
        pygame.display.flip()


game_levels = [level1, level2, level3]
level = 2
run = True
splash()
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    current_level = game_levels[level]
    current_level.iterate()
    if current_level.status() == -1:
        current_level.restart()
    if current_level.status() == 1:
        current_level.restart()
        if level < len(game_levels) - 1:
            level += 1
        else:
            game_end()
            pygame.time.delay(1000)
            splash()
            level = 0
    clock.tick(CLOCK_SPEED)

pygame.quit()
