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
 ["Park Inn Alexanderplatz — Gezer Spa",52.52284,13.41278,"Hotel spa","Mitte",None,"Hotel material lists €5 sauna, but walk-in cash terms are unclear","yes","Classic 4×/mo · Premium & Max 8×/mo · max 2h",
  "95°C Finnish, 75°C bio, infrared cabin, relaxation loungers, tea and water","No pool","12:00–22:00","Best easy / low-friction USC sauna","Easiest USC","Cash walk-in pricing not clearly published — USC entry is the reliable route.",
  "https://urbansportsclub.com/de/venues/gezer-spa-fitness-1"],
 ["InterContinental Berlin",52.50727,13.34540,"Hotel day spa","Tiergarten",60,"€60 / 2h · €100 day","no","Not on Urban Sports Club",
  "Large sauna area, whirlpool, terrace","Pool","07:00–21:00","Large conventional hotel spa",None,None,
  "https://www.berlin.intercontinental.com/wellness/"],
 ["The Westin Grand — Gezer Spa",52.51587,13.38860,"Hotel spa","Mitte",None,"Separate sauna cards exist; current single cash price not clearly published","yes","Classic 4×/mo · Premium & Max 8×/mo · max 2h",
  "Three saunas at roughly 60°C, 85°C and 95°C","Check current spa setup","Currently shown around 14:00–22:00; verify before going","Central USC alternative",None,"Hours and cash pricing both unverified — call ahead.",
  "https://urbansportsclub.com/en/venues/gezer-spa-fitness?view=new"],
 ["sly Berlin",52.50999,13.40558,"Hotel spa","Mitte",None,"No public day pass currently verified; hotel guest access confirmed","no","No current USC listing",
  "KLAFS panoramic rooftop sauna, steam bath, roof terrace, tea, towels and bathrobes","No pool","About 06:00–23:00; hotel pages differ","Top-tier sauna, but access is the problem",None,"No verified public day pass — realistically hotel guests only.",
  "https://www.sly-berlin.com/en/spa-and-gym"],
 ["KIEZ SAUNA Friedrichshain",52.51545,13.44865,"Standalone sauna","Friedrichshain",22,"€22 / 4h","no","Not on Urban Sports Club",
  "90°C Finnish, 60°C bio, steam room, hourly Aufguss, terrace","No pool focus","15:00–24:00","Best neighborhood / proper sauna","Best local sauna",None,
  "https://www.kiezsauna.de/%C3%B6ffnungszeiten/"],
 ["Olivin",52.53160,13.41116,"Standalone sauna","Prenzlauer Berg",22,"€22 / 4h · happy hour about €20","no","Not on Urban Sports Club",
  "Finnish sauna, hourly essential-oil Aufguss, small calm design-focused space","No pool focus","Tue 17:00–24:00; check daily hours","Quiet, smaller, design-y option",None,None,
  "https://olivin-berlin.com/facts/"],
 ["LIQUIDROM",52.50118,13.38140,"Standalone spa","Kreuzberg",24.5,"€24.50 / 2h plus about €2.50 sauna supplement","partial","Premium / Max access exists, but USC entry excludes the sauna",
  "Sauna plus spa facilities and Onsen","Saltwater sound pool","09:00–24:00","Spa / pool atmosphere rather than pure sauna",None,"USC entry does not include the sauna — you pay the supplement.",
  "https://www.liquidrom-berlin.de/en/info.php"],
 ["Saunabad Prenzlauer Berg",52.53578,13.42035,"Standalone sauna","Prenzlauer Berg",18,"€18 / 2.5h · €20 / 4h","no","No verified USC access",
  "Large 95°C sauna, hourly Aufguss, garden, quiet rooms","No pool focus","15:00–24:00","Best cheap traditional sauna","Best cheap sauna",None,
  "https://www.saunabad-berlin.de/"],
 ["Lützow Sauna",52.50154,13.36890,"Standalone sauna","Tiergarten",24,"€24 / 2h · €27 / 3h · €30 day","no","No verified USC access",
  "90°C sauna, sanarium, steam bath, hourly Aufguss","30°C pool and 14°C plunge","Closed Tuesdays; check other daily hours","Excellent classic hot–cold cycles",None,"Closed Tuesdays.",
  "https://www.luetzow-sauna.de/start"],
 ["ANTI SPA",52.53125,13.40084,"Sauna & cold plunge studio","Mitte",29,"Regular sessions around €29; promos vary","yes","Classic 4×/mo · Premium & Max 8×/mo",
  "Cedar sauna, lounge; swimwear mandatory","Proper cold plunge","Session based","Best USC sauna plus serious cold plunge","Best cold plunge",None,
  "https://www.antispaces.com/spa/welcome-pass"],
 ["Stadtbad Neukölln",52.47919,13.43973,"Public bath / sauna","Neukölln",20,"About €20 / 3h · €23 day","yes","Included on Max",
  "Finnish sauna, herbal sauna, steam bath, caldarium","Public bath facilities","Sauna summer break through 31 Oct 2026","Excellent value once the sauna reopens",None,"Sauna closed for summer break through 31 October 2026.",
  "https://www.berlinerbaeder.de/baeder/detail/stadtbad-neukoelln/"],
]
keys = ["name","lat","lon","kind","district","price","priceLabel","usc","uscLabel","sauna","pool","hours","bestFor","badge","flag","url"]
venues = []
for i, row in enumerate(V):
    d = dict(zip(keys, row))
    d["x"], d["y"] = proj(d["lon"], d["lat"])
    d["id"] = i
    venues.append(d)
json.dump(venues, open('venues.json','w'), separators=(',',':'), ensure_ascii=False)
print(len(venues), "venues")
xs=[v['x'] for v in venues]; ys=[v['y'] for v in venues]
print("x range", min(xs), max(xs), "| y range", min(ys), max(ys), "| canvas", g['w'], g['h'])
