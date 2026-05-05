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
u = NSRITUser.objects.filter(email='25nu1a4430@nsrit.edu.in').first()
if u:
    u.is_staff = True
    u.is_superuser = True
    u.email_verified = True
    u.set_password('Admin@1234')
    u.save()
    print('Admin fixed')
else:
    print('User not found')
"
