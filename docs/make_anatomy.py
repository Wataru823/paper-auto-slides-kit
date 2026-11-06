"""Draw the layout anatomy diagram used in the README (Pillow)."""

from PIL import Image, ImageDraw, ImageFont

W, H = 1720, 960
BG = "#ffffff"
INK = "#101a3d"
MUTED = "#6b7490"
CARD = "#f4f6fa"
LINE = "#dfe3ec"
ACCENT = "#00b34a"

img = Image.new("RGB", (W, H), "#eef1f7")
d = ImageDraw.Draw(img)


def font(size, bold=False):
    paths = [
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc" if bold else "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def label(x, y, text, size=26, color=MUTED, bold=False):
    d.text((x, y), text, font=font(size, bold), fill=color)


SLIDE = (60, 90, W - 300, H - 90)
d.rounded_rectangle(SLIDE, radius=18, fill=BG, outline=LINE, width=2)

band = (SLIDE[0], SLIDE[1], SLIDE[2], SLIDE[1] + 62)
d.rectangle(band, fill="#101a3d")
d.rectangle((band[2] - 320, band[1], band[2] - 150, band[1] + 62), fill="#1b3a6b")
label(band[0] + 28, band[1] + 16, "04  METHOD", 24, "#ffffff", True)

left = SLIDE[0] + 46
top = band[3] + 46
label(left, top, "タイトル", 22, ACCENT, True)
label(left, top + 30, "作り方は4ステップ", 44, INK, True)

label(left, top + 110, "claim（言いたいこと1文）", 22, ACCENT, True)
label(left, top + 142, "つまり、型に流し込むと迷わない", 30, "#2b3557", True)

body_top = top + 210
body_bottom = SLIDE[3] - 120
d.rounded_rectangle((left, body_top, SLIDE[2] - 46, body_bottom), radius=14,
                    fill=CARD, outline=LINE, width=2)
label(left + 28, body_top + 22, "本文ブロック", 22, MUTED, True)
label(left + 28, body_top + 56, "図 ／ 表 ／ 動画 のどれかを必ず1つ", 26, INK)
label(left + 28, body_top + 96, "箇条書きは3項目まで", 26, INK)
label(left + 28, body_top + 136, "文字サイズ・余白は全スライドで固定", 26, INK)

foot_y = SLIDE[3] - 54
d.line((left, foot_y - 18, SLIDE[2] - 46, foot_y - 18), fill=LINE, width=2)
label(left, foot_y, "ブランド", 20, "#98a0b6")
right_text = "ページ番号  04 / 08"
tw = d.textlength(right_text, font=font(20))
label(SLIDE[2] - 46 - tw, foot_y, right_text, 20, "#98a0b6")

# callouts
label(SLIDE[2] + 26, band[1] + 16, "セクションバー", 21, MUTED)
label(SLIDE[2] + 26, top + 34, "見出し", 21, MUTED)
label(SLIDE[2] + 26, top + 146, "結論（claim）", 21, MUTED)
label(SLIDE[2] + 26, body_top + 20, "本文＋図表", 21, MUTED)
label(SLIDE[2] + 26, foot_y - 4, "フッター", 21, MUTED)

img.save("docs/layout-anatomy.png")
print("docs/layout-anatomy.png", img.size)
