# -*- coding: utf-8 -*-
"""San Francisco: every fact about its venues. This file is the source of truth.

A first, naive map, made on 15 November 2026. Every venue here passed
engine/verify_venue.py against its own site that day, and every price and
opening hour was read off that site, never off a list. Coordinates are the
venue's own node in OpenStreetMap.

Left out, and why: Pearl Spa & Sauna is women only and by appointment;
Imperial Day Spa sells treatments rather than entry; Alchemy Springs says it
is still opening. Archimedes Banya sells its passes through a booking page
that renders with a script, so it has no price here yet.
"""

# name, lat, lon, kind, district, price(from|None), priceLabel, usc, uscLabel,
# sauna, pool, hours, bestFor, badge, flag, url
V = [
 ["Archimedes Banya",37.730554,-122.37273,"Russian banya","Bayview",None,"Banya pass, booked online","no","",
  "A Russian bathhouse on the bay, with venik platza and a hammam","A pool","Mon, Wed–Fri 12:00–23:00 · Sat–Sun 10:00–23:00 · last check-in 21:00 · Tuesdays only for the monthly women's and men's nights","A proper banya",None,
  "18 and over, with a government ID. A banya pass is required for entry.",
  "https://banyasf.com/"],
 ["Kabuki Springs & Spa",37.784699,-122.432624,"Japanese bathhouse","Japantown",49,"$49 communal baths, 2½ h · 1½ h more for $25","no","",
  "A sauna and an herbal steam room, in a quiet communal Japanese-style bath","A hot pool and a cold plunge pool","By reservation only, in 2½-hour slots","A silent soak",None,
  "Women on Sun, Wed and Fri; men on Thu and Sat (bathing suit optional); all genders Mon and Tue, with bathing suits. Photo ID required.",
  "https://kabukisprings.com/how-to-bathe/"],
]

OPEN = {
 # windows end at last check-in
 "Archimedes Banya": {"weekly": [[720, 1260], None, [720, 1260], [720, 1260], [720, 1260], [600, 1260], [600, 1260]], "src": "venue"},
}

HEAT = {
 "Archimedes Banya": (None, "scheduled", "Aromatherapy (Aufguss) every day at 15:00, 19:00 and 21:00"),
}
HEAT_SOURCE = "read off the venue's own page, 15 Nov 2026"

# --- A banya is a banya whoever throws the water; the badge says so.
BANYA = {"Archimedes Banya"}

LAST_CHECKED = "15 November 2026"
