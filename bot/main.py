from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from bot_parser import parse_expense, format_reply, handle_command
from database import insert_expense, get_summary_today, get_summary_month

app = FastAPI()

HELP_TEXT = """👋 Enzo 記帳 Bot 使用說明

📝 記帳格式
直接輸入：消費描述 + 金額
例如：
- 晚餐咖喱飯 100
- uber 250
- netflix 訂閱 390

📊 查詢指令
- 今天 / 今日 → 今日消費
- 本月 / 月報 → 本月統計
- help / 說明 → 顯示此說明"""

@app.post("/webhook")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    resp = MessagingResponse()
    msg = resp.message()
    text = Body.strip()

    cmd = handle_command(text)
    if cmd == "__TODAY__":
        msg.body(get_summary_today())
    elif cmd == "__MONTH__":
        msg.body(get_summary_month())
    elif cmd == "__HELP__":
        msg.body(HELP_TEXT)
    else:
        expense = parse_expense(text)
        if expense:
            success = insert_expense(expense)
            if success:
                msg.body(format_reply(expense))
            else:
                msg.body("❌ 記錄失敗，請稍後再試")
        else:
            msg.body("⚠️ 看不懂這筆記錄\n\n請輸入格式：描述 + 金額\n例如：晚餐100\n\n輸入「說明」查看完整指令")

    return Response(content=str(resp), media_type="application/xml")

@app.get("/")
def health():
    return {"status": "ok", "service": "Enzo Finance Bot"}
