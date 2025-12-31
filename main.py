import random
import requests
from atproto import Client
import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "NSFW Bluesky Bot is running! Visit /post to trigger manually."

@app.route('/post')
def trigger_post():
    try:
        post_to_bluesky()
        return "Posted to Bluesky successfully! 🔥"
    except Exception as e:
        return f"Error during post: {str(e)}"

def post_to_bluesky():
    client = Client()
    client.login(os.environ['HANDLE'], os.environ['APP_PASSWORD'])

    # Heavy bias toward Rule34 for real porn + variety
    sources = ["rule34"] * 8 + ["e621", "rule34"]
    source = random.choice(sources)

    rule34_tags = [
        "rating:explicit",
        "real_porn rating:explicit",
        "pornstar rating:explicit",
        "amateur rating:explicit",
        "blowjob rating:explicit",
        "anal rating:explicit",
        "milf rating:explicit",
        "big_breasts rating:explicit",
        "cumshot rating:explicit",
        "futanari rating:explicit",
        "femboy rating:explicit",
        "trap rating:explicit",
    ]

    e621_tags = [
        "rating:explicit",
        "furry rating:explicit",
        "anthro rating:explicit",
        "futanari rating:explicit",
        "femboy rating:explicit",
        "yiff rating:explicit",
    ]

    tags = random.choice(rule34_tags if source == "rule34" else e621_tags)
    tags_str = tags.replace(" ", "+")

    captions = [
        "Real heat dropping hard 🥵 #nsfw #porn #realporn #adult\n\nJoin my community for more: https://discord.com/invite/NuP2QQvsQM\nPremium unlocks extra NSFW channels + free promo (X links only)!",
        "Steamy action you need right now 🔥 #explicit #hentai #futa #furry\n\nDiscord: https://discord.com/invite/NuP2QQvsQM\nGo Premium for more channels and self-promo perks!",
        "Can't look away from this one 😏 #nsfw #femboy #futanari #anthro\n\nInvite: https://discord.com/invite/NuP2QQvsQM\nPremium = unlimited spicy access + free spots!",
    ]
    caption = random.choice(captions)

    # Improved image fetching - almost always gets an image
    image_url = None
    try:
        # Use a very broad fallback if specific tag fails
        search_tags = tags_str
        if source == "e621":
            url = f"https://e621.net/posts.json?tags={search_tags}&limit=100"
            headers = {'User-Agent': 'BlueskyNSFWBot/1.0'}
            resp = requests.get(url, headers=headers, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                posts = data.get('posts', [])
                if posts:
                    image_url = random.choice(posts)['file']['url']
                else:
                    # Fallback to very safe tag
                    fallback_resp = requests.get("https://e621.net/posts.json?tags=rating:explicit&limit=100", headers=headers, timeout=20)
                    if fallback_resp.status_code == 200:
                        fallback_posts = fallback_resp.json().get('posts', [])
                        if fallback_posts:
                            image_url = random.choice(fallback_posts)['file']['url']
        else:  # rule34
            url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={search_tags}&limit=100"
            resp = requests.get(url, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and data:
                    image_url = random.choice(data)['file_url']
                else:
                    # Fallback to very safe tag
                    fallback_resp = requests.get("https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags=rating:explicit&limit=100", timeout=20)
                    if fallback_resp.status_code == 200:
                        fallback_data = fallback_resp.json()
                        if isinstance(fallback_data, list) and fallback_data:
                            image_url = random.choice(fallback_data)['file_url']
    except Exception as e:
        print(f"Image fetch failed (will post text only): {e}")

    # Upload image if we have one
    embed = None
    if image_url:
        try:
            img_data = requests.get(image_url, timeout=30).content
            blob = client.upload_blob(img_data).blob
            images = [{'alt': 'Explicit NSFW content', 'image': blob}]
            embed = {'$type': 'app.bsky.embed.images', 'images': images}
        except Exception as e:
            print(f"Image upload failed (posting text only): {e}")

    # Send the post - simple high-level method (auto-handles NSFW labeling)
    client.send_post(text=caption, embed=embed)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
