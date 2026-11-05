#!/usr/bin/env python3
"""Kuala Lumpur Living Pixel Farm (weather-aware, ordered seasonal animation).

The Kuala Lumpur weather and sunrise/sunset determine the rendered weather and
sun/moon. The four seasons are **fictional, decorative themes**, shown in their
natural order: spring -> summer -> autumn -> winter, 20 seconds each.

When invoked by GitHub Actions, the script refreshes assets/banner.svg and
assets/footer.svg. The seasons animate inside SVG between workflow updates.
GitHub Actions is not a real-time clock: sunrise/sunset and weather may lag by
roughly one scheduled update (or longer if GitHub delays the workflow).

Examples (no network needed when weather and daytime are both specified):
    python3 living_farm.py --weather stormy --daytime day
    python3 living_farm.py --weather cloudy --daytime night --season autumn
    python3 living_farm.py --weather auto --daytime auto

Requires Python 3.9+ and the existing generate.py in the same directory.
"""

import argparse
import copy
import json
import random
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

import generate as farm

BASE = Path(__file__).resolve().parent
OUT = BASE / "assets"
LATITUDE = 3.1390  # Public reference point for Kuala Lumpur, not a user's address
LONGITUDE = 101.6869
TIMEZONE = "Asia/Kuala_Lumpur"

SEASONS = ("spring", "summer", "autumn", "winter")
SEASON_HOLD_SECONDS = 8  # Change to 30 for a more relaxed garden
SEASON_TRANSITION_SECONDS = 2  # Gentle cross-fade at the end of each season

WEATHER_OPTIONS = (
    "sunny", "partly_cloudy", "cloudy", "drizzle", "rainy", "showers",
    "stormy", "windy", "foggy",
)

THUNDER_CODES = {95, 96, 99}
FOG_CODES = {45, 48}
DRIZZLE_CODES = {51, 53, 55, 56, 57}
RAIN_CODES = {61, 63, 65, 66, 67}
SHOWER_CODES = {80, 81, 82}
# Wind thresholds are illustrative visual-effect decisions, not weather alerts.
WIND_SPEED_THRESHOLD_KMH = 25.0
WIND_GUST_THRESHOLD_KMH = 40.0


@dataclass(frozen=True)
class Conditions:
    weather: str
    windy: bool
    sunrise: datetime
    sunset: datetime


def number(value, default=0.0):
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def classify_weather(current):
    """Assign a tropical-friendly visual category using Open-Meteo WMO codes.

    Priority: thunderstorms > precipitation > fog > strong wind > cloud cover.
    Strong wind can also animate alongside a rainy/thunderstorm scene.
    """
    code = int(number(current.get("weather_code"), 0))
    rain = number(current.get("precipitation"))
    clouds = number(current.get("cloud_cover"))
    windy = (number(current.get("wind_speed_10m")) >= WIND_SPEED_THRESHOLD_KMH
             or number(current.get("wind_gusts_10m")) >= WIND_GUST_THRESHOLD_KMH)

    if code in THUNDER_CODES:
        return "stormy", windy
    if code in SHOWER_CODES:
        return "showers", windy
    if code in RAIN_CODES:
        return "rainy", windy
    if code in DRIZZLE_CODES:
        return "drizzle", windy
    if rain > 0:
        return "rainy", windy
    if code in FOG_CODES:
        return "foggy", windy
    if windy:
        return "windy", True
    if code == 3 or clouds >= 80:
        return "cloudy", False
    if code == 2 or clouds >= 40:
        return "partly_cloudy", False
    return "sunny", False


def parse_conditions(data, timezone=TIMEZONE):
    """Parse forecast data, including *local* sunrise and sunset timestamps."""
    current = data["current"]
    weather, windy = classify_weather(current)
    zone = ZoneInfo(timezone)
    sunrise = datetime.fromisoformat(data["daily"]["sunrise"][0]).replace(tzinfo=zone)
    sunset = datetime.fromisoformat(data["daily"]["sunset"][0]).replace(tzinfo=zone)
    return Conditions(weather, windy, sunrise, sunset)


def fetch_conditions(latitude=LATITUDE, longitude=LONGITUDE, timezone=TIMEZONE):
    query = urlencode({
        "latitude": latitude,
        "longitude": longitude,
        "current": "weather_code,precipitation,cloud_cover,wind_speed_10m,wind_gusts_10m",
        "daily": "sunrise,sunset",
        "timezone": timezone,
        "forecast_days": 1,
        "wind_speed_unit": "kmh",
    })
    request = Request(
        "https://api.open-meteo.com/v1/forecast?" + query,
        headers={"User-Agent": "yx114-living-pixel-farm/3.0 (GitHub profile artwork)"},
    )
    with urlopen(request, timeout=30) as response:
        return parse_conditions(json.load(response), timezone)


def is_daytime(now, sunrise, sunset):
    return sunrise <= now < sunset


def modify_palette(base, season, weather):
    p = copy.deepcopy(base)
    night = p["night"]

    # These are aesthetic seasons, NOT actual seasons in Kuala Lumpur.
    if season == "spring":
        p["grass"] = "#8ad65a" if not night else "#4a8f4c"
        p["grass_dk"] = "#72c047" if not night else "#3a7a3d"
        p["grass_lt"] = "#a8e87a" if not night else "#5fa65c"
        p["tree_dk"] = "#d9739f" if not night else "#8a4a6a"
        p["tree_md"] = "#f09abd" if not night else "#a8607f"
        p["tree_lt"] = "#ffc9dc" if not night else "#c98aa5"
        p["flowers"] = ["#ff91bd", "#f9dd6d", "#ead1ff", "#fdf0f4"]
    elif season == "autumn":
        p["grass"] = "#b2a14e" if not night else "#777035"
        p["grass_dk"] = "#8d8637" if not night else "#58552e"
        p["grass_lt"] = "#d9b25b" if not night else "#a58e49"
        p["hill"] = "#929b49" if not night else "#62623a"
        p["hill_hi"] = "#a9ad5e" if not night else "#817a45"
        p["tree_dk"] = "#a45123" if not night else "#733921"
        p["tree_md"] = "#d8762e" if not night else "#97502a"
        p["tree_lt"] = "#efaa42" if not night else "#b7773b"
        p["flowers"] = ["#de7735", "#eeb33c", "#ffdfa0", "#c36b35"]
    elif season == "winter":
        p["grass"] = "#bfdce2" if not night else "#667e94"
        p["grass_dk"] = "#a0c4cf" if not night else "#4c6577"
        p["grass_lt"] = "#eff7fa" if not night else "#8dabc1"
        p["hill"] = "#b5d4dd" if not night else "#5a698b"
        p["hill_hi"] = "#d9edf3" if not night else "#8896b8"
        p["tree_lt"] = "#9fd3c8" if not night else "#6a9997"
        p["flowers"] = ["#fafcff", "#e0eff5", "#c9dfea", "#b0c9d8"]
    # Summer uses the original pixel-farm palette.

    if weather in {"cloudy", "drizzle", "rainy", "showers", "stormy", "foggy"}:
        if weather == "stormy":
            p["sky"] = (["#5e7b98", "#7389a2", "#8499ae", "#94aabe", "#a4b7c9", "#b4c7d4"]
                        if not night else ["#0a1130", "#111a3b", "#1a2448", "#253153", "#324060", "#40506b"])
        elif weather == "foggy":
            p["sky"] = (["#a6c4cb", "#b3cbd1", "#bdd3d6", "#c7dcdb", "#d1e5e2", "#dceae5"]
                        if not night else ["#243451", "#30405b", "#3a4b64", "#48586c", "#526274", "#5c6c7e"])
        elif weather == "cloudy":
            p["sky"] = (["#86b3d0", "#93bfd5", "#a2c9dc", "#b2d3e1", "#c0dce8", "#ccE4ec"]
                        if not night else ["#101a3c", "#182349", "#233052", "#2f3e60", "#3b496c", "#455675"])
        else:  # drizzle, rain, showers
            p["sky"] = (["#82aec6", "#91b9cc", "#a3c5d2", "#b1cdd8", "#c3d8dc", "#d0dfe1"]
                        if not night else ["#101938", "#172345", "#24314f", "#31405d", "#3c4c67", "#485974"])
        p["cloud"] = "#e0e9ed" if not night else "#65748d"
        p["cloud_sh"] = "#bfcbd4" if not night else "#4a5873"
    elif weather == "partly_cloudy":
        p["cloud"] = "#f8fbff" if not night else "#414f85"
    return p


def extra_weather_art(weather, windy, night, role):
    """SVG weather accents; keeps the large banner sign unobscured."""
    w, h = 225, (96 if role == "banner" else 52)
    rng = random.Random(20261105 + len(weather) * 101 + int(windy) + int(night))
    overlay = []
    precipitation = {"drizzle": 18, "rainy": 48, "showers": 75, "stormy": 90}
    if weather in precipitation:
        count = precipitation[weather] if role == "banner" else max(8, precipitation[weather] // 3)
        color = "#bedffb" if night else "#d9f2fb"
        length = 2 if weather == "drizzle" else 4
        drops = []
        for _ in range(count):
            x = rng.randint(2, w - 3)
            y = rng.randint(51, h - 5) if role == "banner" else rng.randint(27, h - 5)
            drops.append(f'<path d="M{x} {y}l-1 {length}" stroke="{color}" stroke-width=".8" opacity=".85"/>')
        overlay.append('<g class="rain-streaks">' + "".join(drops) + '</g>')

    if weather == "stormy":
        # Stylized bolt at the right edge, away from the name sign.
        x, y = (205, 30) if role == "banner" else (174, 12)
        overlay.append(f'<g class="lightning"><path d="M{x} {y}l-7 12h6l-4 11 13-16h-7l5-7z" '
                       'fill="#ffda5c" stroke="#fff6ae" stroke-width="1"/></g>')

    if weather == "foggy":
        overlay.append(f'<g class="mist"><rect x="0" y="{int(h * .62)}" width="225" '
                       f'height="{h - int(h * .62)}" fill="#edf4f2" opacity=".23"/></g>')

    if windy or weather == "windy":
        leaves = []
        for _ in range(10 if role == "banner" else 5):
            x = rng.randint(10, w - 15)
            y = rng.randint(55, h - 5) if role == "banner" else rng.randint(30, h - 5)
            col = ["#dfaa4f", "#c27c36", "#8bcf63"][rng.randrange(3)]
            leaves.append(f'<rect x="{x}" y="{y}" width="2" height="1" fill="{col}"/>')
        overlay.append('<g class="wind-leaves">' + "".join(leaves) + '</g>')

    if weather in {"cloudy", "stormy", "partly_cloudy"}:
        cloud_col = "#677a93" if night else ("#d0dce3" if weather != "partly_cloudy" else "#ffffff")
        # In the banner, top corners remain visible around the wooden sign.
        positions = [(11, 28), (188, 40)] if role == "banner" else [(110, 17), (180, 11)]
        blocks = []
        for x, y in positions[: (1 if weather == "partly_cloudy" else 2)]:
            blocks.append(f'<rect x="{x}" y="{y}" width="17" height="3" fill="{cloud_col}" opacity=".85"/>')
            blocks.append(f'<rect x="{x+3}" y="{y-2}" width="9" height="2" fill="{cloud_col}" opacity=".85"/>')
        overlay.append('<g class="weather-clouds">' + "".join(blocks) + '</g>')
    return "".join(overlay)


def render_scene(weather, season, night, windy, role):
    palette = modify_palette(farm.NIGHT if night else farm.DAY, season, weather)
    generated = farm.banner(palette) if role == "banner" else farm.footer(palette)
    inner = generated.split("</style>", 1)[1].rsplit("</svg>", 1)[0]

    # In dense cloud or rain, original twinkling stars would look out of place.
    if night and weather in {"cloudy", "drizzle", "rainy", "showers", "stormy", "foggy"}:
        inner = re.sub(r'<g class="t[12]">.*?</g>', "", inner)
    return inner + extra_weather_art(weather, windy, night, role)


def season_animation_css(hold=SEASON_HOLD_SECONDS, transition=SEASON_TRANSITION_SECONDS):
    """Ordered cycle, easing between scenes; no random jumps."""
    if hold <= 0 or not 0 < transition < hold:
        raise ValueError("Season hold must be positive and transition shorter than hold")
    duration = hold * len(SEASONS)
    slice_pct = 100 / len(SEASONS)
    fade_pct = 100 * transition / duration
    css = [".season{opacity:0}", ".season-0{opacity:1}"]

    for i in range(len(SEASONS)):
        start = i * slice_pct
        end = (i + 1) * slice_pct
        if i == 0:
            points = [
                (0, 1), (end - fade_pct, 1), (end, 0),
                (100 - fade_pct, 0), (100, 1),
            ]
        else:
            points = [
                (0, 0), (start - fade_pct, 0), (start, 1),
                (end - fade_pct, 1), (end, 0), (100, 0),
            ]
        frames = "".join(f"{percent:.4f}%{{opacity:{opacity}}}" for percent, opacity in points)
        css.append(f"@keyframes seasonfade{i}{{{frames}}}")
        css.append(f".season-{i}{{animation:seasonfade{i} {duration}s linear infinite}}")

    # Weather effects are not linked to the changing decorative seasons.
    css.extend([
        ".rain-streaks{animation:drop .8s linear infinite}",
        "@keyframes drop{0%{transform:translateY(-3px);opacity:.25}100%{transform:translateY(4px);opacity:1}}",
        ".wind-leaves{animation:breeze 3.6s ease-in-out infinite alternate}",
        "@keyframes breeze{from{transform:translateX(-5px)}to{transform:translateX(11px)}}",
        ".lightning{animation:flash 6s steps(1) infinite}",
        "@keyframes flash{0%,8%,11%,100%{opacity:0}9%,10%{opacity:1}}",
    ])
    return "".join(css)


def build_svg(role, weather, night, windy=False, fixed_season=None):
    if weather not in WEATHER_OPTIONS:
        raise ValueError(f"Unknown weather state: {weather}")
    w, h = 225, (96 if role == "banner" else 52)
    if fixed_season:
        if fixed_season not in SEASONS:
            raise ValueError(f"Unknown season: {fixed_season}")
        groups = f'<g>{render_scene(weather, fixed_season, night, windy, role)}</g>'
        css = season_animation_css()  # only weather animations are used here
    else:
        groups = "".join(
            f'<g class="season season-{i}">{render_scene(weather, season, night, windy, role)}</g>'
            for i, season in enumerate(SEASONS)
        )
        css = season_animation_css()
    label = weather.replace("_", " ").title()
    cycle_description = "Fixed " + fixed_season if fixed_season else "Decorative spring, summer, autumn, winter loop"
    description = (f"Adda's Kuala Lumpur pixel farm. {label} weather. "
                   f"{'Moon' if night else 'Sun'} based on local sunrise and sunset. {cycle_description}.")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w * 4}" height="{h * 4}" shape-rendering="crispEdges" '
        f'role="img" aria-label="Kuala Lumpur living pixel farm">'
        f'<title>Living Pixel Farm — {label}</title><desc>{description}</desc>'
        f'<style>{farm.CSS}{css}</style>{groups}</svg>'
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lat", type=float, default=LATITUDE)
    parser.add_argument("--lon", type=float, default=LONGITUDE)
    parser.add_argument("--tz", default=TIMEZONE)
    parser.add_argument("--weather", choices=("auto", "rain", *WEATHER_OPTIONS), default="auto")
    parser.add_argument("--daytime", choices=("auto", "day", "night"), default="auto")
    parser.add_argument("--season", choices=SEASONS, help="Freeze season for a preview")
    parser.add_argument("--wind", action="store_true", help="Preview wind effects")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    weather = args.weather
    night = args.daytime == "night"
    windy = args.wind
    if weather == "rain":
        weather = "rainy"  # Backward-compatible alias from your old script.

    if args.weather == "auto" or args.daytime == "auto":
        try:
            live = fetch_conditions(args.lat, args.lon, args.tz)
            now = datetime.now(ZoneInfo(args.tz))
        except Exception as exc:
            print(f"Weather lookup failed. Existing artwork was left untouched: {exc}", file=sys.stderr)
            return 1
        if args.weather == "auto":
            weather, windy = live.weather, (live.windy or windy)
        if args.daytime == "auto":
            night = not is_daytime(now, live.sunrise, live.sunset)
        print(f"KL sunrise {live.sunrise:%H:%M}, sunset {live.sunset:%H:%M}; "
              f"rendering {'night' if night else 'day'} ({weather})")

    args.out.mkdir(parents=True, exist_ok=True)
    for role in ("banner", "footer"):
        output = args.out / f"{role}.svg"
        svg = build_svg(role, weather, night, windy, args.season)
        if output.exists() and output.read_text(encoding="utf-8") == svg:
            print(f"Unchanged: {output}")
        else:
            output.write_text(svg, encoding="utf-8")
            print(f"Updated: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
