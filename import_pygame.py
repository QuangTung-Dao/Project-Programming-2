import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 1000, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solar System Simulation")

# Colors
BLACK        = (  0,   0,   0)
BLUE         = (100, 149, 237)
CYAN         = (  0, 255, 255)
DARK_GREY    = (140, 135, 130)
DARK_SAND    = (210, 160, 100)
DEEP_BLUE    = ( 63,  84, 186)
GOLD         = (255, 215,   0)
GOLDEN_BROWN = (200, 165,  75)
LIGHT_BLUE   = (173, 216, 230)
RED          = (188,  39,  50)
SUN_CORE     = (255, 250, 180)
SUN_GLOW     = (255, 140,   0)
SUN_MID      = (255, 200,  60)
TAN          = (215, 195, 140)
WHITE        = (255, 255, 255)
YELLOW       = (255, 220,  50)

FONT_SMALL  = pygame.font.SysFont("consolas", 13)
FONT_MED    = pygame.font.SysFont("consolas", 15, bold=True)
FONT_TITLE  = pygame.font.SysFont("consolas", 24, bold=True)

AU          = 149.6e6 * 1000
G           = 6.67428e-11
TIMESTEP    = 3600 * 24
BASE_SCALE  = 14.5 / AU       # zoom=1 shows all 8 planets


# ── Camera ───────────────────────────────────────────────────────────────────
class Camera:
    def __init__(self):
        self.zoom      = 1.0
        self.pan_x     = WIDTH  / 2
        self.pan_y     = HEIGHT / 2
        self.dragging  = False
        self.drag_st   = (0, 0)
        self.pan_st    = (0, 0)

    def w2s(self, wx, wy):
        return (int(wx * BASE_SCALE * self.zoom + self.pan_x),
                int(wy * BASE_SCALE * self.zoom + self.pan_y))

    def zoom_at(self, mx, my, factor):
        wx = (mx - self.pan_x) / (BASE_SCALE * self.zoom)
        wy = (my - self.pan_y) / (BASE_SCALE * self.zoom)
        self.zoom  = max(0.25, min(80.0, self.zoom * factor))
        self.pan_x = mx - wx * BASE_SCALE * self.zoom
        self.pan_y = my - wy * BASE_SCALE * self.zoom

    def reset(self):
        self.zoom  = 1.0
        self.pan_x = WIDTH  / 2
        self.pan_y = HEIGHT / 2

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button in (2, 3):
            self.dragging = True
            self.drag_st  = event.pos
            self.pan_st   = (self.pan_x, self.pan_y)
        elif event.type == pygame.MOUSEBUTTONUP and event.button in (2, 3):
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            dx = event.pos[0] - self.drag_st[0]
            dy = event.pos[1] - self.drag_st[1]
            self.pan_x = self.pan_st[0] + dx
            self.pan_y = self.pan_st[1] + dy
        elif event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if mx > 230:
                self.zoom_at(mx, my, 1.12 if event.y > 0 else 1/1.12)


# ── Stars ─────────────────────────────────────────────────────────────────────
HUE_MAP = {
    "white":  (255, 255, 255),
    "blue":   (180, 205, 255),
    "orange": (255, 200, 140),
    "red":    (255, 160, 140),
    "yellow": (255, 240, 160),
}

def make_stars():
    stars = []
    for _ in range(1000):
        x   = random.uniform(230, WIDTH)
        y   = random.uniform(0, HEIGHT)
        sz  = random.choices([1, 1, 2, 3], weights=[60, 20, 15, 5])[0]
        bb  = random.randint(110, 255)
        sp  = random.uniform(0.006, 0.055)
        of  = random.uniform(0, math.pi * 2)
        hue = random.choices(
            ["white","white","white","blue","orange","red","yellow"],
            weights=[50, 15, 10, 10, 7, 5, 3]
        )[0]
        stars.append([x, y, sz, bb, sp, of, hue])
    return stars

def draw_stars(win, stars, tick):
    for (x, y, sz, bb, sp, of, hue) in stars:
        t   = 0.55 + 0.45 * math.sin(tick * sp + of)
        b   = max(30, min(255, int(bb * t)))
        tr, tg, tb = HUE_MAP[hue]
        col = (b * tr // 255, b * tg // 255, b * tb // 255)
        ix, iy = int(x), int(y)
        if sz == 1:
            win.set_at((ix, iy), col)
        elif sz == 2:
            pygame.draw.circle(win, col, (ix, iy), 1)
        else:
            pygame.draw.circle(win, col, (ix, iy), 2)
            if b > 170:
                pygame.draw.line(win, col, (ix-4, iy), (ix+4, iy), 1)
                pygame.draw.line(win, col, (ix, iy-4), (ix, iy+4), 1)


# ── Glow ──────────────────────────────────────────────────────────────────────
def draw_glow(win, color, pos, radius, layers=5, max_alpha=60):
    for i in range(layers, 0, -1):
        r = int(radius * (1 + 0.55 * i / layers))
        a = int(max_alpha * (i / layers) ** 2)
        s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, a), (r, r), r)
        win.blit(s, (pos[0]-r, pos[1]-r))


# ── Planet ────────────────────────────────────────────────────────────────────
class Planet:
    def __init__(self, x, y, vis_r, color, mass, name,
                 has_rings=False, ring_color=None,
                 has_atm=False, atm_color=None):
        self.x         = x
        self.y         = y
        self.vis_r     = vis_r
        self.color     = color
        self.mass      = mass
        self.name      = name
        self.has_rings = has_rings
        self.ring_color= ring_color or (200, 180, 140)
        self.has_atm   = has_atm
        self.atm_color = atm_color  or (100, 180, 255)
        self.orbit     = []
        self.sun       = False
        self.dist_sun  = 0
        self.x_vel     = 0.0
        self.y_vel     = 0.0
        self.speed     = 0.0
        self.days      = 0
        self.time_elapsed_seconds = 0

    def screen_r(self, cam):
        return max(3, int(self.vis_r * min(cam.zoom, 5) ** 0.45))

    def draw_orbit(self, win, cam):
        if len(self.orbit) < 2:
            return
        pts = [cam.w2s(ox, oy) for ox, oy in self.orbit]
        n   = len(pts)
        r, g, b = self.color
        grey = (r+g+b)//3
        cr   = (r*2 + grey)//3
        cg   = (g*2 + grey)//3
        cb   = (b*2 + grey)//3
        for i in range(1, n):
            frac = i / n
            if frac < 0.1:
                continue
            try:
                pygame.draw.line(win, (min(cr,210), min(cg,210), min(cb,210)),
                                 pts[i-1], pts[i], 1)
            except Exception:
                pass

    def draw(self, win, cam, show_labels, selected):
        sx, sy = cam.w2s(self.x, self.y)
        r = self.screen_r(cam)

        if self.has_atm:
            draw_glow(win, self.atm_color, (sx, sy), r, layers=4, max_alpha=50)

        if self.has_rings:
            rw = int(r * 2.8)
            rh = int(r * 0.95)
            rs = pygame.Surface((rw*2, rh*2), pygame.SRCALPHA)
            cr, cg, cb = self.ring_color
            for off in range(rw, int(r*1.25), -1):
                frac = (off - r*1.25) / max(1, rw - r*1.25)
                a    = int(150 * frac)
                pygame.draw.ellipse(rs, (cr, cg, cb, a),
                                    (rw-off, rh-off//3, off*2, off*2//3), 2)
            win.blit(rs, (sx - rw, sy - rh))

        pygame.draw.circle(win, self.color, (sx, sy), r)
        hl = tuple(min(255, c+65) for c in self.color)
        pygame.draw.circle(win, hl, (sx - max(1, r//3), sy - max(1, r//3)),
                           max(1, r//4))

        if selected:
            pygame.draw.circle(win, CYAN, (sx, sy), r + 5, 2)

        if show_labels:
            ns = FONT_SMALL.render(self.name, True, WHITE)
            win.blit(ns, (sx - ns.get_width()//2, sy + r + 4))

    def draw_sun(self, win, cam, tick):
        sx, sy = cam.w2s(self.x, self.y)
        r = max(8, int(self.vis_r * min(cam.zoom, 5) ** 0.45))

        draw_glow(win, SUN_GLOW, (sx, sy), r, layers=7, max_alpha=50)
        pulse = 1.0 + 0.05 * math.sin(tick * 0.022)
        cr    = int(r * 1.3 * pulse)
        cs    = pygame.Surface((cr*2, cr*2), pygame.SRCALPHA)
        pygame.draw.circle(cs, (*SUN_GLOW, 40), (cr, cr), cr)
        win.blit(cs, (sx - cr, sy - cr))
        pygame.draw.circle(win, SUN_MID,  (sx, sy), r)
        pygame.draw.circle(win, SUN_CORE, (sx, sy), int(r * 0.65))

        ls = FONT_MED.render("Sun", True, GOLD)
        win.blit(ls, (sx - ls.get_width()//2, sy + r + 5))

    def update(self, planets):
        fx = fy = 0
        for p in planets:
            if p is self:
                continue
        
            # Tính lực hấp dẫn Newton: F = G*m1*m2 / r^2
            dx = p.x - self.x
            dy = p.y - self.y
            dist_sq = dx*dx + dy*dy
            dist = math.sqrt(dist_sq)
        
            if p.sun: self.dist_sun = dist
            
            force = G * self.mass * p.mass / dist_sq
            theta = math.atan2(dy, dx)
            fx += math.cos(theta) * force
            fy += math.sin(theta) * force
    
        # Cập nhật vận tốc và vị trí (Euler-Cromer)
        self.x_vel += fx / self.mass * TIMESTEP
        self.y_vel += fy / self.mass * TIMESTEP
        self.speed  = math.sqrt(self.x_vel**2 + self.y_vel**2)
        self.x += self.x_vel * TIMESTEP
        self.y += self.y_vel * TIMESTEP
    
        # Lưu quỹ đạo (giới hạn để tránh lag)
        # Quỹ đạo tuyệt đối
        self.orbit.append((self.x, self.y))
        if len(self.orbit) > 900: 
            self.orbit.pop(0)
    
        self.time_elapsed_seconds += TIMESTEP
        self.days = int(self.time_elapsed_seconds / 86400)

# ── SHOOTING STAR───────────────────────────────────────────────────────────────

class ShootingStar:
    def __init__(self):
        self.reset()

    def reset(self):
        # Xuất hiện ngẫu nhiên ở nửa trên/phải màn hình
        self.x = random.randint(WIDTH, WIDTH + 200)
        self.y = random.randint(-200, HEIGHT)
        # Vận tốc nhanh và chéo
        self.vx = random.uniform(-20, -10) 
        self.vy = random.uniform(7, 15)
        self.active = False
        self.timer = random.randint(100, 200) 
        # Độ dài vệt sáng (số phân đoạn đuôi)
        self.segments = 15 

    def update(self):
        if not self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.active = True
            return

        self.x += self.vx
        self.y += self.vy

        if self.x < -500 or self.y > HEIGHT + 500:
            self.reset()

    def draw(self, win):
        if not self.active: return
        
        # Vẽ đuôi mờ dần bằng cách lặp ngược từ cuối đuôi về đầu
        for i in range(self.segments):
            # Tỷ lệ mờ: đoạn càng xa đầu sao băng càng mờ (xem xét nên giảm tuyến tính hay hàm mũ)
            #alpha = int(255 * ((1 - i / self.segments) ** 2))
            alpha = int(255 * math.exp(-2 * i / self.segments))
            if alpha <= 0: continue
            
            # Tính toán vị trí đoạn đuôi thứ i
            # (Lùi lại theo hướng ngược với vận tốc)
            start_x = self.x - self.vx * (i * 0.8)
            start_y = self.y - self.vy * (i * 0.8)
            end_x = self.x - self.vx * ((i + 1) * 0.8)
            end_y = self.y - self.vy * ((i + 1) * 0.8)

            color = (180, 200, 255) # Màu xanh trắng nhạt
            
            # Để tối ưu, ta vẽ trực tiếp đường thẳng với độ dày giảm dần
            width = max(1, 3 - i // 5)
            # Giả lập mờ bằng cách trộn màu với nền đen (vì nền vũ trụ màu đen)
            faded_color = tuple(int(c * (alpha/255)) for c in color)
            
            pygame.draw.line(win, faded_color, (start_x, start_y), (end_x, end_y), width)

# ── UI ────────────────────────────────────────────────────────────────────────
SIDEBAR_ROW_H  = 24
SIDEBAR_ROW_Y0 = 55        # compact header → Mercury always visible

def sidebar_hit(my, n_planets, row_y0=SIDEBAR_ROW_Y0):
    """Return planet index if my falls on a sidebar row, else -1."""
    y = row_y0
    for i in range(n_planets):
        if y <= my < y + SIDEBAR_ROW_H:
            return i
        y += SIDEBAR_ROW_H
    return -1


def draw_sidebar(win, non_sun, sel, hover_idx=-1):
    sb = pygame.Surface((230, HEIGHT), pygame.SRCALPHA)
    sb.fill((4, 4, 20, 215))
    win.blit(sb, (0, 0))

    # ── Compact header ──
    t1 = FONT_MED.render("✦ SOLAR SYSTEM ✦", True, GOLD)
    t2 = FONT_SMALL.render("Physics simulation", True, (130, 130, 185))
    win.blit(t1, (10, 6))
    win.blit(t2, (10, 6 + t1.get_height() + 2))
    line_y = 6 + t1.get_height() + 2 + t2.get_height() + 3
    pygame.draw.line(win, (50, 50, 105), (8, line_y), (222, line_y), 1)

    y = line_y + 5            # first planet row — Mercury always shows here
    for i, p in enumerate(non_sun):
        is_sel   = (i == sel)
        is_hover = (i == hover_idx and not is_sel)

        # Row background
        row = pygame.Surface((222, SIDEBAR_ROW_H - 3), pygame.SRCALPHA)
        if is_sel:
            row.fill((28, 52, 98, 200))
        elif is_hover:
            row.fill((35, 40, 70, 180))
        else:
            row.fill((14, 14, 34, 135))
        win.blit(row, (4, y))

        # Left accent bar for selected
        if is_sel:
            pygame.draw.rect(win, CYAN, (0, y, 3, SIDEBAR_ROW_H - 3))

        # Colour dot
        dot = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.circle(dot, p.color, (7, 7), 6)
        win.blit(dot, (10, y + 4))

        # Name
        nc = CYAN if is_sel else (200, 220, 255) if is_hover else WHITE
        win.blit(FONT_SMALL.render(p.name, True, nc), (28, y + 5))

        # AU distance
        au = p.dist_sun / AU
        win.blit(FONT_SMALL.render(f"{au:.2f} AU", True, (165, 165, 175)), (150, y + 5))

        # Hover arrow hint
        if is_hover:
            win.blit(FONT_SMALL.render("◀", True, (80, 120, 180)), (210, y + 5))

        y += SIDEBAR_ROW_H

    pygame.draw.line(win, (50,50,105), (10, y+2), (220, y+2), 1)

    # ── Detail panel for selected planet ──
    if 0 <= sel < len(non_sun):
        p    = non_sun[sel]
        y   += 12
        au   = p.dist_sun / AU
        km   = p.dist_sun / 1000
        vkms = p.speed / 1000

        # Planet name header with dot
        hdr_surf = pygame.Surface((222, 24), pygame.SRCALPHA)
        hdr_surf.fill((20, 35, 70, 160))
        win.blit(hdr_surf, (4, y))
        dot2 = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.circle(dot2, p.color, (7, 7), 6)
        win.blit(dot2, (10, y + 4))
        win.blit(FONT_MED.render(p.name, True, CYAN), (28, y + 4))
        y += 28

        # Stats rows
        stats = [
            ("Distance",  f"{au:.3f} AU",          None),
            ("",          f"{km:,.0f} km",          None),
            ("Speed",     f"{vkms:.2f} km/s",       None),
            ("Sim. Days", f"{p.days:,}",            None),
            ("Mass",      f"{p.mass:.2e} kg",       None),
        ]
        for lbl, val, _ in stats:
            if lbl:
                win.blit(FONT_SMALL.render(lbl + ":", True, (135, 185, 255)), (14, y))
            win.blit(FONT_SMALL.render(val, True, WHITE), (120, y))
            y += 18

    pygame.draw.line(win, (50,50,105), (10, HEIGHT-108), (220, HEIGHT-108), 1)
    hints = [
        "Click row / planet: select",
        "Scroll: zoom  R: reset",
        "Right-drag: pan camera",
        "L: labels   SPACE: pause",
        "+/-: sim speed",
    ]
    yh = HEIGHT - 104
    for h in hints:
        win.blit(FONT_SMALL.render(h, True, (105, 125, 160)), (10, yh)); yh += 17


def draw_hud(win, mult, paused, zoom, days):
    hud = pygame.Surface((315, 66), pygame.SRCALPHA)
    hud.fill((4,4,20,190))
    win.blit(hud, (WIDTH-320, 5))
    st = "⏸  PAUSED" if paused else f"▶  ×{mult} speed"
    sc = (255,100,100) if paused else CYAN
    win.blit(FONT_MED.render(st, True, sc),                              (WIDTH-310, 10))
    win.blit(FONT_SMALL.render(f"Zoom: {zoom:.2f}×", True, (190,190,190)), (WIDTH-310, 32))
    win.blit(FONT_SMALL.render(f"Days elapsed: {days:,}", True, (190,190,190)), (WIDTH-310, 48))


def draw_planet_tooltip(win, p, cam):
    """Floating info card anchored near the selected planet."""
    sx, sy = cam.w2s(p.x, p.y)
    r      = max(3, int(p.vis_r * min(cam.zoom, 5) ** 0.45))

    au     = p.dist_sun / AU
    km     = p.dist_sun / 1000
    vkms   = p.speed / 1000

    lines = [
        (p.name, True),
        (f"Distance : {au:.3f} AU", False),
        (f"           {km:,.0f} km", False),
        (f"Orb.Speed: {vkms:.2f} km/s", False),
        (f"Sim. Days: {p.days:,}", False),
        (f"Mass     : {p.mass:.2e} kg", False),
    ]

    pad    = 8
    lh     = 17
    tw     = 220
    th     = pad*2 + lh * len(lines) + 4
    tx     = sx + r + 12
    ty     = sy - th // 2

    # Keep on screen
    if tx + tw > WIDTH - 10:
        tx = sx - r - tw - 12
    ty = max(5, min(ty, HEIGHT - th - 5))
    if tx < 235:
        tx = 235

    # Background card
    card = pygame.Surface((tw, th), pygame.SRCALPHA)
    card.fill((8, 12, 35, 215))
    pygame.draw.rect(card, CYAN, (0, 0, tw, th), 1, border_radius=6)
    win.blit(card, (tx, ty))

    # Colour dot + name
    dot = pygame.Surface((12, 12), pygame.SRCALPHA)
    pygame.draw.circle(dot, p.color, (6, 6), 5)
    win.blit(dot, (tx + pad, ty + pad + 2))

    y = ty + pad
    for i, (txt, bold) in enumerate(lines):
        font = FONT_MED if bold else FONT_SMALL
        col  = CYAN if bold else WHITE
        xoff = tx + pad + (16 if bold else 0)
        win.blit(font.render(txt, True, col), (xoff, y))
        y += lh

    # Connector line from card to planet
    cx = tx if tx > sx else tx + tw
    cy = ty + th // 2
    pygame.draw.line(win, CYAN, (cx, cy), (sx, sy), 1)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    clock = pygame.time.Clock()
    cam   = Camera()
    stars = make_stars()
    tick  = 0

    #This code is using for running music
    pygame.mixer.init()
    pygame.mixer.music.load("do mi xi.mp3")
    pygame.mixer.music.play(-1)
    #end

    sun = Planet(0, 0, 18, YELLOW, 1.98892e30, "Sun")
    sun.sun = True

    specs = [
    # name, a (AU), e, vis_r, color, mass, extra_parameters
    ("Mercury",      0.387,     0.2056,     5,    DARK_GREY,       3.30e23,   {}),
    ("Venus",        0.723,     0.0067,     9,    GOLDEN_BROWN,    4.87e24,   dict(has_atm=True, atm_color=(210,170,40))),
    ("Earth",        1.000,     0.0167,    10,    BLUE,            5.97e24,   dict(has_atm=True, atm_color=(60,120,200))),
    ("Mars",         1.524,     0.0934,     7,    RED,             6.39e23,   dict(has_atm=True, atm_color=(170,70,50))),
    ("Jupiter",      5.203,     0.0484,    20,    DARK_SAND,       1.90e27,   dict(has_atm=True, atm_color=(200,150,90))),
    ("Saturn",       9.537,     0.0541,    17,    TAN,             5.68e26,   dict(has_rings=True, ring_color=(175,155,105), has_atm=True, atm_color=(195,175,115))),
    ("Uranus",      19.195,     0.0472,    13,    LIGHT_BLUE,      8.68e25,   dict(has_rings=True, ring_color=(140,205,215), has_atm=True, atm_color=(95,195,215))),
    ("Neptune",     30.076,     0.0086,    12,    DEEP_BLUE,       1.02e26,   dict(has_atm=True, atm_color=(45,95,195))),
]

    planets = [sun]
    non_sun = []
    # 1. Khởi tạo các hành tinh theo quỹ đạo Elip
    for name, a_au, e, rv, color, mass, kw in specs:
        A = a_au * AU
        # Khoảng cách tại điểm cận nhật (trang 3 PDF)
        rp = A * (1 - e)
        # Vận tốc tại điểm cận nhật (trang 4 PDF - biến tấu từ công thức năng lượng)
        vp = math.sqrt((G * sun.mass / A) * ((1 + e) / (1 - e)))
        # 2. Chọn một góc xuất phát ngẫu nhiên (từ 0 đến 2π)
        theta = random.uniform(0, 2 * math.pi)
    
        # 3. Xoay vị trí (x, y)
        # Tại điểm cận nhật ban đầu là (rp, 0)
        start_x = rp * math.cos(theta)
        start_y = rp * math.sin(theta)
    
        # 4. Xoay véc-tơ vận tốc (vx, vy)
        # Vận tốc tại điểm cận nhật vuông góc với bán kính. 
        # Nếu vị trí là (cos, sin) thì hướng vuông góc sẽ là (sin, -cos) để quay ngược chiều kim đồng hồ
        start_vx = vp * math.sin(theta)
        start_vy = -vp * math.cos(theta)
        p = Planet(start_x, start_y, rv, color, mass, name, **kw)
        p.x_vel = start_vx
        p.y_vel = start_vy
        planets.append(p)
        non_sun.append(p)
    
    shooting_stars = [ShootingStar() for _ in range(5)]

    sel       = 2       # Earth
    show_lbl  = True
    paused    = False
    mult      = 1
    tot_seconds = 0     # Thêm biến này để lưu trữ chính xác đến từng giây
    tot_days  = 0
    hover_idx = -1      # sidebar row under mouse

    while True:
        clock.tick(60)
        tick += 1

        mx, my = pygame.mouse.get_pos()
        # Update hover: only when mouse is inside sidebar column
        if mx <= 226:
            hover_idx = sidebar_hit(my, len(non_sun))
        else:
            hover_idx = -1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); return
            cam.handle(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if mx <= 226:
                    # Click on sidebar row
                    hit = sidebar_hit(my, len(non_sun))
                    if hit >= 0:
                        sel = hit
                else:
                    # Click on canvas — find nearest planet
                    clicked   = None
                    best_dist = float("inf")
                    for i, p in enumerate(non_sun):
                        sx, sy = cam.w2s(p.x, p.y)
                        d = math.sqrt((mx-sx)**2 + (my-sy)**2)
                        hit_r = max(14, p.screen_r(cam) + 6)
                        if d <= hit_r and d < best_dist:
                            best_dist = d
                            clicked = i
                    if clicked is not None:
                        sel = clicked
            if event.type == pygame.KEYDOWN:
                if   event.key == pygame.K_l:     show_lbl = not show_lbl
                elif event.key == pygame.K_SPACE: paused   = not paused
                elif event.key == pygame.K_r:     cam.reset()
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    mult = min(mult * 2, 128)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    mult = max(mult // 2, 1)
                elif event.key == pygame.K_DOWN:  sel = (sel + 1) % len(non_sun)
                elif event.key == pygame.K_UP:    sel = (sel - 1) % len(non_sun)

        if not paused:
            for _ in range(mult):
                for p in non_sun:
                    p.update(planets)
            tot_days += mult #check dòng này xem có cần giữ lại hem
            for ss in shooting_stars:
                ss.update()
            seconds_per_frame = mult * TIMESTEP
            tot_seconds += seconds_per_frame 
            tot_days = int(tot_seconds / 86400)

        WIN.fill(BLACK)
        draw_stars(WIN, stars, tick)

        for ss in shooting_stars:
            ss.draw(WIN)
        for p in non_sun:
            p.draw_orbit(WIN, cam)
        for i, p in enumerate(non_sun):
            p.draw(WIN, cam, show_lbl, selected=(i == sel))
        sun.draw_sun(WIN, cam, tick)

        draw_sidebar(WIN, non_sun, sel, hover_idx)
        draw_hud(WIN, mult, paused, cam.zoom, tot_days)
        draw_planet_tooltip(WIN, non_sun[sel], cam)

        pygame.display.update()


main()

