# -*- coding: utf-8 -*-
"""New York: every fact about its venues. This file is the source of truth.

A first, naive map, made on 15 November 2026. Every venue here passed
engine/verify_venue.py against its own site that day, and every price and
opening hour was read off that site, never off a list. Coordinates are the
venue's own node in OpenStreetMap.

Most of these sites render their prices with a script, so several venues have
no price here yet. World Spa (1571 McDonald Ave) checked out but is south of
this map's frame. Akari Sauna was not taking bookings when its site was read.
"""

# name, lat, lon, kind, district, price(from|None), priceLabel, usc, uscLabel,
# sauna, pool, hours, bestFor, badge, flag, url
V = [
 ["Bathhouse Williamsburg",40.720518,-73.957404,"Bathhouse","Williamsburg",39,"Day pass from $39","no","",
  "A day-pass bathhouse; the saunas and pools are listed on their site","Check their site","Daily 08:00–23:30","A day at the baths",None,None,
  "https://bathhouse.com/"],
 ["Bathhouse Flatiron",40.741118,-73.991235,"Bathhouse","Flatiron",39,"Day pass from $39","no","",
  "A day-pass bathhouse; the saunas and pools are listed on their site","Check their site","Daily 08:00–23:30","A day at the baths in Manhattan",None,None,
  "https://bathhouse.com/"],
 ["Bathhouse Atlantic Ave",40.684868,-73.980039,"Bathhouse","Boerum Hill",29,"Day pass from $29","no","",
  "A day-pass bathhouse; the saunas and pools are listed on their site","Check their site","Daily 08:00–23:30","The cheapest Bathhouse pass",None,None,
  "https://bathhouse.com/"],
 ["Russian & Turkish Baths",40.728278,-73.983622,"Russian bathhouse","East Village",None,"Admission on their site","no","",
  "A Russian bathhouse on East 10th Street","Check their site","Not found on their site as read","The old-school banya",None,
  "Walk-ins only: they take no reservations for the baths, massages or treatments. Their site as read gives no prices or hours.",
  "https://www.russianturkishbaths.com/"],
 ["Othership Flatiron",40.740444,-73.992492,"Sauna & ice bath studio","Flatiron",None,"Sessions booked online","no","",
  "Guided sauna and ice bath sessions","Ice baths","Session times on their site","Guided hot and cold sessions",None,None,
  "https://www.othership.us/flatiron"],
]

D = lambda a, b: [[a, b]] * 7
# --- Photos. Sent in through the photo desk on 26 November 2026 by a visitor, without a name to credit.
IMG = {"Russian & Turkish Baths": "rtb"}
PHOTOS = {"rtb": None}

OPEN = {
 "Bathhouse Williamsburg": {"weekly": D(480, 1410), "src": "venue"},
 "Bathhouse Flatiron": {"weekly": D(480, 1410), "src": "venue"},
 "Bathhouse Atlantic Ave": {"weekly": D(480, 1410), "src": "venue"},
}

# --- A banya is a banya whoever throws the water; the badge says so.
BANYA = {"Russian & Turkish Baths"}

LAST_CHECKED = "15 November 2026"
