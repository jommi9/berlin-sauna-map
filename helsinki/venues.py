# -*- coding: utf-8 -*-
"""Helsinki: every fact about its venues. This file is the source of truth.

First made as a naive map on 15 November 2026 and filled out on 25 November
2026, when every venue's own site was read again. Every venue here passed
engine/verify_venue.py against its own site, and every price, opening hour,
temperature and word about who throws the water was read off that site, never
off a list. Coordinates are the venue's own node or building in OpenStreetMap.

Added on 25 November: Lapinlahden Lähteen sauna, Löylykontti Sörnäinen,
Yrjönkadun uimahalli and Lonnan sauna. Lonna is shut for the winter; its site
says only that the island opens again in May 2027, so its closedUntil is the
last day it is certainly shut, and its coordinates are the one sauna building
OpenStreetMap has on the islet, which carries no name there.

Changed on 25 November: Allas now prints its ticket prices and its sauna
temperatures in the page itself; Löyly and Kulttuurisauna now give fixed weekly
hours. Both keep a morning turn as well as the main one on some days, and the
map takes one window a day, so OPEN holds the main window and the morning turn
is only in the hours text.

Looked at and left out:
- Kaurilan Sauna: its own story page says the public sauna was founded in Vanha
  Meilahti in 2009 and that sauna operations were suspended in 2020, when the
  premises had to be given up, with a search for new ones under way;
  kaurilansauna.fi is now a natural cosmetics shop. (Re-read 25 November.)
- Sauna Arla: arlansauna.net could not be reached on 25 November, so nothing
  about it is confirmed.
- Kyrö Sauna Bar: its page now redirects to the distillery's visitor-centre
  page on another site, which could not be read; not confirmed.
- Private hire only, no single entry: Merihaka Sauna, Urbansauna Kallio,
  Teurastamon sauna, Pasilan Saunatilat, red s Tilaussauna, Saunalautta Hiisi,
  Tamminiemen sauna and the island booking saunas.
- Swimming-hall changing-room saunas other than Yrjönkatu, the two gay saunas
  (a different kind of venue from what these maps list) and the winter-swimming
  club saunas that need membership.

Still empty, rather than guessed: who throws the water at Löyly, Uusi Sauna,
Kulttuurisauna, Sauna Hermanni, Lapinlahti, Löylykontti, Yrjönkatu and Lonna
(their pages do not say it in words); cabin temperatures everywhere but Allas
and Yrjönkatu; every plunge figure (Allas shows the day's sea temperature, which
is a reading and not a fixed figure); the Finnish scores and the picks.
"""

# name, lat, lon, kind, district, price(from|None), priceLabel, usc, uscLabel,
# sauna, pool, hours, bestFor, badge, flag, url
V = [
 ["Löyly",60.152121,24.930332,"Public sauna & restaurant","Hernesaari",29,"€29 / 2h · extra hour €12 · towel, seat cover, shampoo and soap included","no","",
  "A smoke sauna (18 m²) and a wood-heated sauna (22 m²), both single-fired, about 20 bathers each","The sea, from the terrace, all year if the weather allows","Mon, Tue & Thu 12:00–22:00 · Wed 09:00–11:00 & 13:00–22:00 · Fri 13:00–23:00 · Sat 09:00–11:00 & 13:00–23:00 · Sun 11:00–21:00","Smoke sauna by the sea",None,
  "The saunas are mixed, so swimwear is required (rental €8). Booking ahead is recommended.",
  "https://www.loylyhelsinki.fi/yleinensauna"],
 ["Allas Sea Pool",60.167105,24.957993,"Sea pool & saunas","Katajanokka",19,"€19 / 2h Mon–Thu and Fri until 14:00 · €24 from Fri 14:00, at weekends and on holidays · students, pensioners, conscripts and unemployed €14 / €18 · 10 visits €158","no","",
  "Five saunas","A heated 25 m pool at 27°C and a seawater pool, both open all year; a children's pool in summer","Mon–Fri 06:30–21:00 · Sat–Sun 08:00–21:00; ticket sales end an hour before closing, swimming and sauna 20 minutes before","Swim in the harbour, then a sauna",None,
  "Swimwear is required in the mixed saunas, and a towel is not included (rental €8.90). The floating saunas take turns shut for upkeep until 12:00: the mixed one on Mondays, the men's on Tuesdays, the women's on Wednesdays.",
  "https://www.allaspool.fi/altaat-ja-saunat/"],
 ["Kotiharjun sauna",60.186511,24.957341,"Public sauna","Kallio",16,"€16 · reduced €13 · 10 visits €140 · 5 visits €75 · towel €4 · full wash €15 (Thu & Sat)","no","",
  "Helsinki's last wood-heated neighbourhood sauna: separate men's and women's public saunas with single-fired stoves, plus an electric sauna for hire","No pool; you cool off on the pavement out front","Tue–Sun 14:00–20:00, bathe until 21:30 · closed Mon","The classic wood-heated public sauna",None,
  "No booking for the public saunas. The men's sauna is used naked; you may wrap a towel around you.",
  "https://www.kotiharjunsauna.fi/"],
 ["Uusi Sauna",60.159356,24.918119,"Public sauna & bar","Jätkäsaari",18,"€18, seat cover included · towel €5 · bathrobe €8 · no booking needed","no","",
  "Separate men's and women's saunas heated with wood pellets, about 20 bathers each, and an electric mixed sauna for 10 to 15","No pool; a terrace for cooling off","Tue–Fri 17:00–24:00 · Sat 16:00–24:00 · Sun 16:00–23:00 · closed Mon","A public sauna with a bar",None,None,
  "https://www.uusisauna.fi/"],
 ["Kulttuurisauna",60.17804,24.963281,"Public sauna","Merihaka",17,"€17 / 90 min · reduced €13 · 7 visits €77 · cards only","no","",
  "Wood- and pellet-heated, one single-fired mass stove; Friday evenings are silent","The sea, and an ice hole in winter","Evenings Wed–Sun 16:00–20:00, booked ahead, last entry 18:45 · mornings Fri–Sun 08:00–11:30, walk in, last entry 10:30 · closed Mon & Tue","A quiet sauna on the water",None,
  "No groups: more than two people count as one and are not admitted. Bring your own towel, a seat towel and a water bottle.",
  "https://kulttuurisauna.fi/"],
 ["Sompasauna",60.180751,24.998883,"Free community sauna","Kalasatama",0,"Free; donations welcome","no","",
  "Run by volunteers with no staff: whoever comes heats it. Mixed, and clothing is up to you","The sea","Always open","A free sauna you heat yourself",None,
  "No running water, showers or changing rooms. Bring drinking water, a towel and a padlock for the lockers.",
  "https://sompasauna.fi/"],
 ["Sauna Hermanni",60.193507,24.965028,"Public sauna","Hermanni",14,"€14 · reduced €10 · under 15 free · 10 visits €110 · 5 visits €60 · towel €4","no","",
  "Separate men's (30 bathers) and women's (20) sides, heated with IKI stoves; a public sauna since the 1950s","No pool","Mon, Wed–Fri 15:00–20:00 · Sat 14:00–18:00, bathe for an hour after · closed Tue & Sun","An old-school neighbourhood sauna",None,None,
  "https://www.saunahermanni.fi/"],
 ["Lapinlahden Lähteen sauna",60.168218,24.912706,"Public sauna","Lapinlahti",12,"€12 / 2h · students, unemployed and pensioners €6 · towel €5 · seat cover €2.50","no","",
  "The 1880s sauna building of the old Lapinlahti hospital, by their account the oldest working sauna in Helsinki open to the public; room for 10, one shared changing room, a volunteer sauna host on duty","No pool; the shore is under 100 m away","Public turns on set dates, listed month by month on their page: mixed turns and women's turns, no booking","A small sauna in the old hospital park",None,
  "Open to the public only on the listed turns, so check the month's dates first. Pay at Café Lähde, or the sauna host when the café is shut.",
  "https://lapinlahdenlahde.fi/en/the-lahde-sauna/"],
 ["Löylykontti Sörnäinen",60.182325,24.963295,"Self-service sauna","Sörnäinen",5,"€5–14 per person per hour, by time of day · whole sauna €29–129 / hour · booked and paid online","no","",
  "Two saunas on the seafront promenade, Meri and Suvi, 10 bathers each and sold by the hour; mixed, swimsuits required. Self-service: a door code comes by email and the stove heats itself for the booking","The sea, all year, down heated steps from the terrace; an ice hole in winter","By the booked hour; free times are in their calendar","A booked hour by the sea",None,
  "Online booking only. The booked hour is sauna time, so arrive 15 minutes early to change. Bring a swimsuit, a towel and a water bottle.",
  "https://www.loylykontti.fi/fi/saunas/helsinki/sornainen"],
 ["Yrjönkadun uimahalli",60.168337,24.939076,"Swimming hall & saunas","Kamppi",6,"€6 / 2h on the first floor (reduced €3.30) · second floor €20 / 2h (reduced €15) with a rest cabin, towel and bathrobe · extra hour €12 · towel hire €8","no","",
  "First floor: two electric saunas, 85°C and 75°C. Second floor, on its own ticket: a wood-heated sauna, a small steam sauna and an infrared sauna","A 25 m pool at 27°C in a 1920s hall, 0.9–3.4 m deep; swimmers only","Women: Mon 12:00–20:00 · Wed & Fri 06:30–20:00 · Sun 11:00–20:00 · Men: Tue & Thu 06:30–20:00 · Sat 07:00–20:00 · second floor from 13:00, shut on Mondays · swimming ends 20:30 · closed in summer","A 1920s hall where swimsuits are optional",None,
  "Women and men bathe on different days: women Mon, Wed, Fri and Sun, men Tue, Thu and Sat. The second floor holds 40 and is often full; advance tickets for it are sold online only.",
  "https://www.hel.fi/fi/kulttuuri-ja-vapaa-aika/liikunta/yrjonkadun-uimahalli/aukioloajat-ja-yhteystiedot"],
 ["Lonnan sauna",60.153901,24.990964,"Island public sauna","Lonna",23,"€23 / 2h · under 12 free · soap, shampoo and seat cover included · towel €9","no","",
  "A log building with two loft saunas, each heated by a large single-fired wood stove; mixed every day, with or without a swimsuit; 12 places open on each side every hour","The sea, over a rocky shore; bring shoes for it","Summer season only; Tuesday to Saturday in season","A wood-fired sauna on a small island",None,
  "Seasonal: the island shuts for the winter. In season a waterbus runs from Kauppatori in about ten minutes, and booking the sauna ahead is strongly recommended.",
  "https://www.lonna.fi/en/services/sauna/"],
]

# Wikimedia Commons photo per venue, where a freely licensed one shows the venue itself.
# Sompasauna has photographs there only of its earlier sites, Sauna Hermanni and
# Löylykontti have none, and Lonna's were not looked through; those get a map tile.
IMG = {
 "Löyly": "loyly", "Allas Sea Pool": "allas", "Kotiharjun sauna": "kotiharju",
 "Uusi Sauna": "uusi", "Kulttuurisauna": "kulttuuri",
 "Lapinlahden Lähteen sauna": "lapinlahti", "Yrjönkadun uimahalli": "yrjo",
 "Sompasauna": "sompa",
}
# Sent in through the photo desk on 26 November 2026 by a visitor, without a name to credit.
PHOTOS = {"sompa": None}

# --- Opening hours, as in berlin/venues.py: Mon..Sun, [open, close] in minutes,
#     ending at the last entry where the venue gives one. A day with a morning turn
#     and an evening one is a list of both windows (Löyly on Wed and Sat,
#     Kulttuurisauna Fri to Sun, whose morning ends at its last entry, 10:30).
D = lambda a, b: [[a, b]] * 7
OPEN = {
 "Löyly": {"weekly": [[720, 1320], [720, 1320], [[540, 660], [780, 1320]], [720, 1320], [780, 1380], [[540, 660], [780, 1380]], [660, 1260]], "src": "venue"},
 "Allas Sea Pool": {"weekly": [[390, 1200]] * 5 + [[480, 1200]] * 2, "src": "venue"},
 "Kotiharjun sauna": {"weekly": [None] + [[840, 1200]] * 6, "src": "venue"},
 "Uusi Sauna": {"weekly": [None] + [[1020, 1440]] * 4 + [[960, 1440], [960, 1380]], "src": "venue"},
 "Kulttuurisauna": {"weekly": [None, None] + [[960, 1125]] * 2 + [[[480, 630], [960, 1125]]] * 3, "src": "venue"},
 "Sompasauna": {"weekly": D(0, 1440), "src": "venue"},
 "Sauna Hermanni": {"weekly": [[900, 1200], None, [900, 1200], [900, 1200], [900, 1200], [840, 1080], None], "src": "venue"},
 # The hall's own hours end at 20:00; swimming goes on until 20:30.
 "Yrjönkadun uimahalli": {"weekly": [[720, 1200], [390, 1200], [390, 1200], [390, 1200], [390, 1200], [420, 1200], [660, 1200]], "src": "venue"},
 # Shut for the winter. lonna.fi says only that the island opens again in May 2027, with no
 # day, so this is the last day it is certainly shut; read the new season's hours off their
 # page when it lapses.
 "Lonnan sauna": {"closedUntil": "2027-04-30", "src": "venue"},
}

# --- Who throws the water, where the venue's own page says it in words, with the cabin
#     temperatures where the page gives them.
HEAT = {
 "Allas Sea Pool": ("Five saunas: the Kulmasauna at 90°C, the Maisemasauna at 80°C with a sea view, and three floating saunas at 70°C (mixed, women's and men's)",
   "self", "You throw your own water on the stones; in the Maisemasauna a button releases the löyly instead"),
 "Kotiharjun sauna": (None, "self", "Bathers throw the water, from a tap on the stove; ask the others first, and by old rule whoever sits in the hottest spot decides"),
 "Sompasauna": (None, "self", "Nobody works there: whoever comes heats the sauna themselves"),
}
HEAT_SOURCE = "read off the venue's own page, 25 Nov 2026"

# --- The cold plunge in °C, where the venue states a figure. None does: Allas shows the
#     day's sea temperature on its page (0 to 22 degrees over the year), which is a reading.
PLUNGE = {}

# --- Banyas. None of the listed venues is one.
BANYA = set()

# --- What heats the sauna: (fuel, brand, note, source). Fuel is wood, smoke, pellet, electric,
#     gas or infrared, or None where that is not known; brand is the stove's maker, or None.
#     Source is "venue" for what its own site says and "editor" for the owner's own knowledge.
STOVE = {
 "L\u00f6yly": ("wood", None, "A smoke sauna and a wood-heated sauna, both single-fired", "venue"),
 "Kotiharjun sauna": ("wood", None, "The public saunas are wood-heated; the sauna for hire is electric", "venue"),
 "Uusi Sauna": ("pellet", None, "The men's and women's saunas burn wood pellets; the mixed sauna is electric", "venue"),
 "Kulttuurisauna": ("wood", None, "Wood and pellets in one single-fired mass stove", "venue"),
 "Sauna Hermanni": (None, "IKI", "New IKI stoves on both sides; its site does not say what they burn", "venue"),
 "Yrj\u00f6nkadun uimahalli": ("electric", None, "Two electric saunas on the first floor; the second floor adds a wood-heated sauna, a steam sauna and an infrared one", "venue"),
 "Lonnan sauna": ("wood", None, "Two loft saunas, each with a large single-fired wood stove", "venue"),
}

LAST_CHECKED = "25 November 2026"

# --- Wikimedia Commons file behind each photo key in IMG. engine/fetch_images.py
#     reads the credits for these into img/credits.json.
COMMONS = {
 "loyly": "File:Löyly in Hernesaari, Helsinki, Finland, 2022 May.jpg",
 "allas": "File:Allas Sea Pool in Katajanokka, Helsinki, Finland, 2021 June.jpg",
 "kotiharju": "File:Kotiharjun sauna 2025-1 Marit Henriksson.jpg",
 "uusi": "File:Uusi Sauna in November.jpg",
 "kulttuuri": "File:Kulttuurisauna Hakaniemenrannassa 2024 (202429;+G78296).jpg",
 "lapinlahti": "File:Puusepänverstas- Saunarakennus.jpg",
 "yrjo": "File:Yrjönkadun uimahalli.jpg",
}
