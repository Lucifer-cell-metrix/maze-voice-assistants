"""
MAZE — Telegram Bot Module
Control MAZE from your phone via Telegram.
Includes /internship command to find internships on Internshala.

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
            from assistant.actions.internship import find_internships, format_internships_telegram

            async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
                user_id = update.effective_user.id
                user_name = update.effective_user.first_name
                await update.message.reply_text(
                    f"🤖 MAZE is online!\n\n"
                    f"Hello {user_name}! Your Telegram ID is: {user_id}\n\n"
                    f"Add this ID to TELEGRAM_ALLOWED_USERS in config.py to authorize yourself.\n\n"
                    f"Commands:\n"
                    f"• Just type any message — I'll respond like voice mode\n"
                    f"• /internship <keyword> — Find internships on Internshala\n"
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
                    "• 'who is Elon Musk' — Ask AI anything\n"
                    "• 'find internship python' — Search internships\n\n"
                    "🔧 Special commands:\n"
                    "• /internship <keyword> — Search Internshala\n"
                    "• /internship python remote — Remote internships\n"
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

            async def internship_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                """Handle /internship <keyword> [remote] command."""
                user_id = update.effective_user.id

                # Check authorization
                if TELEGRAM_ALLOWED_USERS and user_id not in TELEGRAM_ALLOWED_USERS:
                    await update.message.reply_text(
                        f"⛔ Unauthorized. Your ID is {user_id}. "
                        f"Add it to TELEGRAM_ALLOWED_USERS in config.py"
                    )
                    return

                # Extract keyword from args
                args = context.args if context.args else []
                if not args:
                    await update.message.reply_text(
                        "🔍 Usage: /internship <keyword> [remote]\n\n"
                        "Examples:\n"
                        "• /internship python\n"
                        "• /internship cybersecurity remote\n"
                        "• /internship web development\n"
                        "• /internship data science remote"
                    )
                    return

                # Check for "remote" flag
                remote = False
                keyword_parts = []
                for arg in args:
                    if arg.lower() == "remote":
                        remote = True
                    else:
                        keyword_parts.append(arg)

                keyword = " ".join(keyword_parts) if keyword_parts else "python"

                await update.message.reply_text(
                    f"🔍 Searching internships for: {keyword}"
                    f"{' (remote)' if remote else ''}...\n"
                    f"Please wait..."
                )

                # Run scraping (might take a few seconds)
                try:
                    results = find_internships(keyword, remote=remote)
                    formatted = format_internships_telegram(results)
                    await update.message.reply_text(
                        formatted,
                        parse_mode="Markdown",
                        disable_web_page_preview=True
                    )
                except Exception as e:
                    await update.message.reply_text(f"❌ Error searching internships: {str(e)[:200]}")

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

            # Error handler — suppress Conflict errors from duplicate bot instances
            async def error_handler(update, context: ContextTypes.DEFAULT_TYPE):
                import telegram.error
                if isinstance(context.error, telegram.error.Conflict):
                    # Another instance was running — this is expected, silently ignore
                    pass
                else:
                    print(f"   ⚠️  Telegram error: {context.error}")

            # Build and run the bot
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("help", help_cmd))
            app.add_handler(CommandHandler("status", status))
            app.add_handler(CommandHandler("internship", internship_cmd))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            app.add_error_handler(error_handler)

            # Force-disconnect any previous polling session before we start
            import httpx
            try:
                resp = httpx.get(
                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates",
                    params={"offset": -1, "timeout": 1},
                    timeout=5,
                )
            except Exception:
                pass
            import time
            time.sleep(1)  # Brief pause to let old session release

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
