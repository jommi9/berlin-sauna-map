import json, math
g = json.load(open('geo.json'))
LON0, LAT0, LON1, LAT1 = g['bbox']; SX = g['sx']; DM1 = g['dm1']
def proj(lon, lat):
    dm = math.degrees(math.log(math.tan(math.pi/4 + math.radians(lat)/2)))
    return round((lon-LON0)*SX, 1), round((DM1-dm)*SX, 1)

# name, lat, lon, kind, district, price(from|None), priceLabel, usc, uscLabel,
# sauna, pool, hours, bestFor, badge, flag, url
V = [
 ["Vabali",52.52840,13.35889,"Standalone spa","Moabit",27.5,"€27.50 / 2h · €36.50 / 4h · €51.50 day","no","Not on Urban Sports Club",
  "10 saunas, 3 steam baths, frequent Aufguss, large garden","4 pools","09:00–24:00","Best full sauna day","Best sauna day",None,
  "https://www.vabali.de/berlin/"],
 ["Grand Hyatt — Club Olympus",52.50819,13.37248,"Hotel day spa","Tiergarten",40,"Weekday €40 / 2h · €80 day; weekend €50 / 2h · €95 day","no","Not on Urban Sports Club",
  "90°C Finnish sauna, steam bath, whirlpool, rooftop terrace","Indoor rooftop pool + cold plunge","07:00–21:00","Best premium hotel sauna","Most premium",None,
  "https://www.hyatt.com/de-DE/spas/Club-Olympus-Berlin/day-spa"],
 ["Hilton Berlin — LivingWell",52.51210,13.39253,"Hotel spa","Mitte",33,"€33 / 2.5h · €39 day","yes","Premium 4×/mo · Max 8×/mo · 2h per visit",
  "Finnish saunas, steam rooms, experience showers, relaxation area; towels included with USC","14 m heated pool","07:00–21:00","Best overall USC hotel option","Best USC hotel",None,
  "https://urbansportsclub.com/de/venues/hilton-berlin-living-well-health-club?view=new"],
 ["Steigenberger — Sky Spa",52.52366,13.36747,"Hotel spa","Mitte",25,"€25 / 2h · €40 day","yes","Premium & Max 4×/mo · reserved 2h slot",
  "90°C Finnish, 60°C bio, outdoor sauna, steam bath, terrace","No major pool focus","Tue 14:00–22:00; hours vary by day","Best USC option if sauna matters most","Best USC sauna",None,
  "https://www.sky-spa-fitnesslounge.de/day-spa/"],
 ["Hotel de Rome — De Rome Spa",52.51579,13.39406,"Hotel day spa","Mitte",90,"From about €90 day","no","Not on Urban Sports Club",
  "Finnish sauna, steam room, ice fountain, Kneipp circuit","20 m pool in a former bank vault","Sauna roughly 10:00–21:00","Most atmospheric / beautiful","Most beautiful",None,
  "https://www.visitberlin.de/de/berlins-beste-sauna"],
 ["Hotel Adlon Kempinski",52.51557,13.38006,"Hotel day spa","Mitte",65,"€65 weekday · €85 weekend day pass","no","Not on Urban Sports Club",
  "Sauna area, steam bath, relaxation rooms, whirlpool","Pool","07:00–21:00","Luxury hotel experience",None,None,
  "https://www.kempinski.com/de/hotel-adlon/luxus-spa/mitgliedschaften/tagespass-und-mitgliedschaften"],
 ["Hotel Palace — Palace Spa",52.50491,13.33884,"Hotel day spa","Charlottenburg",34,"About €34–35 / 3h · €39 day","no","Not on Urban Sports Club",
  "Sauna, tepidarium, ice grotto","Pool","Tue 06:30–22:00; check daily hours","Best-value cash hotel spa","Best value hotel",None,
  "https://www.palace.de/hotel/palace-spa-fitness"],
 ["Titanic Gendarmenmarkt — BeFine",52.51490,13.39451,"Hotel day spa","Mitte",35,"About €35 day","no","Not on Urban Sports Club",
  "Dry sauna, steam bath, Turkish hammam, ice fountain, relaxation rooms","No major pool focus","Tue 12:30–21:00; check daily hours","Hammam plus sauna",None,None,
  "https://www.titanic.com.tr/de/titanic-gendarmenmarkt-berlin/befine-spa/sauna"],
 ["Park Inn Alexanderplatz — Gezer Spa",52.52284,13.41278,"Hotel spa","Mitte",12.5,"€12.50 / 2h · €17.50 / 4h · €22.50 day card (Stadtgäste)","yes","Classic 4×/mo · Premium & Max 8×/mo · max 2h",
  "95°C Finnish, 75°C bio, infrared cabin, relaxation loungers, tea and water","No pool","12:00–22:00","Best easy / low-friction USC sauna","Cheapest session",None,
  "https://urbansportsclub.com/de/venues/gezer-spa-fitness-1"],
 ["InterContinental Berlin",52.50727,13.34540,"Hotel day spa","Tiergarten",60,"€60 / 2h · €100 day (day visitors) · hotel guests €10 pool, €20 pool + sauna per day","no","Not on Urban Sports Club",
  "Large sauna area, whirlpool, terrace","Pool","07:00–21:00","Large conventional hotel spa",None,None,
  "https://www.berlin.intercontinental.com/wellness/"],
 ["The Westin Grand — Gezer Spa",52.51587,13.38860,"Hotel spa","Mitte",15,"€15 / 2h · €20 / 4h · €25 day card (Stadtgäste)","yes","Classic 4×/mo · Premium & Max 8×/mo · max 2h",
  "Only the Sanarium is open, 60–65°C — two saunas still under repair","Check current spa setup","Currently shown around 14:00–22:00; verify before going","Central USC alternative",None,"Gezer Spa confirmed by email on 3 September 2026 that the spa has reopened, but two of the three saunas are still under repair with no completion date. Only the Sanarium (60–65°C) is running. The Urban Sports Club listing still shows the old closure banner.",
  "https://urbansportsclub.com/en/venues/gezer-spa-fitness?view=new"],
 ["sly Berlin",52.50999,13.40558,"Hotel spa","Mitte",None,"Hotel guests only — no public access","no","No current USC listing",
  "KLAFS panoramic rooftop sauna, steam bath, roof terrace, tea, towels and bathrobes","No pool","About 06:00–23:00; hotel pages differ","Top-tier sauna, but you cannot get in",None,"Confirmed by sly Berlin on 2 September 2026: because of the spa's size it is open to hotel guests only. There is no public day pass.",
  "https://www.sly-berlin.com/en/spa-and-gym"],
 ["KIEZ SAUNA Friedrichshain",52.51545,13.44865,"Standalone sauna","Friedrichshain",22,"€22 / 4h","no","Not on Urban Sports Club",
  "90°C Finnish, 60°C bio, steam room, hourly Aufguss, terrace","No pool focus","15:00–24:00","Best neighborhood / proper sauna","Best local sauna",None,
  "https://www.kiezsauna.de/%C3%B6ffnungszeiten/"],
 ["Olivin",52.53160,13.41116,"Standalone sauna","Prenzlauer Berg",22,"€22 / 4h · reduced €21 · extra hour +€6 · late tariff from 21:30 €20 · happy hour Mon–Fri €20","no","Not on Urban Sports Club",
  "Finnish sauna, hourly essential-oil Aufguss, small calm design-focused space","No pool focus","Tue 17:00–24:00; check daily hours","Quiet, smaller, design-y option",None,None,
  "https://olivin-berlin.com/facts/"],
 ["LIQUIDROM",52.50118,13.38140,"Standalone spa","Kreuzberg",24.5,"Short Escape 90 min €22 · Urban Flow 2h €24.50 · Deep Dive 3h €29.50 · +€5 per extra 30 min · sauna add-on +€2.50","partial","Premium / Max access exists, but USC entry excludes the sauna",
  "Sauna plus spa facilities and Onsen","Saltwater sound pool","09:00–24:00","Spa / pool atmosphere rather than pure sauna",None,"USC entry does not include the sauna — you pay the supplement.",
  "https://www.liquidrom-berlin.de/en/info.php"],
 ["Saunabad Prenzlauer Berg",52.53578,13.42035,"Standalone sauna","Prenzlauer Berg",18,"€18 / 2.5h · €20 / 4h","no","No verified USC access",
  "Large 95°C sauna, hourly Aufguss, garden, quiet rooms","No pool focus","15:00–24:00","Best cheap traditional sauna","Best cheap sauna","Their own site saunabad-berlin.de is dead \u2014 the domain now serves a hosting parking page and https fails, so this links to their Facebook instead. Rykestr. 10, tel. 030 44046397.",
  "https://www.facebook.com/p/Saunabad-Berlin-Prenzlauer-Berg-100061924915931/"],
 ["Lützow Sauna",52.50154,13.36890,"Standalone sauna","Tiergarten",24,"€24 / 2h · €27 / 3h · €30 day","no","No verified USC access",
  "90°C sauna, sanarium, steam bath, hourly Aufguss","30°C pool and 14°C plunge","Closed Tuesdays; check other daily hours","Excellent classic hot–cold cycles",None,"Closed Tuesdays.",
  "https://www.luetzow-sauna.de/start"],
 ["ANTI SPA",52.53125,13.40084,"Sauna & cold plunge studio","Mitte",29,"Regular sessions around €29; promos vary","yes","Classic 4×/mo · Premium & Max 8×/mo",
  "Cedar sauna, lounge; swimwear mandatory","Proper cold plunge","Session based","Best USC sauna plus serious cold plunge","Best cold plunge",None,
  "https://www.antispaces.com/spa/welcome-pass"],
 ["Stadtbad Neukölln",52.47919,13.43973,"Public bath / sauna","Neukölln",20,"About €20 / 3h · €23 day","yes","Included on Max",
  "Finnish sauna, herbal sauna, steam bath, caldarium","Public bath facilities","Sauna summer break through 31 Oct 2026","Excellent value once the sauna reopens",None,"Sauna closed for summer break through 31 October 2026.",
  "https://www.berlinerbaeder.de/baeder/detail/stadtbad-neukoelln/"],
 ["Finnland Zentrum",52.48963,13.39737,"Private rental sauna","Kreuzberg",40,"€40 for up to 4 people (3h) · extra adults €10","no","Not mentioned",
  "Indoor sauna on the 2nd floor, adjacent shower and small changing room, fireplace room on the same floor; BYO drinks allowed, take the empties with you","No pool; cool off by the changing-room windows or in the rear courtyard","Booking by email or phone (+49 30 781 81 89); weekend availability varies","Private group sauna with BYO drinks",None,"Booked by email or phone rather than walking in — the €40 covers the whole group for three hours.",
  "https://www.finnlandzentrum.de/sauna/"],
]

# Wikimedia Commons photo per venue, where a freely licensed one exists.
# The standalone saunas have none - they get a generated map tile instead.
IMG = {
 "Grand Hyatt \u2014 Club Olympus":"hyatt", "Hilton Berlin \u2014 LivingWell":"hilton",
 "Steigenberger \u2014 Sky Spa":"steigenberger", "Hotel de Rome \u2014 De Rome Spa":"derome",
 "Hotel Adlon Kempinski":"adlon", "Hotel Palace \u2014 Palace Spa":"palace",
 "Titanic Gendarmenmarkt \u2014 BeFine":"titanic", "Park Inn Alexanderplatz \u2014 Gezer Spa":"parkinn",
 "InterContinental Berlin":"intercon", "The Westin Grand \u2014 Gezer Spa":"westin",
 "LIQUIDROM":"liquidrom", "Stadtbad Neuk\u00f6lln":"neukoelln",
}


# --- Which Urban Sports Club tiers actually get into the SAUNA (not just the gym).
#     Liquidrom is deliberately empty: USC access exists but excludes the sauna.
USC_TIERS = {
 "Hilton Berlin \u2014 LivingWell": ["Premium", "Max"],
 "Steigenberger \u2014 Sky Spa": ["Premium", "Max"],
 "Park Inn Alexanderplatz \u2014 Gezer Spa": ["Classic", "Premium", "Max"],
 "The Westin Grand \u2014 Gezer Spa": ["Classic", "Premium", "Max"],
 "ANTI SPA": ["Classic", "Premium", "Max"],
 "Stadtbad Neuk\u00f6lln": ["Max"],
 "LIQUIDROM": [],
}

# --- Opening hours. weekly = Mon..Sun, each [open, close] in minutes past
#     midnight (1440 = midnight, >1440 = past midnight), or None for closed.
#     seasons override weekly between two MM-DD dates and may wrap the year.
#     src: "venue" = read off the operator's own page, "osm" = OpenStreetMap,
#     "listed" = as published on the hotel page and not re-verified since.
D = lambda a, b: [[a, b]] * 7
WINTER = "10-01", "03-31"
OPEN = {
 "Vabali": {"weekly": D(540, 1440), "src": "venue",
            "seasons": [{"from": WINTER[0], "to": WINTER[1], "weekly": D(480, 1440)}]},
 "KIEZ SAUNA Friedrichshain": {"weekly": D(900, 1440), "src": "venue",
            "seasons": [{"from": WINTER[0], "to": WINTER[1], "weekly": D(780, 1440)}]},
 "Park Inn Alexanderplatz \u2014 Gezer Spa": {"weekly": D(720, 1320), "src": "venue",
            "seasons": [{"from": WINTER[0], "to": WINTER[1], "weekly": D(720, 1080)}]},
 # Olivin runs SHORTER hours in summer, not longer - opens at 17:00 except Thursdays.
 "Olivin": {"weekly": D(720, 1440), "src": "venue",
            "seasons": [{"from": "06-01", "to": "09-30",
                         "weekly": [[1020,1440]]*3 + [[720,1440]] + [[1020,1440]]*3}]},
 "Hotel Palace \u2014 Palace Spa": {"weekly": [[390,1320]]*6 + [[480,1320]], "src": "venue"},
 "Titanic Gendarmenmarkt \u2014 BeFine":
                {"weekly": [[750,1260]]*4 + [[600,1260],[600,1260],[600,1110]], "src": "venue"},
 "Steigenberger \u2014 Sky Spa": {"weekly": [[840,1320]]*5 + [[600,1320],[600,1080]], "src": "osm"},
 "L\u00fctzow Sauna": {"weekly": [[1080,1380], None, [960,1380], None,
                                 [960,1380], [960,1380], [960,1380]], "src": "osm"},
 "LIQUIDROM": {"weekly": [[600,1440]]*4 + [[600,1500]]*3, "src": "osm"},
 "InterContinental Berlin": {"weekly": D(420, 1260), "src": "venue"},
 "Grand Hyatt \u2014 Club Olympus": {"weekly": D(420, 1260), "src": "listed"},
 "Hilton Berlin \u2014 LivingWell": {"weekly": D(420, 1260), "src": "listed"},
 "Hotel Adlon Kempinski": {"weekly": D(420, 1260), "src": "listed"},
 "Hotel de Rome \u2014 De Rome Spa": {"weekly": D(600, 1260), "src": "listed"},
 "sly Berlin": {"weekly": D(360, 1380), "src": "listed"},
 "Saunabad Prenzlauer Berg": {"weekly": D(900, 1440), "src": "listed"},
 "The Westin Grand \u2014 Gezer Spa": {"weekly": D(840, 1320), "src": "venue"},
 "Stadtbad Neuk\u00f6lln": {"closedUntil": "2026-10-31", "src": "venue"},
}

HOURS_TEXT = {
 "Vabali": "Daily 09:00\u201324:00 (08:00\u201324:00 from 1 Oct to 31 Mar)",
 "KIEZ SAUNA Friedrichshain": "Daily 15:00\u201324:00 (13:00\u201324:00 from 1 Oct to 31 Mar)",
 "Park Inn Alexanderplatz \u2014 Gezer Spa": "Daily 12:00\u201322:00 (12:00\u201318:00 from 1 Oct to 31 Mar)",
 "Olivin": "Daily 12:00\u201324:00; in summer (1 Jun\u201330 Sep) 17:00\u201324:00, Thu 12:00\u201324:00",
 "Hotel Palace \u2014 Palace Spa": "Mon\u2013Sat 06:30\u201322:00 \u00b7 Sun & holidays 08:00\u201322:00; mixed sauna from 16:30",
 "Titanic Gendarmenmarkt \u2014 BeFine": "Mon\u2013Thu 12:30\u201321:00 \u00b7 Fri\u2013Sat 10:00\u201321:00 \u00b7 Sun 10:00\u201318:30",
 "Steigenberger \u2014 Sky Spa": "Mon\u2013Fri 14:00\u201322:00 \u00b7 Sat 10:00\u201322:00 \u00b7 Sun 10:00\u201318:00",
 "L\u00fctzow Sauna": "Mon 18:00\u201323:00 \u00b7 Wed, Fri\u2013Sun 16:00\u201323:00 \u00b7 closed Tue & Thu",
 "LIQUIDROM": "Mon\u2013Thu 10:00\u201324:00 \u00b7 Fri\u2013Sun 10:00\u201301:00",
 "InterContinental Berlin": "Daily 07:00\u201321:00 (Spa Card); Time Card Mon\u2013Fri 07:00\u201315:00",
 "Finnland Zentrum": "By arrangement \u2014 book by phone or email (+49 30 781 81 89)",
 "ANTI SPA": "Session based \u2014 book a slot",
 "The Westin Grand \u2014 Gezer Spa": "Daily 14:00\u201322:00 \u2014 only the Sanarium is running while two saunas are repaired",
}


# --- Priced per booking rather than per head. A EUR 40 group hire is not
#     comparable to a EUR 12.50 entry, so these are drawn as circles rather than
#     squares and are excluded from the per-person "cheapest" figure.
GROUP_PRICED = {"Finnland Zentrum"}


# --- Cabin temperatures and Aufguss practice, answered by the venues themselves
#     in September 2026 (email). "aufguss" drives the filter chip:
#     scheduled = run to a plan, self = buckets provided, request = ask staff,
#     auto = automatic aroma dosing, unknown = they did not reply.
HEAT = {
 "Vabali": ("13 saunas: bio 55\u00b0C coolest, Gratensauna 90\u00b0C hottest, steam 45\u00b0C",
   "scheduled", "Plan rewritten daily and posted in-house \u2014 birch ceremonies, Asian scent journey, mint, orange peeling"),
 "Steigenberger \u2014 Sky Spa": ("2 Finnish saunas 90\u00b0C, bio 60\u00b0C, steam 45\u00b0C at high humidity",
   "self", "No staff plan; guests pour their own, preparations provided"),
 "Hotel Adlon Kempinski": ("Finnish 80\u2013100\u00b0C, bio/soft 50\u201360\u00b0C, steam 40\u201345\u00b0C at 98% humidity",
   "auto", "No plan; the cabins release aroma automatically every 20 minutes"),
 "Hotel Palace \u2014 Palace Spa": ("Finnish 90\u00b0C, tepidarium 55\u00b0C with colour therapy, ladies' sauna 90\u00b0C from 16:30, ice grotto 4\u00b0C",
   "self", "Self-serve buckets: rose, herbal, lemongrass"),
 "Titanic Gendarmenmarkt \u2014 BeFine": ("Finnish 90\u00b0C, steam 40\u201350\u00b0C, Turkish hammam 40\u00b0C",
   "request", "No fixed plan; ask the team on the day"),
 "Park Inn Alexanderplatz \u2014 Gezer Spa": ("Two Finnish saunas, 70\u201380\u00b0C and 90\u2013100\u00b0C",
   "self", "No plan; pour your own freely"),
 "InterContinental Berlin": ("Large Finnish 90\u00b0C, ladies' sauna 90\u00b0C, steam and herbal bath both 45\u00b0C; textile optional",
   "self", "A bucket stands ready in both Finnish saunas; guests pour their own"),
 "The Westin Grand \u2014 Gezer Spa": ("Only the Sanarium is open, 60\u201365\u00b0C \u2014 two saunas still under repair",
   "unknown", None),
 "sly Berlin": ("One electric Finnish sauna, fixed at 80\u00b0C", "unknown", None),
 "Olivin": ("A single Finnish sauna at 90\u00b0C \u2014 there are no other cabins",
   "scheduled", "On the hour, every hour"),
 "LIQUIDROM": ("Hot Room 90\u00b0C, Kelo herbal room 80\u00b0C, Salt Room 65\u00b0C, steam 45\u00b0C; 36\u00b0C saltwater dome",
   "scheduled", "Hourly heat sessions, roughly 10:00\u201323:00 (to 00:00 Fri\u2013Sat)"),
 "Finnland Zentrum": ("One sauna, yours alone for the booking",
   "self", "You are your own saunameister, as in Finland"),
 "KIEZ SAUNA Friedrichshain": (None, "scheduled", "Hourly"),
 "Saunabad Prenzlauer Berg": (None, "scheduled", "Hourly"),
 "L\u00fctzow Sauna": (None, "scheduled", "Hourly"),
}

keys = ["name","lat","lon","kind","district","price","priceLabel","usc","uscLabel","sauna","pool","hours","bestFor","badge","flag","url"]
venues = []
for i, row in enumerate(V):
    d = dict(zip(keys, row))
    d["x"], d["y"] = proj(d["lon"], d["lat"])
    d["img"] = IMG.get(d["name"])
    d["uscTiers"] = USC_TIERS.get(d["name"], [])
    d["open"] = OPEN.get(d["name"])
    d["pricing"] = "group" if d["name"] in GROUP_PRICED else "person"
    t, a, note = HEAT.get(d["name"], (None, "unknown", None))
    if t: d["sauna"] = t
    d["aufguss"], d["aufgussNote"] = a, note
    d["hours"] = HOURS_TEXT.get(d["name"], d["hours"])
    d["id"] = i
    venues.append(d)
json.dump(venues, open('venues.json','w'), separators=(',',':'), ensure_ascii=False)
print(len(venues), "venues")
xs=[v['x'] for v in venues]; ys=[v['y'] for v in venues]
print("x range", min(xs), max(xs), "| y range", min(ys), max(ys), "| canvas", g['w'], g['h'])
