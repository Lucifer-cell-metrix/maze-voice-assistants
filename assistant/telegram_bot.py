"""
MAZE — Telegram Bot Module
Control MAZE from your phone via Telegram.

Setup:
1. Open Telegram, search @BotFather
2. Send /newbot, follow steps to create a bot
3. Copy the bot token
4. Add it to config.py: TELEGRAM_BOT_TOKEN = "your_token"
5. Start a chat with your bot on Telegram
6. Add your Telegram user ID to config.py: TELEGRAM_ALLOWED_USERS = [your_id]
   (Send /start to the bot, it will show your user ID)
"""

import os
import sys
import threading
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def start_telegram_bot():
    """Start the Telegram bot in a background thread."""
    try:
        from config import TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_USERS
    except ImportError:
        print("   ⚠️  Telegram not configured. Add TELEGRAM_BOT_TOKEN to config.py")
        return False

    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
        print("   ⚠️  Telegram bot token not set. See config.py for instructions.")
        return False

    def _run_bot():
        """Run the bot in its own asyncio event loop."""
        try:
            from telegram import Update
            from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
            from assistant.brain import get_response

            async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
                user_id = update.effective_user.id
                user_name = update.effective_user.first_name
                await update.message.reply_text(
                    f"🤖 MAZE is online!\n\n"
                    f"Hello {user_name}! Your Telegram ID is: {user_id}\n\n"
                    f"Add this ID to TELEGRAM_ALLOWED_USERS in config.py to authorize yourself.\n\n"
                    f"Commands:\n"
                    f"• Just type any message — I'll respond like voice mode\n"
                    f"• /help — Show available commands\n"
                    f"• /status — Check MAZE status"
                )

            async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                await update.message.reply_text(
                    "🤖 MAZE — Telegram Commands\n\n"
                    "📱 Just send me any text command:\n"
                    "• 'open youtube' — Opens YouTube on PC\n"
                    "• 'play kesariya' — Plays song on YouTube\n"
                    "• 'add task homework' — Adds a task\n"
                    "• 'show tasks' — Lists your tasks\n"
                    "• 'note buy groceries' — Saves a note\n"
                    "• 'volume up' — Increases PC volume\n"
                    "• 'calculate 25 x 4' — Does math\n"
                    "• 'write code for calculator' — Writes code\n"
                    "• 'who is Elon Musk' — Ask AI anything\n\n"
                    "🔧 Special commands:\n"
                    "• /status — Check if MAZE is running\n"
                    "• /help — Show this help message"
                )

            async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
                import datetime
                now = datetime.datetime.now().strftime("%I:%M %p, %A %B %d")
                await update.message.reply_text(
                    f"🤖 MAZE Status: Online ✅\n"
                    f"⏰ PC Time: {now}\n"
                    f"🔌 All systems running."
                )

            async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
                user_id = update.effective_user.id

                # Check if user is authorized
                if TELEGRAM_ALLOWED_USERS and user_id not in TELEGRAM_ALLOWED_USERS:
                    await update.message.reply_text(
                        f"⛔ Unauthorized. Your ID is {user_id}. "
                        f"Add it to TELEGRAM_ALLOWED_USERS in config.py"
                    )
                    return

                command = update.message.text.strip()
                print(f"\n📱 Telegram ({update.effective_user.first_name}): {command}")

                try:
                    response = get_response(command.lower())
                    print(f"🤖 MAZE → Telegram: {response}")
                    await update.message.reply_text(f"🤖 {response}")
                except Exception as e:
                    await update.message.reply_text(f"❌ Error: {str(e)[:100]}")

            # Build and run the bot
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("help", help_cmd))
            app.add_handler(CommandHandler("status", status))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

            print("   ✅ Telegram bot started! Send messages to your bot on Telegram.")
            app.run_polling(drop_pending_updates=True)

        except ImportError:
            print("   ⚠️  python-telegram-bot not installed. Run: pip install python-telegram-bot")
        except Exception as e:
            print(f"   ❌ Telegram bot error: {e}")

    # Run bot in background thread
    bot_thread = threading.Thread(target=_run_bot, daemon=True)
    bot_thread.start()
    return True
