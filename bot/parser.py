import re
from datetime import datetime

CATEGORY_KEYWORDS = {
    "餐飲": ["早餐", "午餐", "晚餐", "宵夜", "咖啡", "飲料", "珍奶", "手搖", "便當", "麥當勞",
             "肯德基", "kfc", "711", "全家", "超商", "火鍋", "燒烤", "牛肉麵", "拉麵", "壽司",
             "咖哩", "pizza", "漢堡", "三明治", "沙拉", "下午茶"],
    "交通": ["uber", "taxi", "計程車", "捷運", "公車", "火車", "高鐵", "台鐵", "油錢", "停車",
             "機票", "gogoro", "youbike", "加油"],
    "購物": ["衣服", "鞋子", "包包", "3c", "電子", "蝦皮", "pchome", "momo", "amazon", "ikea",
             "全聯", "好市多", "costco", "家樂福"],
    "娛樂": ["netflix", "spotify", "youtube", "游泳", "健身", "電影", "ktv", "遊戲", "steam"],
    "訂閱": ["訂閱", "年費", "會員", "premium", "plus"],
    "醫療": ["醫院", "診所", "藥局", "藥", "掛號", "看診", "牙醫"],
    "住宿": ["房租", "水電", "網路", "瓦斯", "管理費", "hotel", "airbnb"],
    "教育": ["書", "課程", "補習", "學費", "udemy", "coursera"],
}

def detect_category(text: str) -> str:
    text_lower = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return category
    return "其他"

def parse_expense(text: str) -> dict | None:
    text = text.strip()
    amount_match = re.search(r'(\d+\.?\d*)', text)
    if not amount_match:
        return None
    amount = float(amount_match.group(1))
    description = re.sub(r'\d+\.?\d*', '', text).strip()
    description = re.sub(r'[元塊NTnttwd$＄]', '', description, flags=re.IGNORECASE).strip()
    description = re.sub(r'\s+', ' ', description).strip()
    if not description:
        description = "未分類消費"
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "description": description,
        "amount": amount,
        "category": detect_category(text),
    }

def format_reply(expense: dict) -> str:
    emoji_map = {
        "餐飲": "🍽️", "交通": "🚗", "購物": "🛍️",
        "娛樂": "🎬", "訂閱": "📱", "醫療": "💊",
        "住宿": "🏠", "教育": "📚", "其他": "📝"
    }
    emoji = emoji_map.get(expense["category"], "📝")
    return (
        f"✅ 已記錄！\n"
        f"{emoji} {expense['description']}\n"
        f"💰 NT$ {expense['amount']:,.0f}\n"
        f"🏷️ {expense['category']}\n"
        f"📅 {expense['date']} {expense['time']}"
    )

def handle_command(text: str) -> str | None:
    cmd = text.strip().lower()
    if cmd in ["今日", "today", "今天"]: return "__TODAY__"
    if cmd in ["本月", "this month", "月報"]: return "__MONTH__"
    if cmd in ["help", "說明", "幫助", "指令"]: return "__HELP__"
    return None
