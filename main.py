import zlib
import struct
import math
import os

W, H = 1024, 853
PAPER = (246, 239, 221)
INK = (25, 25, 25)
RED = (185, 28, 28)
GREY = (107, 107, 107)
WHITE = (255, 255, 255)
CREAM = (251, 246, 233)

# 5x7 bitmap font. Each glyph is 7 rows; bit 4 (0x10) is the left column.
FONT = {
    'A': [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    'B': [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E],
    'C': [0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E],
    'D': [0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E],
    'E': [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F],
    'F': [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10],
    'G': [0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F],
    'H': [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    'I': [0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
    'J': [0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C],
    'K': [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
    'L': [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
    'M': [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11],
    'N': [0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11],
    'O': [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    'P': [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10],
    'Q': [0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D],
    'R': [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
    'S': [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E],
    'T': [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
    'U': [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    'V': [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04],
    'W': [0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11],
    'X': [0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11],
    'Y': [0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04],
    'Z': [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F],
    'a': [0x00, 0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F],
    'b': [0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x1E],
    'c': [0x00, 0x00, 0x0E, 0x10, 0x10, 0x11, 0x0E],
    'd': [0x01, 0x01, 0x0F, 0x11, 0x11, 0x11, 0x0F],
    'e': [0x00, 0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0E],
    'f': [0x06, 0x08, 0x08, 0x1E, 0x08, 0x08, 0x08],
    'g': [0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x0E],
    'h': [0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x11],
    'i': [0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E],
    'j': [0x02, 0x00, 0x06, 0x02, 0x02, 0x12, 0x0C],
    'k': [0x10, 0x10, 0x12, 0x14, 0x18, 0x14, 0x12],
    'l': [0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
    'm': [0x00, 0x00, 0x1A, 0x15, 0x15, 0x11, 0x11],
    'n': [0x00, 0x00, 0x1E, 0x11, 0x11, 0x11, 0x11],
    'o': [0x00, 0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E],
    'p': [0x00, 0x00, 0x1E, 0x11, 0x11, 0x1E, 0x10],
    'q': [0x00, 0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01],
    'r': [0x00, 0x00, 0x16, 0x19, 0x10, 0x10, 0x10],
    's': [0x00, 0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E],
    't': [0x04, 0x04, 0x1F, 0x04, 0x04, 0x04, 0x03],
    'u': [0x00, 0x00, 0x11, 0x11, 0x11, 0x13, 0x0D],
    'v': [0x00, 0x00, 0x11, 0x11, 0x11, 0x0A, 0x04],
    'w': [0x00, 0x00, 0x11, 0x11, 0x15, 0x15, 0x0A],
    'x': [0x00, 0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11],
    'y': [0x00, 0x00, 0x11, 0x11, 0x0F, 0x01, 0x0E],
    'z': [0x00, 0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F],
    '0': [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E],
    '1': [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E],
    '2': [0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F],
    '3': [0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E],
    '4': [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02],
    '5': [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E],
    '6': [0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E],
    '7': [0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08],
    '8': [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E],
    '9': [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C],
    ' ': [0, 0, 0, 0, 0, 0, 0],
    '.': [0, 0, 0, 0, 0, 0x0C, 0x0C],
    ',': [0, 0, 0, 0, 0x0C, 0x04, 0x08],
    ':': [0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0],
    ';': [0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08],
    "'": [0x04, 0x04, 0x08, 0, 0, 0, 0],
    '-': [0, 0, 0, 0x0E, 0, 0, 0],
    '&': [0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D],
    '$': [0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04],
    '%': [0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13],
    '(': [0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02],
    ')': [0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08],
    '/': [0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10],
    '+': [0, 0x04, 0x04, 0x0E, 0x04, 0x04, 0],
    '=': [0, 0, 0x1F, 0, 0x1F, 0, 0],
    '?': [0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04],
    '!': [0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04],
    '·': [0, 0, 0, 0x06, 0x06, 0, 0],
}
FONT['’'] = FONT["'"]
FONT['–'] = FONT['-']
FONT['—'] = FONT['-']

BUF = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        BUF[i] = c[0]
        BUF[i + 1] = c[1]
        BUF[i + 2] = c[2]


def fill_rect(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(c) * (x1 - x0)
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        BUF[i:i + len(row)] = row


def hline(x, y, w, c):
    fill_rect(x, y, w, 1, c)


def vline(x, y, h, c):
    fill_rect(x, y, 1, h, c)


def rect_outline(x, y, w, h, c):
    hline(x, y, w, c)
    hline(x, y + h - 1, w, c)
    vline(x, y, h, c)
    vline(x + w - 1, y, h, c)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def thick_line(x0, y0, x1, y1, c, w):
    r = w // 2
    for a in range(-r, r + 1):
        for b in range(-r, r + 1):
            line(x0 + a, y0 + b, x1 + a, y1 + b, c)


def circle(cx, cy, r, c):
    if r <= 0:
        return
    for yy in range(cy - r, cy + r + 1):
        dx = int(math.sqrt(max(0, r * r - (yy - cy) * (yy - cy))))
        hline(cx - dx, yy, 2 * dx + 1, c)


def circle_outline(cx, cy, r, c, w=1):
    steps = max(24, int(2 * math.pi * r))
    for i in range(steps):
        a = 2 * math.pi * i / steps
        px(int(round(cx + r * math.cos(a))), int(round(cy + r * math.sin(a))), c)
        if w > 1:
            px(int(round(cx + r * math.cos(a))) + 1, int(round(cy + r * math.sin(a))), c)


def ellipse(cx, cy, rx, ry, c):
    if rx <= 0 or ry <= 0:
        return
    for yy in range(cy - ry, cy + ry + 1):
        t = (yy - cy) / ry
        dx = int(rx * math.sqrt(max(0.0, 1.0 - t * t)))
        hline(cx - dx, yy, 2 * dx + 1, c)


def poly(points, c):
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    y0, y1 = min(ys), max(ys)
    n = len(points)
    for yy in range(y0, y1 + 1):
        xs = []
        for i in range(n):
            x0, ya = points[i]
            x1, yb = points[(i + 1) % n]
            if ya == yb:
                continue
            if (yy >= min(ya, yb)) and (yy < max(ya, yb)):
                xs.append(x0 + (yy - ya) * (x1 - x0) / (yb - ya))
        if len(xs) >= 2:
            xs.sort()
            hline(int(round(xs[0])), yy, int(round(xs[-1])) - int(round(xs[0])) + 1, c)


def arc(cx, cy, r, a0, a1, c):
    steps = max(8, int(abs(a1 - a0) * r))
    for i in range(steps + 1):
        a = a0 + (a1 - a0) * i / steps
        px(int(round(cx + r * math.cos(a))), int(round(cy + r * math.sin(a))), c)


def spiral(cx, cy, r0, r1, turns, c):
    steps = int(turns * 90)
    prev = None
    for i in range(steps + 1):
        t = i / steps
        a = t * turns * 2 * math.pi
        r = r0 + (r1 - r0) * t
        p = (int(round(cx + r * math.cos(a))), int(round(cy + r * math.sin(a))))
        if prev is not None:
            line(prev[0], prev[1], p[0], p[1], c)
        prev = p


def text_w(s, sc):
    if not s:
        return 0
    return len(s) * 6 * sc - sc


def draw_text(x, y, s, sc, c):
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT['?'])
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits & (0x10 >> col):
                    fill_rect(cx + col * sc, y + row * sc, sc, sc, c)
        cx += 6 * sc
    return cx


def draw_text_c(cx, y, s, sc, c):
    draw_text(cx - text_w(s, sc) // 2, y, s, sc, c)


def wrap_greedy(s, max_chars):
    words = s.split(' ')
    lines = []
    cur = ''
    for w in words:
        if cur == '':
            cur = w
        elif len(cur) + 1 + len(w) <= max_chars:
            cur = cur + ' ' + w
        else:
            lines.append(cur)
            cur = w
    if cur != '':
        lines.append(cur)
    return lines


def wrap_balanced(s, max_chars):
    words = s.split(' ')
    if len(words) == 1:
        return wrap_greedy(s, max_chars)
    best = None
    for i in range(1, len(words)):
        l1 = ' '.join(words[:i])
        l2 = ' '.join(words[i:])
        if len(l1) <= max_chars and len(l2) <= max_chars:
            d = abs(len(l1) - len(l2))
            if best is None or d < best[0]:
                best = (d, [l1, l2])
    if best is not None:
        return best[1]
    return wrap_greedy(s, max_chars)


def draw_wrapped(x, y, s, sc, c, max_chars, lh, max_lines=None):
    lines = wrap_balanced(s, max_chars)
    if max_lines is not None:
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        draw_text(x, y + i * lh, ln, sc, c)
    return y + len(lines) * lh


# ---------- flat-vector illustrations ----------

def illus_cyclone(x, y, w, h):
    fill_rect(x, y, w, h, (47, 111, 126))
    cx, cy = x + int(w * 0.36), y + int(h * 0.46)
    spiral(cx, cy, 6, 62, 3.2, WHITE)
    thick_line(cx - 58, cy + 40, cx + 58, cy + 40, WHITE, 2)
    circle(cx, cy, 11, (246, 239, 221))
    # rain slashes: denser, across the whole panel, varied lengths
    rain = [(0.06, 0.20), (0.12, 0.42), (0.18, 0.16), (0.24, 0.55),
            (0.28, 0.30), (0.50, 0.14), (0.56, 0.36), (0.62, 0.22),
            (0.66, 0.52), (0.72, 0.18), (0.78, 0.58), (0.82, 0.32),
            (0.88, 0.14), (0.92, 0.46), (0.96, 0.28)]
    for i, (rx, ry) in enumerate(rain):
        ln = 12 + (i % 3) * 3
        dx = 6 + (i % 2) * 2
        line(x + int(w * rx), y + int(h * ry),
             x + int(w * rx) - dx, y + int(h * ry) + ln, (220, 235, 240))
    # waves: four layered lines, alternating shades, so the sea reads deeper
    for k, (wy, amp, wc) in enumerate([(0.78, 3, WHITE), (0.84, 4, (170, 205, 218)),
                                       (0.90, 4, WHITE), (0.95, 3, (170, 205, 218))]):
        prev = None
        for i in range(0, w + 1, 8):
            py = y + int(h * wy) + int(amp * math.sin(i / 22.0 + k * 1.3))
            if prev is not None:
                line(prev[0], prev[1], x + i, py, wc)
            prev = (x + i, py)


def illus_gta(x, y, w, h):
    fill_rect(x, y, w, h, (232, 114, 42))
    fill_rect(x, y + int(h * 0.55), w, h - int(h * 0.55), (244, 164, 66))
    circle(x + int(w * 0.68), y + int(h * 0.34), int(h * 0.22), (250, 226, 150))
    # skyline: 10 buildings, varied heights, with lit windows
    base = y + h
    for bx, bw, bh in [(0.02, 0.09, 0.28), (0.12, 0.09, 0.42),
                       (0.22, 0.10, 0.50), (0.33, 0.09, 0.26),
                       (0.43, 0.10, 0.36), (0.54, 0.09, 0.48),
                       (0.64, 0.08, 0.30), (0.73, 0.10, 0.44),
                       (0.84, 0.09, 0.34), (0.94, 0.05, 0.26)]:
        px = x + int(w * bx)
        pw = int(w * bw)
        ph = int(h * bh)
        top = base - ph
        fill_rect(px, top, pw, ph, (38, 32, 54))
        for wy in (top + 4, top + 11):
            if wy + 4 > base - 3:
                continue
            for wx in (px + 4, px + pw - 7):
                if wx + 3 > px + pw - 3:
                    continue
                fill_rect(wx, wy, 3, 4, (250, 226, 150))
    # palm
    tx, ty = x + int(w * 0.16), y + int(h * 0.62)
    thick_line(tx, ty, tx + 14, ty - int(h * 0.34), (58, 44, 30), 3)
    for a in (-0.5, -0.15, 0.2, 0.55):
        ex = tx + 14 + int(30 * math.cos(a - 1.2))
        ey = ty - int(h * 0.34) + int(22 * math.sin(a - 1.2))
        thick_line(tx + 14, ty - int(h * 0.34), ex, ey, (34, 96, 58), 2)
    # car silhouette: larger, with a lit cabin window and headlight
    carx, cary = x + int(w * 0.56), y + int(h * 0.84)
    fill_rect(carx, cary - 13, 96, 13, (25, 25, 25))
    poly([(carx + 16, cary - 13), (carx + 28, cary - 25),
          (carx + 68, cary - 25), (carx + 80, cary - 13)], (25, 25, 25))
    fill_rect(carx + 31, cary - 22, 30, 7, (250, 226, 150))
    circle(carx + 90, cary - 6, 2, (250, 226, 150))
    circle(carx + 18, cary + 1, 7, (25, 25, 25))
    circle(carx + 78, cary + 1, 7, (25, 25, 25))


def illus_dove(x, y, w, h):
    fill_rect(x, y, w, h, (127, 163, 200))
    cx, cy = x + int(w * 0.46), y + int(h * 0.52)
    # tail
    poly([(cx - 30, cy + 2), (cx - 62, cy - 12), (cx - 58, cy + 14)], WHITE)
    # body
    ellipse(cx, cy, 34, 17, WHITE)
    # head
    circle(cx + 32, cy - 12, 11, WHITE)
    # beak
    poly([(cx + 42, cy - 14), (cx + 52, cy - 11), (cx + 42, cy - 8)], (232, 114, 42))
    # wing
    ellipse(cx - 4, cy - 8, 24, 9, (226, 236, 244))
    # eye (a single pixel was too small to read)
    circle(cx + 34, cy - 14, 2, INK)
    # olive branch
    thick_line(x + int(w * 0.74), y + int(h * 0.78), x + int(w * 0.94),
               y + int(h * 0.62), (58, 110, 66), 2)
    for lx, ly in [(0.78, 0.74), (0.84, 0.70), (0.90, 0.66)]:
        ellipse(x + int(w * lx), y + int(h * ly), 6, 3, (58, 110, 66))


def illus_space(x, y, w, h):
    fill_rect(x, y, w, h, (31, 42, 68))
    for sx, sy in [(0.08, 0.15), (0.22, 0.3), (0.9, 0.12), (0.78, 0.28),
                   (0.55, 0.1), (0.35, 0.55), (0.95, 0.5), (0.12, 0.7)]:
        px(x + int(w * sx), y + int(h * sy), WHITE)
        px(x + int(w * sx) + 1, y + int(h * sy), WHITE)
    # asteroid
    poly([(x + int(w * 0.72), y + int(h * 0.30)), (x + int(w * 0.86), y + int(h * 0.22)),
          (x + int(w * 0.97), y + int(h * 0.40)), (x + int(w * 0.9), y + int(h * 0.58)),
          (x + int(w * 0.74), y + int(h * 0.55))], (140, 140, 150))
    # spacecraft
    bx, by = x + int(w * 0.30), y + int(h * 0.42)
    fill_rect(bx - 34, by - 8, 26, 16, (70, 110, 180))
    fill_rect(bx + 8, by - 8, 26, 16, (70, 110, 180))
    fill_rect(bx - 8, by - 12, 16, 24, (200, 200, 210))
    circle(bx + 18, by - 16, 6, (200, 200, 210))
    line(bx + 18, by - 16, bx + 30, by - 24, (200, 200, 210))


def illus_haiti(x, y, w, h):
    fill_rect(x, y, w, h, (214, 178, 130))
    base = y + h
    for bx, bw, bh, c in [(0.04, 0.20, 0.55, (120, 84, 60)),
                          (0.28, 0.16, 0.72, (96, 66, 48)),
                          (0.48, 0.22, 0.48, (140, 100, 70)),
                          (0.74, 0.20, 0.64, (110, 78, 56))]:
        fill_rect(x + int(w * bx), base - int(h * bh), int(w * bw), int(h * bh), c)
        for wy in range(3):
            for wx in range(2):
                fill_rect(x + int(w * bx) + 6 + wx * 16,
                          base - int(h * bh) + 6 + wy * 12, 7, 7, (250, 226, 150))
    fill_rect(x, base - 6, w, 6, (70, 60, 52))


def illus_court(x, y, w, h):
    fill_rect(x, y, w, h, (228, 220, 200))
    bx, by = x + int(w * 0.5), y + int(h * 0.30)
    poly([(bx - 52, by), (bx + 52, by), (bx, by - 22)], (150, 140, 120))
    circle(bx, by - 8, 5, (120, 110, 90))
    for i in range(4):
        cx = bx - 42 + i * 28
        fill_rect(cx - 5, by + 2, 10, int(h * 0.52), (250, 248, 240))
    fill_rect(bx - 58, by + 2 + int(h * 0.52), 116, 6, (120, 110, 90))
    fill_rect(x + int(w * 0.08), y + h - 8, int(w * 0.84), 4, (150, 140, 120))


def illus_flags(x, y, w, h):
    fill_rect(x, y, w, h, (196, 214, 228))
    # pole 1
    px0, py0 = x + int(w * 0.18), y + int(h * 0.14)
    vline(px0, py0, int(h * 0.72), (90, 80, 70))
    # flag 1: stripes
    for i in range(5):
        fill_rect(px0 + 2, py0 + i * 7, 52, 7, RED if i % 2 == 0 else WHITE)
    fill_rect(px0 + 2, py0, 22, 14, (40, 60, 120))
    # pole 2
    px1 = x + int(w * 0.62)
    vline(px1, py0, int(h * 0.72), (90, 80, 70))
    for i, c in enumerate([(250, 200, 40), (40, 90, 170), (200, 40, 40)]):
        fill_rect(px1 + 2, py0 + i * 9, 52, 9, c)


def illus_vangogh(x, y, w, h):
    fill_rect(x, y, w, h, (96, 130, 170))
    # frame
    rect_outline(x + int(w * 0.30), y + int(h * 0.10), int(w * 0.40), int(h * 0.80), (90, 64, 30))
    fill_rect(x + int(w * 0.30) + 3, y + int(h * 0.10) + 3, int(w * 0.40) - 6,
              int(h * 0.80) - 6, (244, 214, 130))
    cx, cy = x + int(w * 0.5), y + int(h * 0.44)
    # petals
    for i in range(10):
        a = 2 * math.pi * i / 10
        tx = cx + int(15 * math.cos(a))
        ty = cy + int(15 * math.sin(a))
        poly([(cx, cy), (tx - 3, ty - 3), (tx + 3, ty + 3)], (250, 180, 30))
    circle(cx, cy, 7, (120, 72, 30))
    # stem
    thick_line(cx, cy + 9, cx - 4, y + int(h * 0.86), (52, 110, 60), 2)


def illus_baseball(x, y, w, h):
    fill_rect(x, y, w, h, (88, 140, 90))
    cx, cy = x + int(w * 0.38), y + int(h * 0.52)
    circle(cx, cy, 20, WHITE)
    arc(cx - 6, cy, 16, -1.1, 1.1, RED)
    arc(cx + 6, cy, 16, math.pi - 1.1, math.pi + 1.1, RED)
    # bat
    thick_line(x + int(w * 0.66), y + int(h * 0.82), x + int(w * 0.86),
               y + int(h * 0.16), (150, 110, 70), 5)


def illus_missile(x, y, w, h):
    fill_rect(x, y, w, h, (150, 178, 198))
    cx, cy = x + int(w * 0.42), y + int(h * 0.50)
    # shield
    poly([(cx + 52, cy - 34), (cx + 78, cy - 22), (cx + 78, cy + 6),
          (cx + 65, cy + 30), (cx + 52, cy + 20)], (40, 90, 150))
    # missile body
    poly([(cx - 26, cy - 40), (cx - 14, cy - 40), (cx - 14, cy + 22),
          (cx - 26, cy + 22)], (220, 220, 225))
    poly([(cx - 26, cy - 40), (cx - 20, cy - 54), (cx - 14, cy - 40)], RED)
    poly([(cx - 26, cy + 22), (cx - 34, cy + 34), (cx - 26, cy + 30)], (120, 120, 130))
    poly([(cx - 14, cy + 22), (cx - 6, cy + 34), (cx - 14, cy + 30)], (120, 120, 130))
    # flame
    poly([(cx - 24, cy + 34), (cx - 20, cy + 48), (cx - 16, cy + 34)], (240, 160, 40))


# ---------- layout ----------

SUMC = (88, 88, 88)
GREEN = (52, 140, 70)


def draw_hero(x, y, w, h, illus_fn, kicker, headline, summary, badge,
              hsc, ssc, illus_h, h_lh, s_lh):
    fill_rect(x, y, w, h, CREAM)
    illus_fn(x, y, w, illus_h)
    rect_outline(x, y, w, h, INK)
    bx, by = x + 17, y + 17
    circle(bx, by, 13, RED)
    draw_text_c(bx, by - 7, str(badge), 2, WHITE)
    ky = y + illus_h + 8
    draw_text(x + 12, ky, kicker, 2, RED)
    hy = ky + 16
    hlines = wrap_balanced(headline, (w - 24) // (6 * hsc))
    for i, ln in enumerate(hlines):
        draw_text(x + 12, hy + i * h_lh, ln, hsc, INK)
    sy = hy + len(hlines) * h_lh + 4
    slines = wrap_balanced(summary, (w - 24) // (6 * ssc))
    for i, ln in enumerate(slines):
        draw_text(x + 12, sy + i * s_lh, ln, ssc, SUMC)
    return sy + len(slines) * s_lh


def draw_cat(x, y, w, h, tag, illus_fn, kicker, headline, summary, badge,
             illus_h, h_lh, s_lh):
    fill_rect(x, y, w, h, CREAM)
    # category tag
    tw = text_w(tag, 1) + 12
    fill_rect(x + 8, y + 6, tw, 13, RED)
    draw_text(x + 14, y + 9, tag, 1, WHITE)
    # number badge, top right
    bx, by = x + w - 16, y + 16
    circle(bx, by, 10, RED)
    draw_text_c(bx, by - 4, str(badge), 1, WHITE)
    # illustration
    iy = y + 22
    illus_fn(x + 1, iy, w - 2, illus_h)
    rect_outline(x, y, w, h, INK)
    # kicker
    ky = iy + illus_h + 3
    draw_text(x + 10, ky, kicker, 1, RED)
    # headline
    hy = ky + 11
    hlines = wrap_balanced(headline, (w - 20) // 12)
    for i, ln in enumerate(hlines):
        draw_text(x + 10, hy + i * h_lh, ln, 2, INK)
    # summary
    sy = hy + len(hlines) * h_lh + 2
    slines = wrap_balanced(summary, (w - 20) // 6)
    for i, ln in enumerate(slines):
        draw_text(x + 10, sy + i * s_lh, ln, 1, SUMC)
    return sy + len(slines) * s_lh


def draw_masthead():
    hline(24, 10, 976, INK)
    draw_text_c(512, 18, 'THE WORLD IN ONE DAY', 6, INK)
    draw_text_c(512, 70, 'Friday 20 November 2026', 3, RED)
    hline(24, 100, 976, INK)


def draw_heroes():
    draw_hero(24, 108, 536, 276, illus_cyclone,
              "ODISHA \u00b7 STORM",
              "Cyclone Akvan slams India's east coast",
              "300,000 evacuated, 423 rescue teams deployed as the storm makes landfall.",
              1, 3, 2, 160, 24, 15)
    draw_hero(576, 108, 424, 134, illus_gta,
              "VICE CITY \u00b7 GAMES",
              "GTA VI sales pass $1.80bn in a day",
              "Rockstar's blockbuster overtakes The Odyssey's global run within 24 hours.",
              2, 2, 1, 56, 14, 9)
    draw_hero(576, 250, 424, 134, illus_dove,
              "BERLIN \u00b7 DIPLOMACY",
              "Europe ready for talks with Russia",
              "Leaders say they are open to negotiations on ending the war in Ukraine.",
              3, 2, 1, 56, 14, 9)


def draw_categories():
    # row 1: 3 cards
    draw_cat(24, 392, 317, 114, 'SPACE', illus_space,
             "TOKYO \u00b7 SPACE",
             "Japan's Hayabusa2 drops asteroid landing",
             "Engine trouble forces JAXA's probe to change its plans.",
             4, 24, 14, 9)
    draw_cat(353, 392, 317, 114, 'WAR', illus_haiti,
             "PORT-AU-PRINCE \u00b7 WAR",
             "Haiti offensive kills 34 gang suspects",
             "Security forces push to retake the Martissant corridor.",
             5, 24, 14, 9)
    draw_cat(682, 392, 318, 114, 'LAW', illus_court,
             "SEOUL \u00b7 LAW",
             "South Korea court clears ex-PM Han",
             "Supreme Court overturns Han Duck-soo's conviction over martial law.",
             6, 24, 14, 9)
    # row 2: 4 cards
    draw_cat(24, 514, 235, 124, 'DEAL', illus_flags,
             "CARACAS \u00b7 DEAL",
             "US and Venezuela restore military ties",
             "Deal signed less than a year after Maduro's ouster.",
             7, 20, 14, 9)
    draw_cat(271, 514, 235, 124, 'ART', illus_vangogh,
             "NEW YORK \u00b7 ART",
             "Van Gogh sells for record $190.4m",
             "Painting fetches a record price despite its Nazi-era history.",
             8, 20, 14, 9)
    draw_cat(518, 514, 235, 124, 'SPORT', illus_baseball,
             "WASHINGTON \u00b7 SPORT",
             "Trump pardons baseball legend Pete Rose",
             "Posthumous pardon for the late hits king.",
             9, 20, 14, 9)
    draw_cat(765, 514, 235, 124, 'DEFENCE', illus_missile,
             "NEW DELHI \u00b7 DEFENCE",
             "India signs Barak missile upgrade deal",
             "Defence pact with Israel Aerospace Industries worth Rs 1,976 crore.",
             10, 20, 14, 9)


BRIEFS = [
    "US sanctions Comanchero biker gang",
    "Fiona the hippo dies after swallowing a hat",
    "Philippines and Chile sign free trade deal",
    "Elon Musk visits the Philippines",
    "Grindr launches $120 AI subscription",
    "Rome rebukes Kyiv over lawmaker blacklist",
    "Irish man indicted over $60m military jet attack",
    "The Economist unveils World Ahead 2027",
    "Uganda landslide survivors seek UN justice",
    "Migrant boat sinks off Senegal, dozens missing",
    "Taiz residents speak to BBC under siege",
    "Canada embraces AI data centres",
    "California targets Nvidia in China chip probe",
    "Cumin sodas challenge cola giants in India",
    "ICMR completes 100 tech transfer deals",
    "India beats Pakistan 2-1 for 10th SAFF title",
    "SpaceX Dragon departs space station",
    "New flying frog species found in Indonesia",
    "Astronomers see star swallow its companion",
    "NEET paper leak charges framed for 14",
]


def draw_briefs():
    for i, text in enumerate(BRIEFS):
        n = 11 + i
        row, col = i // 4, i % 4
        x = 24 + col * 248
        y = 646 + row * 23
        draw_text(x, y, str(n) + '.', 1, RED)
        lines = wrap_greedy(text, 35)
        for j, ln in enumerate(lines[:2]):
            draw_text(x + 24, y + j * 9, ln, 1, INK)


def draw_map(x, y, w, h):
    fill_rect(x, y, w, h, (232, 222, 200))
    cont = (186, 166, 124)
    poly([(44, 772), (100, 770), (112, 778), (96, 790), (70, 794), (48, 788), (38, 778)], cont)
    poly([(96, 796), (118, 794), (124, 804), (112, 818), (100, 816), (94, 804)], cont)
    poly([(150, 774), (172, 772), (176, 780), (162, 786), (150, 782)], cont)
    poly([(152, 790), (186, 788), (192, 798), (182, 814), (166, 818), (154, 806), (148, 796)], cont)
    poly([(180, 772), (240, 768), (272, 774), (268, 788), (236, 796), (200, 792), (184, 782)], cont)
    poly([(238, 806), (266, 804), (272, 812), (258, 818), (240, 814)], cont)


def draw_bottom():
    hline(24, 762, 976, INK)
    draw_map(24, 766, 280, 60)
    # date check box
    rect_outline(320, 766, 384, 60, INK)
    circle(344, 796, 13, GREEN)
    line(336, 796, 342, 802, WHITE)
    line(342, 802, 354, 788, WHITE)
    draw_text(366, 772, 'DATE CHECK', 2, INK)
    draw_text(366, 788, 'Friday 20 November 2026', 2, RED)
    draw_text(366, 806, 'ALL STORIES VERIFIED FOR THIS DATE', 1, GREY)
    # globe panel
    fill_rect(720, 766, 280, 60, (214, 228, 238))
    circle_outline(860, 796, 24, INK)
    vline(860, 772, 48, INK)
    hline(836, 796, 48, INK)
    arc(848, 796, 12, -1.2, 1.2, INK)
    arc(872, 796, 12, math.pi - 1.2, math.pi + 1.2, INK)
    poly([(852, 788), (862, 786), (866, 792), (858, 796)], (186, 166, 124))
    poly([(866, 802), (876, 800), (878, 806), (870, 808)], (186, 166, 124))
    # count row + footer
    draw_text_c(512, 832, '3 HIGHLIGHTS \u00b7 7 IN CATEGORIES \u00b7 20 BRIEFS = 30 STORIES', 1, INK)
    draw_text_c(512, 846, 'Sources: Reuters \u00b7 AP \u00b7 BBC \u00b7 Financial Times \u00b7 The Hindu', 1, GREY)


# ---------- PNG writer ----------

def _chunk(typ, data):
    return (struct.pack('>I', len(data)) + typ + data +
            struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff))


def save_png(path):
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw.extend(BUF[yy * W * 3:(yy + 1) * W * 3])
    comp = zlib.compress(bytes(raw), 6)
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    png = (b'\x89PNG\r\n\x1a\n' + _chunk(b'IHDR', ihdr) +
           _chunk(b'IDAT', comp) + _chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)


def main():
    fill_rect(0, 0, W, H, PAPER)
    draw_masthead()
    draw_heroes()
    draw_categories()
    draw_briefs()
    draw_bottom()
    out = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(out, exist_ok=True)
    save_png(os.path.join(out, 'entry.png'))


if __name__ == '__main__':
    main()
