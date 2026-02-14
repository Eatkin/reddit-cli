import os

_themes_dir = os.path.join(os.path.dirname(__file__), "themes")
THEMES = {
    os.path.splitext(filename)[0]: os.path.join(_themes_dir, filename)
    for filename in os.listdir(_themes_dir)
    if filename.endswith(".tcss")
}

if not THEMES:
    raise ValueError(f"No themes found in {_themes_dir}. Please add at least one .tcss file to the themes directory.")