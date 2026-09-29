from pathlib import Path
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH = 1600
HEIGHT = 1000
OUTPUT = Path(__file__).resolve().parents[1] / "img" / "japan-dusk.png"
FONT_PATH = Path("C:/Windows/Fonts/msgothic.ttc")
random.seed(31)


def gradient_color(top, bottom, amount):
    return tuple(round(first + (second - first) * amount) for first, second in zip(top, bottom))


def add_tower(draw, x, y, width, height, base_color, accent_color, window_seed):
    random.seed(window_seed)
    roof_step = random.randrange(0, 26)
    draw.polygon(
        [(x, HEIGHT), (x, y + roof_step), (x + width * .32, y), (x + width, y + roof_step // 2), (x + width, HEIGHT)],
        fill=base_color,
    )
    draw.line((x + width * .32, y, x + width * .32, HEIGHT), fill=(*accent_color, 64), width=2)
    draw.line((x + width - 3, y + 5, x + width - 3, HEIGHT), fill=(118, 142, 184, 78), width=2)

    columns = max(3, width // 20)
    rows = max(6, height // 24)
    cell_width = max(4, (width - 16) // columns)
    cell_height = max(5, (height - 24) // rows)
    for row in range(rows):
        for column in range(columns):
            if random.random() < .48:
                continue
            window_x = x + 7 + column * cell_width
            window_y = y + 18 + row * cell_height
            window_color = random.choice((accent_color, (70, 221, 239), (239, 75, 184), (249, 194, 99)))
            alpha = random.randrange(85, 220)
            draw.rectangle((window_x, window_y, window_x + max(2, cell_width - 7), window_y + max(3, cell_height - 10)), fill=(*window_color, alpha))

    for antenna_x in (x + width * .32, x + width * .72):
        if random.random() > .45:
            draw.line((antenna_x, y, antenna_x, y - random.randrange(25, 90)), fill=(133, 171, 211, 170), width=2)


def add_vertical_sign(draw, x, y, width, height, label, fill_color, font):
    draw.rounded_rectangle((x, y, x + width, y + height), radius=5, fill=(10, 13, 29, 238), outline=(*fill_color, 220), width=3)
    draw.rounded_rectangle((x + 5, y + 5, x + width - 5, y + height - 5), radius=3, outline=(*fill_color, 95), width=1)
    characters = list(label)
    character_height = min(font.size + 4, (height - 18) // max(1, len(characters)))
    sign_font = ImageFont.truetype(str(FONT_PATH), max(12, character_height))
    for index, character in enumerate(characters):
        draw.text((x + width // 2, y + 11 + index * character_height), character, font=sign_font, fill=(*fill_color, 255), anchor="ma", stroke_width=1, stroke_fill=(*fill_color, 80))


sky = Image.new("RGB", (WIDTH, HEIGHT))
sky_draw = ImageDraw.Draw(sky)
for row in range(HEIGHT):
    amount = row / (HEIGHT - 1)
    if amount < .62:
        color = gradient_color((5, 11, 29), (28, 25, 57), amount / .62)
    else:
        color = gradient_color((28, 25, 57), (69, 27, 76), (amount - .62) / .38)
    sky_draw.line((0, row, WIDTH, row), fill=color)

scene = sky.convert("RGBA")
glow = Image.new("RGBA", (WIDTH, HEIGHT))
glow_draw = ImageDraw.Draw(glow, "RGBA")
glow_draw.ellipse((420, 410, 1180, 980), fill=(19, 104, 187, 58))
glow_draw.ellipse((650, 500, 1050, 930), fill=(226, 38, 155, 54))
glow_draw.ellipse((95, 240, 480, 780), fill=(20, 164, 204, 36))
scene = Image.alpha_composite(scene, glow.filter(ImageFilter.GaussianBlur(100)))
draw = ImageDraw.Draw(scene, "RGBA")

for _ in range(220):
    star_x = random.randrange(WIDTH)
    star_y = random.randrange(HEIGHT // 2)
    star_size = random.choice((1, 1, 2))
    draw.ellipse((star_x, star_y, star_x + star_size, star_y + star_size), fill=(188, 220, 255, random.randrange(45, 170)))

far_buildings = [(525, 365, 100, 310), (635, 285, 105, 395), (755, 420, 82, 265), (850, 340, 115, 340), (978, 390, 115, 290)]
for index, (x, y, width, height) in enumerate(far_buildings):
    add_tower(draw, x, y, width, height, (15, 24, 45, 245), (33, 198, 231), index + 7)

city_palette = [
    ((12, 18, 34, 255), (248, 54, 177)),
    ((13, 24, 43, 255), (49, 216, 242)),
    ((18, 17, 38, 255), (165, 102, 255)),
    ((15, 25, 39, 255), (244, 103, 139)),
    ((12, 20, 37, 255), (56, 200, 218)),
]

near_buildings = [
    (-40, 125, 230, 875, 1), (190, 235, 190, 765, 3), (0, 390, 320, 610, 2),
    (330, 475, 165, 525, 4), (1115, 425, 160, 575, 1), (1260, 250, 190, 750, 3),
    (1440, 90, 205, 910, 0), (1080, 310, 140, 690, 2),
]

for index, (x, y, width, height, palette_index) in enumerate(near_buildings):
    base_color, accent_color = city_palette[palette_index]
    add_tower(draw, x, y, width, height, base_color, accent_color, 40 + index)
    roof_y = y - random.randrange(12, 35)
    draw.line((x + width * .32, roof_y, x + width, roof_y + 8), fill=(*accent_color, 150), width=3)

sign_font = ImageFont.truetype(str(FONT_PATH), 36)
small_font = ImageFont.truetype(str(FONT_PATH), 24)
add_vertical_sign(draw, 257, 385, 66, 206, "新宿", (255, 67, 178), sign_font)
add_vertical_sign(draw, 1320, 341, 61, 246, "東京", (53, 218, 239), sign_font)
add_vertical_sign(draw, 1120, 520, 54, 165, "夜景", (243, 110, 161), small_font)
add_vertical_sign(draw, 405, 590, 48, 132, "電脳", (79, 218, 241), small_font)

for sign_x, sign_y, sign_width, label, color in [
    (72, 567, 152, "TOKYO 24H", (245, 70, 178)),
    (1270, 672, 166, "NEON / CITY", (65, 216, 242)),
    (918, 600, 138, "サクラ", (248, 117, 161)),
]:
    draw.rounded_rectangle((sign_x, sign_y, sign_x + sign_width, sign_y + 40), radius=4, fill=(8, 12, 27, 225), outline=(*color, 235), width=2)
    draw.text((sign_x + sign_width // 2, sign_y + 20), label, font=small_font, fill=(*color, 255), anchor="mm")

vanishing_point = (800, 590)
road = [(560, 592), (1035, 592), (1600, 1000), (0, 1000)]
draw.polygon(road, fill=(8, 12, 26, 250))
draw.line((560, 592, 0, 1000), fill=(37, 173, 216, 125), width=4)
draw.line((1035, 592, 1600, 1000), fill=(239, 55, 156, 130), width=4)

light_trails = Image.new("RGBA", (WIDTH, HEIGHT))
trail_draw = ImageDraw.Draw(light_trails, "RGBA")
for trail_index in range(28):
    start_x = random.randrange(735, 870)
    end_x = random.randrange(-80, WIDTH + 80)
    end_y = random.randrange(755, HEIGHT + 80)
    trail_color = random.choice(((30, 211, 241, 195), (248, 47, 161, 205), (253, 174, 83, 170)))
    trail_width = random.choice((2, 3, 4, 6))
    trail_draw.line((start_x, vanishing_point[1] + random.randrange(10, 50), end_x, end_y), fill=trail_color, width=trail_width)
scene = Image.alpha_composite(scene, light_trails.filter(ImageFilter.GaussianBlur(10)))
scene = Image.alpha_composite(scene, light_trails)
draw = ImageDraw.Draw(scene, "RGBA")

for car_index in range(10):
    distance = random.random()
    car_y = 620 + round(distance * 260)
    car_width = 8 + round(distance * 40)
    car_x = random.randrange(max(0, 800 - car_y // 2), min(WIDTH - car_width, 800 + car_y // 2))
    car_color = random.choice(((57, 214, 239, 245), (241, 65, 164, 245), (255, 187, 98, 245)))
    draw.rounded_rectangle((car_x, car_y, car_x + car_width, car_y + max(4, car_width // 3)), radius=3, fill=car_color)
    draw.line((car_x - car_width, car_y + 8, car_x, car_y + 8), fill=(*car_color[:3], 125), width=2)

rain_layer = Image.new("RGBA", (WIDTH, HEIGHT))
rain_draw = ImageDraw.Draw(rain_layer, "RGBA")
for _ in range(520):
    rain_x = random.randrange(WIDTH)
    rain_y = random.randrange(HEIGHT)
    rain_length = random.randrange(8, 27)
    rain_draw.line((rain_x, rain_y, rain_x - 4, rain_y + rain_length), fill=(147, 198, 230, random.randrange(18, 73)), width=1)
scene = Image.alpha_composite(scene, rain_layer)

mist = Image.new("RGBA", (WIDTH, HEIGHT))
mist_draw = ImageDraw.Draw(mist, "RGBA")
mist_draw.ellipse((180, 600, 1420, 1060), fill=(81, 135, 171, 38))
mist_draw.ellipse((440, 530, 1200, 850), fill=(163, 57, 131, 26))
scene = Image.alpha_composite(scene, mist.filter(ImageFilter.GaussianBlur(65)))

vignette = Image.new("L", (WIDTH, HEIGHT), 0)
vignette_draw = ImageDraw.Draw(vignette)
vignette_draw.ellipse((-WIDTH * .2, -HEIGHT * .25, WIDTH * 1.2, HEIGHT * 1.25), fill=220)
vignette = vignette.filter(ImageFilter.GaussianBlur(100))
shade = Image.new("RGBA", (WIDTH, HEIGHT), (3, 7, 20, 110))
scene = Image.composite(scene, Image.alpha_composite(scene, shade), vignette)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
scene.convert("RGB").save(OUTPUT, quality=93, optimize=True)
print(f"Generated {OUTPUT}")