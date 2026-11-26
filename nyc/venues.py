# -*- coding: utf-8 -*-
"""New York: every fact about its venues. This file is the source of truth.

First made as a naive map on 15 November 2026 and filled out on 26 November
2026. Every venue here was checked with engine/verify_venue.py against its own
site that day and its pages were read by hand; every price, opening hour and
temperature was read off that site, never off a list. The verifier calls all
of them THIN, because it looks for euro prices and 24-hour times and these
sites print dollars and am/pm.

The Russian & Turkish Baths' link goes to its facility page, because its home
page no longer says "sauna" and the verifier calls that SUSPECT.

Coordinates are the venue's own object in OpenStreetMap: the nodes in
nyc/candidates.json, and for QC NY the building way/405898225 ("QC NY spa",
112 Andes Road, tagged with the venue's own website and phone number), which
is not sauna-tagged and so is not in that file.

Filled in on 26 November: each Bathhouse location from its own page (its
saunas, pools and their temperatures, the daily Aufguss schedule, the age
limit and dress code); the Russian & Turkish Baths, whose site now prints its
hours and admission ($60); Othership Flatiron's sauna and ice bath
temperatures and house rules. Added: QC NY on Governors Island.

Left out, and why:
- Akari Sauna (202 Grand St, 149 Franklin St, 60 Orchard St) is open, but it
  is members only: its FAQ says walk-ins are not allowed and there are no
  trial visits, and the only prices are monthly memberships (from $140) and a
  $35 guest pass for a member's guest.
- cityWell Brooklyn (496 President St) says on its home page that its
  hydrotherapy (steam, soak, sauna) is currently on pause.
- AIRE Ancient Baths: the Tribeca pages never mention a sauna, and the Upper
  East Side lists a "Saunarium (Dry Sauna)" on one experience page only. They
  are thermal baths, and the verifier calls both SUSPECT.
- Othership Williamsburg (25 Kent Ave) has its own page and the same facts as
  Flatiron, but no object of its own in OpenStreetMap, so it has no
  coordinates yet.
- World Spa (1571 McDonald Ave), Spa Castle (11-11 131st St, College Point)
  and Brooklyn Bathhouse (731 Flatbush Ave) are outside this map's frame. Spa
  Castle's site answered HTTP 500 when it was read.
- Lore Bathing Club, Wall Street Bath & Spa, Brooklyn Banya, Mermaid Spa,
  Chill Space and the Korean spas in Midtown could not be read: their hosts
  were not reachable from where this was made.
- The infrared studios and the gym saunas in OpenStreetMap were not looked at.

Still empty: Othership's drop-in price and session times (both are only in its
booking widget); temperatures at the Russian & Turkish Baths and QC NY (their
sites give none); who throws the water everywhere but Bathhouse; a plunge
figure for Bathhouse Williamsburg and Flatiron (each has two plunges, 45 and
50 F, which are in the pool text) and for Othership (a range, 32-40 F); what
heats any of these saunas (no site says); the Finnish scores and picks.
"""

# name, lat, lon, kind, district, price(from|None), priceLabel, usc, uscLabel,
# sauna, pool, hours, bestFor, badge, flag, url
V = [
 ["Bathhouse Williamsburg",40.720518,-73.957404,"Bathhouse","Williamsburg",39,"Day pass from $39, the price moves with the day and time · no time limit · Core membership, $99 a year, gets the member price on every pass","no","",
  "A dry sauna at 175–190°F, a banya at 185–195°F and an event sauna for guided sessions at up to 175°F, with a steam room at 115°F and heated marble hammams","Cold plunges at 45°F and 50°F, hot pools at 104°F, neutral pools at 98°F and a rooftop pool at 84°F, weather permitting","Daily 08:00–23:30 · stay as long as you like, no re-entry","Saunas, thermal pools and a rooftop pool",None,
  "18 and over. Bathing suits are required everywhere but the locker rooms; towels and slippers are provided. Book ahead: walk-ins only when there is room, and weekends usually sell out. Phones stay in the locker.",
  "https://bathhouse.com/williamsburg"],
 ["Bathhouse Flatiron",40.741118,-73.991235,"Bathhouse","Flatiron",39,"Day pass from $39, the price moves with the day and time · no time limit · Core membership, $99 a year, gets the member price on every pass","no","",
  "Three saunas: a dry sauna for Aufguss sessions at up to 185°F, a banya at 185–195°F and an infrared sauna at up to 135°F, with a steam room at 115°F and heated marble hammams","Six thermal pools: cold plunges at 45°F and 50°F, hot pools at 104°F, a neutral pool at 98°F and a salt pool at 98°F in the quiet area","Daily 08:00–23:30 · stay as long as you like, no re-entry","Saunas and thermal pools in Manhattan",None,
  "18 and over. Bathing suits are required everywhere but the locker rooms; towels and slippers are provided. Book ahead: walk-ins only when there is room, and weekends usually sell out. Phones stay in the locker.",
  "https://bathhouse.com/flatiron"],
 ["Bathhouse Atlantic Ave",40.684868,-73.980039,"Bathhouse","Boerum Hill",29,"Day pass from $29, the price moves with the day and time · no time limit · Core membership, $99 a year, gets the member price on every pass","no","",
  "A banya at 185–195°F, an event sauna for Aufguss sessions at up to 175°F, an infrared sauna at 135°F and a backyard sauna at 175°F, open all year, with a steam room at 115°F","A cold plunge at 50°F, a hot pool at 104°F, a neutral pool at 98°F and a backyard pool kept at 80°F in summer and 104°F in winter","Daily 08:00–23:30 · stay as long as you like, no re-entry","Saunas, pools and a backyard sauna",None,
  "18 and over. Bathing suits are required everywhere but the locker rooms; towels and slippers are provided. Book ahead: walk-ins only when there is room, and weekends usually sell out. Phones stay in the locker.",
  "https://bathhouse.com/atlantic-ave"],
 ["Russian & Turkish Baths",40.728278,-73.983622,"Russian bathhouse","East Village",60,"$60 single admission · 5 admissions $250 · 10 for $475, valid for two people · prices do not include sales tax and card fees","no","",
  "Five saunas and steam rooms, among them the Russian Room, a Redwood Sauna, a Turkish Room and an Aromatherapy Room; platza with oak leaves in the Russian Room","An ice-cold plunge pool, and a roof deck","Mon–Wed, Fri 12:00–22:00 · Thu 12:00–22:00, men only until 17:00 · Sat 10:00–22:00 · Sun 09:00–22:00, men only until 14:00 · open 365 days a year","A Russian bathhouse since 1892",None,
  "Walk-ins only: they take no reservations for the baths, massages or treatments. 18 and over. You must be covered during co-ed hours; robes, towels, shorts and slippers are provided. Two owners run alternate shifts, and a multi-visit pass or gift card is good only on the shift of the owner who sold it.",
  "https://www.russianturkishbaths.com/baths"],
 ["Othership Flatiron",40.740444,-73.992492,"Sauna & ice bath studio","Flatiron",None,"Sessions booked online · the drop-in price is shown only in their booking widget","no","",
  "A performance sauna of Western Red Cedar heated up to 185°F, with aromatic snowballs for humidity; 75-minute guided classes or self-guided free flow sessions","Eight ice baths kept at 32–40°F, some for four people","Session times on their site · booked online, up to two weeks ahead","Guided hot and cold sessions",None,
  "18 and over. Bathing suits are required and it is barefoot beyond the changing rooms; two towels are provided. Arrive 10 to 15 minutes early: there is no late entry once the sauna doors close. No phones past the entrance, and no alcohol.",
  "https://www.othership.us/flatiron"],
 ["QC NY",40.692898,-74.017918,"Spa with saunas & outdoor pools","Governors Island",124,"Sunset session, from 17:00, from $124 · Escape, 5 hours, from $138 · Daily, no time limit, from $170 · robe, towels and slippers included","no","",
  "Seven saunas, among them the City, Fall, Mountain and Refuge saunas, with two steam baths, an infrared room, Vichy showers and relaxation rooms","Two heated outdoor pools facing the Manhattan skyline, and a music pool","Sun–Thu 09:00–22:00 · Fri–Sat 09:00–23:00 · entry by reserved time slot · hours change on holidays","Saunas and outdoor pools facing the skyline",None,
  "21 and over, with a valid ID. It is on Governors Island: ferries leave from the Battery Maritime Building, 10 South Street. Bring a bathing suit. They recommend arriving at least two hours before closing, and there is no re-entry.",
  "https://www.qcny.com/"],
]

D = lambda a, b: [[a, b]] * 7
# --- Photos. Sent in through the photo desk on 26 November 2026 by a visitor, without a name to credit.
IMG = {"Russian & Turkish Baths": "rtb"}
PHOTOS = {"rtb": None}

OPEN = {
 # no last entry is given for any of these; the windows are the stated opening hours
 "Bathhouse Williamsburg": {"weekly": D(480, 1410), "src": "venue"},
 "Bathhouse Flatiron": {"weekly": D(480, 1410), "src": "venue"},
 "Bathhouse Atlantic Ave": {"weekly": D(480, 1410), "src": "venue"},
 # Thursday until 17:00 and Sunday until 14:00 are men only; the hours text says so
 "Russian & Turkish Baths": {"weekly": [[720, 1320]] * 5 + [[600, 1320], [540, 1320]], "src": "venue"},
 "QC NY": {"weekly": [[540, 1320]] * 4 + [[540, 1380]] * 2 + [[540, 1320]], "src": "venue"},
}

# --- Only where the venue's own page says who throws the water. Bathhouse's Sauna Masters
#     host an Aufguss to a daily schedule at every location; the other sites do not say.
_AUFGUSS = ("Sauna Masters host a 15-minute Aufguss with essential oils, music and towel waving every day at "
            "12:00, 13:30, 15:00, 16:30, 18:00, 19:30 and 21:00. It is announced in the house, costs nothing extra and needs no booking")
HEAT = {
 "Bathhouse Williamsburg": ("A dry sauna at 175–190°F, a banya at 185–195°F and an event sauna for guided sessions at up to 175°F, with a steam room at 115°F and heated marble hammams",
   "scheduled", _AUFGUSS),
 "Bathhouse Flatiron": ("Three saunas: a dry sauna for Aufguss sessions at up to 185°F, a banya at 185–195°F and an infrared sauna at up to 135°F, with a steam room at 115°F and heated marble hammams",
   "scheduled", _AUFGUSS),
 "Bathhouse Atlantic Ave": ("A banya at 185–195°F, an event sauna for Aufguss sessions at up to 175°F, an infrared sauna at 135°F and a backyard sauna at 175°F, open all year, with a steam room at 115°F",
   "scheduled", _AUFGUSS),
}
HEAT_SOURCE = "read off the venues' own pages, 26 Nov 2026"

# --- The cold plunge in °C, only where the venue states one figure. Bathhouse Atlantic Ave
#     has one plunge, at 50°F; the other two Bathhouses have two each, at 45°F and 50°F.
PLUNGE = {
 "Bathhouse Atlantic Ave": 10.0,
}

# --- A banya is a banya whoever throws the water; the badge says so.
BANYA = {"Russian & Turkish Baths"}

LAST_CHECKED = "26 November 2026"
