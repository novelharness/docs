#!/usr/bin/env bash
set -euo pipefail

curl -sS http://localhost:8100/health
curl -sS http://localhost:8200/health
curl -sS -X POST http://localhost:8100/api/v1/chapters/run \
  -H 'Content-Type: application/json' \
  -d '{"chapter_id":"ch001","brief":"主角初战","target_words":1800}'
