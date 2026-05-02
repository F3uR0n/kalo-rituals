from math import cos, degrees, radians, sin
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import random
import math
import time

camera_pos = (0,350,300)
angle = 3.1416 / 2
radius = 350
fovY = 110
GRID_LENGTH = 490
playerX = 0
playerY = 0
playerAngle = 0

arenaScale = 2
currentFloor = 1

firstPersonMode = True
isLookBack = False
lookBackAngleOffset = 0

gameOver = False
cheatMode = False

gunX = 0
gunY = 0
gunSpawned = False
hasGun = False
canPickGun = False
bulletAvailable = False

bulletX = 0
bulletY = 0
bulletAngle = 0
bulletActive = False
bulletSpeed = 15

hudDepth = 0.0
windowWidth = 1400
windowHeight = 1000

reverse = True
reverseStartTime = 0
reverseDuration = 10

ghostFrozen = False
ghostFreezeStart = 0
ghostFreezeDuration = 30

regenCount = 3
playerInvisible = False
invisibleStartTime = 0
invisibleDuration = 10

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def beginHUD():
    global hudDepth, windowWidth, windowHeight

    hudDepth = 0.0

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()

    # HUD now uses the real current window size
    gluOrtho2D(0, windowWidth, 0, windowHeight)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

def endHUD():
    glPopMatrix()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()

    glMatrixMode(GL_MODELVIEW)

def drawHUDText(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glRasterPos2f(x, y)

    for ch in text:
        glutBitmapCharacter(font, ord(ch))

def drawHUDRect(x, y, w, h, r, g, b):
    global hudDepth

    glColor3f(r, g, b)

    z = hudDepth
    hudDepth += 0.001   # IMPORTANT: increase, do not decrease

    glBegin(GL_QUADS)
    glVertex3f(x, y, z)
    glVertex3f(x + w, y, z)
    glVertex3f(x + w, y + h, z)
    glVertex3f(x, y + h, z)
    glEnd()

def drawHUDBorder(x, y, w, h, r, g, b):
    # top
    drawHUDRect(x, y + h - 4, w, 4, r, g, b)

    # bottom
    drawHUDRect(x, y, w, 4, r, g, b)

    # left
    drawHUDRect(x, y, 4, h, r, g, b)

    # right
    drawHUDRect(x + w - 4, y, 4, h, r, g, b)

def drawItemIcon(x, y, item):

    if item == "Candle":
        drawHUDRect(x + 14, y + 10, 16, 34, 0.85, 0.72, 0.35)
        drawHUDRect(x + 18, y + 45, 8, 12, 1.0, 0.35, 0.0)

    elif item == "Lemon":
        drawHUDRect(x + 10, y + 18, 34, 26, 0.9, 0.85, 0.0)

    elif item == "Lighter":
        drawHUDRect(x + 13, y + 14, 25, 36, 0.55, 0.55, 0.55)
        drawHUDRect(x + 18, y + 50, 15, 8, 0.9, 0.9, 0.9)

    elif item == "Rope":
        drawHUDRect(x + 8, y + 20, 40, 10, 0.45, 0.25, 0.08)
        drawHUDRect(x + 14, y + 34, 30, 10, 0.45, 0.25, 0.08)

    elif item == "Doll":
        # head (moved a bit lower so it does not touch the border)
        drawHUDRect(x + 19, y + 40, 14, 12, 0.82, 0.66, 0.55)

        # body / dress
        drawHUDRect(x + 17, y + 22, 18, 18, 0.55, 0.20, 0.65)

    # two legs
        drawHUDRect(x + 20, y + 12, 4, 10, 0.82, 0.66, 0.55)
        drawHUDRect(x + 28, y + 12, 4, 10, 0.82, 0.66, 0.55)

    elif item == "Wood":
        drawHUDRect(x + 8, y + 18, 42, 16, 0.45, 0.23, 0.05)
        drawHUDRect(x + 12, y + 38, 35, 14, 0.35, 0.18, 0.04)

    elif item == "Red Powder":
        drawHUDRect(x + 14, y + 16, 28, 34, 0.75, 0.0, 0.0)

    else:
        drawHUDRect(x + 15, y + 18, 25, 25, 0.15, 0.15, 0.15)

def drawHealthHUD():
    global health, maxHealth, windowWidth, windowHeight

    panel_w = 380
    panel_h = 88

    # upper center of actual viewport
    x = (windowWidth - panel_w) / 2
    y = windowHeight - 130

    block_w = 26
    block_h = 30
    gap = 6
    total_blocks = 10

    # dark ash background
    drawHUDRect(x, y, panel_w, panel_h, 0.16, 0.16, 0.16)

    # darker inner strip
    drawHUDRect(x + 18, y + 18, panel_w - 36, 44, 0.06, 0.06, 0.06)

    glColor3f(1, 1, 1)
    drawHUDText(x + 128, y + 64, "PLAYER LIFE")

    if health > 60:
        hr, hg, hb = 0.0, 1.0, 0.15
    elif health > 30:
        hr, hg, hb = 1.0, 0.72, 0.0
    else:
        hr, hg, hb = 1.0, 0.0, 0.0

    filled_blocks = int((health / maxHealth) * total_blocks)

    if health > 0 and filled_blocks == 0:
        filled_blocks = 1

    if filled_blocks < 0:
        filled_blocks = 0

    if filled_blocks > total_blocks:
        filled_blocks = total_blocks

    start_x = x + 38
    block_y = y + 25

    for i in range(total_blocks):
        bx = start_x + i * (block_w + gap)

        # empty block
        drawHUDRect(bx, block_y, block_w, block_h, 0.22, 0.22, 0.22)

        # filled health block
        if i < filled_blocks:
            drawHUDRect(bx + 3, block_y + 3, block_w - 6, block_h - 6, hr, hg, hb)

        drawHUDBorder(bx, block_y, block_w, block_h, 0.75, 0.75, 0.75)

    glColor3f(1, 1, 1)
    drawHUDText(x + 160, y + 4, str(health) + "/" + str(maxHealth))

def drawInventoryHUD():
    global collection, hud_items, selectedSlot, windowWidth

    slot = 72
    gap = 8
    total_width = len(hud_items) * slot + (len(hud_items) - 1) * gap

    start_x = (windowWidth - total_width) / 2
    y = 55

    glColor3f(1, 1, 1)
    drawHUDText(start_x, y + 82, "RITUAL ITEMS")

    for i in range(len(hud_items)):
        item = hud_items[i]

        x = start_x + i * (slot + gap)

        # slot background
        drawHUDRect(x, y, slot, slot, 0.08, 0.08, 0.08)

        # selected slot border
        if i == selectedSlot:
            drawHUDBorder(x, y, slot, slot, 1.0, 0.85, 0.2)
        else:
            drawHUDBorder(x, y, slot, slot, 0.45, 0.45, 0.45)

        # if collected, draw icon
        if item in collection:
            drawItemIcon(x + 8, y + 5, item)
        else:
            # empty slot shadow
            drawHUDRect(x + 18, y + 20, 34, 28, 0.02, 0.02, 0.02)

        # short item label
        glColor3f(1, 1, 1)

        if item == "Red Powder":
            label = "Red"
        else:
            label = item[:5]

        drawHUDText(x + 10, y - 18, label)

def drawStatusHUD():
    global currentFloor, firstPersonMode, windowWidth, windowHeight

    glColor3f(1, 1, 1)

    x = windowWidth - 270
    y = windowHeight - 45

    drawHUDText(x, y, "FLOOR: " + str(currentFloor))

    if firstPersonMode:
        drawHUDText(x, y - 25, "CAMERA: FIRST PERSON")
    else:
        drawHUDText(x, y - 25, "CAMERA: THIRD PERSON")

    drawHUDText(x, y - 50, "ITEMS: " + str(len(collection)) + "/" + str(len(hud_items)))

def drawPlayerHUD():
    beginHUD()

    drawHealthHUD()
    drawInventoryHUD()
    drawStatusHUD()

    endHUD()

def drawPlayer():
    
    glPushMatrix()
    glTranslatef(playerX, playerY, 0)
    glRotatef(playerAngle, 0, 0, 1)

    # Head
    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(0, 0, 117)
    gluSphere(gluNewQuadric(), 20, 20, 20)
    glPopMatrix()

    # Body
    glColor3f(0.3, 0.25, 0.21)
    glPushMatrix()
    glTranslatef(0, 0, 40)
    glutSolidCube(40)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 0, 80)
    glutSolidCube(40)
    glPopMatrix()

    # Arms
    glColor3f(0.8, 0.67, 0.6)

    # Right arm
    glPushMatrix()
    glTranslatef(20, 15, 90)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 10, 5, 20, 30, 30)
    glPopMatrix()

    # Left arm
    glPushMatrix()
    glTranslatef(20, -15, 90)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 10, 5, 20, 30, 30)
    glPopMatrix()

    if hasGun:
        glPushMatrix()
        glTranslatef(25, 0, 90)
        glTranslatef(0, 0, -10)

        drawGunModel()
        glPopMatrix()

    # Legs
    glColor3f(0.6, 0.53, 0.47)
    glPushMatrix()
    glTranslatef(0, 15, 0)
    gluCylinder(gluNewQuadric(), 10, 10, 50, 30, 30)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, -15, 0)
    gluCylinder(gluNewQuadric(), 10, 10, 50, 30, 30)
    glPopMatrix()

    glPopMatrix()

def spawnGun():
    global gunX, gunY, gunSpawned

    rooms = [
        (-320*arenaScale, 280*arenaScale),   # top-left room
        (0, 280*arenaScale),                 # top-middle
        (320*arenaScale, 280*arenaScale),    # top-right
        (-320*arenaScale, -300*arenaScale),  # bottom-left
        (0, -300*arenaScale),                # bottom-middle
        (320*arenaScale, -300*arenaScale)    # bottom-right
    ]
    gunX, gunY = random.choice(rooms)
    gunSpawned = True

def drawGunModel():
    glColor3f(0.1, 0.1, 0.1)

    # body
    glPushMatrix()
    glScalef(30, 10, 8)
    glutSolidCube(1)
    glPopMatrix()

    # barrel
    glPushMatrix()
    glTranslatef(15, 0, 0)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 3, 3, 25, 10, 10)
    glPopMatrix()

    # handle
    glPushMatrix()
    glTranslatef(-5, -5, -10)
    glRotatef(-20, 1, 0, 0)
    glScalef(8, 5, 20)
    glutSolidCube(1)
    glPopMatrix()

def drawGun():
    if not gunSpawned:
        return

    glPushMatrix()
    glTranslatef(gunX, gunY, 20)
    glRotatef(90, 0, 0, 1)
    drawGunModel()
    glPopMatrix()

def checkGunPickup():
    global hasGun, bulletAvailable, gunSpawned, canPickGun

    if not gunSpawned:
        canPickGun = False
        return

    dist = ((playerX - gunX)**2 + (playerY - gunY)**2) ** 0.5
    if dist < 60:   # pickup radius
        canPickGun = True
    else:
        canPickGun = False

def drawBullet():
    if not bulletActive:
        return

    glPushMatrix()
    glColor3f(1, 0, 0)
    glTranslatef(bulletX, bulletY, 80)
    glutSolidCube(8)
    glPopMatrix()

level=""
levelSelected=False
def movePlayer(step):
    global playerX, playerY, playerAngle

    playerCurrentX = playerX + step * cos(radians(playerAngle))
    playerCurrentY = playerY + step * sin(radians(playerAngle))

    if not isBlocked(playerCurrentX, playerCurrentY):
        playerX = playerCurrentX
        playerY = playerCurrentY
    else:
        # try sliding X only
        if not isBlocked(playerCurrentX, playerY):
            playerX = playerCurrentX

        # try sliding Y only
        elif not isBlocked(playerX, playerCurrentY):
            playerY = playerCurrentY

def keyboardListener(key, x, y):
    global playerX, playerY, playerAngle, gameOver, firstPersonMode, currentFloor, isLookBack, lookBackTimer, canPickGun, hasGun, bulletAvailable, gunSpawned,ghostVisible,ghostSpawned,ghostStartTime,level,levelSelected, reverse, reverseStartTime, reverseDuration, regenCount, playerInvisible, invisibleStartTime, invisibleDuration, cheatMode

    if not gameOver:
        if key == b'w':
            if reverse:
                movePlayer(-20)
            else:
                movePlayer(20)
        if key == b's':
            if reverse:
                movePlayer(20)
            else:
                movePlayer(-20)

        if key == b'a':
            if reverse:
                playerAngle -= 10
            else:
                playerAngle += 10
        if key == b'd':
            if reverse:
                playerAngle += 10
            else:
                playerAngle -= 10

        if key == b'c':
            cheatMode = not cheatMode
        if key == b' ':
            isLookBack = not isLookBack
        if key == b'r':
            resetGame()
        if key == b'e':
            if canPickGun and gunSpawned:
                hasGun = True
                bulletAvailable = True
                gunSpawned = False
        if key == b'f':
            if regenCount > 0 and not playerInvisible:
                regenCount -= 1
                playerInvisible = True
                invisibleStartTime = time.time()

        if key == b'1':
            level="Easy"
            levelSelected=True
        if key == b'2':
            level="Medium"
            levelSelected=True
        if key == b'3':
            level="Hard"
            levelSelected=True                               
        
        # Teleporting Pad
        if currentFloor == 1:
            if (350*arenaScale < playerX < 470*arenaScale and
                -500*arenaScale < playerY < -350*arenaScale):

                currentFloor = 2

                #Ghost Spawn Later In Second Floor
                ghostStartTime = time.time()
                ghostVisible = False
                ghostSpawned = False

                playerX = 410 * arenaScale
                playerY = -300 * arenaScale
                playerAngle += 180 
        elif currentFloor == 2:
            
            if (350*arenaScale < playerX < 470*arenaScale and
                -500*arenaScale < playerY < -350*arenaScale):

                currentFloor = 1
                playerX = 300 * arenaScale + 20
                playerY = -400 * arenaScale + 20
                playerAngle += 180

def mouseListener(button, state, x, y):
    global firstPersonMode, hasGun, bulletAvailable, bulletX, bulletY, bulletAngle, bulletActive,ghostX,ghostY

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if hasGun and bulletAvailable:
            angleRad = radians(playerAngle)

            # spawn bullet from player front
            bulletX = playerX + 30 * cos(angleRad)
            bulletY = playerY + 30 * sin(angleRad)
            bulletAngle = playerAngle
            bulletActive = True
            bulletAvailable = False
            hasGun = False
            print("Bullet Fired!")

    
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        firstPersonMode = not firstPersonMode

def resetGame():
    global playerX, playerY, playerAngle
    global health, gameOver, currentFloor
    global collection, candlePicked, lemonPicked, lighterPicked
    global ropePicked, dollPicked, redPicked, woodPicked
    global ghostX, ghostY, ghostState, currentTarget
    global bulletActive, hasGun, bulletAvailable, gunSpawned
    global regenCount, playerInvisible, cheatMode

    # Player reset
    playerX = 0
    playerY = 0
    playerAngle = 0

    # Game state
    health = maxHealth
    gameOver = False
    currentFloor = 1

    # Items
    collection.clear()
    candlePicked = False
    lemonPicked = False
    lighterPicked = False
    ropePicked = False
    dollPicked = False
    redPicked = False
    woodPicked = False

    # Ghost reset
    ghostX = -400
    ghostY = 600
    ghostState = PATROL
    currentTarget = 0

    # Gun reset
    hasGun = False
    bulletAvailable = False
    bulletActive = False
    gunSpawned = False
    spawnGun()

    # Abilities
    regenCount = 3
    playerInvisible = False
    cheatMode = False

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.4, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if firstPersonMode:        
        finalAngle = playerAngle + lookBackAngleOffset

        gluLookAt(
            playerX + 20 * cos(radians(finalAngle)),
            playerY + 20 * sin(radians(finalAngle)),
            120,

            playerX + 100 * cos(radians(finalAngle)),
            playerY + 100 * sin(radians(finalAngle)),
            120,

            0, 0, 1
        )
    else:
        camX = playerX - 120 * cos(radians(playerAngle))
        camY = playerY - 120 * sin(radians(playerAngle))

        gluLookAt(
            camX, camY,150,
            playerX, playerY, 80,
            0, 0, 1
        )

def idle():
    global lookBackAngleOffset, isLookBack, bulletX, bulletY, bulletAngle, bulletActive, playerInvisible, invisibleStartTime
    if not gameOver:
        turnSpeed = 0.5
        returnSpeed = 1

        if isLookBack:
            if lookBackAngleOffset < 180:
                lookBackAngleOffset += turnSpeed
        else:
            if lookBackAngleOffset > 0:
                lookBackAngleOffset -= returnSpeed

        if lookBackAngleOffset < 0:
            lookBackAngleOffset = 0
        if lookBackAngleOffset > 180:
            lookBackAngleOffset = 180

        if bulletActive:
            bulletX += bulletSpeed * cos(radians(bulletAngle))
            bulletY += bulletSpeed * sin(radians(bulletAngle))

        # remove if out of map
        if bulletX < -490*arenaScale or bulletX > 490*arenaScale or bulletY < -560*arenaScale or bulletY > 420*arenaScale:
            bulletActive = False

        # HANDLE INVISIBILITY TIMER
        if playerInvisible:
            if time.time() - invisibleStartTime > invisibleDuration:
                playerInvisible = False


    ghostMovement()
    checkBulletHit()
    updateSafeRoom()
    glutPostRedisplay()

#Bullet Collision Handle
flag=True
def checkBulletHit():
    global flag, bulletActive
    global ghostFrozen, ghostFreezeStart

    dx = bulletX - ghostX
    dy = bulletY - ghostY
    
    if dx*dx + dy*dy < 900 and flag == True:
        print("Bullet Hit")
        flag = False
        bulletActive = False

        # FREEZE GHOST
        ghostFrozen = True
        ghostFreezeStart = time.time()       

def drawWall(x1, y1, x2, y2, height=300, thickness=20):
    glColor3f(0.2, 0.2, 0.2)

    dx = x2 - x1
    dy = y2 - y1
    length = (dx*dx + dy*dy) ** 0.5

    # perpendicular direction
    px = -dy / length * thickness
    py = dx / length * thickness

    # 4 base points
    p1 = (x1, y1)
    p2 = (x2, y2)
    p3 = (x2 + px, y2 + py)
    p4 = (x1 + px, y1 + py)

    glBegin(GL_QUADS)

    # FRONT
    glVertex3f(*p1, 0)
    glVertex3f(*p2, 0)
    glVertex3f(*p2, height)
    glVertex3f(*p1, height)

    # BACK
    glVertex3f(*p4, 0)
    glVertex3f(*p3, 0)
    glVertex3f(*p3, height)
    glVertex3f(*p4, height)

    # LEFT SIDE
    glVertex3f(*p1, 0)
    glVertex3f(*p4, 0)
    glVertex3f(*p4, height)
    glVertex3f(*p1, height)

    # RIGHT SIDE
    glVertex3f(*p2, 0)
    glVertex3f(*p3, 0)
    glVertex3f(*p3, height)
    glVertex3f(*p2, height)

    glEnd()

def drawRoomFloors():
    glColor3f(1, 1, 1)

    glBegin(GL_QUADS)
    # TOP ROOMS
    glVertex3f(-490*arenaScale, 420*arenaScale, 0.05)
    glVertex3f(490*arenaScale, 420*arenaScale, 0.05)
    glVertex3f(490*arenaScale, 140*arenaScale, 0.05)
    glVertex3f(-490*arenaScale, 140*arenaScale, 0.05)

    # BOTTOM ROOMS
    glVertex3f(-490*arenaScale, -140*arenaScale, 0.05)
    glVertex3f(490*arenaScale, -140*arenaScale, 0.05)
    glVertex3f(490*arenaScale, -560*arenaScale, 0.05)
    glVertex3f(-490*arenaScale, -560*arenaScale, 0.05)
    glEnd()

def drawCorridorFloor():
    glColor3f(0.6, 0.6, 0.6)

    glBegin(GL_QUADS)
    glVertex3f(-490*arenaScale, 140*arenaScale, 0.1)
    glVertex3f(490*arenaScale, 140*arenaScale, 0.1)
    glVertex3f(490*arenaScale, -140*arenaScale, 0.1)
    glVertex3f(-490*arenaScale, -140*arenaScale, 0.1)
    glEnd()

def drawArenaBorders():
    drawWall(-490*arenaScale, 420*arenaScale, 490*arenaScale, 420*arenaScale)
    drawWall(-490*arenaScale, -560*arenaScale, 490*arenaScale, -560*arenaScale)
    drawWall(-490*arenaScale, -560*arenaScale, -490*arenaScale, 420*arenaScale)
    drawWall(490*arenaScale, -560*arenaScale, 490*arenaScale, 420*arenaScale)

def isBlocked(x, y):

    if currentFloor == 1:
        margin = 60
        wall = 30

        # OUTER BORDER
        if not (-490*arenaScale+margin < x < 490*arenaScale-margin and
                -560*arenaScale+margin < y < 420*arenaScale-margin):
            return True

        # ===== CORRIDOR WALLS =====
        if 140*arenaScale - wall < y < 140*arenaScale + wall:
            if not (-240*arenaScale < x < -120*arenaScale or
                    120*arenaScale < x < 240*arenaScale):
                return True

        if -140*arenaScale - wall < y < -140*arenaScale + wall:
            if not (-240*arenaScale < x < -120*arenaScale or
                    120*arenaScale < x < 240*arenaScale):
                return True

        # ===== TOP ROOM DIVIDERS =====
        if -160*arenaScale - wall < x < -160*arenaScale + wall and 140*arenaScale < y < 420*arenaScale:
            if not (240*arenaScale < y < 340*arenaScale):
                return True

        if 160*arenaScale - wall < x < 160*arenaScale + wall and 140*arenaScale < y < 420*arenaScale:
            if not (240*arenaScale < y < 340*arenaScale):
                return True

        # ===== BOTTOM ROOM DIVIDERS =====
        if -160*arenaScale - wall < x < -160*arenaScale + wall and -560*arenaScale < y < -140*arenaScale:
            if not (-340*arenaScale < y < -240*arenaScale):
                return True

        if 160*arenaScale - wall < x < 160*arenaScale + wall and -560*arenaScale < y < -140*arenaScale:
            if not (-340*arenaScale < y < -240*arenaScale):
                return True

    elif currentFloor == 2:

        margin = 60
        wall = 30

        # OUTER BORDER
        if not (-490*arenaScale+margin < x < 490*arenaScale-margin and
                -560*arenaScale+margin < y < 420*arenaScale-margin):
            return True

        # corridor walls with doors
        if 140*arenaScale - wall < y < 140*arenaScale + wall:
            if not (-240*arenaScale < x < -120*arenaScale or
                    120*arenaScale < x < 240*arenaScale):
                return True

        if -140*arenaScale - wall < y < -140*arenaScale + wall:
            if not (-240*arenaScale < x < -120*arenaScale or
                    120*arenaScale < x < 240*arenaScale):
                return True

        # vertical top dividers
        if -160*arenaScale - wall < x < -160*arenaScale + wall and y > 140*arenaScale:
            if not (260*arenaScale < y < 340*arenaScale):
                return True

        if 160*arenaScale - wall < x < 160*arenaScale + wall and y > 140*arenaScale:
            if not (260*arenaScale < y < 340*arenaScale):
                return True

        # bottom divider
        if 100*arenaScale - wall < x < 100*arenaScale + wall and y < -140*arenaScale:
            if not (-320*arenaScale < y < -220*arenaScale):
                return True

    return False

def drawCeiling():
    h = 300

    # darker tone than walls
    glColor3f(0.45, 0.04, 0.01)

    glBegin(GL_QUADS)
    glVertex3f(-490*arenaScale, 420*arenaScale, h)
    glVertex3f(490*arenaScale, 420*arenaScale, h)
    glVertex3f(490*arenaScale, -560*arenaScale, h)
    glVertex3f(-490*arenaScale, -560*arenaScale, h)
    glEnd()

def drawCorridor():
    # Top divider line
    drawWall(-490*arenaScale, 140*arenaScale, 490*arenaScale, 140*arenaScale)

    # Bottom divider line
    drawWall(-490*arenaScale, -140*arenaScale, 490*arenaScale, -140*arenaScale)

def drawTopRooms():
    y_top = 420 * arenaScale
    y_bottom = 140 * arenaScale

    x_left = -490 * arenaScale
    x_mid1 = -160 * arenaScale
    x_mid2 = 160 * arenaScale
    x_right = 490 * arenaScale

    # LEFT ROOM (Room 1A)
    drawWall(x_left, y_top, x_mid1, y_top)       # top wall
    drawWall(x_left, y_bottom, x_left, y_top)    # left wall

    # Divider (Room1 ↔ Room2) with vertical door
    drawWall(x_mid1, y_bottom, x_mid1, y_bottom + 120*arenaScale)
    drawWall(x_mid1, y_bottom + 220*arenaScale, x_mid1, y_top)

    # MIDDLE ROOM (Room 1B)
    drawWall(x_mid1, y_top, x_mid2, y_top)

    # Divider (Room2 ↔ Room3) with vertical door
    drawWall(x_mid2, y_bottom, x_mid2, y_bottom + 120*arenaScale)
    drawWall(x_mid2, y_bottom + 220*arenaScale, x_mid2, y_top)

    # RIGHT ROOM (Safe Room 1C)
    drawWall(x_mid2, y_top, x_right, y_top)
    drawWall(x_right, y_bottom, x_right, y_top)  # right wall

def drawBottomRooms():
    y_top = -140 * arenaScale
    y_bottom = -560 * arenaScale

    x_left = -490 * arenaScale
    x_mid1 = -160 * arenaScale
    x_mid2 = 160 * arenaScale
    x_right = 490 * arenaScale

    # LEFT ROOM (Room 1D)
    drawWall(x_left, y_bottom, x_mid1, y_bottom)  # bottom wall
    drawWall(x_left, y_bottom, x_left, y_top)     # left wall

    # Divider (Room1 ↔ Room2) with vertical door
    drawWall(x_mid1, y_bottom, x_mid1, y_bottom + 200*arenaScale)
    drawWall(x_mid1, y_top - 120*arenaScale, x_mid1, y_top)

    # MIDDLE ROOM (Room 1E)
    drawWall(x_mid1, y_bottom, x_mid2, y_bottom)

    # Divider (Room2 ↔ Room3) with vertical door
    drawWall(x_mid2, y_bottom, x_mid2, y_bottom + 200*arenaScale)
    drawWall(x_mid2, y_top - 120*arenaScale, x_mid2, y_top)

    # RIGHT ROOM (Room 1F)
    drawWall(x_mid2, y_bottom, x_right, y_bottom)
    drawWall(x_right, y_bottom, x_right, y_top)

def drawCorridorWithDoors():
    y_top = 140 * arenaScale
    y_bottom = -140 * arenaScale

    # LEFT wall
    drawWall(-490*arenaScale, y_top, -240*arenaScale, y_top)
    drawWall(-490*arenaScale, y_bottom, -240*arenaScale, y_bottom)

    # MIDDLE wall
    drawWall(-120*arenaScale, y_top, 120*arenaScale, y_top)
    drawWall(-120*arenaScale, y_bottom, 120*arenaScale, y_bottom)

    # RIGHT wall
    drawWall(240*arenaScale, y_top, 490*arenaScale, y_top)
    drawWall(240*arenaScale, y_bottom, 490*arenaScale, y_bottom)

def drawSafeRoomFloor():
    glColor3f(0.3, 0.8, 0.6)

    glBegin(GL_QUADS)
    glVertex3f(160 * arenaScale, 420 * arenaScale, 0.2)
    glVertex3f(490 * arenaScale, 420 * arenaScale, 0.2)
    glVertex3f(490 * arenaScale, 140 * arenaScale, 0.2)
    glVertex3f(160 * arenaScale, 140 * arenaScale, 0.2)
    glEnd()

def drawTeleportPad():
    x1 = 350*arenaScale
    x2 = 470*arenaScale
    y1 = -500*arenaScale
    y2 = -350*arenaScale
    h = 20
    glColor3f(0.2, 0.2, 1)
    glBegin(GL_QUADS)

    # TOP
    glVertex3f(x1, y1, h)
    glVertex3f(x2, y1, h)
    glVertex3f(x2, y2, h)
    glVertex3f(x1, y2, h)

    # BOTTOM
    glVertex3f(x1, y1, 0)
    glVertex3f(x2, y1, 0)
    glVertex3f(x2, y2, 0)
    glVertex3f(x1, y2, 0)

    # FRONT
    glVertex3f(x1, y1, 0)
    glVertex3f(x2, y1, 0)
    glVertex3f(x2, y1, h)
    glVertex3f(x1, y1, h)

    # BACK
    glVertex3f(x1, y2, 0)
    glVertex3f(x2, y2, 0)
    glVertex3f(x2, y2, h)
    glVertex3f(x1, y2, h)

    # LEFT
    glVertex3f(x1, y1, 0)
    glVertex3f(x1, y2, 0)
    glVertex3f(x1, y2, h)
    glVertex3f(x1, y1, h)

    # RIGHT
    glVertex3f(x2, y1, 0)
    glVertex3f(x2, y2, 0)
    glVertex3f(x2, y2, h)
    glVertex3f(x2, y1, h)
    glEnd()

def drawSecondFloor():

    # ===== WALLS =====
    drawArenaBorders()

    # ===== FLOOR COLORS =====
    # base floor
    glColor3f(0.15, 0.15, 0.15)
    glBegin(GL_QUADS)
    glVertex3f(-490*arenaScale, 420*arenaScale, 0.1)
    glVertex3f(490*arenaScale, 420*arenaScale, 0.1)
    glVertex3f(490*arenaScale, -560*arenaScale, 0.1)
    glVertex3f(-490*arenaScale, -560*arenaScale, 0.1)
    glEnd()

    # corridor
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(-490*arenaScale, 140*arenaScale, 0.4)
    glVertex3f(490*arenaScale, 140*arenaScale, 0.4)
    glVertex3f(490*arenaScale, -140*arenaScale, 0.4)
    glVertex3f(-490*arenaScale, -140*arenaScale, 0.4)
    glEnd()

    glColor3f(0.15, 0.15, 0.15)
    glBegin(GL_QUADS)
    glVertex3f(-100*arenaScale, 420*arenaScale, 0.2)
    glVertex3f(100*arenaScale, 420*arenaScale, 0.2)
    glVertex3f(100*arenaScale, 140*arenaScale, 0.2)
    glVertex3f(-100*arenaScale, 140*arenaScale, 0.2)
    glEnd()

    # RITUAL ROOM
    glColor3f(1, 0.55, 0)
    glBegin(GL_QUADS)
    glVertex3f(-490*arenaScale, -140*arenaScale, 0.3)
    glVertex3f(100*arenaScale, -140*arenaScale, 0.3)
    glVertex3f(100*arenaScale, -560*arenaScale, 0.3)
    glVertex3f(-490*arenaScale, -560*arenaScale, 0.3)
    glEnd()

    # corridor walls (WITH DOORS)
    # TOP corridor
    drawWall(-490*arenaScale, 140*arenaScale, -240*arenaScale, 140*arenaScale)
    drawWall(-120*arenaScale, 140*arenaScale, 120*arenaScale, 140*arenaScale)
    drawWall(240*arenaScale, 140*arenaScale, 490*arenaScale, 140*arenaScale)

    # BOTTOM corridor
    drawWall(-490*arenaScale, -140*arenaScale, -240*arenaScale, -140*arenaScale)
    drawWall(-120*arenaScale, -140*arenaScale, 120*arenaScale, -140*arenaScale)
    drawWall(240*arenaScale, -140*arenaScale, 490*arenaScale, -140*arenaScale)
    # ===== TOP ROOMS =====

    # left room
    drawWall(-490*arenaScale, 420*arenaScale, -160*arenaScale, 420*arenaScale)
    drawWall(-490*arenaScale, 140*arenaScale, -490*arenaScale, 420*arenaScale)

    # divider with door
    drawWall(-160*arenaScale, 140*arenaScale, -160*arenaScale, 260*arenaScale)
    drawWall(-160*arenaScale, 340*arenaScale, -160*arenaScale, 420*arenaScale)

    # middle room
    drawWall(-160*arenaScale, 420*arenaScale, 160*arenaScale, 420*arenaScale)

    # divider with door
    drawWall(160*arenaScale, 140*arenaScale, 160*arenaScale, 260*arenaScale)
    drawWall(160*arenaScale, 340*arenaScale, 160*arenaScale, 420*arenaScale)

    # right room
    drawWall(160*arenaScale, 420*arenaScale, 490*arenaScale, 420*arenaScale)
    drawWall(490*arenaScale, 140*arenaScale, 490*arenaScale, 420*arenaScale)

    # ===== BOTTOM ROOMS =====

    # ritual room (left big)
    drawWall(-490*arenaScale, -560*arenaScale, 100*arenaScale, -560*arenaScale)
    drawWall(-490*arenaScale, -560*arenaScale, -490*arenaScale, -140*arenaScale)

    # divider with door
    drawWall(100*arenaScale, -560*arenaScale, 100*arenaScale, -320*arenaScale)
    drawWall(100*arenaScale, -220*arenaScale, 100*arenaScale, -140*arenaScale)

    # dark hallway (right)
    drawWall(100*arenaScale, -560*arenaScale, 490*arenaScale, -560*arenaScale)
    drawWall(490*arenaScale, -560*arenaScale, 490*arenaScale, -140*arenaScale)

def drawBox(x, y, z, size, r, g, b):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(r, g, b)
    glutSolidCube(size)
    glPopMatrix()

def drawAllRoomBoxes():
    if currentFloor==1:
        #1A
        drawBox(-930,790,30,50,1,0,0)
        drawBox(-930,330,30,50,0,1, 0)
        drawBox(-370,790,30,50,0,0,1)
        drawBox(-650,790,30,50,1,1,0)

        #1B
        drawBox(-270,790,30,50,1,0,0)
        drawBox(10,790,30,50,0,1,0)
        drawBox(270,790,30,50,0,0,1)
        drawBox(10,330,30, 50,0.5,0,1)

        #1D
        drawBox(-930,-1050,30,50,1,0.3,0)
        drawBox(-930,-540,30, 50,0.3,1,0)
        drawBox(-370,-1050,30,50,0,0.3,1)
        drawBox(-650,-1050,30,50,1,1,0.3)

        
        #1E
        drawBox(-270,-1050,30,50,0.8,0,1)
        drawBox(0,-330,30,50,0,1,0.8)
        drawBox(270,-1050,30,50,1,0.8, 0)
        drawBox(0,-1050,30,50,0.3,0.3,1)

        #1F
        drawBox(370,-1050,30,50,1,0,0)
        drawBox(650,-320,30,50,0,1,0)
        drawBox(500,-1050,30,50,0,0,1)
        drawBox(930,-320,30,50,1,1,0)

    else:
        #2A
        drawBox(-930,790,30,50,1,0,0)
        drawBox(-930,330,30,50,0,1,0)
        drawBox(-370,790,30,50,0,0,1)
        drawBox(-650,790,30,50,1,1,0)

        #2C
        drawBox(370,790,30,50,1,0,0)
        drawBox(650,790,30,50,0,1,0)
        drawBox(770,320,30,50,0,0,1)
        drawBox(930,790,30,50,1,1,0)

        #Ritual Room(2D)
        drawBox(-930,-1050,30,50,1,0.3,0)
        drawBox(-930,-540,30,50,0.3,1,0)
        drawBox(-370,-1050,30,50,0,0.3,1)
        drawBox(-650,-1050,30,50,1,1,0.3)
        drawBox(-270,-1050,30,50,0.8,0,1)
        drawBox(0,-330,30, 50,0,1,0.8)
        drawBox(270,-1050,30,50,1,0.8,0)
        drawBox(0,-1050,30,50,0.3,0.3,1)

        #2E
        drawBox(370,-1050,30,50,1,0,0)
        drawBox(650,-320,30,50,0,1,0)
        drawBox(500,-1050,30,50,0,0,1)
        drawBox(930,-320,30,50,1,1,0)

roomAFlag=False
roomBFlag=False
roomDFlag=False
roomEFlag=False
roomFFlag=False

def clue():
    if currentFloor==1:
        if (-980<playerX<-320 and 280<playerY<840):
            draw_text(10, 770, f"Clue to Get a Candle: 2+5*3")
            draw_text(10, 750, f"Red:17")
            draw_text(10, 730, f"Green:21")
            draw_text(10, 710, f"Blue:11")
            draw_text(10, 690, f"Yellow:31")
        elif(-320<playerX<320 and 280<playerY<840):
            draw_text(10, 770, f"Clue to Get a Lemon:2+3*?=11")
            draw_text(10, 750, f"Red:6")
            draw_text(10, 730, f"Green:9")
            draw_text(10, 710, f"Blue:3")
            draw_text(10, 690, f"Purple:1")
        elif(-980<playerX<-320 and -1120<playerY<-280):
            draw_text(10, 770, f"Clue to Get a Matches: (3+2)/(2*4)*6")
            draw_text(10, 750, f"Orange:3")
            draw_text(10, 730, f"Green:4.5")
            draw_text(10, 710, f"Blue:3.75")
            draw_text(10, 690, f"Yellow:7.35")
        elif(-320<playerX<320 and -1120<playerY<-280):
            draw_text(10, 770, f"Clue to Get a Rope:3^2+9*2^5")
            draw_text(10, 750, f"Purple:729")
            draw_text(10, 730, f"Cyan:217")
            draw_text(10, 710, f"Orange:297")
            draw_text(10, 690, f"Blue:432")
        elif(320<playerX<980 and -1120<playerY<-280):
            draw_text(10, 770, f"Clue to Get a Doll: 9^2-3^2-2*7")
            draw_text(10, 750, f"Red:98")
            draw_text(10, 730, f"Green:121")
            draw_text(10, 710, f"Blue:111")
            draw_text(10, 690, f"Yellow:58")
    else:
        if (-980<playerX<-320 and 280<playerY<840):
            draw_text(10, 770, f"Clue to Get a Knife: x^2+3x+2=0 the value of x is?")
            draw_text(10, 750, f"Red:(-1,-2)")
            draw_text(10, 730, f"Green:(1,2)")
            draw_text(10, 710, f"Blue:(1,-2)")
            draw_text(10, 690, f"Yellow:(-1,2)")
        elif(320<playerX<980 and 280<playerY<840):
            draw_text(10, 770, f"Clue to Get a wood: 3x+3=9 the value of x is?")
            draw_text(10, 750, f"Red:1")
            draw_text(10, 730, f"Green:2")
            draw_text(10, 710, f"Blue:3")
            draw_text(10, 690, f"Yellow:4")
        elif(-980<playerX<200 and -1120<playerY<-280):
            draw_text(10, 770, f"Clue to Get a Surprise: (x/2)+(x/3)=10 the value of x is?")
            draw_text(10, 750, f"Red:10")
            draw_text(10, 730, f"Green:11")
            draw_text(10, 710, f"Blue:31")
            draw_text(10, 690, f"Purple:34")
            draw_text(10, 670, f"Cyan:20")
            draw_text(10, 650, f"Orange:14")
            draw_text(10, 630, f"Indigo:12")
        elif(200<playerX<980 and -1120<playerY<-280):
            draw_text(10, 770, f"Clue to Get a wood:x^2-9=0 the value of x is?")
            draw_text(10, 750, f"Red:+3")
            draw_text(10, 730, f"Green:-3")
            draw_text(10, 710, f"Blue:+3 or -3")
            draw_text(10, 690, f"Yellow:+3 and -3")

health = 100
maxHealth = 100
collection = []
lastDamageTime = 0
hud_items = ["Candle", "Lemon", "Lighter", "Rope", "Doll", "Wood", "Red Powder"]
selectedSlot = 0
candlePicked=False
lemonPicked=False
lighterPicked=False
ropePicked=False
dollPicked=False
redPicked=False
woodPicked=False
firstFloorReverseBoxes = [
    # Room 1A wrong boxes only
    {"room": "1A", "color": "Green", "area": (-970, -890, 290, 370)},
    {"room": "1A", "color": "Blue", "area": (-410, -330, 750, 830)},
    {"room": "1A", "color": "Yellow", "area": (-690, -610, 750, 830)},

    # Room 1B wrong boxes only
    {"room": "1B", "color": "Red", "area": (-310, -230, 750, 830)},
    {"room": "1B", "color": "Green", "area": (-30, 50, 750, 830)},
    {"room": "1B", "color": "Purple", "area": (-30, 50, 290, 370)},

    # Room 1D wrong boxes only
    {"room": "1D", "color": "Orange", "area": (-970, -890, -1090, -1010)},
    {"room": "1D", "color": "Green", "area": (-970, -890, -580, -500)},
    {"room": "1D", "color": "Yellow", "area": (-690, -610, -1090, -1010)},

    # Room 1E wrong boxes only
    {"room": "1E", "color": "Purple", "area": (-310, -230, -1090, -1010)},
    {"room": "1E", "color": "Cyan", "area": (-40, 40, -370, -290)},
    {"room": "1E", "color": "Blue", "area": (-40, 40, -1090, -1010)},

    # Room 1F wrong boxes only
    {"room": "1F", "color": "Red", "area": (330, 410, -1090, -1010)},
    {"room": "1F", "color": "Green", "area": (610, 690, -360, -280)},
    {"room": "1F", "color": "Blue", "area": (460, 540, -1090, -1010)},
]
reverseBox = random.choice(firstFloorReverseBoxes)

def takeDamage(amount):
    global health, lastDamageTime, gameOver

    if cheatMode:
        return

    now = time.time()
    # prevents damage from happening every frame while standing on the same wrong box
    if now - lastDamageTime > 1.0:
        health -= amount

        if health < 0:
            health = 0

        lastDamageTime = now

        if health <= 0:
            gameOver = True

def wrongAnswer():
    draw_text(300, 770, "Wrong Answer! Health decreased.")
    takeDamage(10)

def insideReverseBox():
    global playerX, playerY, reverseBox

    x1, x2, y1, y2 = reverseBox["area"]

    if x1 < playerX < x2 and y1 < playerY < y2:
        return True

    return False

def startReverseControl():
    global reverse, reverseStartTime

    reverse = True
    reverseStartTime = time.time()

def updateReverseControl():
    global reverse

    if reverse:
        if time.time() - reverseStartTime > reverseDuration:
            reverse = False

def checkReverseBox():
    global currentFloor

    updateReverseControl()

    if currentFloor == 1 and insideReverseBox():
        startReverseControl()
        draw_text(300, 735, "DISADVANTAGE: Controls reversed!")

    if reverse:
        remaining = int(reverseDuration - (time.time() - reverseStartTime))

        if remaining < 0:
            remaining = 0

        draw_text(300, 715, "Reverse controls: " + str(remaining) + "s")

def correctBoxDetection():
    global health,candlePicked,lemonPicked,lighterPicked,woodPicked,redPicked,ropePicked,dollPicked
    if currentFloor == 1:
        # 1A
        if -970 < playerX < -890 and 750 < playerY < 830:
            draw_text(300,770,f"Red Box:Correct Answer--> Picked Candle")
            candlePicked=True
            storeCollection()
        elif -970 < playerX < -890 and 290 < playerY < 370:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)
        elif -410 < playerX < -330 and 750 < playerY < 830:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)
        elif -690 < playerX < -610 and 750 < playerY < 830:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)

        # 1B
        elif -310 < playerX < -230 and 750 < playerY < 830:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)
        elif -30 < playerX < 50 and 750 < playerY < 830:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)
        elif 230 < playerX < 310 and 750 < playerY < 830:
            draw_text(300,770,"Blue Box:Correct Answer--> Picked a Lemon")
            lemonPicked=True
            storeCollection()
        elif -30 < playerX < 50 and 290 < playerY < 370:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)

        # 1D
        elif -970 < playerX < -890 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)
        elif -970 < playerX < -890 and -580 < playerY < -500:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)
        elif -410 < playerX < -330 and -1090 < playerY < -1010:
            draw_text(300,770,"Blue Box: Correct Answer--> Picked Lighter")
            lighterPicked=True
            storeCollection()
        elif -690 < playerX < -610 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)

        # 1E
        elif -310 < playerX < -230 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)
        elif -40 < playerX < 40 and -370 < playerY < -290:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)
        elif 230 < playerX < 310 and -1090 < playerY < -1010:
            draw_text(300,770,"Orange Box: Correct Answer--> Picked Rope")
            ropePicked=True
            storeCollection()
        elif -40 < playerX < 40 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)

        # 1F
        elif 330 < playerX < 410 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)
        elif 610 < playerX < 690 and -360 < playerY < -280:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)
        elif 460 < playerX < 540 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)
        elif 890 < playerX < 970 and -360 < playerY < -280:
            draw_text(300,770,"1F Yellow Box: Correct Answer--> Picked a Doll")
            dollPicked=True 
            storeCollection()

    elif currentFloor == 2:

        # 2A
        if -970 < playerX < -890 and 750 < playerY < 830:
            draw_text(300,770,"Red Box: Correct Answer--> Picked Red Powder")
            redPicked=True
            storeCollection()
        elif -970 < playerX < -890 and 290 < playerY < 370:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)
        elif -410 < playerX < -330 and 750 < playerY < 830:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)
        elif -690 < playerX < -610 and 750 < playerY < 830:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)

        # 2C
        elif 330 < playerX < 410 and 750 < playerY < 830:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)
        elif 610 < playerX < 690 and 750 < playerY < 830:
            draw_text(300,770,"Green Box: Correct Answer-->Hint: You have to Collect solve all the room Clue")
        elif 730 < playerX < 810 and 280 < playerY < 360:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)
        elif 890 < playerX < 970 and 750 < playerY < 830:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)

        # Ritual Room
        elif -970 < playerX < -890 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)

        elif -970 < playerX < -890 and -580 < playerY < -500:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)

        elif -410 < playerX < -330 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)

        elif -690 < playerX < -610 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)

        elif -310 < playerX < -230 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)

        elif -40 < playerX < 40 and -370 < playerY < -290:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)

        elif 230 < playerX < 310 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)

        elif -40 < playerX < 40 and -1090 < playerY < -1010:
            draw_text(300,770,"Indigo Box: Correct Answer--> Health Full")
            health = maxHealth   

        # 2E
        elif 330 < playerX < 410 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)
        elif 610 < playerX < 690 and -360 < playerY < -280:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)
        elif 460 < playerX < 540 and -1090 < playerY < -1010:
            draw_text(300,770,"Blue Box: Correct Answer-->Picked Wood")
            woodPicked=True
            storeCollection()
        elif 890 < playerX < 970 and -360 < playerY < -280:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
            takeDamage(10)

collectionPrinted = False
def storeCollection():
    global collectionPrinted

    if candlePicked and "Candle" not in collection:
        collection.append("Candle")

    if lemonPicked and "Lemon" not in collection:
        collection.append("Lemon")

    if lighterPicked and "Lighter" not in collection:
        collection.append("Lighter")

    if ropePicked and "Rope" not in collection:
        collection.append("Rope")

    if dollPicked and "Doll" not in collection:
        collection.append("Doll")

    if redPicked and "Red Powder" not in collection:
        collection.append("Red Powder")

    if woodPicked and "Wood" not in collection:
        collection.append("Wood")

    #checkRitualStart()    

ritualItem=["Candle","Lemon","Lighter","Doll","Rope","Wood","Red Powder"]
ritualFlag=False
def checkRitualStart():
    global ritualItem, ritualFlag

    ritualFlag = True
    for i in ritualItem:
        found=False
        for j in collection:
            if i==j:
                found=True
                break

        if found == False:
            ritualFlag = False
            break

    print(ritualFlag)  

ghostX=-400
ghostY=600
ghostAngle=0
def drawGhost():
    glPushMatrix()
    glTranslatef(ghostX, ghostY, 0)
    glRotatef(ghostAngle, 0, 0, 1)

    # Head
    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(0, 0,175)
    gluSphere(gluNewQuadric(), 20, 20, 20)
    glPopMatrix()

    # Body
    glColor3f(1,1,1)
    glPushMatrix()
    glTranslatef(0, 0,60)
    gluCylinder(gluNewQuadric(), 50,20,100,5, 100)
    glPopMatrix()

    # Arms
    glColor3f(1, 0.2,0.2)

    glPushMatrix()
    glTranslatef(20, 15,130)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 10, 5,50, 30, 30)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(20, -15, 130)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 10, 5, 50, 30, 30)
    glPopMatrix()

    # Legs
    glColor3f(0.6, 0.53, 0.47)

    glPushMatrix()
    glTranslatef(0, 15, 20)
    gluCylinder(gluNewQuadric(), 10, 10, 60, 30, 30)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, -15, 20)
    gluCylinder(gluNewQuadric(), 10, 10,60, 30, 30)
    glPopMatrix()

    glPopMatrix()

ghostPaths= [(-400,500),(-400,280),(-400,0),(-400,-800),(-750,-800),(-600,-800),(-400,-280),(-400,-140),(-280,280),(-80,500),(270,500),(270,0),(250,-500),(400,-500),(400,-280),(400,250)]
currentTarget =0
ghostSpeed =0.05
direction=1
PATROL = 0
CHASE = 1

ghostState = PATROL
detectRadius = 200
def ghostMovement():
    global ghostX, ghostY, ghostAngle, ghostState, level, currentTarget, direction, ghostFrozen, ghostFreezeStart, playerInvisible, cheatMode

    # FREEZE SYSTEM
    if ghostFrozen:
        if time.time() - ghostFreezeStart < ghostFreezeDuration:
            return   # ❌ stop all movement
        else:
            ghostFrozen = False  # resume movement

    # CHEAT MODE: player becomes fully invisible
    if cheatMode:
        playerInvisible = True
        ghostState = PATROL   # force reset if already chasing
    
    if levelSelected==True:
        
        dxP = playerX - ghostX
        dyP = playerY - ghostY
        distP = math.sqrt(dxP*dxP + dyP*dyP)

        # IF PLAYER INVISIBLE → ghost cannot detect
        if not playerInvisible:
            if ghostState == PATROL:
                if distP < detectRadius:
                    ghostState = CHASE
        else:
            ghostState = PATROL   # force ghost to ignore player

        if 320<playerX<980 and 280<playerY<840:
            targetX = ghostX
            targetY = ghostY
        else:
            targetX = playerX
            targetY = playerY

        if ghostState == CHASE and not playerInvisible:
            dx = targetX - ghostX
            dy = targetY - ghostY
            distance = math.sqrt(dx*dx + dy*dy)

            if distance > 1:
                ghostX += ghostSpeed * 2 * dx / distance
                ghostY += ghostSpeed * 2 * dy / distance

                ghostAngle = degrees(math.atan2(dy, dx))

        else:
            targetX, targetY = ghostPaths[currentTarget]

            dx = targetX - ghostX
            dy = targetY - ghostY
            distance = math.sqrt(dx*dx + dy*dy)

            if distance < 10:
                currentTarget += direction

                if currentTarget >= len(ghostPaths):
                    currentTarget = len(ghostPaths) - 2
                    direction = -1

                elif currentTarget < 0:
                    currentTarget = 1
                    direction = 1

            else:
                ghostX += ghostSpeed * dx / distance
                ghostY += ghostSpeed * dy / distance

                ghostAngle = degrees(math.atan2(dy, dx))

inSafeRoom = False
safeRoomStartTime = 0
SAFE_LIMIT = 10
def updateSafeRoom():
    global inSafeRoom, safeRoomStartTime, playerX, playerY, currentFloor,ghostState

    if currentFloor == 1 and 320<playerX<980 and 280<playerY<840:

        if not inSafeRoom:
            inSafeRoom = True
            safeRoomStartTime = time.time()

        else:
            elapsed = time.time() - safeRoomStartTime

            if elapsed >= SAFE_LIMIT:
                print("Time up! Sending player back to 1A")

                playerX = 300 * arenaScale
                playerY = -400 * arenaScale
                ghostState=PATROL
                inSafeRoom = False

    else:
        inSafeRoom = False

ghostVisible = False
ghostStartTime = None
ghostDelay = 10

ghostSpawned = False

def ghostTimer():
    global ghostVisible, ghostStartTime,ghostX,ghostY

    if ghostStartTime is None:
        return

    currentTime = time.time()

    if currentTime - ghostStartTime >= ghostDelay:
        ghostVisible = True

def levelSelection():
    global ghostSpeed
    if levelSelected==False:
        draw_text(400,400,"Please Select The Level By Pressing 1/2/3:")
        draw_text(400,370,"1.Easy  2.Medium 3.Hard")
    else:
        if level=="Easy":
            ghostSpeed=0.05
        elif level=="Medium":
            ghostSpeed=0.5
        else:
            ghostSpeed=1                

def showScreen():
    global currentFloor,ghostStartTime,ghostX,ghostY, ghostFrp, ghostState, levelSelected, ghostFreezeStart, ghostFrozen, ghostFreezeDuration, playerInvisible, invisibleStartTime, invisibleDuration, regenCount
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glLoadIdentity()
    glViewport(0, 0, 1400, 1000)
    setupCamera()

    if currentFloor == 1:
        drawSafeRoomFloor()
        drawRoomFloors()
        drawCorridorFloor()

        drawArenaBorders()
        drawCorridorWithDoors()
        drawTopRooms()
        drawBottomRooms()
        drawTeleportPad()
        drawCeiling()
        checkGunPickup()
        drawGun()

    elif currentFloor == 2:
        drawSecondFloor()
        drawTeleportPad()
        drawCeiling()

    drawAllRoomBoxes()
    drawPlayer()

    if currentFloor==1:
        drawGhost()
    elif currentFloor == 2:
        ghostTimer()
        if ghostVisible:
            drawGhost() 

    drawBullet()
    clue()
    correctBoxDetection()
    levelSelection()
    checkReverseBox()
    glClear(GL_DEPTH_BUFFER_BIT)
    drawPlayerHUD()

    if cheatMode:
        draw_text(10, 610, "CHEAT MODE: GOD MODE ACTIVE")

    if canPickGun and not hasGun:
        draw_text(10, 590, "Press E to pick gun But But But you only have 1 bullet, use it wisely!")

    if ghostFrozen:
        remaining = int(ghostFreezeDuration - (time.time() - ghostFreezeStart))
        if remaining < 0:
            remaining = 0
        draw_text(10, 670, f"GHOST STUNNED: {remaining}s")

    draw_text(10, 650, f"Regenerators: {regenCount}")
    if playerInvisible:
        remaining = int(invisibleDuration - (time.time() - invisibleStartTime))
        if remaining < 0:
            remaining = 0
        draw_text(10, 630, f"INVISIBLE: {remaining}s")

    glutSwapBuffers()

def main():
    global ghostStartTime
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1400, 1000)
    glutInitWindowPosition(50,50)
    wind = glutCreateWindow(b"Kalo Ritual")

    spawnGun()
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    # glutReshapeFunc(reshapeListener)
    glutMainLoop()

if __name__ == "__main__":
    main()