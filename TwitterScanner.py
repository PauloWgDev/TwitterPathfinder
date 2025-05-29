from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import json
import os

# ---------- CONFIGURATION ----------
MAX_DEPTH = 4
MAX_TWEETS = 10
WAIT_TIME = 2
USERS_PER_PART = 30  # Save every 100 visited users

# ---------- GLOBALS ----------
stop_requested = False  # Set this True to stop crawling gracefully (e.g., from another thread or manually in notebook)

# ---------- UTILITY FUNCTIONS ----------
def extract_mentions(text):
    return re.findall(r"@\w+", text)

def save_partial(edges, start_user, max_depth, max_tweets, part_num):
    os.makedirs("mention_networks", exist_ok=True)
    json_name = f"{start_user}_{max_depth}_{max_tweets}_part{part_num}.json"
    json_path = os.path.join("mention_networks", json_name)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(edges, f, indent=2)
    print(f"\n💾 Saved partial mention graph to {json_path}")

# ---------- TWITTER SCRAPER ----------
def login_to_twitter():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://twitter.com/login")
    print("\n🔐 Please log in manually in the opened browser window.")
    input("✅ Press ENTER after you have successfully logged in...\n")
    return driver

def wait_for_tweets(driver, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//article"))
        )
    except:
        print("⚠️ Timeout waiting for tweets to load.")

def scrape_mentions(driver, username):
    url = f"https://twitter.com/{username}"
    print(f"Opening: {url}")
    driver.get(url)
    wait_for_tweets(driver)

    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(WAIT_TIME)

    tweet_texts = {}
    scroll_attempts = 0

    def collect_tweets():
        articles = driver.find_elements(By.XPATH, "//article")
        for article in articles:
            try:
                spans = article.find_elements(By.XPATH, ".//span")
                text = " ".join(span.text for span in spans if span.text.strip())
                if text and text not in tweet_texts:
                    tweet_texts[text] = text
            except:
                continue

    # Initial scroll and collection
    collect_tweets()

    if len(tweet_texts) == 0:
        print("⚠️ No tweets found. Trying Replies tab temporarily...")
        try:
            # Click "Replies" tab
            replies_tab = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Replies"))
            )
            replies_tab.click()
            time.sleep(WAIT_TIME)
        except Exception as e:
            print(f"⚠️ Failed to switch tabs: {e}")

    # Continue scrolling and collecting
    while len(tweet_texts) < MAX_TWEETS and scroll_attempts < 4:
        collect_tweets()
        scroll_attempts += 1
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(WAIT_TIME)

    tweets_texts = list(tweet_texts.values())[:MAX_TWEETS]
    print(f"🧪 Found {len(tweets_texts)} unique tweet articles on @{username}")

    mentions = set()
    for i, text in enumerate(tweets_texts):
        found_mentions = extract_mentions(text)
        if found_mentions:
            print(f"    ↳ Mentions: {found_mentions}")
        mentions.update(found_mentions)

    return list(mentions)[:10]

# ---------- RECURSIVE CRAWLER ----------
def crawl_mentions_network(start_user, max_depth=MAX_DEPTH, max_tweets=MAX_TWEETS):
    global stop_requested

    driver = login_to_twitter()
    visited = set()
    edges = []
    part_counter = 1

    def dfs(user, depth):
        nonlocal part_counter
        if stop_requested:
            print("⚠️ Stop requested, aborting DFS.")
            return
        if depth > max_depth or user in visited:
            return

        visited.add(user)

        # Periodic saving
        if len(visited) % USERS_PER_PART == 0:
            print(f"\n⏳ Reached {len(visited)} visited users, saving partial results...")
            save_partial(edges, start_user, max_depth, max_tweets, part_counter)
            part_counter += 1

        try:
            mentions = scrape_mentions(driver, user)
        except Exception as e:
            print(f"❌ Failed to scrape @{user}: {e}")
            return

        for mentioned in mentions:
            if stop_requested:
                print("⚠️ Stop requested, breaking mention loop.")
                return
            mentioned_user = mentioned[1:]  # Remove '@'
            edges.append((user, mentioned_user))
            dfs(mentioned_user, depth + 1)

    try:
        dfs(start_user, 0)
    except KeyboardInterrupt:
        print("\n⚠️ KeyboardInterrupt detected! Stopping safely...")
        stop_requested = True
    except Exception as e:
        print(f"❌ Unexpected exception: {e}")

    print("\n⏳ Saving final results...")
    save_partial(edges, start_user, max_depth, max_tweets, part_counter)
    driver.quit()
    return edges

# ---------- MAIN ----------
if __name__ == "__main__":
    start_username = "WgPaulo"  # Replace with your starting username

    try:
        mention_edges = crawl_mentions_network(start_username)
    except KeyboardInterrupt:
        print("\n⚠️ KeyboardInterrupt detected in main! Exiting safely...")

    print("\n📈 Mention Edges:")
    for source, target in mention_edges:
        print(f"{source} -> {target}")
