from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from bot_parser import parse_expense, format_reply, handle_command
from database import insert_expense, get_summary_today, get_summary_month, get_recent_expenses, delete_expense

app = FastAPI()

# 暫存每個用戶的刪除狀態
delete_sessions = {}

HELP_TEXT = """👋 Enzo 記帳 Bot 使用說明

📝 記帳格式
直接輸入：消費描述 + 金額
例如：
• 晚餐咖喱飯 100
• uber 250
• netflix 訂閱 390

📊 查詢指令
• 今天 / 今日 → 今日消費
• 本月 / 月報 → 本月統計
• 刪除 → 列出最近5筆選擇刪除
• help / 說明 → 顯示此說明"""

@app.post("/webhook")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    resp = MessagingResponse()
    msg = resp.message()
    text = Body.strip()
    user = From

    # 檢查是否在刪除選擇模式
    if user in delete_sessions:
        records = delete_sessions[user]
        if text.isdigit() and 1 <= int(text) <= len(records):
            idx = int(text) - 1
            record = records[idx]
            success = delete_expense(record["id"])
            del delete_sessions[user]
            if success:
                msg.body(f"✅ 已刪除：{record['description']} NT${record['amount']:,.0f}")
            else:
                msg.body("❌ 刪除失敗，請稍後再試")
        elif text.lower() in ["取消", "cancel", "0"]:
            del delete_sessions[user]
            msg.body("❌ 已取消刪除")
        else:
            records = delete_sessions[user]
            reply = "請輸入編號選擇要刪除的記錄：\n\n"
            for i, r in enumerate(records, 1):
                reply += f"{i}. {r['date']} {r['description']} NT${r['amount']:,.0f}\n"
            reply += "\n輸入「取消」放棄"
            msg.body(reply)
        return Response(content=str(resp), media_type="application/xml")

    # 一般指令處理
    cmd = handle_command(text)
    if cmd == "__TODAY__":
        msg.body(get_summary_today())
    elif cmd == "__MONTH__":
        msg.body(get_summary_month())
    elif cmd == "__HELP__":
        msg.body(HELP_TEXT)
    elif cmd == "__DELETE__":
        records = get_recent_expenses(5)
        if not records:
            msg.body("最近沒有記錄可以刪除")
        else:
            delete_sessions[user] = records
            reply = "請輸入編號選擇要刪除的記錄：\n\n"
            for i, r in enumerate(records, 1):
                reply += f"{i}. {r['date']} {r['description']} NT${r['amount']:,.0f}\n"
            reply += "\n輸入「取消」放棄"
            msg.body(reply)
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
