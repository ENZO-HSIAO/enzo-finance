import os
from supabase import create_client, Client
from datetime import datetime, date

SUPABASE_URL = "https://zofdsownonnuuwsmhnjy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpvZmRzb3dub25udXV3c21obmp5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY5NDc5NzcsImV4cCI6MjA5MjUyMzk3N30.aXVehZNR4zaMYtCkE5EeU21HCMqO8JLHH8e3DpsoOmo"

def get_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_expense(expense: dict) -> bool:
    try:
        sb = get_client()
        sb.table("expenses").insert({
            "date": expense["date"],
            "time": expense["time"],
            "description": expense["description"],
            "amount": expense["amount"],
            "category": expense["category"],
        }).execute()
        return True
    except Exception as e:
        print(f"DB insert error: {e}")
        return False

def delete_expense(expense_id: int) -> bool:
    try:
        sb = get_client()
        sb.table("expenses").delete().eq("id", expense_id).execute()
        return True
    except Exception as e:
        print(f"DB delete error: {e}")
        return False

def get_recent_expenses(limit: int = 5) -> list:
    try:
        sb = get_client()
        res = sb.table("expenses").select("*").order("created_at", desc=True).limit(limit).execute()
        return res.data
    except Exception as e:
        print(f"DB query error: {e}")
        return []

def get_today_expenses() -> list:
    try:
        sb = get_client()
        today = date.today().isoformat()
        res = sb.table("expenses").select("*").eq("date", today).order("time").execute()
        return res.data
    except Exception as e:
        print(f"DB query error: {e}")
        return []

def get_month_expenses(year: int = None, month: int = None) -> list:
    try:
        sb = get_client()
        now = datetime.now()
        year = year or now.year
        month = month or now.month
        start = f"{year}-{month:02d}-01"
        end = f"{year}-{month:02d}-31"
        res = sb.table("expenses").select("*").gte("date", start).lte("date", end).order("date").execute()
        return res.data
    except Exception as e:
        print(f"DB query error: {e}")
        return []

def get_summary_today() -> str:
    rows = get_today_expenses()
    if not rows:
        return "今天還沒有記錄哦！"
    total = sum(r["amount"] for r in rows)
    lines = [f"📊 今日消費摘要\n💸 共 NT$ {total:,.0f}\n"]
    by_cat = {}
    for r in rows:
        by_cat.setdefault(r["category"], []).append(r)
    emoji_map = {"餐飲": "🍽️", "交通": "🚗", "購物": "🛍️", "娛樂": "🎬",
                 "訂閱": "📱", "醫療": "💊", "住宿": "🏠", "教育": "📚", "其他": "📝"}
    for cat, items in by_cat.items():
        cat_total = sum(i["amount"] for i in items)
        emoji = emoji_map.get(cat, "📝")
        lines.append(f"{emoji} {cat}：NT$ {cat_total:,.0f}")
        for i in items:
            lines.append(f"   • {i['description']} {i['amount']:,.0f}")
    return "\n".join(lines)

def get_summary_month() -> str:
    rows = get_month_expenses()
    if not rows:
        return "本月還沒有記錄哦！"
    total = sum(r["amount"] for r in rows)
    now = datetime.now()
    lines = [f"📅 {now.year}/{now.month} 月報\n💸 共 NT$ {total:,.0f}\n"]
    by_cat = {}
    for r in rows:
        by_cat.setdefault(r["category"], 0)
        by_cat[r["category"]] += r["amount"]
    emoji_map = {"餐飲": "🍽️", "交通": "🚗", "購物": "🛍️", "娛樂": "🎬",
                 "訂閱": "📱", "醫療": "💊", "住宿": "🏠", "教育": "📚", "其他": "📝"}
    for cat, amt in sorted(by_cat.items(), key=lambda x: -x[1]):
        emoji = emoji_map.get(cat, "📝")
        pct = amt / total * 100
        lines.append(f"{emoji} {cat}：NT$ {amt:,.0f} ({pct:.0f}%)")
    return "\n".join(lines)
