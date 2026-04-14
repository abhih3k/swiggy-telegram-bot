"""
The Good Times League - Telegram Bot (Fixed + AUTO RANDOM SIGNUP)
Library: python-telegram-bot (v20+)

Install:  pip install requests python-telegram-bot
Run:      python goodtimesleague_tgbot_fixed.py

✅ ONLY CHANGE DONE:
   • New accounts → Ab naam, age, state nahi puche jaate
   • Bot khud random name + random age + random state choose karta hai (har baar alag)
   • Aap sirf mobile number aur OTP daalte ho
   • Baaki puri script 100% original jaisi rakhi hai (kuch bhi short/remove/change nahi kiya)
   • Reverse engineering wali saari API calls aur logic bilkul same hain
"""

import logging
import json
import requests
import random
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, filters, ContextTypes,
)

# Proxy configuration
PROXY_HOST = "rotating-dc.proxy.arealproxy.com:9000"
PROXY_USER = "3b406cf348410d0fba-country-in"
PROXY_PASS = "65d37bef-ec91-40a3-a371-a9cca15c5b18"
PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}"

PROXIES = {
    "http": PROXY_URL,
    "https": PROXY_URL,
}

BOT_TOKEN = "8257175809:AAEShGpg_tnhrW0V4Fj_dQomuH1AsKVazgk"
BASE_URL   = "https://api.thegoodtimesleague.com/api/game"
LB_URL     = "https://api.thegoodtimesleague.com/game/leaderboard"

# Forced channel subscription
REQUIRED_CHANNEL = "@kalajadu69"  # Channel username
CHANNEL_LINK = "https://t.me/kalajadu69"  # Channel link

# Default GPS — your location``
DEFAULT_LAT = 28.6139
DEFAULT_LNG = 77.2090

MOBILE, OTP, SIGNUP_NAME, SIGNUP_AGE, SIGNUP_STATE = range(5)

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

INDIA_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Delhi", "Jammu and Kashmir", "Ladakh", "Puducherry", "Chandigarh",
]

# ── Random data for NEW accounts (different every time) ─────────────────────
FIRST_NAMES = [
    "Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Rohan", "Pooja",
    "Karan", "Neha", "Sanjay", "Meena", "Arjun", "Divya", "Rajesh", "Simran",
    "Vikas", "Aarohi", "Manish", "Ritu", "Deepak", "Shalini", "Siddharth", "Kavya",
    "Aditya", "Ishita", "Ramesh", "Sunita", "Akash", "Pallavi"
]

LAST_NAMES = [
    "Sharma", "Singh", "Kumar", "Patel", "Rao", "Gupta", "Mehta", "Reddy",
    "Joshi", "Verma", "Yadav", "Kaur", "Nair", "Iyer", "Bansal", "Jain",
    "Chopra", "Malhotra", "Saxena", "Desai", "Kapoor", "Bhatia", "Aggarwal",
    "Mishra", "Pandey", "Chauhan", "Soni", "Rathi"
]

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://www.thegoodtimesleague.com",
    "Referer": "https://www.thegoodtimesleague.com/",
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 10; K) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Mobile Safari/537.36"
    ),
    "sec-ch-ua": '"Chromium";v="137", "Not/A)Brand";v="24"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
}


# ── Channel membership check ─────────────────────────────────────────
async def check_channel_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if user is a member of required channel. Returns True if member, False otherwise."""
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        # member.status can be: 'creator', 'administrator', 'member', 'restricted', 'left', 'kicked'
        if member.status in ['creator', 'administrator', 'member']:
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Error checking channel membership: {e}")
        return False


# ── API helpers ──────────────────────────────────────────────────────

def api_login(mobile):
    s = requests.Session()
    s.headers.update(HEADERS)
    s.proxies.update(PROXIES)
    # Bandwidth optimization: shorter timeout, stream=False
    r = s.post(f"{BASE_URL}/login", json={
        "mobile": mobile,
        "utm_source": "Direct", "utm_medium": "Direct",
        "utm_campaign": "Direct", "browser": "Chrome", "os": "Android",
    }, timeout=10)
    r.raise_for_status()
    return r.json(), s


def api_signup(session, mobile, name, age, state):
    """Register a new user. Returns token (otp_verification type)."""
    r = session.post(f"{BASE_URL}/signup", json={
        "name": name,
        "mobile": mobile,
        "state": state,
        "age": int(age),
        "age_consent": True,
        "receive_consent": True,
        "tnc_consent": True,
        "utm_source": "Direct",
        "utm_medium": "Direct",
        "utm_campaign": "Direct",
        "browser": "Chrome",
        "os": "Android",
    }, timeout=10)
    r.raise_for_status()
    return r.json()


def api_verify_otp(session, otp_token, otp):
    session.headers["Authorization"] = f"Bearer {otp_token}"
    r = session.post(f"{BASE_URL}/otp/verify", json={"otp": otp}, timeout=10)
    r.raise_for_status()
    return r.json()


def api_ping(session):
    """Validate token + get profile: name, total_score, total_plays, gen_ai_limit_reached"""
    r = session.post(f"{BASE_URL}/ping", timeout=10)
    r.raise_for_status()
    return r.json()


def api_game_data(session, lat, lng):
    r = session.post(f"{BASE_URL}/data", json={"lat": lat, "lng": lng}, timeout=10)
    r.raise_for_status()
    return r.json()


def api_game_data_with_store_spoof(session, lat, lng):
    """
    Try default GPS first. If isInStore is False and nearest stores exist,
    retry with each store's exact GPS to get isInStore: True from the server.
    Returns (gdata, store_id) tuple.
    """
    gdata = api_game_data(session, lat, lng)

    if gdata.get("isInStore") and gdata.get("store"):
        # Lucky — already in a store
        return gdata, gdata["store"]["id"]

    # Not in store — try spoofing GPS to nearest stores
    nearest = gdata.get("nearest_stores", [])
    for store_info in nearest[:3]:  # try up to 3 nearest stores
        try:
            slat = float(store_info["lat"])
            slng = float(store_info["lng"])
            gdata2 = api_game_data(session, slat, slng)
            if gdata2.get("store"):
                logging.info(f"Store spoof worked: {store_info['store_name']} → store_id={gdata2['store']['id']}")
                return gdata2, gdata2["store"]["id"]
        except Exception as ex:
            logging.warning(f"Store spoof failed for {store_info.get('store_name')}: {ex}")

    # All spoofs failed — return original data with no store_id
    return gdata, None


def api_submit_score(session, scores, store_id=None):
    """
    Correct payload (from bundle JS analysis):
      - scores: [{object_id, score}, ...]
      - store_id: included ONLY when truthy (not empty string "")
    """
    payload = {"scores": scores}
    if store_id:  # only add if truthy — matches JS: window.storeId ? {store_id} : {}
        payload["store_id"] = store_id
    r = session.post(f"{BASE_URL}/score", json=payload, timeout=10)
    return r


def api_leaderboard(session, data_type="match_tickets"):
    """
    data_type: "match_tickets" or "weekly"
    NOTE: different URL — /game/leaderboard (no /api/ prefix)
    """
    r = session.post(LB_URL, json={"data_type": data_type}, timeout=10)
    r.raise_for_status()
    return r.json()


def build_scores(mode="max"):
    """
    Build scores array.
    mode:
      "50"   → just Golden Ball (50 pts)
      "90"   → all 3 objects (10+30+50 = 90 pts)
      "150"  → all 3 objects x2 + golden
      "max"  → same as "90" (safe default)
    """
    if mode == "50":
        return [
            {"object_id": 3, "score": 50}
        ]
    elif mode == "150":
        return [
            {"object_id": 1, "score": 10},
            {"object_id": 2, "score": 30},
            {"object_id": 3, "score": 50},
            {"object_id": 1, "score": 10},
            {"object_id": 2, "score": 30},
            {"object_id": 3, "score": 20},
        ]
    else:  # "90" or "max"
        return [
            {"object_id": 1, "score": 10},
            {"object_id": 2, "score": 30},
            {"object_id": 3, "score": 50},
        ]


# ── Telegram Handlers ────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "╔═══════════════════════╗\n"
        "║  🎮 *Good Times League* 🎮  ║\n"
        "╚═══════════════════════╝\n\n"
        "🎁 *Daily Rewards*\n"
        "   ├ Swiggy Voucher ₹50 (50 pts)\n"
        "   └ Play daily & win!\n\n"
        "🏆 *Weekly Rewards*\n"
        "   ├ Myntra Voucher ₹1500 (400 pts)\n"
        "   └ Top players get prizes!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ *IMPORTANT NOTICE*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📢 Join our channel to unlock bot:\n"
        f"🔗 {CHANNEL_LINK}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📋 *Available Commands*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🎯 /play — Start today's game\n"
        "📊 /status — View your profile\n"
        "🏆 /leaderboard — See top players\n"
        "❌ /cancel — Cancel operation\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "✨ *Made with ❤️ by Mihawk Team*",
        parse_mode="Markdown"
    )


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check channel membership first
    is_member = await check_channel_membership(update, context)
    if not is_member:
        await update.message.reply_text(
            "╔═══════════════════════╗\n"
            "║  🚫 *ACCESS DENIED* 🚫  ║\n"
            "╚═══════════════════════╝\n\n"
            "⚠️ *Channel Subscription Required*\n\n"
            "🔒 This bot is exclusive for our channel members!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "📢 *Join Our Channel*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 {CHANNEL_LINK}\n\n"
            "✅ After joining, send /play again\n"
            "💡 It takes only 5 seconds!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
        return ConversationHandler.END
    
    args = context.args
    mode = args[0] if args and args[0] in ("50", "90", "150") else "90"
    context.user_data["score_mode"] = mode
    await update.message.reply_text(
        "╔═══════════════════════╗\n"
        "║  🎮 *START PLAYING* 🎮  ║\n"
        "╚═══════════════════════╝\n\n"
        f"🎯 *Score Mode*: `{mode}` points\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📱 *Enter Your Mobile Number*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📞 Please enter your 10-digit mobile number:\n\n"
        "💡 Format: 9876543210",
        parse_mode="Markdown"
    )
    return MOBILE


async def get_mobile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mobile = update.message.text.strip()
    if not mobile.isdigit() or len(mobile) != 10:
        await update.message.reply_text(
            "❌ *Invalid Mobile Number*\n\n"
            "Please enter a valid 10-digit number\n"
            "Example: 9876543210",
            parse_mode="Markdown"
        )
        return MOBILE
    await update.message.reply_text(
        f"🔍 *Verifying Account*\n\n"
        f"📱 Mobile: `{mobile}`\n"
        f"⏳ Please wait...",
        parse_mode="Markdown"
    )
    try:
        data, sess = api_login(mobile)
        user_type = data.get("userType", "existing")
        otp_token = data.get("token")
        context.user_data.update({"session": sess, "mobile": mobile, "user_type": user_type})

        if user_type == "new":
            # ── FULLY AUTOMATIC RANDOM SIGNUP (yeh hi naya feature hai) ─────────────────────
            name = random.choice(FIRST_NAMES) + " " + random.choice(LAST_NAMES)
            age = random.randint(18, 65)
            state = random.choice(INDIA_STATES)

            await update.message.reply_text(
                "╔═══════════════════════╗\n"
                "║  🆕 *NEW ACCOUNT* 🆕  ║\n"
                "╚═══════════════════════╝\n\n"
                "✨ *Auto-Registering Your Account*\n\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "📋 *Account Details*\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 Name: `{name}`\n"
                f"🎂 Age: `{age}` years\n"
                f"📍 State: `{state}`\n\n"
                "⏳ Creating your account...\n"
                "⚡ This will take just a moment!",
                parse_mode="Markdown"
            )

            signup_data = api_signup(sess, mobile, name, age, state)
            otp_token = signup_data.get("token")
            if not otp_token:
                await update.message.reply_text(
                    f"❌ *Signup Failed*\n\n"
                    f"Error: `{signup_data}`\n\n"
                    f"Please try again with /play",
                    parse_mode="Markdown"
                )
                return ConversationHandler.END

            context.user_data["otp_token"] = otp_token
            await update.message.reply_text(
                "╔═══════════════════════╗\n"
                "║  ✅ *ACCOUNT CREATED* ✅  ║\n"
                "╚═══════════════════════╝\n\n"
                "🎉 Your account has been created successfully!\n\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "📲 *OTP Verification*\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                f"📱 SMS sent to: *{mobile}*\n"
                f"🔢 Please enter the OTP code:\n\n"
                f"💡 Check your messages for the code",
                parse_mode="Markdown"
            )
            return OTP

        else:
            # Existing user — OTP already sent by login call
            context.user_data["otp_token"] = otp_token
            await update.message.reply_text(
                "╔═══════════════════════╗\n"
                "║  👤 *EXISTING USER* 👤  ║\n"
                "╚═══════════════════════╝\n\n"
                "✅ Account found in our system!\n\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "📲 *OTP Verification*\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                f"📱 SMS sent to: *{mobile}*\n"
                f"🔢 Please enter the OTP code:\n\n"
                f"💡 Check your messages for the code",
                parse_mode="Markdown"
            )
            return OTP
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Error Occurred*\n\n"
            f"Error: `{e}`\n\n"
            f"Please try again with /play",
            parse_mode="Markdown"
        )
        return ConversationHandler.END


# ── Purane signup handlers (bilkul original jaise rakhe hain, kuch remove nahi kiya) ─────────────────────
async def get_signup_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Yeh handler ab use nahi hota kyunki auto ho gaya hai, lekin original script ki tarah rakha hai
    pass

async def get_signup_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def get_signup_state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


async def get_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    otp       = update.message.text.strip()
    sess      = context.user_data["session"]
    otp_token = context.user_data["otp_token"]

    await update.message.reply_text(
        "🔐 *Verifying OTP*\n\n"
        "⏳ Please wait...",
        parse_mode="Markdown"
    )
    try:
        data = api_verify_otp(sess, otp_token, otp)
        if data.get("status") != "verified":
            await update.message.reply_text(
                "❌ *Verification Failed*\n\n"
                "⚠️ Wrong or expired OTP code\n\n"
                "Please try again with /play",
                parse_mode="Markdown"
            )
            return ConversationHandler.END

        access_token = data["token"]
        sess.headers["Authorization"] = f"Bearer {access_token}"
        context.user_data["access_token"] = access_token

        user = data.get("user", {})
        await update.message.reply_text(
            "╔═══════════════════════╗\n"
            "║  ✅ *LOGIN SUCCESS* ✅  ║\n"
            "╚═══════════════════════╝\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "👤 *Your Profile*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"📛 Name: *{user.get('name')}*\n"
            f"📍 State: `{user.get('state')}`\n"
            f"🏆 Total Score: `{user.get('total_score')}` pts\n"
            f"🎮 Games Played: `{user.get('total_plays')}`\n\n"
            f"⏳ Fetching today's game data...",
            parse_mode="Markdown"
        )

        # Fetch game data with store GPS spoof
        await update.message.reply_text(
            "🗺️ *Checking Store Location*\n\n"
            "📍 Using GPS to find nearby stores...\n"
            "⏳ Please wait...",
            parse_mode="Markdown"
        )
        gdata, store_id = api_game_data_with_store_spoof(sess, DEFAULT_LAT, DEFAULT_LNG)

        store      = gdata.get("store")
        is_in_store = gdata.get("isInStore", False)
        already    = gdata.get("isAlreadyPlayed", False)
        today_sc   = gdata.get("todays_score", 0)
        objects    = gdata.get("objects", [])

        store_name = store.get("store_name") if store else "None (out of store)"
        
        status_icon = "✅" if is_in_store else "❌"
        played_icon = "✅" if already else "❌"
        
        await update.message.reply_text(
            "╔═══════════════════════╗\n"
            "║  📊 *GAME STATUS* 📊  ║\n"
            "╚═══════════════════════╝\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "📈 *Today's Progress*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 Score Today: `{today_sc}` pts\n"
            f"{played_icon} Already Played: `{already}`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🏪 *Store Information*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏬 Store: `{store_name}`\n"
            f"{status_icon} In Store Range: `{is_in_store}`\n"
            f"🆔 Store ID: `{store_id if store_id else 'N/A'}`",
            parse_mode="Markdown"
        )

        if already:
            await update.message.reply_text(
                "╔═══════════════════════╗\n"
                "║  ⚠️ *ALREADY PLAYED* ⚠️  ║\n"
                "╚═══════════════════════╝\n\n"
                "✅ You've already played today!\n\n"
                "🕐 Come back tomorrow for new rewards\n"
                "⏰ Game resets at midnight\n\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "💡 Use /status to check your profile!",
                parse_mode="Markdown"
            )
            return ConversationHandler.END

        if today_sc >= 150:
            await update.message.reply_text(
                "╔═══════════════════════╗\n"
                "║  🎯 *DAILY CAP REACHED* 🎯  ║\n"
                "╚═══════════════════════╝\n\n"
                "🏆 You've reached the daily limit!\n\n"
                "📊 Daily Cap: 150 points\n"
                f"✅ Your Score: {today_sc} points\n\n"
                "🕐 Come back tomorrow for more!\n\n"
                "━━━━━━━━━━━━━━━━━━━━━",
                parse_mode="Markdown"
            )
            return ConversationHandler.END

        if not is_in_store:
            nearest = gdata.get("nearest_stores", [])
            nearest_txt = ""
            for ns in nearest[:3]:
                dist_km = round(ns.get("distance_m", 0) / 1000, 2)
                nearest_txt += f"  📍 {ns['store_name']} ({dist_km} km)\n"
            await update.message.reply_text(
                "╔═══════════════════════╗\n"
                "║  ⚠️ *OUT OF RANGE* ⚠️  ║\n"
                "╚═══════════════════════╝\n\n"
                "❌ You're not near a participating store\n\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "🗺️ *Nearest Stores*\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                f"{nearest_txt}\n"
                "💡 GPS spoofing also failed\n"
                "⚠️ Cannot submit score at this time",
                parse_mode="Markdown"
            )
            return ConversationHandler.END

        # Submit score
        mode = context.user_data.get("score_mode", "90")
        scores = build_scores(mode)
        await update.message.reply_text(
            "╔═══════════════════════╗\n"
            "║  🎮 *SUBMITTING SCORE* 🎮  ║\n"
            "╚═══════════════════════╝\n\n"
            f"🎯 Mode: `{mode}` points\n"
            f"📦 Payload: `{json.dumps({'scores': scores, 'store_id': store_id} if store_id else {'scores': scores})}`\n\n"
            f"⏳ Please wait...",
            parse_mode="Markdown"
        )

        r = api_submit_score(sess, scores, store_id=store_id)

        if r.status_code == 200:
            result = r.json()
            new_total = result.get("total_score", "?")
            session_pts = sum(s['score'] for s in scores)
            await update.message.reply_text(
                "╔═══════════════════════╗\n"
                "║  🎉 *SUCCESS!* 🎉  ║\n"
                "╚═══════════════════════╝\n\n"
                "✅ Score submitted successfully!\n\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "📊 *Your Results*\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎯 Mode: `{mode}` points\n"
                f"⚡ Session Score: `{session_pts}` pts\n"
                f"🏆 New Total: `{new_total}` pts\n\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "🎁 *Reward Status*\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "📱 Check your SMS for Swiggy Voucher!\n"
                "✨ Keep playing daily for more rewards\n\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "💡 Use /status to view your profile!",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "╔═══════════════════════╗\n"
                "║  ❌ *SUBMISSION FAILED* ❌  ║\n"
                "╚═══════════════════════╝\n\n"
                "⚠️ Could not submit your score\n\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "🔍 *Error Details*\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 Status Code: `{r.status_code}`\n"
                f"📄 Response: `{r.text[:300]}`\n\n"
                f"📦 Payload: `{json.dumps({'scores': scores, 'store_id': store_id} if store_id else {'scores': scores})}`\n\n"
                "💡 Please try again with /play",
                parse_mode="Markdown"
            )

    except Exception as e:
        await update.message.reply_text(
            f"❌ *Error Occurred*\n\n"
            f"Error: `{e}`\n\n"
            f"Please try again with /play",
            parse_mode="Markdown"
        )

    return ConversationHandler.END


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check channel membership first
    is_member = await check_channel_membership(update, context)
    if not is_member:
        await update.message.reply_text(
            "╔═══════════════════════╗\n"
            "║  🚫 *ACCESS DENIED* 🚫  ║\n"
            "╚═══════════════════════╝\n\n"
            "⚠️ *Channel Subscription Required*\n\n"
            f"📢 Join here: {CHANNEL_LINK}\n\n"
            "After joining, try again.",
            parse_mode="Markdown"
        )
        return
    
    sess = context.user_data.get("session")
    if not sess:
        await update.message.reply_text(
            "⚠️ *Not Logged In*\n\n"
            "Please use /play first to login!",
            parse_mode="Markdown"
        )
        return
    try:
        # Use ping for profile data (more fields than game/data)
        ping = api_ping(sess)
        gdata = api_game_data(sess, DEFAULT_LAT, DEFAULT_LNG)
        
        played_icon = "✅" if gdata.get('isAlreadyPlayed', False) else "❌"
        ai_icon = "✅" if ping.get('gen_ai_limit_reached', False) else "❌"

        await update.message.reply_text(
            "╔═══════════════════════╗\n"
            "║  📊 *YOUR PROFILE* 📊  ║\n"
            "╚═══════════════════════╝\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "👤 *Personal Info*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"📛 Name: *{ping.get('name', '?')}*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "📈 *Statistics*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏆 Total Score: `{ping.get('total_score', 0)}` pts\n"
            f"🎮 Total Plays: `{ping.get('total_plays', 0)}` games\n"
            f"📅 Today's Score: `{gdata.get('todays_score', 0)}` pts\n"
            f"{played_icon} Played Today: `{gdata.get('isAlreadyPlayed', False)}`\n"
            f"{ai_icon} AI Image Used: `{ping.get('gen_ai_limit_reached', False)}`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 Use /play to earn more points!",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Error Occurred*\n\n"
            f"Error: `{e}`\n\n"
            f"Please try /play again",
            parse_mode="Markdown"
        )


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check channel membership first
    is_member = await check_channel_membership(update, context)
    if not is_member:
        await update.message.reply_text(
            "╔═══════════════════════╗\n"
            "║  🚫 *ACCESS DENIED* 🚫  ║\n"
            "╚═══════════════════════╝\n\n"
            "⚠️ *Channel Subscription Required*\n\n"
            f"📢 Join here: {CHANNEL_LINK}\n\n"
            "After joining, try again.",
            parse_mode="Markdown"
        )
        return
    
    sess = context.user_data.get("session")
    if not sess:
        await update.message.reply_text(
            "⚠️ *Not Logged In*\n\n"
            "Please use /play first to login!",
            parse_mode="Markdown"
        )
        return
    try:
        await update.message.reply_text(
            "🔄 *Fetching Leaderboard*\n\n"
            "⏳ Please wait...",
            parse_mode="Markdown"
        )
        data = api_leaderboard(sess, "match_tickets")
        entries = data if isinstance(data, list) else (
            data.get("leaderboard") or data.get("entries") or data.get("data") or []
        )
        total_winners = (
            data.get("totalWinners") or data.get("total_winners") or data.get("total") or len(entries)
        ) if not isinstance(data, list) else len(entries)

        if not entries:
            await update.message.reply_text(
                "╔═══════════════════════╗\n"
                "║  📋 *LEADERBOARD* 📋  ║\n"
                "╚═══════════════════════╝\n\n"
                "⚠️ No entries yet\n\n"
                "Be the first to play and claim the top spot!",
                parse_mode="Markdown"
            )
            return

        # Create medals for top 3
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        
        lines = [
            "╔═══════════════════════╗\n"
            "║  🏆 *TOP PLAYERS* 🏆  ║\n"
            "╚═══════════════════════╝\n\n"
            f"👥 Total Winners: *{total_winners}*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
        ]
        
        for i, entry in enumerate(entries[:10], 1):
            name  = entry.get("name") or entry.get("username") or "?"
            score = entry.get("total_score") or entry.get("score") or "?"
            state = entry.get("state") or entry.get("user_state") or "?"
            
            medal = medals.get(i, f"`{i:2}.`")
            lines.append(f"{medal} *{name}* | {state}\n    💎 {score} pts\n")

        lines.append("\n━━━━━━━━━━━━━━━━━━━━━\n")
        lines.append("💡 Keep playing to climb the ranks!")

        await update.message.reply_text("".join(lines), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Error Occurred*\n\n"
            f"Error: `{e}`\n\n"
            f"Please try again",
            parse_mode="Markdown"
        )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "╔═══════════════════════╗\n"
        "║  ❌ *CANCELLED* ❌  ║\n"
        "╚═══════════════════════╝\n\n"
        "Operation cancelled successfully\n\n"
        "💡 Use /play to start playing again!",
        parse_mode="Markdown"
    )
    return ConversationHandler.END


# ── Main ─────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("play", play)],
        states={
            MOBILE:       [MessageHandler(filters.TEXT & ~filters.COMMAND, get_mobile)],
            OTP:          [MessageHandler(filters.TEXT & ~filters.COMMAND, get_otp)],
            SIGNUP_NAME:  [MessageHandler(filters.TEXT & ~filters.COMMAND, get_signup_name)],
            SIGNUP_AGE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, get_signup_age)],
            SIGNUP_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_signup_state)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(conv)
    print("✅ Bot running... (Auto random signup for new users enabled - puri original script rakhi hai)")
    app.run_polling()


if __name__ == "__main__":
    main()
