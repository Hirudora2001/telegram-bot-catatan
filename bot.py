import logging
from datetime import datetime
import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Konfigurasi
SHEETDB_API_URL = "https://sheetdb.io/api/v1/75b6ljkcswneo"
BOT_TOKEN = "7959054705:AAEYuShDiXrPCByTe30j-xeksLnMYJx8dLA"

# Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Fungsi parsing input gaya natural (tanpa delimiter)
def parse_input(text):
    words = text.strip().split()

    if len(words) < 5:
        return None

    nominal = words[-1]
    bank = words[-2]
    kategori = words[-3]
    transaksi = words[0]
    uraian = ' '.join(words[1:-3])

    return {
        "transaksi": transaksi,
        "uraian": uraian,
        "kategori": kategori,
        "bank": bank,
        "nominal": nominal
    }

# Handler pesan masuk
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    now = datetime.now()

    result = parse_input(text)
    if not result:
        await update.message.reply_text("❌ Formate gak ngunu wo.\n\nContoh yang benar:\nTransfer Warteg Makan BCA 15000")
        return

    # Ambil hasil parsing
    transaksi = result['transaksi']
    uraian = result['uraian']
    kategori = result['kategori']
    bank = result['bank']
    nominal = result['nominal']

    # Siapkan data untuk SheetDB
    data = {
        "data": {
            "Tanggal": now.strftime("%Y-%m-%d"),
            "Bulan": now.strftime("%B"),
            "Transaksi": transaksi,
            "Uraian": uraian,
            "Kategori": kategori,
            "Bank": bank,
            "Nominal": nominal
        }
    }

    try:
        response = requests.post(SHEETDB_API_URL, json=data)
        if response.status_code == 201:
            await update.message.reply_text("✅ Oke wes tak catet ndan.")
        else:
            logging.error(f"Gagal mencatat data: {response.text}")
            await update.message.reply_text("❌ Gagal mencatat data. Coba cek koneksi.")
    except Exception as e:
        logging.exception("Terjadi kesalahan saat mengirim data")
        await update.message.reply_text("❌ Terjadi kesalahan saat mengirim data.")

# Fungsi utama
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    await app.bot.delete_webhook(drop_pending_updates=True)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot sedang berjalan...")
    await app.run_polling()

# Jalankan
if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
