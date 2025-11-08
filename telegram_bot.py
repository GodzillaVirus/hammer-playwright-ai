import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import json
import base64

BOT_TOKEN = "8387132475:AAEZjVnDdESzbWe2Xn0fo2_yoAZb8slRoPs"
ADMIN_CHAT_ID = 5328767896
API_URL = "http://localhost:8000"

active_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ Unauthorized access")
        return

    keyboard = [
        [InlineKeyboardButton("🆕 Create Session", callback_data="pw_create")],
        [InlineKeyboardButton("📋 View Sessions", callback_data="pw_list")],
        [InlineKeyboardButton("💚 Health Check", callback_data="health_check")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎭 *Hammer Playwright Bot*\n\n"
        "Professional Browser Automation Service\n\n"
        "Choose an option:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "back_main":
        keyboard = [
            [InlineKeyboardButton("🆕 Create Session", callback_data="pw_create")],
            [InlineKeyboardButton("📋 View Sessions", callback_data="pw_list")],
            [InlineKeyboardButton("💚 Health Check", callback_data="health_check")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "🎭 *Hammer Playwright Bot*\n\n"
            "Professional Browser Automation Service\n\n"
            "Choose an option:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    elif query.data == "pw_create":
        response = requests.post(f"{API_URL}/api/playwright", json={
            "action": "create"
        })
        data = response.json()

        if data.get('success'):
            session_id = data['session_id']
            active_sessions[query.from_user.id] = session_id

            keyboard = [
                [InlineKeyboardButton("🌐 Open Website", callback_data="pw_navigate")],
                [InlineKeyboardButton("📸 Take Screenshot", callback_data="pw_screenshot")],
                [InlineKeyboardButton("⚙️ Execute JS", callback_data="pw_execute")],
                [InlineKeyboardButton("📄 Get Content", callback_data="pw_content")],
                [InlineKeyboardButton("❌ Close Session", callback_data="pw_close")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"✅ Playwright session created!\n\n"
                f"🆔 Session ID: `{session_id[:8]}...`\n\n"
                f"Choose an action:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(f"❌ Failed to create session")

    elif query.data == "pw_list":
        if active_sessions:
            sessions_text = "📋 *Active Sessions:*\n\n"
            for user_id, session_id in active_sessions.items():
                sessions_text += f"👤 User: {user_id}\n🆔 Session: `{session_id[:8]}...`\n\n"
        else:
            sessions_text = "📋 No active sessions"

        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            sessions_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    elif query.data == "pw_navigate":
        await query.edit_message_text("🌐 Send the URL you want to visit:")
        context.user_data['waiting_for'] = 'pw_url'

    elif query.data == "pw_screenshot":
        session_id = active_sessions.get(query.from_user.id)
        if not session_id:
            await query.edit_message_text("❌ No active session!")
            return

        await query.edit_message_text("📸 Capturing screenshot...")

        response = requests.post(f"{API_URL}/api/playwright", json={
            "action": "screenshot",
            "session_id": session_id,
            "full_page": True
        })
        data = response.json()

        if data.get('success'):
            screenshot_data = base64.b64decode(data['screenshot'])
            
            keyboard = [
                [InlineKeyboardButton("🌐 Open Website", callback_data="pw_navigate")],
                [InlineKeyboardButton("📸 Take Screenshot", callback_data="pw_screenshot")],
                [InlineKeyboardButton("⚙️ Execute JS", callback_data="pw_execute")],
                [InlineKeyboardButton("📄 Get Content", callback_data="pw_content")],
                [InlineKeyboardButton("❌ Close Session", callback_data="pw_close")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_photo(
                chat_id=query.from_user.id,
                photo=screenshot_data,
                caption="📸 Screenshot captured successfully",
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(f"❌ Failed to capture screenshot")

    elif query.data == "pw_execute":
        await query.edit_message_text("⚙️ Send JavaScript code to execute:")
        context.user_data['waiting_for'] = 'pw_js'

    elif query.data == "pw_content":
        session_id = active_sessions.get(query.from_user.id)
        if not session_id:
            await query.edit_message_text("❌ No active session!")
            return

        await query.edit_message_text("📄 Retrieving page content...")

        response = requests.post(f"{API_URL}/api/playwright", json={
            "action": "get_content",
            "session_id": session_id
        })
        data = response.json()

        if data.get('success'):
            content_preview = data['content'][:500] if len(data['content']) > 500 else data['content']
            
            keyboard = [
                [InlineKeyboardButton("🌐 Open Website", callback_data="pw_navigate")],
                [InlineKeyboardButton("📸 Take Screenshot", callback_data="pw_screenshot")],
                [InlineKeyboardButton("⚙️ Execute JS", callback_data="pw_execute")],
                [InlineKeyboardButton("📄 Get Content", callback_data="pw_content")],
                [InlineKeyboardButton("❌ Close Session", callback_data="pw_close")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"✅ Content retrieved successfully!\n\n"
                f"🌐 URL: {data['url']}\n"
                f"📄 Title: {data['title']}\n\n"
                f"📝 Content Preview:\n`{content_preview}...`",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(f"❌ Failed to retrieve content")

    elif query.data == "pw_close":
        session_id = active_sessions.get(query.from_user.id)
        if not session_id:
            await query.edit_message_text("❌ No active session!")
            return

        response = requests.post(f"{API_URL}/api/playwright", json={
            "action": "close",
            "session_id": session_id
        })
        data = response.json()

        if data.get('success'):
            del active_sessions[query.from_user.id]
            
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "✅ Session closed successfully!",
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(f"❌ Failed to close session")

    elif query.data == "health_check":
        response = requests.get(f"{API_URL}/api/health")
        data = response.json()

        status_emoji = "✅" if data['status'] == 'healthy' else "❌"

        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"{status_emoji} *API Health Status*\n\n"
            f"📊 Status: {data['status']}\n"
            f"🎭 Browser: {'✅ Running' if data['browser_running'] else '❌ Stopped'}\n"
            f"📈 Active Sessions: {data['active_sessions']}\n"
            f"⏰ Timestamp: {data['timestamp']}\n\n"
            f"{data['message']}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_CHAT_ID:
        return

    waiting_for = context.user_data.get('waiting_for')
    
    if not waiting_for:
        return

    if waiting_for == 'pw_url':
        url = update.message.text
        session_id = active_sessions.get(update.effective_user.id)

        if not session_id:
            await update.message.reply_text("❌ No active session!")
            return

        await update.message.reply_text(f"🌐 Opening {url}...")

        response = requests.post(f"{API_URL}/api/playwright", json={
            "action": "navigate",
            "session_id": session_id,
            "url": url
        })
        data = response.json()

        if data.get('success'):
            keyboard = [
                [InlineKeyboardButton("🌐 Open Website", callback_data="pw_navigate")],
                [InlineKeyboardButton("📸 Take Screenshot", callback_data="pw_screenshot")],
                [InlineKeyboardButton("⚙️ Execute JS", callback_data="pw_execute")],
                [InlineKeyboardButton("📄 Get Content", callback_data="pw_content")],
                [InlineKeyboardButton("❌ Close Session", callback_data="pw_close")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"✅ Website opened successfully!\n\n"
                f"🌐 URL: {data['url']}\n"
                f"📄 Title: {data['title']}",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(f"❌ Failed to open website")

        context.user_data['waiting_for'] = None

    elif waiting_for == 'pw_js':
        js_code = update.message.text
        session_id = active_sessions.get(update.effective_user.id)

        if not session_id:
            await update.message.reply_text("❌ No active session!")
            return

        await update.message.reply_text("⚙️ Executing code...")

        response = requests.post(f"{API_URL}/api/playwright", json={
            "action": "execute",
            "session_id": session_id,
            "script": js_code
        })
        data = response.json()

        if data.get('success'):
            result = data.get('result', 'No result')
            
            keyboard = [
                [InlineKeyboardButton("🌐 Open Website", callback_data="pw_navigate")],
                [InlineKeyboardButton("📸 Take Screenshot", callback_data="pw_screenshot")],
                [InlineKeyboardButton("⚙️ Execute JS", callback_data="pw_execute")],
                [InlineKeyboardButton("📄 Get Content", callback_data="pw_content")],
                [InlineKeyboardButton("❌ Close Session", callback_data="pw_close")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"✅ Code executed successfully!\n\n"
                f"📊 Result:\n`{result}`",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(f"❌ Execution failed")

        context.user_data['waiting_for'] = None

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Hammer Playwright Bot Started!")
    print("🎭 Professional Browser Automation Service")
    application.run_polling()

if __name__ == "__main__":
    main()
