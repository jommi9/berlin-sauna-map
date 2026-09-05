#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-read what the venues publish, and update build_venues.py where it is proven.

This is the part that lets the map keep itself current. verify_venue.py asks
"is this venue alive"; watch_changes.py asks "did something move"; this asks
"did something move in a way I can prove, and can I therefore fix it myself".

Proof means an anchor from sources.py matching EXACTLY ONCE on the venue's own
page. Anything less is reported and left alone.

Three guardrails, because an unattended writer that is wrong is worse than one
that does nothing:

  * a price may not move by more than half or more than double - a
    misparse fails loudly rather than quietly writing 6 EUR over 22 EUR;
  * if more than MAX_CHANGES venues change in one run, nothing is applied,
    because five venues rarely all reprice on the same Monday and a broken
    parser looks exactly like that;
  * every edit asserts its target appears exactly once before replacing it,
    the rule CLAUDE.md already imposes on venue data by hand.

Exit 0 = nothing to do or changes applied cleanly. Exit 1 = a human is needed.
Use --dry-run to see what it would do without touching the file.
"""
import datetime, json, re, sys, unicodedata, urllib.request
import concurrent.futures as cf
import sources

UA = {"User-Agent": "berlin-sauna-map/1.0 (personal project; https://github.com/jommi9/berlin-sauna-map)"}
MAX_CHANGES = 4
DRY = "--dry-run" in sys.argv
TODAY = datetime.date.today()

def norm(s):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s)
                  .replace("–", "-").replace("—", "-"))

def page_text(url):
    raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40)\
            .read(1_200_000).decode("utf-8", "replace")
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S | re.I)
    return norm(re.sub(r"<[^>]+>", " ", body))

def once(pattern, text):
    """Proof means the page states one value, not that it states it once.

    A price repeated in a summary box and again in the table is the same claim
    twice; two DIFFERENT values under the same label is the ambiguity that
    matters. So this collapses identical matches and refuses only real conflict.
    """
    ms = list(re.finditer(pattern, text))
    if not ms:
        return None
    if len({m.groups() for m in ms}) != 1:
        return None
    return ms[0]

def frag_re(template):
    """The priceLabel fragment as a pattern, so 'EUR {}' cannot match the '2' of
    '22'. The amount is captured, everything else stays literal, and a trailing
    digit or separator disqualifies the match."""
    tok = "\x00AMT\x00"
    return (re.escape(template.replace("{}", tok))
            .replace(re.escape(tok), r"(\d{1,4}(?:[.,]\d{1,2})?)") + r"(?![\d.,])")

def amount(s):
    return float(s.replace(",", "."))

def money(f):
    """Back to the notation build_venues.py uses: 27.5 -> '27.5', 22.0 -> '22'."""
    return f"{f:g}"

def label_money(f):
    """priceLabel keeps trailing cents: 27.5 -> '27.50', 22.0 -> '22'."""
    return f"{f:.2f}" if f % 1 else f"{f:.0f}"

venues = {v["name"]: v for v in json.load(open("venues.json", encoding="utf-8"))}
src = open("build_venues.py", encoding="utf-8").read()
changes, problems, notes = [], [], []

def fetch(name):
    try:
        return name, page_text(venues[name]["url"]), None
    except Exception as e:
        return name, None, f"{type(e).__name__}"

targets = sorted(set(sources.PRICES) | set(sources.CLOSURES))
pages = {}
with cf.ThreadPoolExecutor(6) as ex:
    for name, txt, err in ex.map(fetch, targets):
        if err:
            problems.append(f"{name}: could not read its page ({err})")
        else:
            pages[name] = txt

# ---------- prices ----------
for name, rules in sources.PRICES.items():
    txt = pages.get(name)
    if txt is None:
        continue
    label = venues[name]["priceLabel"]
    for template, headline, pattern in rules:
        m = once(pattern, txt)
        if not m:
            n = len(re.findall(pattern, txt))
            problems.append(f"{name}: anchor for {template.format('N')!r} matched "
                            f"{n} times, not once - not proof, left alone")
            continue
        new = amount(m.group(1))
        lm = list(re.finditer(frag_re(template), label))
        if len(lm) != 1:
            problems.append(f"{name}: {template.format('N')!r} matches our own price text "
                            f"{len(lm)} times - anchor and label have drifted apart")
            continue
        old_frag, old_val = lm[0].group(0), amount(lm[0].group(1))
        if abs(old_val - new) < 0.005:
            continue
        if not (0.5 * old_val <= new <= 2 * old_val):
            problems.append(f"{name}: {template.format('N')} would go {old_val:g} -> {new:g}, "
                            f"too big a jump to trust a parser with")
            continue
        changes.append({"venue": name, "what": template.format("N"),
                        "old": old_val, "new": new, "headline": headline,
                        "old_frag": old_frag, "new_frag": template.format(label_money(new)),
                        "evidence": norm(m.group(0)), "url": venues[name]["url"]})

# ---------- dated closures the venue publishes ----------
for name, pattern in sources.CLOSURES.items():
    txt = pages.get(name)
    if txt is None:
        continue
    m = once(pattern, txt)
    if not m:
        notes.append(f"{name}: no closure notice on the page now "
                     f"(matched {len(re.findall(pattern, txt))} times)")
        continue
    d, mo, y = (int(x) for x in m.groups())
    y += 2000 if y < 100 else 0
    try:
        until = datetime.date(y, mo, d)
    except ValueError:
        problems.append(f"{name}: closure notice has an impossible date {m.group(0)!r}")
        continue
    cur = (venues[name].get("open") or {}).get("closedUntil")
    if cur == until.isoformat():
        continue
    if until < TODAY:
        notes.append(f"{name}: its notice says {until} which has passed - the venue is "
                     f"reopening and the page has not caught up; leaving for a human")
        continue
    changes.append({"venue": name, "what": "closedUntil", "old": cur, "new": until.isoformat(),
                    "headline": False, "old_frag": f'"closedUntil": "{cur}"',
                    "new_frag": f'"closedUntil": "{until.isoformat()}"',
                    "evidence": norm(m.group(0)), "url": venues[name]["url"]})

# ---------- report ----------
for c in changes:
    print(f"CHANGED  {c['venue']}: {c['what']}  {c['old']} -> {c['new']}")
    print(f"           its page says: \"{c['evidence']}\"")
    print(f"           {c['url']}")
for p in problems:
    print(f"!!       {p}")
for n in notes:
    print(f"note     {n}")

if not changes:
    print(f"\nnothing provable changed ({len(problems)} anchor problem(s))")
    sys.exit(1 if problems else 0)

if len(changes) > MAX_CHANGES:
    print(f"\nREFUSED: {len(changes)} changes in one run (limit {MAX_CHANGES}). That is the "
          f"shape of a broken parser, not of a week's price rises. Nothing written.")
    sys.exit(1)

# ---------- apply ----------
def replace_once(text, old, new, why):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"REFUSED: {why}: {old!r} appears {n} times in build_venues.py, "
                         f"expected exactly once. Nothing written.")
    return text.replace(old, new)

for c in changes:
    if c["what"] == "closedUntil":
        src = replace_once(src, c["old_frag"], c["new_frag"], c["venue"])
        continue
    # The price fragment must be edited inside this venue's own row, so the row
    # is isolated first - "EUR 22 / 4h" occurs at both KIEZ SAUNA and Olivin.
    i = src.index(f'["{c["venue"]}",') if f'["{c["venue"]}",' in src else src.index(f'"{c["venue"]}"')
    j = src.index("\n ][", i) if "\n ][" in src[i:i+4000] else src.index('"],\n', i) + 4
    row = src[i:j]
    new_row = replace_once(row, c["old_frag"], c["new_frag"], f"{c['venue']} price text")
    if c["headline"]:
        old_num, new_num = money(c["old"]), money(c["new"])
        new_row = replace_once(new_row, f",{old_num},\"", f",{new_num},\"",
                               f"{c['venue']} headline price")
    src = src[:i] + new_row + src[j:]

stamp = TODAY.strftime("%-d %B %Y")
src = replace_once(src, re.search(r'LAST_CHECKED = "[^"]+"', src).group(0),
                   f'LAST_CHECKED = "{stamp}"', "last-checked stamp")

if DRY:
    print(f"\n--dry-run: {len(changes)} change(s) not written")
    sys.exit(0)

open("build_venues.py", "w", encoding="utf-8").write(src)
print(f"\nwrote {len(changes)} change(s) into build_venues.py, stamped {stamp}")
sys.exit(1 if problems else 0)
