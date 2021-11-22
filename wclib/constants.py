from pathlib import Path

SIZE = (1024, 768)
ROOT_DIR = Path(__file__).parent.parent
ASSETS = ROOT_DIR / "wclib" / "assets"

TITLE_FONT = "title"

ACCENT = "#48929B"
BACKGROUND = "#151515"
LIGHT = "#EEEEEE"
GREY = "#8090A0"
OVERLAY = (0, 0, 0, 100)

CASUAL = "Casual"
AMBITOUS = "Ambitious"
ADVENTUROUS = "Adventurous"
DIFFICULTIES = [CASUAL, AMBITOUS, ADVENTUROUS]
DIFFICULY_COLOR = {
    CASUAL: "#F6EDD4",
    AMBITOUS: "#9B59B6",
    ADVENTUROUS: "#2980B9",
}
