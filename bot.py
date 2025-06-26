import os
import logging
import hashlib
import random
from PIL import Image, ImageDraw
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment Token
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Constants
PASSKEY_BASIC = "AqWSedrFtgYHUjIkOlP"
PASSKEY_KING = "ZawEDxcftGvYUJnHy"
SELECT_PLAN, ENTER_PASSKEY, ENTER_CLIENT_SEED = range(3)

# In-memory user state
user_states = {}

# --- Image Generation ---
def generate_prediction_image(safe_tiles):
    tile_size = 64
    grid_size = 5
    img = Image.new("RGB", (tile_size * grid_size, tile_size * grid_size), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)

    for i in range(25):
        row, col = divmod(i, 5)
        x0, y0 = col * tile_size + 4, row * tile_size + 4
        x1, y1 = x0 + tile_size - 8, y0 + tile_size - 8

        if i in safe_tiles:
            draw.rectangle([x0, y0, x1, y1], fill=(0, 255, 0))  # Green diamond tile
        else:
            draw.rectangle([x0, y0, x1, y1], fill=(60, 60, 60))  # Empty tile

    return img

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("💎 Mines Basic", callback_data="basic")],
        [InlineKeyboardButton("👑 Mines King", callback_data="king")]
    ]
text = f"Hello {user_first_name} 👋\n\nPlease choose a plan:\n\n" \
           "💎 *Mines Basic* — Lifetime access, 20 sureshot signals per day\n" \
           "👑 *Mines King* — Lifetime access, 45 sureshot signals per day\n\n" \
           f"✨ *{user_first_name}*, we recommend choosing the *Mines King* plan for best results!"

  await update.message.reply_text(
    text,  # <<< 4 spaces se indent karo (standard Python style)
)
)
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def plan_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    plan = query.data
    user_states[user_id] = {"plan": plan}

    await query.message.reply_text(
        "🔐 Please enter your passkey.\n\n"
        "ℹ️ *If you don't have a passkey, contact the Admin: @Stake_Mines_God*",
        parse_mode="Markdown"
    )
    return ENTER_PASSKEY

async def handle_passkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    passkey = update.message.text.strip()

    plan = user_states[user_id]["plan"]
    valid = (plan == "basic" and passkey == PASSKEY_BASIC) or (plan == "king" and passkey == PASSKEY_KING)

    if not valid:
        await update.message.reply_text("❌ Invalid passkey. Please try again.")
        return ENTER_PASSKEY

    await update.message.reply_text(
        "✅ Passkey verified!\nAapka account verify ho gaya hai\n\n"
        "Please enter your client seed.\n\n"
        "\u26A0\uFE0F Disclaimer: Use this only with 3 mines.",
        parse_mode="Markdown"
    )
    return ENTER_CLIENT_SEED

async def handle_client_seed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    client_seed = update.message.text.strip()
    safe_tiles = get_safe_tiles(client_seed)
    image = generate_prediction_image(safe_tiles)

    bio = os.path.join("/tmp", f"{client_seed}.png")
    image.save(bio)

    keyboard = [[InlineKeyboardButton("🔄 Next Signal", callback_data="next_signal")]]
    await update.message.reply_photo(
        photo=open(bio, "rb"),
        caption="✅ Here is your signal.\n\nClick below for the next one.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ENTER_CLIENT_SEED
