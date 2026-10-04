"""Adds the Supply Insight card to Section 08 of app.py."""

import ast
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "app.py"

ANCHOR = (
    '        "sugar, because production data covers sugar cane."\n'
    "    )\n"
)

BLOCK = '''
    if pd.notna(dependency_value) and 0 <= float(dependency_value) <= 100:
        dep_pct = float(dependency_value)

        if dep_pct >= 70:
            insight_label = "HIGH IMPORT DEPENDENCY"
            insight_text = "India relies heavily on imports for this food's domestic supply."
            insight_pill = "coral"
        elif dep_pct >= 30:
            insight_label = "MODERATE IMPORT DEPENDENCY"
            insight_text = "Imports make up a meaningful share of this food's domestic supply."
            insight_pill = "cyan"
        else:
            insight_label = "LOW IMPORT DEPENDENCY"
            insight_text = "Most of this food's domestic supply comes from domestic production."
            insight_pill = "mint"

        render(
            f"""
            <div class="kpi">
            <div class="eyebrow">Supply Insight</div>
            <div style="margin:.55rem 0 .45rem;">
            <span class="pill {insight_pill}">{insight_label}</span>
            </div>
            <div class="kpi-sub">{insight_text}</div>

            <div style="display:flex;gap:2.4rem;margin-top:.85rem;">

            <div>
            <div class="kpi-label">Import share</div>
            <div class="kpi-value small" style="color:var(--mint);">
            {dep_pct:.2f}%
            </div>
            </div>

            <div>
            <div class="kpi-label">Domestic share</div>
            <div class="kpi-value small" style="color:var(--cyan);">
            {100 - dep_pct:.2f}%
            </div>
            </div>

            </div>
            </div>
            """
        )
'''

with open(path, encoding="utf-8", newline="") as f:
    src = f.read()

crlf = "\r\n" in src
src = src.replace("\r\n", "\n")

if "SUPPLY INSIGHT" in src or "Supply Insight" in src:
    sys.exit("Supply Insight already present. Nothing changed.")

if src.count(ANCHOR) != 1:
    sys.exit(
        f"Anchor found {src.count(ANCHOR)} times (expected 1). Nothing changed."
    )

new = src.replace(ANCHOR, ANCHOR + BLOCK)

ast.parse(new)

if crlf:
    new = new.replace("\n", "\r\n")

with open(path, "w", encoding="utf-8", newline="") as f:
    f.write(new)

print("Done: Supply Insight card added to", path)