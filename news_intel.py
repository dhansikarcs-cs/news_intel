import feedparser
from google import genai
import os
import time

# --- CONFIG ---
API_KEY = "# Enter your own Api"
RULES_FILE = "rules.txt"
FEEDS = [
    "https://thehackernews.com/feeds/posts/default",
    "https://www.artificialintelligence-news.com/feed/",
    "https://techcrunch.com/category/security/feed/",
    "https://krebsonsecurity.com/feed/"
]

def fetch_and_summarize():
    client = genai.Client(api_key=API_KEY)
    
    # 1. Load instructions from rules.txt
    rules = "Summarize the news headlines."
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r") as f:
            rules = f.read()

    # 2. Scrape Headlines (Reduced count to stay under token limits)
    print("🛰️  Scraping intelligence...")
    news_content = ""
    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:2]: # Just top 2 per feed to be super safe with tokens
                news_content += f"TITLE: {entry.title}\nSUMMARY: {entry.description[:150]}\n---\n"
        except: continue

    # 3. AI Processing with Retry Logic (Using ONLY your verified model IDs)
    models_to_try = ["gemini-2.0-flash", "gemini-flash-latest"]
    
    for model_name in models_to_try:
        for attempt in range(2): # 2 attempts per model
            try:
                print(f"🤖  Trying {model_name} (Attempt {attempt+1})...")
                response = client.models.generate_content(
                    model=model_name, 
                    contents=f"{rules}\n\nDATA:\n{news_content}"
                )
                
                # Success Logic
                report = f"\n📅 --- INTELLIGENCE REPORT ({os.popen('date').read().strip()}) ---\n"
                report += response.text
                print(report)
                
                with open("daily_brief.txt", "a") as f:
                    f.write(report + "\n" + "="*50 + "\n")
                print("✅ Intelligence logged to daily_brief.txt")
                return 
                
            except Exception as e:
                if "429" in str(e):
                    print("⚠️  Quota full. Waiting 15s to bypass the minute-limit...")
                    time.sleep(15)
                else:
                    print(f"❌ {model_name} failed: {e}")
                    break # Move to next model
                    
    print("💀 Mission Failed. Google's gate is closed for now.")

if __name__ == "__main__":
    fetch_and_summarize()
