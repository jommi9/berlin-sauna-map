# -*- coding: utf-8 -*-
"""Helsinki: every fact about its venues. This file is the source of truth.

A first, naive map, made on 15 November 2026. Every venue here passed
engine/verify_venue.py against its own site that day, and every price and
opening hour was read off that site, never off a list. Coordinates are the
venue's own node or building in OpenStreetMap.

Not yet filled in, and left empty rather than guessed: who throws the water at
most places (their pages do not say it in so many words), cabin temperatures,
the Finnish scores, the picks, photographs. Allas publishes its ticket prices
only through a script, and Löyly and Kulttuurisauna keep hours that change
from day to day, so those three have no price or no hours here.
"""

# name, lat, lon, kind, district, price(from|None), priceLabel, usc, uscLabel,
# sauna, pool, hours, bestFor, badge, flag, url
V = [
 ["Löyly",60.152121,24.930332,"Public sauna & restaurant","Hernesaari",29,"€29 / 2h · extra hour €12 · towel and shower things included","no","",
  "A smoke sauna (18 m²) and a wood-heated sauna (22 m²), both single-fired, about 20 bathers each","The sea, from the terrace, all year if the weather allows","Daily, roughly from noon to 22:00; the times change by day, so check their page","Smoke sauna by the sea",None,
  "The saunas are mixed, so swimwear is required (rental €8). Booking ahead is recommended.",
  "https://www.loylyhelsinki.fi/yleinensauna"],
 ["Allas Sea Pool",60.167105,24.957993,"Sea pool & saunas","Katajanokka",None,"Ticket prices on their site","no","",
  "Saunas beside the pools","A heated pool and a seawater pool","Mon–Fri 06:30–21:00 · Sat–Sun 08:00–21:00; ticket sales end an hour before closing","Swim in the harbour, then a sauna",None,None,
  "https://www.allaspool.fi/"],
 ["Kotiharjun sauna",60.186511,24.957341,"Public sauna","Kallio",16,"€16 · reduced €13 · 10 visits €140 · towel €4 · full wash €15 (Thu & Sat)","no","",
  "Helsinki's last wood-heated neighbourhood sauna: separate men's and women's public saunas, plus an electric sauna for hire","No pool; you cool off on the pavement out front","Tue–Sun 14:00–20:00, bathe until 21:30 · closed Mon","The classic wood-heated public sauna",None,None,
  "https://www.kotiharjunsauna.fi/"],
 ["Uusi Sauna",60.159356,24.918119,"Public sauna & bar","Jätkäsaari",18,"€18 · towel €5 · no booking needed","no","",
  "Separate men's and women's saunas heated with wood pellets, about 20 bathers each, and an electric mixed sauna","No pool; a terrace for cooling off","Tue–Fri 17:00–24:00 · Sat 16:00–24:00 · Sun 16:00–23:00 · closed Mon","A public sauna with a bar",None,None,
  "https://www.uusisauna.fi/"],
 ["Kulttuurisauna",60.17804,24.963281,"Public sauna","Merihaka",17,"€17 / 90 min · reduced €13 · 7 visits €77 · cards only","no","",
  "Wood- and pellet-heated, one single-fired mass stove; Friday evenings are silent","The sea, and an ice hole in winter","Mornings Fri–Sun 08:00–11:30, walk in · evenings Wed–Sun 16:00–20:00, booked ahead","A quiet sauna on the water",None,
  "No groups: more than two people count as one and are not admitted. Bring your own towel.",
  "https://kulttuurisauna.fi/"],
 ["Sompasauna",60.180751,24.998883,"Free community sauna","Kalasatama",0,"Free; donations welcome","no","",
  "Run by volunteers with no staff: whoever comes heats it. Mixed, and clothing is up to you","The sea","Always open","A free sauna you heat yourself",None,
  "No running water, showers or changing rooms. Bring drinking water, a towel and a padlock for the lockers.",
  "https://sompasauna.fi/"],
 ["Sauna Hermanni",60.193507,24.965028,"Public sauna","Hermanni",14,"€14 · reduced €10 · 10 visits €110 · towel €4","no","",
  "Separate men's (30 bathers) and women's (20) sides, heated with IKI stoves; a public sauna since the 1950s","No pool","Mon, Wed–Fri 15:00–20:00 · Sat 14:00–18:00, bathe for an hour after · closed Tue & Sun","An old-school neighbourhood sauna",None,None,
  "https://www.saunahermanni.fi/"],
]

# --- Opening hours, as in berlin/venues.py: Mon..Sun, [open, close] in minutes,
#     ending at the last entry where the venue gives one.
D = lambda a, b: [[a, b]] * 7
OPEN = {
 "Allas Sea Pool": {"weekly": [[390, 1200]] * 5 + [[480, 1200]] * 2, "src": "venue"},
 "Kotiharjun sauna": {"weekly": [None] + [[840, 1200]] * 6, "src": "venue"},
 "Uusi Sauna": {"weekly": [None] + [[1020, 1440]] * 4 + [[960, 1440], [960, 1380]], "src": "venue"},
 "Sompasauna": {"weekly": D(0, 1440), "src": "venue"},
 "Sauna Hermanni": {"weekly": [[900, 1200], None, [900, 1200], [900, 1200], [900, 1200], [840, 1080], None], "src": "venue"},
}

# --- Who throws the water, where the venue's own page says it.
HEAT = {
 "Sompasauna": (None, "self", "Nobody works there; whoever comes heats the stove and throws the water"),
}
HEAT_SOURCE = "read off the venue's own page, 15 Nov 2026"

LAST_CHECKED = "15 November 2026"
