#!/usr/bin/env python3
"""Render the Notion page from the repo.

The repo is the source of truth; the Notion page is a generated view of it.
This writes notion_page.md, which is then applied to the page with
notion-update-page (command: replace_content). Do not hand-edit the Notion
table - the next build overwrites it.

Two Notion quirks are handled here:
  * Notion auto-links bare domains, which mangles surrounding bold markers,
    so URLs are only ever emitted inside a proper [label](url).
  * A cell must not contain a raw newline, or the table row breaks.
"""
import json, re, sys

V = json.load(open("venues.json", encoding="utf-8"))
M = json.load(open("meta.json", encoding="utf-8"))

LINK = re.compile(r"\[[^\]]*\]\([^)]*\)")
DOMAIN = re.compile(r"(?<![\w/@.`])((?:[a-z0-9][a-z0-9-]*\.)+(?:de|com|org|net|eu|berlin|io))(?![\w`])")

def cell(s):
    """One table cell: collapse whitespace, never emit a bare newline.

    Notion auto-links bare domains, and when one sits inside a bold run the
    surrounding ** markers come apart - it turned "**their own site
    saunabad-berlin.de is dead**" into mangled markup last time. Bare domains
    are wrapped in backticks so Notion leaves them alone; real links are masked
    first so their targets are untouched.
    """
    s = re.sub(r"\s+", " ", (s or "").strip())
    if not s:
        return "—"
    keep = []
    def mask(m):
        keep.append(m.group(0)); return f"\x00{len(keep)-1}\x00"
    s = LINK.sub(mask, s)
    s = DOMAIN.sub(lambda m: f"`{m.group(1)}`", s)
    return re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], s)

def place(v):
    return f"[{v['name']}]({v['url']})" if v.get("url") else v["name"]

def facilities(v):
    # Who throws the water leads, because it is the distinction that decides
    # whether a Finn would call the place a sauna at all.
    bits = [f"**{v['loylyText']}.**", v["sauna"]]
    if v.get("aufgussScore") is not None:
        bits.append(f"Aufguss rated {v['aufgussScore']}/10.")
    already = re.search(r"aufguss|aroma", v["sauna"], re.I)
    if v.get("aufgussNote") and not already:
        kind = {"scheduled": "Aufguss", "self": "Aufguss (self-serve)",
                "request": "Aufguss on request", "auto": "Aroma"}.get(v["aufguss"], "Aufguss")
        bits.append(f"{kind}: {v['aufgussNote']}")
    elif v.get("aufguss") == "self" and not already:
        bits.append("Aufguss is self-serve")
    if v.get("heatSrc"):
        bits.append(f"*({v['heatSrc']})*")
    return " ".join(bits)

def status(v):
    bits = [v["hours"]]
    src = (v.get("open") or {}).get("src")
    if src == "osm":
        bits.append("(hours from OpenStreetMap)")
    elif src == "listed":
        bits.append("(hours as published, not re-verified)")
    if v.get("flag"):
        # Label the note in bold rather than bolding the whole sentence. A code
        # span inside a bold run collides into "****" in Notion, which is how
        # the Saunabad cell came back mangled; keeping the body unbolded means
        # backticked domains and bold markers never meet.
        bits.append(f"**Heads up:** {v['flag']}")
    return " ".join(bits)

def best(v):
    return f"**{v['bestFor']}**" if v.get("badge") else v["bestFor"]

HEAD = ["Place", "Type", "Cash / separate access", "USC",
        "Sauna and facilities", "Pool / cold", "Hours / status", "Best for"]

out = []
out.append('<callout icon="♨️" color="blue_bg">')
out.append(f"\tBerlin sauna shortlist combining hotel day spas, Urban Sports Club options, and "
           f"regular standalone saunas. **Last checked: {M['lastChecked']}.** Cabin temperatures and "
           f"Aufguss practice were confirmed by the venues themselves by email. Prices, USC limits and "
           f"opening hours change often, so recheck before making a special trip. "
           f"**This page is generated from the berlin-sauna-map repository — edits made here are "
           f"overwritten by the next build.**")
out.append("</callout>")
out.append('<table fit-page-width="true" header-row="true">')
out.append("<tr>")
out += [f"<td>{h}</td>" for h in HEAD]
out.append("</tr>")
for v in V:
    out.append("<tr>")
    for c in (place(v), v["kind"], v["priceLabel"], v["uscLabel"],
              facilities(v), v["pool"], status(v), best(v)):
        out.append(f"<td>{cell(c)}</td>")
    out.append("</tr>")
out.append("</table>")
out.append("## Fast picks")
for label, name in M["picks"]:
    out.append(f"- **{label}:** {name}")
out.append("## Practical note")
out.append(M["practical"])

# Reviews live on the site, not here: they arrive through GitHub issues and are
# joined onto venues at build time, so a Notion column would be a fourth copy.
out.append("## Scores")
scored = [v for v in V if v.get("finnish") is not None]
au = [v for v in V if v.get("aufgussScore") is not None]
out.append("**Finnish score** rates each place as a sauna out of 10 \u2014 heat, l\u00f6yly, and "
           "whether you are allowed to throw water \u2014 judged by a Finn, not by the spa around it. "
           + (", ".join(f"{v['name']} {v['finnish']}/10" for v in scored) + "."
              if scored else "Nothing scored yet."))
out.append("**Aufguss rating** applies only where someone throws for you; it is meaningless "
           "where you pour your own. "
           + (", ".join(f"{v['name']} {v['aufgussScore']}/10" for v in au) + "."
              if au else "Nothing rated yet."))
n_staff = sum(1 for v in V if v["loyly"] == "staff")
n_self = sum(1 for v in V if v["loyly"] == "self")
n_mach = sum(1 for v in V if v["loyly"] == "machine")
out.append(f"Of the {len(V)} venues, {n_staff} run a staff Aufguss, {n_self} let you throw your "
           f"own, {n_mach} only dose aroma automatically, and the rest have not said.")
out.append("## Reviews")
n = sum(len(v.get("reviews", [])) for v in V)
who = ", ".join(r["name"] for r in M["reviewers"].values())
out.append(f"{n} review{'' if n == 1 else 's'} from a panel of "
           f"{len(M['reviewers'])} ({who}). They are shown on the site, "
           f"under each venue. To join the panel or post a review, open an issue: "
           f"`github.com/jommi9/berlin-sauna-map/issues/new/choose`")

doc = "\n".join(out) + "\n"
open("notion_page.md", "w", encoding="utf-8").write(doc)

rows = doc.count("<tr>") - 1
bad = [l for l in doc.splitlines() if l.startswith("<td>") and ("\n" in l or l == "<td></td>")]
print(f"notion_page.md written: {rows} venue rows, {len(doc)} chars")
if rows != len(V):
    print(f"  ! expected {len(V)} rows"); sys.exit(1)
if bad:
    print(f"  ! {len(bad)} malformed cells"); sys.exit(1)
print("  structure OK")
