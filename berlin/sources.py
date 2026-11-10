# -*- coding: utf-8 -*-
"""Claims we can re-read from a venue's OWN page, and prove.

selfupdate.py uses these to change the data without a human. That is only safe
where a claim is pinned to a stable label, so every rule here is a regex that
must match EXACTLY ONCE on the page. Zero matches means the page moved and we
learn nothing; two or more means the anchor is ambiguous and we could pick the
wrong number. Neither is proof, and neither is applied.

Venues absent from PRICES are not neglected - they were measured and rejected:
KIEZ SAUNA, Luetzow, Palace, Titanic and ANTI SPA either render prices with
JavaScript or print bare amounts with no label beside them ("EUR 14.50 EUR
14.50 EUR 29 EUR 29"), so no anchor can tell one tariff from another. Those
stay with the human, via the weekly audit.

Each price rule is (template, headline, pattern):
  template  the exact fragment as it appears in priceLabel, with {} for the
            amount - the old fragment must appear there exactly once
  headline  True for the figure that also feeds the numeric `price` field
  pattern   one capture group, the amount, on the venue's own page
"""

PRICES = {
 "Vabali": [
   ("€{} / 2h",  True,  r"2 Stunden\s*(\d{1,3},\d{2})\s*€"),
   ("€{} / 4h",  False, r"4 Stunden\s*(\d{1,3},\d{2})\s*€"),
   ("€{} day",   False, r"Tageskarte\s*(\d{1,3},\d{2})\s*€"),
 ],
 "Olivin": [
   ("€{} / 4h",              True,  r"Finnische Sauna für 4 Stunden:\s*(\d{1,3})\s*€"),
   ("reduced €{}",           False, r"Ermäßigt für 4 Stunden:\s*(\d{1,3})\s*€"),
   ("extra hour +€{}",       False, r"Verlängerung plus 1 Stunde:\s*(\d{1,3})\s*€"),
   ("late tariff from 21:30 €{}", False, r"Spättarif ab 21\.30 Uhr:\s*(\d{1,3})\s*€"),
 ],
 "LIQUIDROM": [
   ("Short Escape 90 min €{}", False, r"Short Escape 90:\s*90 min\. thermal spa\s*(\d{1,3},\d{2})\s*€"),
   ("Urban Flow 2h €{}",       True,  r"Urban Flow 120:\s*120 min\. thermal spa\s*(\d{1,3},\d{2})\s*€"),
   ("Deep Dive 3h €{}",        False, r"Deep Dive 180:\s*180 min\. thermal spa\s*(\d{1,3},\d{2})\s*€"),
   ("+€{} per extra 30 min",   False, r"Extension per additional 30 min\.\s*\+\s*(\d{1,3},\d{2})\s*€"),
   ("sauna add-on +€{}",       False, r"Sauna area add-on\s*\+\s*(\d{1,3},\d{2})\s*€"),
 ],
 "Finnland Zentrum": [
   ("€{} for up to 4 people (3h)", True,  r"Familiensauna ab [\d.]+:\s*(\d{1,3})\s*€\s*bis 4 Personen"),
   ("extra adults €{}",            False, r"weitere Erwachsene\s*(\d{1,3})\s*€"),
 ],
}

# A dated closure the venue publishes itself. The capture groups are
# (day, month, year); a two-digit year is read as 20xx. Stadtbad shortened its
# 2026 summer break from 31 Oct to 30 Sep without telling anyone, which is
# precisely the drift a weekly re-read is for.
CLOSURES = {
 "Stadtbad Neukölln": r"[Gg]eschlossen bis\s*(\d{1,2})\.(\d{1,2})\.(\d{2,4})",
}
