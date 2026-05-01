from math import cos, degrees, radians, sin
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import random

camera_pos = (0,350,300)
angle = 3.1416 / 2
radius = 350
fovY = 110
GRID_LENGTH = 490
playerX = 0
playerY = 0
playerAngle = 0
gameOver = False
firstPersonMode = True
arenaScale = 2
currentFloor = 1
isLookBack = False
lookBackAngleOffset = 0
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

def keyboardListener(key, x, y):
    global playerX, playerY, playerAngle, gameOver, firstPersonMode, currentFloor, isLookBack, lookBackTimer, canPickGun, hasGun, bulletAvailable, gunSpawned

    if not gameOver:
        if key == b'w':
            playerCurrentX = playerX + 20 * cos(radians(playerAngle)) # Oi Direction e move korar jonno cos(angle)/sin(angle)/Head Movement. Also radian for accurate and correct answers
            playerCurrentY = playerY + 20 * sin(radians(playerAngle))
            if not isBlocked(playerCurrentX, playerCurrentY):
                playerX = playerCurrentX
                playerY = playerCurrentY
            else:
                # try sliding (X only)
                if not isBlocked(playerCurrentX, playerY):
                    playerX = playerCurrentX
                # try sliding (Y only)
                elif not isBlocked(playerX, playerCurrentY):
                    playerY = playerCurrentY
        if key == b's':
            playerCurrentX = playerX - 20 * cos(radians(playerAngle))
            playerCurrentY = playerY - 20 * sin(radians(playerAngle))
            if not isBlocked(playerCurrentX, playerCurrentY):
                playerX = playerCurrentX
                playerY = playerCurrentY
            else:
                # try sliding (X only)
                if not isBlocked(playerCurrentX, playerY):
                    playerX = playerCurrentX
                # try sliding (Y only)
                elif not isBlocked(playerX, playerCurrentY):
                    playerY = playerCurrentY
                    
        if key == b'a':
            playerAngle += 10
        if key == b'd':
            playerAngle -= 10
        if key == b' ':
            isLookBack = not isLookBack
        
        if key == b'e':
            if canPickGun and gunSpawned:
                hasGun = True
                bulletAvailable = True
                gunSpawned = False
        
        # Teleporting Pad
        if currentFloor == 1:
            if (350*arenaScale < playerX < 470*arenaScale and
                -500*arenaScale < playerY < -350*arenaScale):

                currentFloor = 2
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

def specialKeyListener(key, x, y):
    global camera_pos
    x, y, z = camera_pos
    # Move camera up (UP arrow key)
    # if key == GLUT_KEY_UP:

    # # Move camera down (DOWN arrow key)
    # if key == GLUT_KEY_DOWN:

    # moving camera left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        x -= 10  # Small angle decrement for smooth movement

    # moving camera right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        x += 10  # Small angle increment for smooth movement

    if key == GLUT_KEY_UP:
        z += 10  # Small angle decrement for smooth movement

    # moving camera right (RIGHT arrow key)
    if key == GLUT_KEY_DOWN:
        z -= 10  # Small angle increment for smooth movement    

    camera_pos = (x, y, z)

def mouseListener(button, state, x, y):
    global firstPersonMode, hasGun, bulletAvailable, bulletX, bulletY, bulletAngle, bulletActive

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

            # later: check ghost hit here
    
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        firstPersonMode = not firstPersonMode

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
    global lookBackAngleOffset, isLookBack, bulletX, bulletY, bulletAngle, bulletActive
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

    glutPostRedisplay()

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
        if (-980 < playerX < -320 and 280 < playerY < 840):
            draw_text(10, 770, f"Clue to Get a Candle: 2+5*3")
            draw_text(10, 750, f"Red:17")
            draw_text(10, 730, f"Green:21")
            draw_text(10, 710, f"Blue:11")
            draw_text(10, 690, f"Yellow:31")
        elif(-320< playerX <320 and 280< playerY <840):
            draw_text(10, 770, f"Clue to Get a Lemon:2+3*?=11")
            draw_text(10, 750, f"Red:6")
            draw_text(10, 730, f"Green:9")
            draw_text(10, 710, f"Blue:3")
            draw_text(10, 690, f"Purple:1")
        elif(-980 < playerX <-320 and -1120< playerY<-280):
            draw_text(10, 770, f"Clue to Get a Matches: (3+2)/(2*4)*6")
            draw_text(10, 750, f"Orange:3")
            draw_text(10, 730, f"Green:4.5")
            draw_text(10, 710, f"Blue:3.75")
            draw_text(10, 690, f"Yellow:7.35")
        elif(-320< playerX <320 and -1120< playerY <-280):
            draw_text(10, 770, f"Clue to Get a Rope:3^2+9*2^5")
            draw_text(10, 750, f"Purple:729")
            draw_text(10, 730, f"Cyan:217")
            draw_text(10, 710, f"Orange:297")
            draw_text(10, 690, f"Blue:432")
        elif(320< playerX <980 and -1120< playerY <-280):
            draw_text(10, 770, f"Clue to Get a Doll: 9^2-3^2-2*7")
            draw_text(10, 750, f"Red:98")
            draw_text(10, 730, f"Green:121")
            draw_text(10, 710, f"Blue:111")
            draw_text(10, 690, f"Yellow:58")
    else:
        if (-980 < playerX < -320 and 280 < playerY < 840):
            draw_text(10, 770, f"Clue to Get a Knife: x^2+3x+2=0 the value of x is?")
            draw_text(10, 750, f"Red:(-1,-2)")
            draw_text(10, 730, f"Green:(1,2)")
            draw_text(10, 710, f"Blue:(1,-2)")
            draw_text(10, 690, f"Yellow:(-1,2)")
        elif(320< playerX <980 and 280< playerY<840):
            draw_text(10, 770, f"Clue to Get a wood: 3x+3=9 the value of x is?")
            draw_text(10, 750, f"Red:1")
            draw_text(10, 730, f"Green:2")
            draw_text(10, 710, f"Blue:3")
            draw_text(10, 690, f"Yellow:4")
        elif(-980< playerX <200 and -1120< playerY <-280):
            draw_text(10, 770, f"Clue to Get a Surprise: (x/2)+(x/3)=10 the value of x is?")
            draw_text(10, 750, f"Red:10")
            draw_text(10, 730, f"Green:11")
            draw_text(10, 710, f"Blue:31")
            draw_text(10, 690, f"Purple:34")
            draw_text(10, 670, f"Cyan:20")
            draw_text(10, 650, f"Orange:14")
            draw_text(10, 630, f"Indigo:12")
        elif(200< playerX <980 and -1120< playerY <-280):
            draw_text(10, 770, f"Clue to Get a wood:x^2-9=0 the value of x is?")
            draw_text(10, 750, f"Red:+3")
            draw_text(10, 730, f"Green:-3")
            draw_text(10, 710, f"Blue:+3 or -3")
            draw_text(10, 690, f"Yellow:+3 and -3")

health=100
collection=[]
candlePicked=False
lemonPicked=False
lighterPicked=False
ropePicked=False
dollPicked=False
redPicked=False
woodPicked=False

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
        elif -410 < playerX < -330 and 750 < playerY < 830:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
        elif -690 < playerX < -610 and 750 < playerY < 830:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")

        # 1B
        elif -310 < playerX < -230 and 750 < playerY < 830:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
        elif -30 < playerX < 50 and 750 < playerY < 830:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
        elif 230 < playerX < 310 and 750 < playerY < 830:
            draw_text(300,770,"Blue Box:Correct Answer--> Picked a Lemon")
            lemonPicked=True
            storeCollection()
        elif -30 < playerX < 50 and 290 < playerY < 370:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")

        # 1D
        elif -970 < playerX < -890 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
        elif -970 < playerX < -890 and -580 < playerY < -500:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
        elif -410 < playerX < -330 and -1090 < playerY < -1010:
            draw_text(300,770,"Blue Box: Correct Answer--> Picked Lighter")
            lighterPicked=True
            storeCollection()
        elif -690 < playerX < -610 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")

        # 1E
        elif -310 < playerX < -230 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
        elif -40 < playerX < 40 and -370 < playerY < -290:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
        elif 230 < playerX < 310 and -1090 < playerY < -1010:
            draw_text(300,770,"Orange Box: Correct Answer--> Picked Rope")
            ropePicked=True
            storeCollection()
        elif -40 < playerX < 40 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")

        # 1F
        elif 330 < playerX < 410 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
        elif 610 < playerX < 690 and -360 < playerY < -280:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
        elif 460 < playerX < 540 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
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
        elif -410 < playerX < -330 and 750 < playerY < 830:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
        elif -690 < playerX < -610 and 750 < playerY < 830:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")

        # 2C
        elif 330 < playerX < 410 and 750 < playerY < 830:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
        elif 610 < playerX < 690 and 750 < playerY < 830:
            draw_text(300,770,"Green Box: Correct Answer-->Hint: You have to Collect solve all the room Clue")
        elif 730 < playerX < 810 and 280 < playerY < 360:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
        elif 890 < playerX < 970 and 750 < playerY < 830:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")

        # Ritual Room
        elif -970 < playerX < -890 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")

        elif -970 < playerX < -890 and -580 < playerY < -500:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")

        elif -410 < playerX < -330 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")

        elif -690 < playerX < -610 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")

        elif -310 < playerX < -230 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")

        elif -40 < playerX < 40 and -370 < playerY < -290:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")

        elif 230 < playerX < 310 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")

        elif -40 < playerX < 40 and -1090 < playerY < -1010:
            draw_text(300,770,"Indigo Box: Correct Answer--> Health Full")

        # 2E
        elif 330 < playerX < 410 and -1090 < playerY < -1010:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
        elif 610 < playerX < 690 and -360 < playerY < -280:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")
        elif 460 < playerX < 540 and -1090 < playerY < -1010:
            draw_text(300,770,"Blue Box: Correct Answer-->Picked Wood")
            woodPicked=True
            storeCollection()
        elif 890 < playerX < 970 and -360 < playerY < -280:
            draw_text(300,770,f"You have Chosen a Wrong Answer your Helath will be decreased")

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

ritualItem = ["Candle","Lemon","Lighter","Doll","Rope","Wood","Red Powder"]
ritualFlag = False

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

def showScreen():
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
    drawBullet()
    clue()
    correctBoxDetection()

    if canPickGun and not hasGun:
        draw_text(10, 600, "Press E to pick gun But But But you have only 1 bullet, use it wisely!")

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1400, 1000)
    glutInitWindowPosition(50,50)
    wind = glutCreateWindow(b"3D OpenGL Intro")


    spawnGun()

    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()