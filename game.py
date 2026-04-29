from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time


# -----------------------------
# Camera
# -----------------------------
fovY = 70

camera_pos = [0.0, 0.0, 95.0]
camera_angle = 0.0

move_speed = 22.0
turn_speed = 5.0


# -----------------------------
# Map settings
# -----------------------------
WALL_H = 240.0

room_slots = {
    "TL": (-600, -100, 300, 600),
    "ML": (-600, -100, -50, 220),
    "BL": (-600, -100, -600, -160),

    "TR": (100, 600, 300, 600),
    "MR": (100, 600, -50, 220),
    "BR": (100, 600, -600, -160),
}

corridors = {
    "MAIN HALL": (-100, 100, -600, 600),
    "NORTH CONNECTOR L": (-600, -100, 220, 300),
    "WEST CORRIDOR": (-600, -100, -160, -50),
    "NORTH CONNECTOR R": (100, 600, 220, 300),
    "EAST CORRIDOR": (100, 600, -160, -50),
}

# Darker scary colors
room_colors = {
    "CRYPT": (0.22, 0.02, 0.02),
    "ENTRY HALL": (0.07, 0.10, 0.12),
    "SAFE ROOM": (0.00, 0.22, 0.16),
    "BLOOD ROOM": (0.28, 0.04, 0.02),
    "LIBRARY": (0.20, 0.10, 0.02),
    "STOREROOM": (0.08, 0.08, 0.08),
}

room_codes = {
    "CRYPT": "Room 1A",
    "ENTRY HALL": "Room 1B",
    "SAFE ROOM": "Room 1C",
    "BLOOD ROOM": "Room 1D",
    "LIBRARY": "Room 1E",
    "STOREROOM": "Room 1F",
}

slot_room = {}

wall_segments = []
door_markers = []


# -----------------------------
# Text
# -----------------------------
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()

    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x, y)

    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    glPopMatrix()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()

    glMatrixMode(GL_MODELVIEW)


# -----------------------------
# Color helpers
# -----------------------------
def clamp(v):
    if v < 0:
        return 0
    if v > 1:
        return 1
    return v


def scary_color(color, factor):
    r = clamp(color[0] * factor)
    g = clamp(color[1] * factor)
    b = clamp(color[2] * factor)

    return (r, g, b)


def flicker_value(room_name):
    t = time.time()

    if room_name == "CRYPT":
        return 0.08 * math.sin(t * 7.0)

    elif room_name == "BLOOD ROOM":
        return 0.10 * math.sin(t * 9.0)

    elif room_name == "SAFE ROOM":
        return 0.07 * math.sin(t * 3.0)

    elif room_name == "LIBRARY":
        return 0.04 * math.sin(t * 5.0)

    elif room_name == "STOREROOM":
        return 0.04 * math.sin(t * 6.0)

    return 0.03 * math.sin(t * 4.0)


# -----------------------------
# Basic drawing
# -----------------------------
def draw_floor_rect(x1, x2, y1, y2, color):
    glColor3f(color[0], color[1], color[2])

    glBegin(GL_QUADS)
    glVertex3f(x1, y1, 0)
    glVertex3f(x2, y1, 0)
    glVertex3f(x2, y2, 0)
    glVertex3f(x1, y2, 0)
    glEnd()


def draw_box(cx, cy, cz, sx, sy, sz, color):
    glPushMatrix()

    glColor3f(color[0], color[1], color[2])
    glTranslatef(cx, cy, cz)
    glScalef(sx, sy, sz)
    glutSolidCube(1)

    glPopMatrix()


def draw_cylinder_z(cx, cy, cz, r1, r2, h, color):
    glPushMatrix()

    glColor3f(color[0], color[1], color[2])
    glTranslatef(cx, cy, cz)
    gluCylinder(gluNewQuadric(), r1, r2, h, 12, 8)

    glPopMatrix()


def draw_sphere(cx, cy, cz, radius, color):
    glPushMatrix()

    glColor3f(color[0], color[1], color[2])
    glTranslatef(cx, cy, cz)
    gluSphere(gluNewQuadric(), radius, 12, 12)

    glPopMatrix()


def draw_h_wall(y, x1, x2):
    glColor3f(0.38, 0.38, 0.35)

    glBegin(GL_QUADS)
    glVertex3f(x1, y, 0)
    glVertex3f(x2, y, 0)
    glVertex3f(x2, y, WALL_H)
    glVertex3f(x1, y, WALL_H)
    glEnd()


def draw_v_wall(x, y1, y2):
    glColor3f(0.38, 0.38, 0.35)

    glBegin(GL_QUADS)
    glVertex3f(x, y1, 0)
    glVertex3f(x, y2, 0)
    glVertex3f(x, y2, WALL_H)
    glVertex3f(x, y1, WALL_H)
    glEnd()


# -----------------------------
# Wall and door creation
# -----------------------------
def add_h_wall(y, x1, x2, doors):
    global wall_segments, door_markers

    doors.sort()
    now = x1

    for d1, d2 in doors:
        if d1 > now:
            wall_segments.append(("h", y, now, d1))

        door_markers.append(("h", y, d1, d2))
        now = d2

    if now < x2:
        wall_segments.append(("h", y, now, x2))


def add_v_wall(x, y1, y2, doors):
    global wall_segments, door_markers

    doors.sort()
    now = y1

    for d1, d2 in doors:
        if d1 > now:
            wall_segments.append(("v", x, now, d1))

        door_markers.append(("v", x, d1, d2))
        now = d2

    if now < y2:
        wall_segments.append(("v", x, now, y2))


def build_walls():
    global wall_segments, door_markers

    wall_segments = []
    door_markers = []

    # Outer boundary
    add_h_wall(600, -600, 600, [])
    add_h_wall(-600, -600, 600, [])
    add_v_wall(-600, -600, 600, [])
    add_v_wall(600, -600, 600, [])

    # Main hall left boundary
    add_v_wall(-100, -600, 600, [
        (-470, -370),
        (-130, -80),
        (240, 280),
        (430, 510),
    ])

    # Main hall right boundary
    add_v_wall(100, -600, 600, [
        (-130, -80),
        (30, 110),
        (240, 280),
        (430, 510),
    ])

    # Left internal walls
    add_h_wall(300, -600, -100, [
        (-540, -460),
    ])

    add_h_wall(220, -600, -100, [
        (-360, -280),
    ])

    add_h_wall(-50, -600, -100, [
        (-360, -280),
    ])

    add_h_wall(-160, -600, -100, [
        (-360, -280),
    ])

    # Right internal walls
    add_h_wall(300, 100, 600, [
        (460, 540),
    ])

    add_h_wall(220, 100, 600, [
        (360, 440),
    ])

    add_h_wall(-50, 100, 600, [
        (360, 440),
    ])

    add_h_wall(-160, 100, 600, [
        (360, 440),
    ])


def draw_all_walls():
    for w in wall_segments:
        if w[0] == "h":
            draw_h_wall(w[1], w[2], w[3])
        else:
            draw_v_wall(w[1], w[2], w[3])


def draw_all_doors():
    for d in door_markers:
        glColor3f(1.0, 0.62, 0.0)

        if d[0] == "h":
            y = d[1]
            x1 = d[2]
            x2 = d[3]

            glBegin(GL_QUADS)
            glVertex3f(x1, y - 10, 2)
            glVertex3f(x2, y - 10, 2)
            glVertex3f(x2, y + 10, 2)
            glVertex3f(x1, y + 10, 2)
            glEnd()

        else:
            x = d[1]
            y1 = d[2]
            y2 = d[3]

            glBegin(GL_QUADS)
            glVertex3f(x - 10, y1, 2)
            glVertex3f(x + 10, y1, 2)
            glVertex3f(x + 10, y2, 2)
            glVertex3f(x - 10, y2, 2)
            glEnd()


# -----------------------------
# Random room system
# -----------------------------
def randomize_rooms():
    global slot_room, camera_pos, camera_angle

    slot_room = {}

    # Safe room always fixed
    slot_room["TR"] = "SAFE ROOM"

    moving_slots = ["TL", "ML", "MR", "BL", "BR"]

    moving_rooms = [
        "CRYPT",
        "ENTRY HALL",
        "BLOOD ROOM",
        "LIBRARY",
        "STOREROOM",
    ]

    random.shuffle(moving_rooms)

    for i in range(len(moving_slots)):
        slot_room[moving_slots[i]] = moving_rooms[i]

    # Camera spawns inside Entry Hall wherever Entry Hall is placed
    for slot in slot_room:
        if slot_room[slot] == "ENTRY HALL":
            x1, x2, y1, y2 = room_slots[slot]

            camera_pos[0] = (x1 + x2) / 2
            camera_pos[1] = (y1 + y2) / 2
            camera_pos[2] = 95.0

            if camera_pos[0] < 0:
                camera_angle = 0.0
            else:
                camera_angle = 180.0

            break


# -----------------------------
# Place detection
# -----------------------------
def point_inside_rect(px, py, rect):
    x1, x2, y1, y2 = rect

    if x1 <= px <= x2 and y1 <= py <= y2:
        return True

    return False


def get_current_room_type():
    for slot in slot_room:
        room_name = slot_room[slot]

        if point_inside_rect(camera_pos[0], camera_pos[1], room_slots[slot]):
            return room_name

    return None


def get_current_corridor():
    for c in corridors:
        if point_inside_rect(camera_pos[0], camera_pos[1], corridors[c]):
            return c

    return None


def get_current_place():
    room_name = get_current_room_type()

    if room_name != None:
        return room_name + " - " + room_codes[room_name]

    corridor_name = get_current_corridor()

    if corridor_name != None:
        return corridor_name

    return "Outside"


def get_room_slot(room_name):
    for slot in slot_room:
        if slot_room[slot] == room_name:
            return slot

    return "?"


# -----------------------------
# Props
# -----------------------------
def draw_hide_blocks_in_room(room_name, x1, x2, y1, y2, light_factor):
    block_color = scary_color((0.02, 0.02, 0.02), light_factor + 0.25)

    if room_name == "CRYPT":
        draw_box(x1 + 70, y2 - 70, 25, 45, 45, 50, block_color)
        draw_box(x1 + 130, y2 - 70, 25, 45, 45, 50, block_color)

    elif room_name == "ENTRY HALL":
        draw_box(x1 + 85, y1 + 95, 25, 45, 45, 50, block_color)

    elif room_name == "SAFE ROOM":
        draw_box(x1 + 70, y2 - 70, 25, 45, 45, 50, block_color)
        draw_box(x1 + 130, y2 - 70, 25, 45, 45, 50, block_color)

    elif room_name == "BLOOD ROOM":
        draw_box(x1 + 70, y2 - 70, 25, 45, 45, 50, block_color)
        draw_box(x1 + 130, y2 - 70, 25, 45, 45, 50, block_color)

    elif room_name == "LIBRARY":
        draw_box(x1 + 70, y2 - 70, 25, 45, 45, 50, block_color)
        draw_box(x1 + 130, y2 - 70, 25, 45, 45, 50, block_color)

    elif room_name == "STOREROOM":
        draw_box(x1 + 85, y2 - 90, 25, 45, 45, 50, block_color)


def draw_stairs_in_room(x1, x2, y1, y2, light_factor):
    stair_color = scary_color((0.70, 0.70, 0.62), light_factor)

    sx = x2 - 115
    sy = y1 + 95

    draw_box(sx - 35, sy + 45, 15, 8, 130, 30, stair_color)
    draw_box(sx + 35, sy + 45, 15, 8, 130, 30, stair_color)

    for i in range(6):
        draw_box(sx, sy + i * 22, 18, 85, 7, 20, stair_color)


def draw_crypt_props(x1, x2, y1, y2, light_factor):
    coffin_color = scary_color((0.10, 0.05, 0.02), light_factor)
    pillar_color = scary_color((0.20, 0.20, 0.18), light_factor)

    draw_box((x1 + x2) / 2 - 90, (y1 + y2) / 2, 20, 70, 160, 40, coffin_color)
    draw_box((x1 + x2) / 2 + 90, (y1 + y2) / 2, 20, 70, 160, 40, coffin_color)

    draw_cylinder_z(x1 + 70, y1 + 70, 0, 22, 18, 120, pillar_color)
    draw_cylinder_z(x2 - 70, y1 + 70, 0, 22, 18, 120, pillar_color)


def draw_entry_props(x1, x2, y1, y2, light_factor):
    base_color = scary_color((0.18, 0.18, 0.16), light_factor)
    top_color = scary_color((0.32, 0.30, 0.25), light_factor)

    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    draw_box(cx, cy, 15, 85, 85, 30, base_color)
    draw_cylinder_z(cx, cy, 30, 30, 22, 55, top_color)


def draw_safe_room_props(x1, x2, y1, y2, light_factor):
    ring_color = scary_color((0.10, 0.70, 0.50), light_factor + 0.3)

    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    for i in range(5):
        ang = math.radians(90 + i * 72)
        px = cx + math.cos(ang) * 95
        py = cy + math.sin(ang) * 95

        draw_box(px, py, 5, 28, 28, 10, ring_color)

    draw_sphere(cx, cy, 35, 25, scary_color((0.05, 0.50, 0.35), light_factor + 0.2))


def draw_blood_room_props(x1, x2, y1, y2, light_factor):
    broken_color = scary_color((0.08, 0.02, 0.02), light_factor)
    dark_red = scary_color((0.25, 0.00, 0.00), light_factor + 0.1)

    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    draw_box(cx - 90, cy + 30, 15, 85, 45, 30, broken_color)
    draw_box(cx + 65, cy - 55, 15, 60, 90, 30, broken_color)
    draw_box(cx + 130, cy + 80, 15, 45, 45, 30, broken_color)

    draw_floor_rect(cx - 90, cx + 110, cy - 35, cy + 35, dark_red)


def draw_library_props(x1, x2, y1, y2, light_factor):
    shelf_color = scary_color((0.12, 0.06, 0.01), light_factor)
    book_color = scary_color((0.22, 0.18, 0.08), light_factor)

    # bookshelves along left side
    draw_box(x1 + 55, y1 + 120, 70, 45, 170, 140, shelf_color)
    draw_box(x1 + 55, y2 - 120, 70, 45, 170, 140, shelf_color)

    # bookshelves along right side but not blocking door too much
    draw_box(x2 - 55, y1 + 140, 70, 45, 130, 140, shelf_color)
    draw_box(x2 - 55, y2 - 140, 70, 45, 130, 140, shelf_color)

    # low table
    draw_box((x1 + x2) / 2, (y1 + y2) / 2, 20, 120, 55, 40, book_color)


def draw_storeroom_props(x1, x2, y1, y2, light_factor):
    crate_color = scary_color((0.16, 0.10, 0.05), light_factor)

    draw_box(x1 + 80, y1 + 110, 30, 60, 60, 60, crate_color)
    draw_box(x1 + 145, y1 + 110, 30, 60, 60, 60, crate_color)
    draw_box(x1 + 110, y1 + 175, 30, 60, 60, 60, crate_color)

    draw_box(x2 - 200, y2 - 100, 30, 70, 70, 60, crate_color)
    draw_box(x2 - 135, y2 - 100, 30, 70, 70, 60, crate_color)


def draw_room_props(room_name, x1, x2, y1, y2, light_factor):
    draw_hide_blocks_in_room(room_name, x1, x2, y1, y2, light_factor)

    if room_name == "CRYPT":
        draw_crypt_props(x1, x2, y1, y2, light_factor)

    elif room_name == "ENTRY HALL":
        draw_entry_props(x1, x2, y1, y2, light_factor)

    elif room_name == "SAFE ROOM":
        draw_safe_room_props(x1, x2, y1, y2, light_factor)

    elif room_name == "BLOOD ROOM":
        draw_blood_room_props(x1, x2, y1, y2, light_factor)

    elif room_name == "LIBRARY":
        draw_library_props(x1, x2, y1, y2, light_factor)

    elif room_name == "STOREROOM":
        draw_storeroom_props(x1, x2, y1, y2, light_factor)
        draw_stairs_in_room(x1, x2, y1, y2, light_factor)


# -----------------------------
# Draw full floor
# -----------------------------
def draw_rooms():
    current_room = get_current_room_type()
    current_corridor = get_current_corridor()

    # Main hall and corridors with fake darkness
    for c in corridors:
        x1, x2, y1, y2 = corridors[c]

        if current_corridor == c:
            factor = 0.85
        else:
            factor = 0.25

        base = (0.10, 0.10, 0.10)

        if c == "MAIN HALL":
            base = (0.08, 0.08, 0.08)

        draw_floor_rect(x1, x2, y1, y2, scary_color(base, factor))

    # Rooms
    for slot in slot_room:
        room_name = slot_room[slot]
        x1, x2, y1, y2 = room_slots[slot]

        if current_room == room_name:
            factor = 1.00
        else:
            factor = 0.28

        fl = flicker_value(room_name)

        color = room_colors[room_name]
        color = (
            clamp(color[0] + fl),
            clamp(color[1] + fl * 0.35),
            clamp(color[2] + fl * 0.25),
        )

        final_color = scary_color(color, factor)

        draw_floor_rect(x1, x2, y1, y2, final_color)

        draw_room_props(room_name, x1, x2, y1, y2, factor)


# -----------------------------
# Movement and collision
# -----------------------------
def is_inside_floor(px, py):
    for slot in room_slots:
        if point_inside_rect(px, py, room_slots[slot]):
            return True

    for c in corridors:
        if point_inside_rect(px, py, corridors[c]):
            return True

    return False


def line_crosses_wall(x0, y0, x1, y1):
    for w in wall_segments:

        if w[0] == "v":
            wx = w[1]
            wy1 = w[2]
            wy2 = w[3]

            if x1 != x0:
                if (x0 - wx) * (x1 - wx) <= 0:
                    t = (wx - x0) / (x1 - x0)

                    if 0 <= t <= 1:
                        cy = y0 + t * (y1 - y0)

                        if wy1 <= cy <= wy2:
                            return True

        elif w[0] == "h":
            wy = w[1]
            wx1 = w[2]
            wx2 = w[3]

            if y1 != y0:
                if (y0 - wy) * (y1 - wy) <= 0:
                    t = (wy - y0) / (y1 - y0)

                    if 0 <= t <= 1:
                        cx = x0 + t * (x1 - x0)

                        if wx1 <= cx <= wx2:
                            return True

    return False


def move_camera(amount):
    global camera_pos

    rad = math.radians(camera_angle)

    new_x = camera_pos[0] + math.cos(rad) * amount
    new_y = camera_pos[1] + math.sin(rad) * amount

    if is_inside_floor(new_x, new_y) == False:
        return

    if line_crosses_wall(camera_pos[0], camera_pos[1], new_x, new_y) == True:
        return

    camera_pos[0] = new_x
    camera_pos[1] = new_y


# -----------------------------
# Controls
# -----------------------------
def keyboardListener(key, x, y):
    try:
        k = key.decode("utf-8").lower()
    except:
        return

    if k == "r":
        randomize_rooms()

    glutPostRedisplay()


def specialKeyListener(key, x, y):
    global camera_angle

    if key == GLUT_KEY_UP:
        move_camera(move_speed)

    elif key == GLUT_KEY_DOWN:
        move_camera(-move_speed)

    elif key == GLUT_KEY_LEFT:
        camera_angle += turn_speed

    elif key == GLUT_KEY_RIGHT:
        camera_angle -= turn_speed

    glutPostRedisplay()


def mouseListener(button, state, x, y):
    pass


# -----------------------------
# Camera
# -----------------------------
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(fovY, 1.25, 0.1, 2500)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    x = camera_pos[0]
    y = camera_pos[1]
    z = camera_pos[2]

    rad = math.radians(camera_angle)

    look_x = x + math.cos(rad) * 200
    look_y = y + math.sin(rad) * 200
    look_z = z - 25

    gluLookAt(
        x, y, z,
        look_x, look_y, look_z,
        0, 0, 1
    )


# -----------------------------
# Screen
# -----------------------------
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glViewport(0, 0, 1000, 800)

    setupCamera()

    draw_rooms()
    draw_all_doors()
    draw_all_walls()

    glClear(GL_DEPTH_BUFFER_BIT)

    draw_text(20, 765, "FIRST FLOOR WALK MODE - SCARY VISUAL TEST")
    draw_text(20, 735, "UP/DOWN = move    LEFT/RIGHT = turn    R = restart / randomize rooms")
    draw_text(20, 705, "Current Place: " + get_current_place())
    draw_text(20, 675, "Entry Hall Slot: " + get_room_slot("ENTRY HALL") + "     Storeroom Slot: " + get_room_slot("STOREROOM"))
    draw_text(20, 645, "Visuals: dark rooms, tall walls, flicker, props, room-based darkness")

    glutSwapBuffers()


def idle():
    glutPostRedisplay()


# -----------------------------
# Main
# -----------------------------
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)

    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)

    glutCreateWindow(b"First Floor Scary Layout")

    glEnable(GL_DEPTH_TEST)

    build_walls()
    randomize_rooms()

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()