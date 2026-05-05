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
from django.contrib.auth import get_user_model

User = get_user_model()

email = '25nu1a4436@nsrit.edu.in'
password = 'Admin@1234'

user, created = User.objects.get_or_create(email=email)

user.is_staff = True
user.is_superuser = True

user.set_password(password)

if hasattr(user, 'email_verified'):
    user.email_verified = True

user.save()

print('Admin created/updated successfully')
"
