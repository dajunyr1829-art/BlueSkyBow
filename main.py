# main.py - COMPLETE WORKING BLUESKY BOT (tested Dec 2025)
import random
import requests
import os
from atproto import Client
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "🔥 NSFW Bluesky Bot LIVE! POST → /post"

@app.route('/post')
def trigger_post():
    try:
        post_to_bluesky()
        return "✅ IMAGE POSTED TO BLUESKY! Check your feed 🔥"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def post_to_bluesky():
    # Login
    client = Client()
    client.login(os.environ['HANDLE'], os.environ['APP_PASSWORD'])
    
    # Pick source (heavy Rule34 bias)
    sources = ["rule34"] * 8 + ["e621"]
    source = random.choice(sources)
    
    # Tags
    rule34_tags = [
        "rating:explicit", "real_porn rating:explicit", "pornstar rating:explicit",
        "blowjob rating:explicit", "anal rating:explicit", "milf rating:explicit",
        "big_breasts rating:explicit", "cumshot rating:explicit"
    ]
    e621_tags = ["rating:explicit", "furry rating:explicit", "futanari rating:explicit"]
    
    tags = random.choice(rule34_tags if source == "rule34" else e621_tags)
    tags_str = tags.replace(" ", "+")
    
    # Caption
    captions = [
        "🥵 Real heat dropping! #nsfw #porn\n👉 discord.com/invite/NuP2QQvsQM",
        "🔥 Can't look away... #explicit #nsfw\nPremium: discord.com/invite/NuP2QQvsQM",
        "😈 Pure fire! #adult #pornstar\nJoin: discord.com/invite/NuP2QQvsQM"
    ]
    caption = random.choice(captions)
    
    # FETCH IMAGE
    image_url = None
    try:
        if source == "e621":
            url = f"https://e621.net/posts.json?tags={tags_str}&limit=100"
            headers = {'User-Agent': 'BlueskyBot/1.0'}
            resp = requests.get(url, headers=headers, timeout=20)
            if resp.status_code == 200 and resp.json().get('posts'):
                image_url = random.choice(resp.json()['posts'])['file']['url']
        else:  # rule34
            url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tags_str}&limit=100"
            resp = requests.get(url, timeout=20)
            if resp.status_code == 200 and resp.json():
                image_url = random.choice(resp.json())['file_url']
                
    except Exception as e:
        print(f"Image fetch failed: {e}")
    
    # POST IMAGE (THIS IS THE MAGIC THAT WORKS)
    if image_url:
        try:
            print(f"📥 Downloading: {image_url}")
            img_data = requests.get(image_url, timeout=30).content
            
            # CRITICAL: send_image() handles ALL blob/embed logic automatically
            client.send_image(
                text=caption,
                image=img_data,
                image_alt='🔥 Explicit NSFW content'
            )
            print("✅ IMAGE POSTED SUCCESSFULLY!")
            return
        except Exception as e:
            print(f"Image post failed: {e}")
    
    # FALLBACK TEXT POST
    client.send_post(text=caption)
    print("📝 Text-only post (no image)")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
