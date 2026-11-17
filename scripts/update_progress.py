"""Counts ticked books in README.md and redraws the progress block at the top."""
import re
from pathlib import Path

readme = Path(__file__).resolve().parent.parent / "README.md"
text = readme.read_text(encoding="utf-8")

ITEM = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+(.*?)<!--\s*([\w-]+)\s*-->", re.M)
ROUTINE_ID = re.compile(r"^r\d")

levels = []
for chunk in re.split(r"^## ", text, flags=re.M)[1:]:
    title = chunk.splitlines()[0].strip()
    if not title.lower().startswith("level"):
        continue
    core = [m for m in ITEM.finditer(chunk)
            if not ROUTINE_ID.match(m.group(3)) and "(bonus)" not in m.group(2)]
    done = sum(1 for m in core if m.group(1).lower() == "x")
    levels.append((title, done, len(core)))

total = sum(t for _, _, t in levels)
done = sum(d for _, d, _ in levels)
pct = round(100 * done / total) if total else 0
filled = round(20 * done / total) if total else 0
bar = "█" * filled + "░" * (20 - filled)

rows = "\n".join(
    f"| {title} | {d} of {t} | {'✅' if d == t else ''} |" for title, d, t in levels
)
block = (
    "<!-- progress:start -->\n"
    f"**{done} of {total} core books read ({pct}%)**\n\n"
    f"`{bar}`\n\n"
    "| Level | Core books read | |\n|---|---|---|\n"
    f"{rows}\n"
    "<!-- progress:end -->"
)

new = re.sub(r"<!-- progress:start -->.*?<!-- progress:end -->", block, text, flags=re.S)
if new != text:
    readme.write_text(new, encoding="utf-8")
    print(f"Progress updated: {done}/{total}")
else:
    print("No change")
