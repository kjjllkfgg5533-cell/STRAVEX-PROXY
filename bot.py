import os
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.constants import ParseMode
from telegram.error import TelegramError

# ==========================================
# --- CONFIGURATION ---
# ==========================================
TOKEN = "9033757313:AAGWI1h6LuHpW--ne_ghW-SAUIiN1-WEieI"  # التوكن الخاص بك
UID_FILE = "uid.txt"

# القنوات المطلوبة
REQUIRED_CHANNELS = [
    {
        "name": "𝙎𝙏𝙍𝘼𝙑𝙀𝙓 𝙑𝙄𝙋",
        "username": "@stravex_oficiel",
        "url": "https://t.me/stravex_oficiel",
        "channel_id": "-1003536665917",
    },
    {
        "name": "STRAVEX BOT VIP",
        "username": "@stravex_bot_vip",
        "url": "https://t.me/stravex_bot_vip",
        "channel_id": "-1003715704374",
    },
]

# الرابط المباشر للصورة
BOT_IMAGE_DIRECT = "https://i.ibb.co/0pZNhGRJ/image.jpg"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ==========================================
# --- UTILS ---
# ==========================================
def load_uids() -> list:
    if os.path.exists(UID_FILE):
        with open(UID_FILE, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return []


def save_uids(uids: list) -> None:
    with open(UID_FILE, "w") as f:
        f.write("\n".join(uids) + "\n")


async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> tuple:
    """التحقق من اشتراك المستخدم في جميع القنوات"""
    not_subscribed = []
    
    for channel in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(
                chat_id=channel["channel_id"],
                user_id=user_id,
            )
            
            # 'member', 'administrator', 'creator' = مشترك
            # 'left', 'kicked' = غير مشترك
            if member.status in ['member', 'administrator', 'creator']:
                continue
            else:
                not_subscribed.append(channel)
                
        except TelegramError as e:
            logger.error(f"Error checking subscription for {channel['username']}: {e}")
            not_subscribed.append(channel)
    
    return len(not_subscribed) == 0, not_subscribed


def subscription_keyboard() -> InlineKeyboardMarkup:
    """لوحة أزرار الاشتراك الإجباري"""
    keyboard = []
    
    for channel in REQUIRED_CHANNELS:
        keyboard.append([
            InlineKeyboardButton(
                f"اشترك في {channel['name']}",
                url=channel["url"],
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(
            "تحقق من الاشتراك",
            callback_data="check_subscription",
        )
    ])
    
    return InlineKeyboardMarkup(keyboard)


async def send_subscription_required(update: Update, context: ContextTypes.DEFAULT_TYPE, not_subscribed: list):
    """إرسال رسالة الاشتراك الإجباري"""
    
    channels_list = ""
    for ch in not_subscribed:
        channels_list += f"  └─ <b>{ch['name']}</b>\n"
    
    text = (
        f"<b>{LINE}</b>\n"
        f"          <b>STRAVEX VIP</b>\n"
        f"<b>{LINE}</b>\n\n"
        f"<b>عذراً، يجب عليك الاشتراك في القنوات التالية:</b>\n\n"
        f"{channels_list}\n"
        f"<b>{DOTS}</b>\n\n"
        f"<b>بعد الاشتراك في جميع القنوات، اضغط:</b>\n"
        f"<i>تحقق من الاشتراك</i>\n\n"
        f"<b>{LINE}</b>\n"
        f"<i>STRAVEX VIP Protection System</i>"
    )
    
    reply_markup = subscription_keyboard()
    
    if update.message:
        await update.message.reply_photo(
            photo=BOT_IMAGE_DIRECT,
            caption=text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
        )
    elif update.callback_query:
        try:
            await update.callback_query.edit_message_media(
                media=InputMediaPhoto(
                    media=BOT_IMAGE_DIRECT,
                    caption=text,
                    parse_mode=ParseMode.HTML,
                ),
                reply_markup=reply_markup,
            )
        except Exception:
            await update.callback_query.message.reply_photo(
                photo=BOT_IMAGE_DIRECT,
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
            )


async def require_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """التحقق من الاشتراك قبل تنفيذ أي أمر"""
    user_id = update.effective_user.id
    
    is_subscribed, not_subscribed = await check_subscription(user_id, context)
    
    if not is_subscribed:
        await send_subscription_required(update, context, not_subscribed)
        return False
    
    return True


# ==========================================
# --- DESIGN CONSTANTS ---
# ==========================================
LINE = "━━━━━━━━━━━━━━━━━━━━━"
DOTS = "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈"


# ==========================================
# --- COMMANDS ---
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """رسالة الترحيب"""
    
    if not await require_subscription(update, context):
        return
    
    welcome_text = (
        f"<b>{LINE}</b>\n"
        f"          <b>STRAVEX VIP</b>\n"
        f"<b>{LINE}</b>\n\n"
        f"<b>أهلاً بك في النظام الملكي</b>\n\n"
        f"<b>بوابة الحماية الفاخرة</b>\n"
        f"<i>الخاصة بإدارة UIDs المحمية</i>\n\n"
        f"<b>{DOTS}</b>\n\n"
        f"<b>الأوامر المتاحة:</b>\n\n"
        f"  <b>/adduid</b> <code>&lt;UID&gt;</code>\n"
        f"  └─ <i>إضافة UID جديد للنظام</i>\n\n"
        f"  <b>/listuids</b>\n"
        f"  └─ <i>عرض جميع UIDs المسجلة</i>\n\n"
        f"  <b>/count</b>\n"
        f"  └─ <i>إحصائيات النظام</i>\n\n"
        f"  <b>/removeuid</b> <code>&lt;UID&gt;</code>\n"
        f"  └─ <i>حذف UID من النظام</i>\n\n"
        f"<b>{LINE}</b>\n"
        f"<i>STRAVEX VIP Protection System</i>"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("إضافة UID", callback_data="btn_add"),
            InlineKeyboardButton("القائمة", callback_data="btn_list"),
        ],
        [
            InlineKeyboardButton("الإحصائيات", callback_data="btn_count"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_photo(
        photo=BOT_IMAGE_DIRECT,
        caption=welcome_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
    )


async def adduid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """إضافة UID"""
    
    if not await require_subscription(update, context):
        return
    
    if not context.args:
        error_text = (
            f"<b>{LINE}</b>\n"
            f"          <b>خ ط أ</b>\n"
            f"<b>{LINE}</b>\n\n"
            f"<b>لم يتم إدخال UID</b>\n\n"
            f"<b>الطريقة الصحيحة:</b>\n"
            f"<code>/adduid 1234567890</code>\n\n"
            f"<b>{DOTS}</b>\n"
            f"<i>يجب أن يكون UID أرقاماً فقط</i>"
        )
        await update.message.reply_photo(
            photo=BOT_IMAGE_DIRECT,
            caption=error_text,
            parse_mode=ParseMode.HTML,
        )
        return
    
    uid = context.args[0].strip()
    
    if not uid.isdigit():
        error_text = (
            f"<b>{LINE}</b>\n"
            f"          <b>خ ط أ</b>\n"
            f"<b>{LINE}</b>\n\n"
            f"<b>UID يجب أن يحتوي على أرقام فقط</b>\n\n"
            f"<b>المدخل:</b> <code>{uid}</code>\n"
            f"<b>{DOTS}</b>"
        )
        await update.message.reply_photo(
            photo=BOT_IMAGE_DIRECT,
            caption=error_text,
            parse_mode=ParseMode.HTML,
        )
        return
    
    if len(uid) < 5 or len(uid) > 20:
        error_text = (
            f"<b>{LINE}</b>\n"
            f"          <b>خ ط أ</b>\n"
            f"<b>{LINE}</b>\n\n"
            f"<b>طول UID غير صالح</b>\n\n"
            f"<b>الطول الحالي:</b> <code>{len(uid)}</code>\n"
            f"<b>الطول المطلوب:</b> <code>5 - 20</code>\n"
            f"<b>{DOTS}</b>"
        )
        await update.message.reply_photo(
            photo=BOT_IMAGE_DIRECT,
            caption=error_text,
            parse_mode=ParseMode.HTML,
        )
        return
    
    current_uids = load_uids()
    
    if uid in current_uids:
        error_text = (
            f"<b>{LINE}</b>\n"
            f"          <b>م س ج ل</b>\n"
            f"<b>{LINE}</b>\n\n"
            f"<b>هذا UID مسجل بالفعل!</b>\n\n"
            f"<b>UID:</b> <code>{uid}</code>\n"
            f"<b>{DOTS}</b>\n"
            f"<i>لا يمكن إضافة نفس UID مرتين</i>"
        )
        await update.message.reply_photo(
            photo=BOT_IMAGE_DIRECT,
            caption=error_text,
            parse_mode=ParseMode.HTML,
        )
        return
    
    current_uids.append(uid)
    
    try:
        save_uids(current_uids)
        
        user_info = update.effective_user
        username = user_info.username or user_info.first_name or "Unknown"
        logger.info(f"[STRAVEX] User {username} ({user_info.id}) added UID: {uid}")
        
        success_text = (
            f"<b>{LINE}</b>\n"
            f"          <b>ن ج ا ح</b>\n"
            f"<b>{LINE}</b>\n\n"
            f"<b>تمت الإضافة بنجاح!</b>\n\n"
            f"<b>UID:</b> <code>{uid}</code>\n"
            f"<b>الحالة:</b> <i>محفوظ في النظام</i>\n"
            f"<b>إجمالي UIDs:</b> <code>{len(current_uids)}</code>\n\n"
            f"<b>{DOTS}</b>\n"
            f"<i>يمكنك الآن استخدام Proxy</i>"
        )
        await update.message.reply_photo(
            photo=BOT_IMAGE_DIRECT,
            caption=success_text,
            parse_mode=ParseMode.HTML,
        )
        
    except Exception as e:
        logger.error(f"Error saving UID: {e}")
        error_text = (
            f"<b>{LINE}</b>\n"
            f"          <b>خ ط أ  ن ظ ا م</b>\n"
            f"<b>{LINE}</b>\n\n"
            f"<b>فشل حفظ UID</b>\n\n"
            f"<b>السبب:</b>\n"
            f"<code>{e}</code>\n"
            f"<b>{DOTS}</b>"
        )
        await update.message.reply_photo(
            photo=BOT_IMAGE_DIRECT,
            caption=error_text,
            parse_mode=ParseMode.HTML,
        )


async def listuids(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض القائمة"""
    
    if not await require_subscription(update, context):
        return
    
    uids = load_uids()
    
    if not uids:
        empty_text = (
            f"<b>{LINE}</b>\n"
            f"          <b>ا ل ق ا ئ م ة</b>\n"
            f"<b>{LINE}</b>\n\n"
            f"<b>لا توجد UIDs مسجلة حالياً</b>\n\n"
            f"<b>{DOTS}</b>\n"
            f"<i>استخدم /adduid لإضافة UID جديد</i>"
        )
        await update.message.reply_photo(
            photo=BOT_IMAGE_DIRECT,
            caption=empty_text,
            parse_mode=ParseMode.HTML,
        )
        return
    
    header = (
        f"<b>{LINE}</b>\n"
        f"          <b>ق ا ئ م ة  ا ل ن ظ ا م</b>\n"
        f"<b>{LINE}</b>\n\n"
        f"<b>إجمالي UIDs:</b> <code>{len(uids)}</code>\n"
        f"<b>{DOTS}</b>\n\n"
    )
    
    entries = ""
    for i, uid in enumerate(uids, 1):
        entries += f"<b>{i:02d}.</b> <code>{uid}</code>\n"
    
    footer = f"\n<b>{LINE}</b>\n<i>STRAVEX VIP Protection System</i>"
    
    full_text = header + entries + footer
    
    if len(full_text) > 4000:
        brief = (
            f"<b>{LINE}</b>\n"
            f"          <b>ق ا ئ م ة  ا ل ن ظ ا م</b>\n"
            f"<b>{LINE}</b>\n\n"
            f"<b>إجمالي UIDs:</b> <code>{len(uids)}</code>\n\n"
            f"<b>القائمة طويلة جداً للعرض</b>\n"
            f"<i>تم إرسالها كملف مرفق</i>"
        )
        await update.message.reply_photo(
            photo=BOT_IMAGE_DIRECT,
            caption=brief,
            parse_mode=ParseMode.HTML,
        )
        
        with open(UID_FILE, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename="uid.txt",
                caption=f"قائمة UIDs ({len(uids)})",
            )
    else:
        await update.message.reply_photo(
            photo=BOT_IMAGE_DIRECT,
            caption=full_text,
            parse_mode=ParseMode.HTML,
        )


async def removeuid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """حذف UID"""
    
    if not await require_subscription(update, context):
        return
    
    if not context.args:
        error_text = (
            f"<b>{LINE}</b>\n"
            f"          <b>ط ر ي ق ة</b>\n"
            f"<b>{LINE}</b>\n\n"
            f"<b>الاستخدام الصحيح:</b>\n"
            f"<code>/removeuid 1234567890</code>\n\n"
            f"<b>{DOTS}</b>"
        )
        await update.message.reply_photo(
            photo=BOT_IMAGE_DIRECT,
            caption=error_text,
            parse_mode=ParseMode.HTML,
        )
        return
    
    uid = context.args[0].strip()
    current_uids = load_uids()
    
    if uid not in current_uids:
        error_text = (
            f"<b>{LINE}</b>\n"
            f"          <b>غ ي ر  م و ج و د</b>\n"
            f"<b>{LINE}</b>\n\n"
            f"<b>هذا UID غير موجود</b>\n\n"
            f"<b>UID:</b> <code>{uid}</code>\n"
            f"<b>{DOTS}</b>"
        )
        await update.message.reply_photo(
            photo=BOT_IMAGE_DIRECT,
            caption=error_text,
            parse_mode=ParseMode.HTML,
        )
        return
    
    current_uids.remove(uid)
    save_uids(current_uids)
    
    success_text = (
        f"<b>{LINE}</b>\n"
        f"          <b>ح ذ ف</b>\n"
        f"<b>{LINE}</b>\n\n"
        f"<b>تم الحذف بنجاح!</b>\n\n"
        f"<b>UID:</b> <code>{uid}</code>\n"
        f"<b>المتبقي:</b> <code>{len(current_uids)}</code>\n"
        f"<b>{DOTS}</b>"
    )
    await update.message.reply_photo(
        photo=BOT_IMAGE_DIRECT,
        caption=success_text,
        parse_mode=ParseMode.HTML,
    )


async def countuids(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """إحصائيات"""
    
    if not await require_subscription(update, context):
        return
    
    uids = load_uids()
    
    stats_text = (
        f"<b>{LINE}</b>\n"
        f"          <b>إ ح ص ا ئ ي ا ت</b>\n"
        f"<b>{LINE}</b>\n\n"
        f"<b>إجمالي UIDs المسجلة:</b>\n"
        f"     <code>{len(uids)}</code>\n\n"
        f"<b>حالة النظام:</b> <i>يعمل</i>\n"
        f"<b>الحماية:</b> <i>مفعلة</i>\n\n"
        f"<b>{DOTS}</b>\n"
        f"<i>STRAVEX VIP Protection System</i>"
    )
    await update.message.reply_photo(
        photo=BOT_IMAGE_DIRECT,
        caption=stats_text,
        parse_mode=ParseMode.HTML,
    )


# ==========================================
# --- BUTTON HANDLERS ---
# ==========================================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج الأزرار"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "check_subscription":
        user_id = update.effective_user.id
        is_subscribed, not_subscribed = await check_subscription(user_id, context)
        
        if is_subscribed:
            welcome_text = (
                f"<b>{LINE}</b>\n"
                f"          <b>STRAVEX VIP</b>\n"
                f"<b>{LINE}</b>\n\n"
                f"<b>تم التحقق بنجاح!</b>\n\n"
                f"<b>أهلاً بك في النظام الملكي</b>\n\n"
                f"<b>{DOTS}</b>\n\n"
                f"<b>الأوامر المتاحة:</b>\n\n"
                f"  <b>/adduid</b> <code>&lt;UID&gt;</code>\n"
                f"  └─ <i>إضافة UID جديد</i>\n\n"
                f"  <b>/listuids</b>\n"
                f"  └─ <i>عرض القائمة</i>\n\n"
                f"  <b>/count</b>\n"
                f"  └─ <i>الإحصائيات</i>\n\n"
                f"  <b>/removeuid</b> <code>&lt;UID&gt;</code>\n"
                f"  └─ <i>حذف UID</i>\n\n"
                f"<b>{LINE}</b>\n"
                f"<i>STRAVEX VIP Protection System</i>"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("إضافة UID", callback_data="btn_add"),
                    InlineKeyboardButton("القائمة", callback_data="btn_list"),
                ],
                [
                    InlineKeyboardButton("الإحصائيات", callback_data="btn_count"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await query.edit_message_caption(
                    caption=welcome_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                )
            except Exception:
                await query.message.reply_photo(
                    photo=BOT_IMAGE_DIRECT,
                    caption=welcome_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                )
        else:
            channels_list = ""
            for ch in not_subscribed:
                channels_list += f"  └─ <b>{ch['name']}</b>\n"
            
            error_text = (
                f"<b>{LINE}</b>\n"
                f"          <b>غ ي ر  م ش ت ر ك</b>\n"
                f"<b>{LINE}</b>\n\n"
                f"<b>لم تشترك في القنوات التالية بعد:</b>\n\n"
                f"{channels_list}\n"
                f"<b>{DOTS}</b>\n\n"
                f"<i>اشترك أولاً ثم اضغط تحقق</i>"
            )
            
            reply_markup = subscription_keyboard()
            
            try:
                await query.edit_message_caption(
                    caption=error_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                )
            except Exception:
                await query.message.reply_photo(
                    photo=BOT_IMAGE_DIRECT,
                    caption=error_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                )
        return
    
    if not await require_subscription(update, context):
        return
    
    if query.data == "btn_add":
        text = (
            f"<b>{LINE}</b>\n"
            f"          <b>إ ض ا ف ة  U I D</b>\n"
            f"<b>{LINE}</b>\n\n"
            f"<b>أرسل الأمر التالي:</b>\n\n"
            f"<code>/adduid 1234567890</code>\n\n"
            f"<b>{DOTS}</b>\n"
            f"<i>استبدل الأرقام بـ UID الحقيقي</i>"
        )
        try:
            await query.edit_message_caption(
                caption=text,
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass
    
    elif query.data == "btn_list":
        text = (
            f"<b>{LINE}</b>\n"
            f"          <b>ع ر ض  ا ل ق ا ئ م ة</b>\n"
            f"<b>{LINE}</b>\n\n"
            f"<b>أرسل الأمر التالي:</b>\n\n"
            f"<code>/listuids</code>\n\n"
            f"<b>{DOTS}</b>"
        )
        try:
            await query.edit_message_caption(
                caption=text,
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass
    
    elif query.data == "btn_count":
        uids = load_uids()
        text = (
            f"<b>{LINE}</b>\n"
            f"          <b>إ ح ص ا ئ ي ا ت</b>\n"
            f"<b>{LINE}</b>\n\n"
            f"<b>إجمالي UIDs:</b> <code>{len(uids)}</code>\n\n"
            f"<b>الحالة:</b> <i>يعمل</i>\n"
            f"<b>{DOTS}</b>"
        )
        try:
            await query.edit_message_caption(
                caption=text,
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass


# ==========================================
# --- MAIN ---
# ==========================================
def main() -> None:
    print("STRAVEX VIP Bot is starting...")
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("adduid", adduid))
    app.add_handler(CommandHandler("listuids", listuids))
    app.add_handler(CommandHandler("removeuid", removeuid))
    app.add_handler(CommandHandler("count", countuids))
    
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("STRAVEX VIP Bot is running! Press CTRL+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()