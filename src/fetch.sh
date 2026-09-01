#!/bin/zsh
# fetch.sh <outfile> <overpass-ql>
OUT=$1; Q=$2
EPS=("https://overpass-api.de/api/interpreter" "https://overpass.private.coffee/api/interpreter" "https://overpass.osm.ch/api/interpreter" "https://overpass.kumi.systems/api/interpreter")
for attempt in 1 2 3; do
  for EP in $EPS; do
    curl -s --max-time 180 -A "sauna-map-build/1.0 (personal project)" -X POST --data-urlencode "data=$Q" "$EP" -o "$OUT"
    if head -c 1 "$OUT" 2>/dev/null | grep -q '{'; then
      echo "OK  $OUT  <- $EP  ($(wc -c < $OUT) bytes)"; exit 0
    fi
  done
  echo "  retry $attempt for $OUT ..."; sleep 12
done
echo "FAILED $OUT"; exit 1
