from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
import asyncio
import uuid
import base64
import json
from datetime import datetime
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import os

app = FastAPI(
    title="🎭 Hammer Playwright",
    description="Professional Playwright Browser Automation API Service",
    version="4.0.0"
)

active_sessions: Dict[str, Dict[str, Any]] = {}
playwright_instance = None
browser: Optional[Browser] = None

class PlaywrightSessionRequest(BaseModel):
    action: str = Field(description="Action: create, navigate, click, type, screenshot, execute, get_content, close")
    session_id: Optional[str] = None
    url: Optional[str] = None
    selector: Optional[str] = None
    text: Optional[str] = None
    script: Optional[str] = None
    full_page: bool = Field(default=False)
    wait_time: Optional[int] = Field(default=1000, description="Wait time in milliseconds")

@app.on_event("startup")
async def startup_event():
    global playwright_instance, browser
    playwright_instance = await async_playwright().start()
    browser = await playwright_instance.chromium.launch(
        headless=True,
        args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled'
        ]
    )

@app.on_event("shutdown")
async def shutdown_event():
    global browser, playwright_instance
    for session_id in list(active_sessions.keys()):
        await close_session_internal(session_id)
    if browser:
        await browser.close()
    if playwright_instance:
        await playwright_instance.stop()

async def close_session_internal(session_id: str):
    if session_id in active_sessions:
        session = active_sessions[session_id]
        try:
            if session.get('page'):
                await session['page'].close()
            if session.get('context'):
                await session['context'].close()
        except:
            pass
        del active_sessions[session_id]

def get_session(session_id: str) -> Dict[str, Any]:
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail=f"❌ Session {session_id} not found")
    return active_sessions[session_id]

async def inject_stealth_scripts(page: Page):
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        window.chrome = {
            runtime: {}
        };
    """)

@app.get("/", response_class=HTMLResponse)
async def root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎭 Hammer Playwright API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #fff;
            }
            .container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                color: #333;
            }
            h1 {
                color: #667eea;
                text-align: center;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 30px;
            }
            .info-box {
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
            }
            .endpoint {
                background: #fff;
                border: 2px solid #667eea;
                border-radius: 10px;
                padding: 20px;
                margin: 15px 0;
            }
            .endpoint h3 {
                color: #667eea;
                margin-top: 0;
            }
            .method {
                display: inline-block;
                padding: 5px 15px;
                border-radius: 5px;
                font-weight: bold;
                margin-right: 10px;
            }
            .get { background: #28a745; color: white; }
            .post { background: #007bff; color: white; }
            code {
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            .example {
                background: #2d2d2d;
                color: #f8f8f2;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                margin: 10px 0;
            }
            .stats {
                display: flex;
                justify-content: space-around;
                margin: 30px 0;
            }
            .stat-box {
                text-align: center;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px;
                flex: 1;
                margin: 0 10px;
            }
            .stat-number {
                font-size: 2em;
                font-weight: bold;
            }
            .actions-table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            .actions-table th, .actions-table td {
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }
            .actions-table th {
                background: #667eea;
                color: white;
            }
            .actions-table tr:nth-child(even) {
                background: #f8f9fa;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎭 Hammer Playwright</h1>
            <p class="subtitle">Professional Browser Automation API Service</p>
            
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-number">""" + str(len(active_sessions)) + """</div>
                    <div>📊 Active Sessions</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">v4.0.0</div>
                    <div>🚀 Version</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">✅</div>
                    <div>🎭 Browser Status</div>
                </div>
            </div>

            <div class="info-box">
                <strong>📌 About:</strong> Hammer Playwright is a professional API service that provides Playwright browser automation capabilities. Use it to automate web browsing, testing, scraping, and any browser-based tasks programmatically.
            </div>

            <h2>🔧 API Endpoints</h2>

            <div class="endpoint">
                <h3><span class="method get">GET</span> /</h3>
                <p>📄 API documentation and service information (this page)</p>
            </div>

            <div class="endpoint">
                <h3><span class="method get">GET</span> /api/health</h3>
                <p>💚 Health check endpoint - returns service status and statistics</p>
                <div class="example">
{
  "status": "healthy",
  "browser_running": true,
  "active_sessions": 0,
  "timestamp": "2025-11-08T05:00:00"
}
                </div>
            </div>

            <div class="endpoint">
                <h3><span class="method post">POST</span> /api/playwright</h3>
                <p>🎭 Main Playwright automation endpoint - supports multiple actions</p>
                
                <h4>📋 Available Actions:</h4>
                <table class="actions-table">
                    <tr>
                        <th>Action</th>
                        <th>Description</th>
                        <th>Required Fields</th>
                    </tr>
                    <tr>
                        <td><strong>create</strong></td>
                        <td>🆕 Create a new browser session</td>
                        <td>action</td>
                    </tr>
                    <tr>
                        <td><strong>navigate</strong></td>
                        <td>🌐 Navigate to a URL</td>
                        <td>action, session_id, url</td>
                    </tr>
                    <tr>
                        <td><strong>click</strong></td>
                        <td>👆 Click an element</td>
                        <td>action, session_id, selector</td>
                    </tr>
                    <tr>
                        <td><strong>type</strong></td>
                        <td>⌨️ Type text into an element</td>
                        <td>action, session_id, selector, text</td>
                    </tr>
                    <tr>
                        <td><strong>screenshot</strong></td>
                        <td>📸 Take a screenshot (base64)</td>
                        <td>action, session_id, full_page (optional)</td>
                    </tr>
                    <tr>
                        <td><strong>execute</strong></td>
                        <td>⚙️ Execute JavaScript code</td>
                        <td>action, session_id, script</td>
                    </tr>
                    <tr>
                        <td><strong>get_content</strong></td>
                        <td>📄 Get page content (HTML)</td>
                        <td>action, session_id</td>
                    </tr>
                    <tr>
                        <td><strong>close</strong></td>
                        <td>❌ Close a session</td>
                        <td>action, session_id</td>
                    </tr>
                </table>

                <h4>💡 Example - Create Session:</h4>
                <div class="example">
POST /api/playwright
{
  "action": "create"
}

Response:
{
  "success": true,
  "action": "create",
  "session_id": "abc123...",
  "message": "✅ Session created successfully"
}
                </div>

                <h4>💡 Example - Navigate:</h4>
                <div class="example">
POST /api/playwright
{
  "action": "navigate",
  "session_id": "abc123...",
  "url": "https://example.com"
}

Response:
{
  "success": true,
  "action": "navigate",
  "url": "https://example.com",
  "title": "Example Domain",
  "message": "✅ Navigation successful"
}
                </div>

                <h4>💡 Example - Screenshot:</h4>
                <div class="example">
POST /api/playwright
{
  "action": "screenshot",
  "session_id": "abc123...",
  "full_page": true
}

Response:
{
  "success": true,
  "action": "screenshot",
  "screenshot": "iVBORw0KGgoAAAANS...",
  "message": "📸 Screenshot captured"
}
                </div>
            </div>

            <div class="info-box">
                <strong>🔗 Browser Path:</strong> The Playwright browser is managed internally by the API. All browser operations are handled through the API endpoints. No direct browser path access is needed.
            </div>

            <div class="info-box">
                <strong>🚀 Integration:</strong> Use this API in your Python projects, automation scripts, or any application that needs browser automation. Simply make HTTP requests to the endpoints above.
            </div>

            <div class="info-box">
                <strong>📚 Documentation:</strong> For full Playwright documentation, visit <a href="https://playwright.dev" target="_blank">playwright.dev</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/playwright")
async def playwright_service(request: PlaywrightSessionRequest):
    try:
        if request.action == "create":
            session_id = str(uuid.uuid4())
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            await inject_stealth_scripts(page)
            
            active_sessions[session_id] = {
                'context': context,
                'page': page,
                'created_at': datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "action": "create",
                "session_id": session_id,
                "message": "✅ Session created successfully"
            }
        
        elif request.action == "navigate":
            session = get_session(request.session_id)
            page = session['page']
            await page.goto(request.url, wait_until="networkidle", timeout=30000)
            
            return {
                "success": True,
                "action": "navigate",
                "url": page.url,
                "title": await page.title(),
                "message": "✅ Navigation successful"
            }
        
        elif request.action == "click":
            session = get_session(request.session_id)
            page = session['page']
            await page.click(request.selector)
            await asyncio.sleep(request.wait_time / 1000)
            
            return {
                "success": True,
                "action": "click",
                "selector": request.selector,
                "message": "✅ Click successful"
            }
        
        elif request.action == "type":
            session = get_session(request.session_id)
            page = session['page']
            await page.fill(request.selector, request.text)
            
            return {
                "success": True,
                "action": "type",
                "selector": request.selector,
                "message": "✅ Text input successful"
            }
        
        elif request.action == "screenshot":
            session = get_session(request.session_id)
            page = session['page']
            screenshot_bytes = await page.screenshot(full_page=request.full_page)
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            return {
                "success": True,
                "action": "screenshot",
                "screenshot": screenshot_base64,
                "message": "📸 Screenshot captured"
            }
        
        elif request.action == "execute":
            session = get_session(request.session_id)
            page = session['page']
            result = await page.evaluate(request.script)
            
            return {
                "success": True,
                "action": "execute",
                "result": result,
                "message": "⚙️ Script executed successfully"
            }
        
        elif request.action == "get_content":
            session = get_session(request.session_id)
            page = session['page']
            content = await page.content()
            
            return {
                "success": True,
                "action": "get_content",
                "content": content,
                "url": page.url,
                "title": await page.title(),
                "message": "📄 Content retrieved successfully"
            }
        
        elif request.action == "close":
            await close_session_internal(request.session_id)
            
            return {
                "success": True,
                "action": "close",
                "session_id": request.session_id,
                "message": "✅ Session closed successfully"
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"❌ Unknown action: {request.action}")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Playwright error: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "emoji": "💚",
        "browser_running": browser is not None,
        "active_sessions": len(active_sessions),
        "timestamp": datetime.now().isoformat(),
        "message": "✅ Service is running smoothly"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
