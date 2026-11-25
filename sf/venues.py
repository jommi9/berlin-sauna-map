# -*- coding: utf-8 -*-
"""San Francisco: every fact about its venues. This file is the source of truth.

First made as a naive map on 15 November 2026 and filled out on 25 November
2026. Every venue here was checked with engine/verify_venue.py against its own
site that day and its pages were read by hand; every price, opening hour and
temperature was read off that site, never off a list. The verifier calls all
of them THIN, because it looks for euro prices and 24-hour times and these
sites print dollars and am/pm.

Coordinates are the venue's own node in OpenStreetMap (sf/candidates.json),
with two exceptions. Fjord is not mapped there: its coordinates are the
venue's own, printed on its page as 37.86690N 122.49484W. Dogpatch Paddle has
no node under that name: its coordinates are the OpenStreetMap node "Dogpatch
Foil" (node/11124413491), which carries Dogpatch Paddle's own phone number and
sits at its address, Building 49, 701 Illinois Street.

Added on 25 November: Alchemy Springs (it was still opening on the 15th and
now sells drop-in sessions), Onsen (OpenStreetMap tags it as a restaurant, but
its own site runs the bathhouse and dates its booking links this month),
Dogpatch Paddle (a waterfront sauna and cold plunge at Crane Cove Park) and
Fjord, the floating sauna in Sausalito, which is inside the frame since the
map was extended north. Archimedes Banya got its pass prices, which are now
on its Essentials page, and its cabin temperatures; Kabuki got its hours and
temperatures.

Left out, and why:
- Imperial Day Spa (1875 Geary Blvd) is a Korean bathhouse whose FAQ says the
  spa facilities need no appointment, but its site prints no entry-only price,
  only treatments that include two hours of spa, and it has no node under its
  own name in OpenStreetMap.
- Pearl Spa & Sauna is still women only and by appointment, with the baths
  included in a booked treatment.
- Civic Center Sauna & Hot Tub (15 Fell Street) has no site of its own that
  could be found.
- Perspire Sauna Studio in Berkeley is in OpenStreetMap but is an infrared studio
  chain and was not looked at. Oakland is still outside the frame.

Added later on 25 November, at the owner's request, with the frame extended east and
north to take in the East Bay shore: Albany Sauna (1002 Solano Avenue, Albany) and
Good Hot (Terminal 4, Point San Pablo, Richmond). Both are their own nodes in
OpenStreetMap. Albany Sauna's site is a Square Online page that renders by script, so
its markup holds 58 characters of text; its facts were read out of the page data the
site ships (the same text a browser shows), which the verifier now reads too. Its home page still carries
an older "Location & Hours" block (Monday 10:30-7, Tuesday closed) that disagrees
with its sauna page and its booking notice, which both say the sauna opens every day
from 12:00 with the last appointment at 21:00; those are the hours used. Good Hot asks
guests not to put water on the rocks, which is the "dry" kind in HEAT.

Still empty: who throws the water at Kabuki, Alchemy Springs, Onsen and
Dogpatch Paddle (their pages do not say); a plunge temperature for Archimedes Banya, Onsen and Fjord
(none states a figure) and for Alchemy Springs (it gives a range, 45-55 F,
which is in its pool text); the Finnish scores, picks and photos (no freely
licensed photograph of any of these venues was found on Wikimedia Commons).
"""

# name, lat, lon, kind, district, price(from|None), priceLabel, usc, uscLabel,
# sauna, pool, hours, bestFor, badge, flag, url
V = [
 ["Archimedes Banya",37.730554,-122.37273,"Russian banya","Bayview",60,"$60 happy hour pass (weekday check-in 12:00–16:00, 3 h) · $72 basic pass, 3 h, any time · $95 all day","no","",
  "Two Russian saunas (parilki), a Finnish dry sauna and a Turkish hammam steam room, with venik platza","A cold water plunge, a warm swimming pool and jacuzzis","Mon, Wed–Fri 12:00–23:00 · Sat–Sun 10:00–23:00 · last check-in 21:00, saunas and pool close 22:30 · Tuesdays only for the women's night (first Tuesday) and men's night (third Tuesday), 17:00–22:00","Russian banya with venik platza",None,
  "18 and over, with a government ID. A banya pass is required for entry. The banya floor is clothing optional after 18:00 every day and all day on Wednesdays and Fridays.",
  "https://banyasf.com/"],
 ["Kabuki Springs & Spa",37.784699,-122.432624,"Japanese bathhouse","Japantown",49,"$49 communal baths, 2½ h · 1½ h more for $25 · $20 with a treatment","no","",
  "A cedar-lined dry sauna heated to 150°F and an herbal steam room reaching 120°F, in a quiet communal Japanese-style bath","A hot pool at 104°F and a cold plunge pool at 55°F","Mon 14:00–20:00 · Tue–Sun 10:00–21:30 · baths by reservation only, in 2½-hour slots","Quiet communal bathing",None,
  "Women on Sun, Wed and Fri; men on Thu and Sat (bathing suit optional); all genders Mon and Tue, with bathing suits. Photo ID required. No walk-ins unless a reservation slot is free.",
  "https://kabukisprings.com/springs/"],
 ["Alchemy Springs",37.786994,-122.417393,"Modern bathhouse","Lower Nob Hill",45,"Drop-in session, 2 h, from about $45 off-peak · most peak evenings and weekends from $75 · first-timer 2-pass $99","no","",
  "A social sauna at 180°F, a silent sauna at 185–200°F and an herbal steam room at 110–120°F, with an infrared-floored greenhouse to rest in","A hot pool at 102–104°F and a cold plunge at 45–55°F","Mon–Thu 16:00–22:00 · Fri 12:00–22:00 · Sat–Sun 10:00–20:00 · 2-hour sessions, a new group every 30 minutes","Heat, cold and rest circuit",None,
  "Swimwear is required everywhere but the locker rooms, and phones stay in the locker. 18 and over. Walk-ins only when there is space; reservations open two weeks ahead and the price moves with demand.",
  "https://alchemysprings.com/"],
 ["Onsen",37.783703,-122.415362,"Japanese bathhouse","Tenderloin",50,"$50 for 2 hours, with robe, towel and sandals","no","",
  "A redwood dry sauna and a steam room beside a communal soaking tub","A 104°F communal soaking tub and an overhead cold plunge","Mon 16:00–22:00 (men) · Wed 14:00–18:00 (women), 18:00–22:00 co-ed · Thu 14:00–22:00 · Fri–Sun 10:00–22:00 · no Tuesday hours listed","Small sento-style soak with a restaurant",None,
  "Monday is men only and Wednesday 14:00–18:00 women only, both bathing suit optional; a bathing suit is required at all co-ed times. 18 and over, four guests at most per reservation.",
  "https://www.onsensf.com/bathing"],
 ["Dogpatch Paddle",37.763198,-122.388308,"Waterfront sauna & cold plunge","Dogpatch",25,"$25 sauna only, 1 h, shared with up to three others · $35 with the cold plunge · private $100 / $140","no","",
  "A waterfront sauna kept at about 190°F, four people at most","A cold plunge kept at about 49°F (36–55°F), with the beach right outside","Tue–Sun 09:00–17:00, last public sauna 16:00 · closed Mon · one-hour sessions","An hour of hot and cold by the water",None,
  "16 and over. Public sessions run 9 to 5; members get 07:30–21:00.",
  "https://www.dogpatchpaddle.com/sauna/"],
 ["Fjord",37.8669,-122.49484,"Floating sauna","Sausalito",45,"$45 shared session, 90 min · private sauna $270 for 2 h, up to 6 guests","no","",
  "Two Finnish-style saunas on a floating platform in a marina, six people each","No pool: you plunge in the Bay inside a marked zone, or cool off under the outdoor showers","Open daily 08:00–20:30, Tuesdays 14:00–20:30 · sessions are booked ahead; the calendar opens Sundays at 09:00 with a new week, two weeks out","Sauna and a plunge in the Bay",None,
  "Bathing attire is required at all times. Bring at least two towels, water and footwear. No soap in the showers. Minimum age 14, with an adult in the group. Free Open Access sessions run every two weeks.",
  "https://www.thisisfjord.com/"],
 ["Albany Sauna",37.88986,-122.300434,"Private Finnish sauna rooms","Albany",30,"$30 for 30 min, one person · 45 min $45, or $70 for two · 60 min $60, or $85 for two · each further person $25","no","",
  "Four private sauna rooms around one central brick furnace, built in 1934; each room seats up to four and you set your own heat and steam","No pool: water buckets and an overhead waterfall above the bench, and a shower in each room. The outdoor hot tubs are under construction","The sauna opens every day from 12:00, last appointment 21:00 · by reservation, with a signed waiver","A private room where you make your own steam",None,
  "Reservations by phone or text, not online. Staff show first-timers how to work the damper and the water valve: the four rooms share one furnace, so steam you make reaches the others. Towels are included. An older hours block on the same site lists other times; the sauna page and the booking notice agree on the ones given here.",
  "https://www.albanysauna.com/sauna"],
 ["Good Hot",37.962153,-122.427289,"Bayside sauna rental","Point San Pablo, Richmond",30,"$30 a seat in the quiet communal sauna (first and last slots on Mon, Thu and Fri, first slot at weekends) · private sauna $130 for 1½ h, up to 6 people · $150 for the two larger ones, up to 8 · $20 off on Mon and Thu","no","",
  "Five small saunas rented privately and a communal one with six seats, on the shore at Terminal 4; the heat is adjustable up to about 180°F","No pool: a small beach beside the saunas for a plunge in the Bay, and two cold rinse showers","Thu–Mon, generally 09:30–20:15 · closed Tue–Wed · by reservation only, up to 21 days ahead","A private sauna and a dip in the Bay",None,
  "No drop-in bathing: every visit is booked, and the gate code and directions come with the confirmation. 18 and over, no dogs. Wear swimsuit bottoms or a wrap outside the saunas. Sandals or water shoes are required for the water, which is out of reach at very low tide.",
  "https://www.good-hot.com/info"],
]

OPEN = {
 # windows end at last check-in
 "Archimedes Banya": {"weekly": [[720, 1260], None, [720, 1260], [720, 1260], [720, 1260], [600, 1260], [600, 1260]], "src": "venue"},
 "Kabuki Springs & Spa": {"weekly": [[840, 1200]] + [[600, 1290]] * 6, "src": "venue"},
 # no last entry is given for these three; the windows are the stated opening hours
 "Alchemy Springs": {"weekly": [[960, 1320]] * 4 + [[720, 1320]] + [[600, 1200]] * 2, "src": "venue"},
 "Onsen": {"weekly": [[960, 1320], None, [840, 1320], [840, 1320], [600, 1320], [600, 1320], [600, 1320]], "src": "venue"},
 "Fjord": {"weekly": [[480, 1230], [840, 1230]] + [[480, 1230]] * 5, "src": "venue"},
 # ends at the last public sauna, 16:00
 "Dogpatch Paddle": {"weekly": [None] + [[540, 960]] * 6, "src": "venue"},
 # sauna from 12:00, last appointment 21:00, every day
 "Albany Sauna": {"weekly": [[720, 1260]] * 7, "src": "venue"},
 # "generally" 9:30 to 8:15, Thursday through Monday; the whole site shuts at 8:15
 "Good Hot": {"weekly": [[570, 1215], None, None, [570, 1215], [570, 1215], [570, 1215], [570, 1215]], "src": "venue"},
}

# --- Only where the venue's own page says who throws the water. Archimedes Banya's
#     decrees let guests add steam in the Russian sauna (ask the room first) and its
#     staff also run a scheduled Aufguss; Fjord's page allows loyly in so many words.
HEAT = {
 "Archimedes Banya": ("Two Russian saunas (parilki) at 170–210°F and 30–40% humidity, a Finnish dry sauna at 220°F and above, a Turkish hammam steam room below 140°F",
   "self", "Ask the room before adding steam in the Russian sauna; never water in the Finnish dry sauna. Staff also run a free aromatherapy Aufguss in the Russian sauna at 15:00, 19:00 and 21:00 (their home page adds 17:00 at weekends)"),
 "Fjord": ("Two traditional Finnish-style saunas kept at a target of 190°F, six people each, on a floating platform in a marina",
   "self", "Löyly is allowed: pour small amounts of water over the hot stones"),
 "Albany Sauna": ("Four private sauna rooms sharing one central brick furnace filled with several tons of river rocks, built in 1934; each room seats up to four",
   "self", "You open the damper for heat and pull the water valve to put water on the rocks inside the furnace. Wait at least 30 seconds between pulls, because the steam reaches all four rooms"),
 "Good Hot": ("Five small saunas rented privately and a communal one with six seats, on the shore at Terminal 4; the heat is adjustable up to about 180°F",
   "dry", "Guests are asked not to add water to the rocks: the heaters are sensitive to water"),
}
HEAT_SOURCE = "read off the venues' own pages, 25 Nov 2026"

# --- The cold plunge in °C, only where the venue states one figure. Kabuki says 55°F;
#     Dogpatch Paddle keeps its plunge "at about 49°".
PLUNGE = {
 "Kabuki Springs & Spa": 12.8,
 "Dogpatch Paddle": 9.4,
}

# --- A banya is a banya whoever throws the water; the badge says so.
BANYA = {"Archimedes Banya"}

# --- What heats the sauna: (fuel, brand, note, source). Fuel is wood, smoke, pellet, electric,
#     gas or infrared, or None where that is not known; brand is the stove's maker, or None.
#     Source is "venue" for what its own site says and "editor" for the owner's own knowledge.
STOVE = {
 "Alchemy Springs": ("gas", None, "Two gas stoves heat the sauna. Its own site does not describe them", "editor"),
 "Archimedes Banya": (None, None, "Each Russian sauna is built around a 22,000 lb stove faced in handmade ceramic tiles from Russia", "venue"),
 "Albany Sauna": ("gas", None, "One central brick furnace holding several tons of river rocks, gas-fired for five hours each morning and then shut with the chimney closed, so the rocks stay hot through the day", "venue"),
 "Good Hot": (None, None, "Commercial heaters that take no water on the rocks", "venue"),
}

LAST_CHECKED = "25 November 2026"
