# NSRIT eSports Arena — Complete Deployment Guide

## 🎮 Project Overview
Production-ready Django esports tournament platform for NSRIT

**Tech Stack:** Django 4.2 | PostgreSQL | Razorpay | Gunicorn | Nginx

---

## 📁 Project Structure

```
nsrit_esports/
├── manage.py
├── requirements.txt
├── Procfile                    ← Render/Heroku deployment
├── runtime.txt                 ← Python version
├── .env.example                ← Environment variable template
├── nginx.conf                  ← Production Nginx config
├── gunicorn.service            ← Systemd service file
│
├── nsrit_esports/              ← Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                   ← Custom user model (@nsrit.edu.in)
│   ├── models.py               ← NSRITUser (AbstractBaseUser)
│   ├── forms.py                ← Registration, Login forms
│   ├── views.py                ← Register, Login, Logout
│   ├── urls.py
│   └── admin.py
│
├── players/                    ← Player profiles
│   ├── models.py               ← Player (IGN, Game ID, Stats, Tier)
│   ├── views.py                ← Dashboard, Profile, List
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── tournaments/                ← Tournament management
│   ├── models.py               ← Tournament, Registration (+ 3-layer dupe prevention)
│   ├── views.py                ← List, Detail, Register, My-Registrations
│   ├── urls.py
│   ├── urls_home.py
│   ├── admin.py
│   └── management/
│       └── commands/
│           └── seed_data.py    ← Sample data seeder
│
├── teams/                      ← Team management
│   ├── models.py               ← Team, TeamMember, TeamInvite
│   ├── views.py                ← Create, Invite, Join, Leave
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── payments/                   ← Razorpay integration
│   ├── models.py               ← Payment (bound to player+tournament)
│   ├── views.py                ← Initiate, Success, Failure, Webhook
│   ├── urls.py
│   └── admin.py
│
├── leaderboard/                ← Rankings system
│   ├── models.py               ← LeaderboardEntry, TeamLeaderboard
│   ├── views.py                ← Leaderboard display, rebuild
│   ├── urls.py
│   └── admin.py
│
├── matches/                    ← Bracket system
│   ├── models.py               ← Match, TournamentResult
│   ├── views.py                ← Bracket display, generate, update results
│   ├── urls.py
│   └── admin.py
│
├── templates/                  ← All HTML templates
│   ├── base.html               ← Master layout with nav+footer
│   ├── home.html               ← Hero + Featured Tournaments + Leaderboard
│   ├── accounts/
│   │   ├── register.html
│   │   └── login.html
│   ├── players/
│   │   ├── dashboard.html      ← HUD-style player dashboard
│   │   ├── profile.html
│   │   ├── create_profile.html
│   │   ├── edit_profile.html
│   │   └── player_list.html
│   ├── tournaments/
│   │   ├── list.html           ← Tournament browser with filters
│   │   ├── detail.html         ← Tournament detail + registration
│   │   └── my_registrations.html
│   ├── teams/
│   │   ├── list.html
│   │   ├── detail.html
│   │   ├── create_team.html
│   │   └── invite.html
│   ├── payments/
│   │   ├── payment_page.html   ← Razorpay checkout
│   │   └── history.html
│   ├── leaderboard/
│   │   └── leaderboard.html    ← Full rankings with podium
│   └── matches/
│       ├── bracket.html        ← Visual tournament bracket
│       └── update_result.html
│
└── static/
    └── css/
        └── arena.css           ← Complete CSS (Neo Arena theme)
```

---

## 🚀 Local Development Setup

### Step 1: Clone & Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Environment Variables

```bash
# Copy and configure .env
cp .env.example .env
# Edit .env with your Razorpay keys and database URL
```

### Step 3: Database Setup

```bash
# Run migrations
python manage.py makemigrations accounts
python manage.py makemigrations players
python manage.py makemigrations tournaments
python manage.py makemigrations teams
python manage.py makemigrations payments
python manage.py makemigrations leaderboard
python manage.py makemigrations matches
python manage.py migrate

# Seed sample data (creates tournaments + admin account)
python manage.py seed_data

# Collect static files
python manage.py collectstatic
```

### Step 4: Run Server

```bash
python manage.py runserver
```

Access: http://127.0.0.1:8000

**Admin Panel:** http://127.0.0.1:8000/admin/
- Username: `ADMIN001`
- Password: `nsrit@admin2024`

---

## 💳 Razorpay Setup

1. Create account at [razorpay.com](https://razorpay.com)
2. Get API keys from Dashboard → Settings → API Keys
3. Add to `.env`:
```env
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxxxxx
```
4. Configure webhook URL: `https://yourdomain.com/payments/webhook/`

### Payment Flow
```
Student registers for paid tournament
↓
System creates Razorpay order
↓
Payment page shown (Razorpay checkout widget)
↓
Student pays → Razorpay confirms
↓
Webhook fires → Registration confirmed
↓
Player appears in tournament roster
```

---

## 🔒 3-Layer Duplicate Registration Prevention

| Layer | Where | How |
|-------|-------|-----|
| **Layer 1** | Database | `unique_together = [('player', 'tournament')]` in Registration model |
| **Layer 2** | Server | `if Registration.objects.filter(player=player, tournament=tournament).exists():` check before creating |
| **Layer 3** | Payment | `unique_together = [('player', 'tournament')]` in Payment model |

---

## 🌐 Production Deployment (Render)

### Option A: Render (Recommended)

1. Push code to GitHub
2. Create new Web Service on [render.com](https://render.com)
3. Set:
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command:** `gunicorn nsrit_esports.wsgi`
4. Add environment variables from `.env.example`
5. Create PostgreSQL database in Render → copy `DATABASE_URL`

### Option B: Railway

```bash
railway init
railway up
railway vars set SECRET_KEY=... RAZORPAY_KEY_ID=...
```

### Option C: DigitalOcean VPS

```bash
# 1. Update server
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
sudo apt install python3-pip python3-venv nginx postgresql -y

# 3. Setup project
git clone your-repo /var/www/nsrit_esports
cd /var/www/nsrit_esports
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env  # Edit with production values

# 5. Database
sudo -u postgres createdb nsrit_esports
sudo -u postgres createuser nsrit_user -P
python manage.py migrate
python manage.py seed_data
python manage.py collectstatic

# 6. Gunicorn service
sudo cp gunicorn.service /etc/systemd/system/
sudo systemctl enable gunicorn
sudo systemctl start gunicorn

# 7. Nginx
sudo cp nginx.conf /etc/nginx/nginx.conf
# Edit server_name in nginx.conf
sudo nginx -t && sudo systemctl reload nginx
```

---

## 🎛️ Admin Panel Features

Access `/admin/` to:

| Feature | Location |
|---------|----------|
| Create tournaments | Tournaments → Add Tournament |
| Open/close registration | Tournament list → Change status |
| Verify payments | Payments → Mark as successful |
| Generate brackets | Matches → Generate Bracket (via admin view) |
| Export participants | Select all → Export (custom action) |
| Manage teams | Teams section |
| Update leaderboard | Leaderboard → Rebuild |
| Verify students | Accounts → Verify selected |

---

## 📊 Database Schema

| Table | Purpose |
|-------|---------|
| `users` | NSRITUser (AbstractBaseUser) |
| `players` | Extended player profiles |
| `teams` | Team entities |
| `team_members` | Player-team memberships |
| `team_invites` | Pending team invitations |
| `tournaments` | Tournament entities |
| `registrations` | Player-tournament entries (unique constraint) |
| `payments` | Razorpay payment records |
| `matches` | Tournament bracket matches |
| `results` | Final tournament results |
| `leaderboard` | Player rankings |
| `team_leaderboard` | Team rankings |

---

## 🎨 Theme: Neo Arena — Collegiate Cyber Gaming

| Element | Value |
|---------|-------|
| Primary Red | `#C41212` |
| Dark Background | `#0B0F1A` |
| Neon Accent | `#00F5FF` |
| Secondary Accent | `#8A2BE2` |
| Heading Font | Orbitron / Rajdhani |
| Body Font | Inter |
| Design Ratio | 60% dark / 25% red / 15% neon |

---

## 📧 Support

**NSRIT eSports Arena**
Nadimpalli Satyanarayana Raju Institute of Technology
Sontyam, Visakhapatnam – 531173
esports@nsrit.edu.in
