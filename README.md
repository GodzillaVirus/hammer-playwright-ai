# 🎭 Hammer Playwright

**Professional Browser Automation API Service**

A powerful, production-ready API service that provides Playwright browser automation capabilities. Perfect for web scraping, testing, automation, and any browser-based tasks.

---

## ✨ Features

- 🎭 **Full Playwright Support** - Complete browser automation capabilities
- 🚀 **RESTful API** - Easy-to-use HTTP endpoints
- 📱 **Telegram Bot** - Control browser sessions via Telegram
- 🔒 **Session Management** - Multiple concurrent browser sessions
- 📸 **Screenshots** - Capture full-page or viewport screenshots
- ⚙️ **JavaScript Execution** - Run custom scripts in browser context
- 🌐 **Stealth Mode** - Bypass basic bot detection
- 💚 **Health Monitoring** - Built-in health check endpoints
- 🎨 **Beautiful UI** - Interactive API documentation page

---

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
docker build -t hammer-playwright .
docker run -p 8000:8000 hammer-playwright
```

### Manual Installation

```bash
pip install -r requirements.txt
playwright install chromium
python main.py
```

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 🏠 GET `/`
Interactive API documentation page with examples

#### 💚 GET `/api/health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "emoji": "💚",
  "browser_running": true,
  "active_sessions": 0,
  "timestamp": "2025-11-08T05:00:00",
  "message": "✅ Service is running smoothly"
}
```

#### 🎭 POST `/api/playwright`
Main automation endpoint

---

## 🎬 Actions

### 1️⃣ Create Session

**Request:**
```json
{
  "action": "create"
}
```

**Response:**
```json
{
  "success": true,
  "action": "create",
  "session_id": "abc123-def456-...",
  "message": "✅ Session created successfully"
}
```

---

### 2️⃣ Navigate to URL

**Request:**
```json
{
  "action": "navigate",
  "session_id": "abc123-def456-...",
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "success": true,
  "action": "navigate",
  "url": "https://example.com",
  "title": "Example Domain",
  "message": "✅ Navigation successful"
}
```

---

### 3️⃣ Click Element

**Request:**
```json
{
  "action": "click",
  "session_id": "abc123-def456-...",
  "selector": "button#submit",
  "wait_time": 1000
}
```

**Response:**
```json
{
  "success": true,
  "action": "click",
  "selector": "button#submit",
  "message": "✅ Click successful"
}
```

---

### 4️⃣ Type Text

**Request:**
```json
{
  "action": "type",
  "session_id": "abc123-def456-...",
  "selector": "input#username",
  "text": "myusername"
}
```

**Response:**
```json
{
  "success": true,
  "action": "type",
  "selector": "input#username",
  "message": "✅ Text input successful"
}
```

---

### 5️⃣ Take Screenshot

**Request:**
```json
{
  "action": "screenshot",
  "session_id": "abc123-def456-...",
  "full_page": true
}
```

**Response:**
```json
{
  "success": true,
  "action": "screenshot",
  "screenshot": "iVBORw0KGgoAAAANS... (base64)",
  "message": "📸 Screenshot captured"
}
```

---

### 6️⃣ Execute JavaScript

**Request:**
```json
{
  "action": "execute",
  "session_id": "abc123-def456-...",
  "script": "document.title"
}
```

**Response:**
```json
{
  "success": true,
  "action": "execute",
  "result": "Example Domain",
  "message": "⚙️ Script executed successfully"
}
```

---

### 7️⃣ Get Page Content

**Request:**
```json
{
  "action": "get_content",
  "session_id": "abc123-def456-..."
}
```

**Response:**
```json
{
  "success": true,
  "action": "get_content",
  "content": "<!DOCTYPE html>...",
  "url": "https://example.com",
  "title": "Example Domain",
  "message": "📄 Content retrieved successfully"
}
```

---

### 8️⃣ Close Session

**Request:**
```json
{
  "action": "close",
  "session_id": "abc123-def456-..."
}
```

**Response:**
```json
{
  "success": true,
  "action": "close",
  "session_id": "abc123-def456-...",
  "message": "✅ Session closed successfully"
}
```

---

## 🐍 Python Example

```python
import requests
import base64

API_URL = "http://localhost:8000"

session_response = requests.post(f"{API_URL}/api/playwright", json={
    "action": "create"
})
session_id = session_response.json()["session_id"]

navigate_response = requests.post(f"{API_URL}/api/playwright", json={
    "action": "navigate",
    "session_id": session_id,
    "url": "https://example.com"
})
print(navigate_response.json())

screenshot_response = requests.post(f"{API_URL}/api/playwright", json={
    "action": "screenshot",
    "session_id": session_id,
    "full_page": True
})
screenshot_data = screenshot_response.json()["screenshot"]
with open("screenshot.png", "wb") as f:
    f.write(base64.b64decode(screenshot_data))

close_response = requests.post(f"{API_URL}/api/playwright", json={
    "action": "close",
    "session_id": session_id
})
print(close_response.json())
```

---

## 📱 Telegram Bot

The project includes a Telegram bot for easy browser control.

### Setup

1. Update `BOT_TOKEN` in `telegram_bot.py`
2. Update `ADMIN_CHAT_ID` with your Telegram chat ID
3. Run: `python telegram_bot.py`

### Commands

- `/start` - Show main menu
- 🆕 Create Session - Start a new browser session
- 🌐 Open Website - Navigate to a URL
- 📸 Take Screenshot - Capture current page
- ⚙️ Execute JS - Run JavaScript code
- 📄 Get Content - Retrieve page HTML
- ❌ Close Session - End browser session
- 💚 Health Check - Check API status

---

## 🔧 Configuration

### Environment Variables

- `PORT` - API port (default: 8000)
- No API keys required for Playwright

### Browser Configuration

The browser runs in headless mode with the following features:
- No sandbox mode for Docker compatibility
- Stealth scripts to avoid detection
- Full viewport control (1920x1080)
- Network idle wait for complete page loads

---

## 🌐 Browser Path Information

The Playwright browser is managed internally by the API. All browser operations are handled through the API endpoints. The browser executable is installed via Playwright and managed by the service.

**For external integration:**
- Use the API endpoints provided
- No direct browser path access needed
- All automation is done via HTTP requests

---

## 🚀 Deployment

### Railway

1. Connect your GitHub repository
2. Railway will auto-detect the Dockerfile
3. Deploy automatically

### Docker

```bash
docker build -t hammer-playwright .
docker run -d -p 8000:8000 --name playwright-api hammer-playwright
```

### Heroku

```bash
heroku create your-app-name
heroku stack:set container
git push heroku main
```

---

## 📊 Tech Stack

- **FastAPI** - Modern Python web framework
- **Playwright** - Browser automation library
- **Python-Telegram-Bot** - Telegram bot framework
- **Uvicorn** - ASGI server
- **Docker** - Containerization

---

## 🎯 Use Cases

- 🕷️ Web scraping
- 🧪 Automated testing
- 📊 Data extraction
- 🤖 Bot automation
- 📸 Screenshot services
- 🔍 SEO monitoring
- 📱 Social media automation
- 🛒 E-commerce automation

---

## 📝 License

MIT License - Feel free to use in your projects!

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## 📞 Support

For issues and questions, please open a GitHub issue.

---

**Made with ❤️ by Hammer Team**

🎭 **Hammer Playwright** - Professional Browser Automation Made Easy
