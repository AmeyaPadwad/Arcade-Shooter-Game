import pygame
import math

# Pygame variables---------------------
pygame.init()
fps = 60
timer = pygame.time.Clock()
font = pygame.font.Font("assets/font/myFont.ttf", 32)
bigFont = pygame.font.Font("assets/font/myFont.ttf", 60)
width = 900
height = 800
screen = pygame.display.set_mode([width, height])

bgs = []
banners = []
guns = []
menuImg = pygame.image.load(f"assets/menus/mainMenu.png")
pauseImg = pygame.image.load(f"assets/menus/pause.png")
gameOverImg = pygame.image.load(f"assets/menus/gameOver.png")

level = 0
points = 0
mode = 0  # 0 = freeplay, 1 = accuracy, 2 = timed
ammo = 0
shot = False
clicked = False
writeValues = False
totalShots = 0
timeRemaining = 200
timeElapsed = 0
counter = 1
bestScoreFreeplay = 0
bestScoreAccuracy = 0
bestScoreTimed = 0

menu = True
gameOver = False
pause = False
getNewCoords = True
enemies = [[], [], []]  # 3 types for levels 1 and 2, and 4 for lvl 3
hitBoxes = [[], [], []]
noOfEnemies = {1: [10, 5, 4], 2: [12, 8, 5], 3: [15, 12, 8, 3]}  # no of enemies per lvl
lvl1Coords = [[], [], []]
lvl2Coords = [[], [], []]
lvl3Coords = [[], [], [], []]


for i in range(1, 4):
    # importing backgrounds, banners and guns images
    bgs.append(pygame.image.load(f"assets/bgs/{i}.png"))
    banners.append(pygame.image.load(f"assets/banners/{i}.png"))
    guns.append(
        pygame.transform.scale(pygame.image.load(f"assets/guns/{i}.png"), (100, 100))
    )

    # importing enemy images
    if i < 3:
        for j in range(1, 4):
            enemies[i - 1].append(
                pygame.transform.scale(
                    pygame.image.load(f"assets/targets/{i}/{j}.png"),
                    (120 - (j * 18), 80 - (j * 12)),
                )
            )  # reducing image size according to tier of enemy
    else:
        for j in range(1, 5):
            enemies[i - 1].append(
                pygame.transform.scale(
                    pygame.image.load(f"assets/targets/{i}/{j}.png"),
                    (120 - (j * 18), 80 - (j * 12)),
                )
            )  # reducing image size according to tier of enemy

# High Score file

file = open("highScores.txt", "r")
readFile = file.readlines()
file.close()
bestScoreFreeplay = int(readFile[0])
bestScoreAccuracy = int(readFile[1])
bestScoreTimed = int(readFile[2])

# Sound initialisation
pygame.mixer.init()
pygame.mixer.music.load("assets/sounds/bg_music.mp3")
plateSound = pygame.mixer.Sound("assets/sounds/Broken plates.wav")
plateSound.set_volume(0.2)
birdSound = pygame.mixer.Sound("assets/sounds/Drill Gear.mp3")
birdSound.set_volume(0.2)
laserSound = pygame.mixer.Sound("assets/sounds/Laser Gun.wav")
laserSound.set_volume(0.4)
pygame.mixer.music.play()

# Functions-----------------------------


def reset():
    global totalShots, timeElapsed, points, timeRemaining, ammo, getNewCoords
    totalShots = 0
    timeElapsed = 0
    points = 0
    timeRemaining = 0
    ammo = 0
    getNewCoords = True


def drawGun():
    # Function variables
    mousePos = pygame.mouse.get_pos()
    gunPos = (width / 2, height - 200)
    clickColor = ["red", "purple", "green"]
    clicks = pygame.mouse.get_pressed()

    # Getting the rotation of gun
    if mousePos[0] != gunPos[0]:
        slope = (mousePos[1] - gunPos[1]) / (mousePos[0] - gunPos[0])
    else:
        slope = -100000
    angle = math.atan(slope)
    rotation = math.degrees(angle)

    # Drawing the gun and clicks
    if mousePos[0] < width / 2:  # flipping gun if cursor on left side
        gun = pygame.transform.flip(guns[level - 1], True, False)
        if mousePos[1] < 600:  # drawing gun
            screen.blit(
                pygame.transform.rotate(gun, 90 - rotation),
                (gunPos[0] - 90, gunPos[1] - 50),
            )
            if clicks[0]:
                pygame.draw.circle(screen, clickColor[level - 1], mousePos, 10)
    else:
        gun = guns[level - 1]
        if mousePos[1] < 600:  # drawing gun
            screen.blit(
                pygame.transform.rotate(gun, 270 - rotation),
                (gunPos[0] - 30, gunPos[1] - 50),
            )
            if clicks[0]:
                pygame.draw.circle(screen, clickColor[level - 1], mousePos, 10)


def draw_enemies(coords):
    if level == 1 or level == 2:
        hitBoxes = [[], [], []]  # 3 types for levels 1 and 2
    else:
        hitBoxes = [[], [], [], []]  # 4 types for levels 3

    for i in range(len(coords)):
        for j in range(len(coords[i])):
            hitBoxes[i].append(
                pygame.rect.Rect(
                    coords[i][j][0] + 20, coords[i][j][1], 60 - (i * 12), 60 - (i * 12)
                )
            )  # decreasing hit boxes with increase in level

            screen.blit(enemies[level - 1][i], coords[i][j])
    return hitBoxes


def move_enemies(coords):
    if level == 1 or level == 2:
        enemyTiers = 3
    else:
        enemyTiers = 4
    for i in range(enemyTiers):
        for j in range(len(coords[i])):
            temp_coords = coords[i][j]
            if temp_coords[0] < -150:
                coords[i][j] = (width, temp_coords[1])
            else:
                coords[i][j] = (temp_coords[0] - 2**i, temp_coords[1])
    return coords


def check_shot(hitBoxes, coords):
    global points
    mousePos = pygame.mouse.get_pos()
    for i in range(len(hitBoxes)):
        for j in range(len(hitBoxes[i])):
            if hitBoxes[i][j].collidepoint(mousePos):
                coords[i].pop(j)
                points += 10 + 10 * (i**2)
                if level == 1:
                    birdSound.play()
                elif level == 2:
                    plateSound.play()
                elif level == 3:
                    laserSound.play()

    return coords


def drawScore():
    scoreText = font.render(f"Score : {points}", True, "black")
    screen.blit(scoreText, (320, 660))
    shotText = font.render(f"Shots taken : {totalShots}", True, "black")
    screen.blit(shotText, (320, 687))
    timeText = font.render(f"Time elasped : {timeElapsed}", True, "black")
    screen.blit(timeText, (320, 714))
    if mode == 0:
        modeText = font.render("Freeplay!", True, "black")
        screen.blit(modeText, (320, 741))
    if mode == 1:
        modeText = font.render(f"Ammo remaining : {ammo}", True, "black")
        screen.blit(modeText, (320, 741))
    if mode == 2:
        modeText = font.render(f"Time remaining : {timeRemaining}", True, "black")
        screen.blit(modeText, (320, 741))


def drawMenu():
    global gameOver, pause, clicked, mode, level, timeElapsed, totalShots, points, clicked, ammo, timeRemaining, bestScoreAccuracy, bestScoreFreeplay, bestScoreTimed, writeValues, menu

    gameOver = False
    pause = False

    screen.blit(menuImg, (0, 0))

    mousePos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()

    freeplayButton = pygame.rect.Rect((170, 520), (260, 107))
    screen.blit(font.render(f"{bestScoreFreeplay}", True, "black"), (340, 580))

    accuracyButton = pygame.rect.Rect((475, 520), (260, 107))
    screen.blit(font.render(f"{bestScoreAccuracy}", True, "black"), (650, 580))

    timedButton = pygame.rect.Rect((170, 628), (260, 107))
    screen.blit(font.render(f"{bestScoreTimed}", True, "black"), (350, 710))

    resetButton = pygame.rect.Rect((475, 661), (260, 107))

    if freeplayButton.collidepoint(mousePos) and clicks[0] and not clicked:
        reset()
        mode = 0
        level = 1
        menu = False
        clicked = True

    if accuracyButton.collidepoint(mousePos) and clicks[0] and not clicked:
        reset()
        mode = 1
        level = 1
        menu = False
        ammo = 81
        clicked = True

    if timedButton.collidepoint(mousePos) and clicks[0] and not clicked:
        reset()
        mode = 2
        level = 1
        menu = False
        timeRemaining = 30
        clicked = True

    if resetButton.collidepoint(mousePos) and clicks[0] and not clicked:
        bestScoreFreeplay = 0
        bestScoreAccuracy = 0
        bestScoreTimed = 0
        writeValues = True


def drawPause():
    global clicked, pause, level, menu

    screen.blit(pauseImg, (0, 0))
    mousePos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()

    menuButton = pygame.rect.Rect((475, 661), (260, 107))
    resumeButton = pygame.rect.Rect((170, 628), (260, 107))

    if resumeButton.collidepoint(mousePos) and clicks[0] and not clicked:
        level = levelAtPause
        pause = False
        clicked = True

    if menuButton.collidepoint(mousePos) and clicks[0] and not clicked:
        reset()
        level = 0
        pause = False
        menu = True
        clicked = True


def drawGameOver():
    global clicked, level, pause, gameOver, menu

    if mode == 0:
        displayScore = timeElapsed
    else:
        displayScore = points

    screen.blit(gameOverImg, (0, 0))
    screen.blit(bigFont.render(f"{displayScore}", True, "black"), (650, 570))
    mousePos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()

    menuButton = pygame.rect.Rect((475, 661), (260, 107))
    exitButton = pygame.rect.Rect((170, 628), (260, 107))

    if menuButton.collidepoint(mousePos) and clicks[0] and not clicked:
        reset()
        level = 0
        pause = False
        gameOver = False
        menu = True
        clicked = True
    if exitButton.collidepoint(mousePos) and clicks[0] and not clicked:
        global run
        run = False


# Game Loop-----------------------------
run = True
while run:
    timer.tick(fps)
    if level != 0:
        if counter < 60:
            counter += 1
        else:
            counter = 1
            timeElapsed += 1
            if mode == 2:
                timeRemaining -= 1

    screen.fill("black")
    screen.blit(bgs[level - 1], (0, 0))
    screen.blit(banners[level - 1], (0, height - 200))

    if getNewCoords:
        # Initializing Enemy coordinates
        lvl1Coords = [[], [], []]
        lvl2Coords = [[], [], []]
        lvl3Coords = [[], [], [], []]

        for i in range(3):
            lvl1Enemies = noOfEnemies[1]
            for j in range(lvl1Enemies[i]):
                lvl1Coords[i].append(
                    (
                        ((width - 20) // lvl1Enemies[i]) * j,
                        300 - (i * 150) + 30 * (j % 2),
                    )
                )  # increasing height of every other enemy by 30 px just for variation
        for i in range(3):
            lvl2Enemies = noOfEnemies[2]
            for j in range(lvl2Enemies[i]):
                lvl2Coords[i].append(
                    (
                        ((width - 20) // lvl2Enemies[i]) * j,
                        300 - (i * 150) + 30 * (j % 2),
                    )
                )  # increasing height of every other enemy by 30 px just for variation
        for i in range(4):
            lvl3Enemies = noOfEnemies[3]
            for j in range(lvl3Enemies[i]):
                lvl3Coords[i].append(
                    (
                        ((width - 20) // lvl3Enemies[i]) * j,
                        300 - (i * 100) + 30 * (j % 2),
                    )
                )  # increasing height of every other enemy by 30 px just for variation
        getNewCoords = False

    if menu:
        level = 0
        drawMenu()

    if pause:
        level = 0
        drawPause()

    if gameOver:
        level = 0
        drawGameOver()

    if level > 0:
        drawGun()
        drawScore()

    # Drawing enemies
    if level == 1:
        hitBoxes = draw_enemies(lvl1Coords)
        lvl1Coords = move_enemies(lvl1Coords)
        if shot:
            lvl1Coords = check_shot(hitBoxes, lvl1Coords)
            shot = False
    elif level == 2:
        hitBoxes = draw_enemies(lvl2Coords)
        lvl2Coords = move_enemies(lvl2Coords)
        if shot:
            lvl2Coords = check_shot(hitBoxes, lvl2Coords)
            shot = False
    elif level == 3:
        hitBoxes = draw_enemies(lvl3Coords)
        lvl3Coords = move_enemies(lvl3Coords)
        if shot:
            lvl3Coords = check_shot(hitBoxes, lvl3Coords)
            shot = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mousePos = pygame.mouse.get_pos()
            if (0 < mousePos[0] < width) and (0 < mousePos[1] < height - 200):
                shot = True
                totalShots += 1
                if mode == 1:
                    ammo -= 1
            if (670 < mousePos[0] < 860) and (660 < mousePos[1] < 715):
                levelAtPause = level
                pause = True
                clicked = True
            if (670 < mousePos[0] < 860) and (715 < mousePos[1] < 760):
                reset()
                level = 1
                if mode == 1:
                    ammo = 81
                if mode == 2:
                    timeRemaining = 30
                clicked = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and clicked:
            clicked = False

    if level > 0:
        if hitBoxes == [[], [], []] and level < 3:
            level += 1
        if (
            (level == 3 and hitBoxes == [[], [], [], []])
            or (mode == 1 and ammo == 0)
            or (mode == 2 and timeRemaining == 0)
        ):
            getNewCoords = True
            if mode == 0 and (
                timeElapsed < bestScoreFreeplay or bestScoreFreeplay == 0
            ):
                bestScoreFreeplay = timeElapsed
                writeValues = True
            elif mode == 1 and (points > bestScoreAccuracy or bestScoreAccuracy == 0):
                bestScoreAccuracy = points
                writeValues = True
            elif mode == 2 and (points > bestScoreTimed or bestScoreTimed == 0):
                bestScoreTimed = points
                writeValues = True
            gameOver = True

    if writeValues:
        file = open("highScores.txt", "w")
        file.write(f"{bestScoreFreeplay}\n{bestScoreAccuracy}\n{bestScoreTimed}")
        file.close()
        writeValues = False

    pygame.display.flip()
pygame.quit()
