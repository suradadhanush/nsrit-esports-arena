#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# Render Build Script — NSRIT eSports Arena
# ─────────────────────────────────────────────────────────────────
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# ── One-time: unlock all existing unverified accounts
python manage.py shell -c "
from accounts.models import NSRITUser
updated = NSRITUser.objects.filter(email_verified=False).update(email_verified=True)
print(f'Unlocked {updated} unverified accounts')
"
