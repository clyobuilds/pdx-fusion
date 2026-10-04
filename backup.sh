#!/bin/sh
# Make a backup of the site's data: database (safe while the site runs), flyers, settings files.
# usage: ./backup.sh            -> writes backups/pdxfusion-YYYY-MM-DD.tar.gz  (keeps the newest 14)
# Copy the file somewhere else too (another computer or storage): a backup on the same server is not enough.
set -e
cd "$(dirname "$0")"
mkdir -p backups .backup-tmp
python3 - <<'PY'
import sqlite3
src = sqlite3.connect("data/gancio.sqlite")
dst = sqlite3.connect(".backup-tmp/gancio.sqlite")
src.backup(dst); dst.close(); src.close()
PY
OUT="backups/pdxfusion-$(date +%F).tar.gz"
tar czf "$OUT" -C . .backup-tmp/gancio.sqlite data/uploads data/user_locale .env 2>/dev/null || tar czf "$OUT" -C . .backup-tmp/gancio.sqlite data/uploads data/user_locale
rm -rf .backup-tmp
ls -1t backups/pdxfusion-*.tar.gz | tail -n +15 | xargs rm -f 2>/dev/null || true
echo "Backup written: $OUT"
