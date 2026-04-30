from math import cos, degrees, radians, sin
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18

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


def drawPlayer():
    
    glPushMatrix()
    glTranslatef(playerX, playerY, 0)
    glRotatef(playerAngle, 0, 0, 1)

    # Head
    glColor3f(0, 0, 0)
    glTranslatef(0, 0, 117) 
    gluSphere(gluNewQuadric(), 20, 20, 20)
    glTranslatef(0, 0, -117) 

    # Body
    glColor3f(0.3, 0.25, 0.21)
    glTranslatef(0, 0, 40)  
    glutSolidCube(40)
    glTranslatef(0, 0, -40)  
    glTranslatef(0, 0, 80) 
    glutSolidCube(40)
    glTranslatef(0, 0, -80)

    # Arms
    glColor3f(0.8, 0.67, 0.6)
    glTranslatef(20, 15, 90)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 10, 5, 40, 30, 30)
    glTranslatef(-20, -15, -90)
    glTranslatef(20, -15, 90)
    gluCylinder(gluNewQuadric(), 10, 5, 40, 30, 30)
    glTranslatef(-20, 15, -90)

    # Gun
    glColor3f(0.78, 0.78, 0.78)
    glTranslatef(20, 0, 90)
    gluCylinder(gluNewQuadric(), 10, 2, 55, 30, 30)
    glRotatef(-90, 0, 1, 0)
    glTranslatef(-20, 0, -90)

    # Legs
    glColor3f(0.6, 0.53, 0.47)
    glTranslatef(0, 15, 0)
    gluCylinder(gluNewQuadric(), 10, 10, 50, 30, 30)
    glTranslatef(0, -15, 0)
    glTranslatef(0, -15, 0)
    gluCylinder(gluNewQuadric(), 10, 10, 50, 30, 30)
    glTranslatef(0, 15, 0)
    glPopMatrix()

def keyboardListener(key, x, y):
    global playerX, playerY, playerAngle, gameOver, firstPersonMode, currentFloor

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
    pass

def mouseListener(button, state, x, y):
    global firstPersonMode

    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        firstPersonMode = not firstPersonMode

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if firstPersonMode:        
        gluLookAt(  playerX + 20 * cos(radians(playerAngle)), playerY + 20* sin(radians(playerAngle)), 120,
                    playerX + 100* cos(radians(playerAngle)), playerY + 100* sin(radians(playerAngle)), 120,
                    0, 0, 1)
    else:
        camX = playerX - 120 * cos(radians(playerAngle))
        camY = playerY - 120 * sin(radians(playerAngle))

        gluLookAt(
            camX, camY, 150,
            playerX, playerY, 80,
            0, 0, 1
        )

def idle():
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

    # walls (leave space for doors)
    drawWall(-490*arenaScale, y_top, -300*arenaScale, y_top)
    drawWall(-100*arenaScale, y_top, 100*arenaScale, y_top)
    drawWall(300*arenaScale, y_top, 490*arenaScale, y_top)

    drawWall(-490*arenaScale, y_bottom, -300*arenaScale, y_bottom)
    drawWall(-100*arenaScale, y_bottom, 100*arenaScale, y_bottom)
    drawWall(300*arenaScale, y_bottom, 490*arenaScale, y_bottom)

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
    drawWall(-490*arenaScale, 140*arenaScale, -300*arenaScale, 140*arenaScale)
    drawWall(-100*arenaScale, 140*arenaScale, 100*arenaScale, 140*arenaScale)
    drawWall(300*arenaScale, 140*arenaScale, 490*arenaScale, 140*arenaScale)

    drawWall(-490*arenaScale, -140*arenaScale, -300*arenaScale, -140*arenaScale)
    drawWall(-100*arenaScale, -140*arenaScale, 100*arenaScale, -140*arenaScale)
    drawWall(300*arenaScale, -140*arenaScale, 490*arenaScale, -140*arenaScale)

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

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glLoadIdentity()
    glViewport(0, 0, 1000, 1000)
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

    elif currentFloor == 2:
        drawSecondFloor()
        drawTeleportPad()
        drawCeiling()

    drawPlayer()
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 1000)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"3D OpenGL Intro")

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()