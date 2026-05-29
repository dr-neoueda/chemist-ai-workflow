#!/usr/bin/env bash
# check-consistency.sh — release-hygiene guard for the caw distribution.
#
# Catches the recurring manual-mirroring mistakes:
#   1. plugin version vs marketplace version drift
#   2. plugin <-> codex-plugin shared-asset drift (references/ + templates/ must
#      stay byte-identical; SKILL.md legitimately differs per CLI so is excluded)
#   3. personalization leaks in the distributed tree (author / lab / compounds)
#
# Usage:  bash scripts/check-consistency.sh
# Exit:   0 = all good, non-zero = at least one problem (CI-friendly).

set -u
cd "$(dirname "$0")/.." || exit 2
fail=0
red=$'\033[0;31m'; grn=$'\033[0;32m'; dim=$'\033[2m'; off=$'\033[0m'
ok()   { printf '%s OK %s %s\n' "$grn" "$off" "$*"; }
bad()  { printf '%s BAD%s %s\n' "$red" "$off" "$*"; fail=1; }

json_version() { # $1 = file
  grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$1" | head -1 | sed 's/.*"\([^"]*\)"$/\1/'
}

# --- 1. plugin vs marketplace version ---
pv=$(json_version plugin/.claude-plugin/plugin.json)
mv=$(json_version .claude-plugin/marketplace.json)
cv=$(json_version codex-plugin/.codex-plugin/plugin.json)
if [ -n "$pv" ] && [ "$pv" = "$mv" ]; then
  ok "plugin version == marketplace version ($pv)"
else
  bad "plugin ($pv) != marketplace ($mv) — bump both together"
fi
printf '%s    codex-plugin version: %s%s\n' "$dim" "${cv:-?}" "$off"

# --- 2. plugin <-> codex mirror (byte-identical shared assets only) ---
mirror_dirs=(
  "skills/caw-slides/references"
  "skills/caw-slides/templates"
)
for d in "${mirror_dirs[@]}"; do
  p="plugin/$d"; c="codex-plugin/$d"
  if [ ! -d "$p" ] || [ ! -d "$c" ]; then
    printf '%s    skip mirror %s (missing)%s\n' "$dim" "$d" "$off"; continue
  fi
  # Exclude build/run artifacts (all gitignored): bytecode + smoke-test output.
  dx=(-x '__pycache__' -x '*.pyc' -x 'presentations')
  if diff -r -q "${dx[@]}" "$p" "$c" >/dev/null 2>&1; then
    ok "mirror identical: $d"
  else
    bad "mirror DRIFT: $d (plugin vs codex-plugin differ)"
    diff -r -q "${dx[@]}" "$p" "$c" 2>&1 | sed 's/^/      /'
  fi
done

# --- 3. personalization leak scan (distributed tree only) ---
# Specific proper nouns only — generic field terms (MLIP/CP2K/DFT) are allowed.
leak_re='aaBrAdox|SPReAD|Bis\(BrPhCH2O\)|NU-[0-9]|PILATUS|n267302|neoueda@'
hits=$(grep -RInE "$leak_re" plugin codex-plugin 2>/dev/null \
        | grep -v 'Binary file' || true)
if [ -z "$hits" ]; then
  ok "no personalization leaks in plugin/ or codex-plugin/"
else
  bad "personalization leak(s) found:"
  printf '%s\n' "$hits" | sed 's/^/      /'
fi

echo
if [ "$fail" -eq 0 ]; then printf '%sAll consistency checks passed.%s\n' "$grn" "$off"
else printf '%sConsistency checks FAILED — fix the BAD items above.%s\n' "$red" "$off"; fi
exit "$fail"
