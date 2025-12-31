import random
import requests
from atproto import Client, models
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

    # Heavy bias toward Rule34 (tons of real porn + hentai/futa/femboy)
    sources = ["rule34"] * 8 + ["e621", "rule34"]

    source = random.choice(sources)

    # Tags focused on real + explicit
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

    # Promotional captions
    captions = [
        "Real heat dropping hard 🥵 #nsfw #porn #realporn #adult\n\nJoin my community for more: https://discord.com/invite/NuP2QQvsQM\nPremium unlocks extra NSFW channels + free promo (X links only)!",
        "Steamy action you need right now 🔥 #explicit #hentai #futa #furry\n\nDiscord: https://discord.com/invite/NuP2QQvsQM\nGo Premium for more channels and self-promo perks!",
        "Can't look away from this one 😏 #nsfw #femboy #futanari #anthro\n\nInvite: https://discord.com/invite/NuP2QQvsQM\nPremium = unlimited spicy access + free spots!",
    ]
    caption = random.choice(captions)

    # Safe image fetching
    image_url = None
    try:
        if source == "e621":
            url = f"https://e621.net/posts.json?tags={tags_str}&limit=100"
            headers = {'User-Agent': 'BlueskyNSFWBot/1.0'}
            resp = requests.get(url, headers=headers, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('posts'):
                    posts = data['posts']
                    if posts:
                        image_url = random.choice(posts)['file']['url']
        else:  # rule34
            url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tags_str}&limit=100"
            resp = requests.get(url, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and data:
                    image_url = random.choice(data)['file_url']
    except Exception as e:
        print(f"Image fetch failed: {e}")

    # Prepare embed if we have an image
    embed = None
    if image_url:
        try:
            img_data = requests.get(image_url, timeout=30).content
            blob = client.upload_blob(img_data).blob
            embed = models.AppBskyEmbedImages.Main(
                images=[models.AppBskyEmbedImages.Image(alt="Explicit NSFW content", image=blob)]
            )
        except Exception as e:
            print(f"Image upload failed: {e}")
            embed = None

    # Create the post record (do NOT pass embed=None)
    record_kwargs = {
        "text": caption,
        "created_at": client.get_current_time_iso(),
        "labels": models.ComAtprotoLabelDefs.SelfLabels(
            values=[models.ComAtprotoLabelDefs.LabelValue(val='porn')]
        ),
    }
    if embed:
        record_kwargs["embed"] = embed

    record = models.AppBskyFeedPost.Record(**record_kwargs)

    # Send the post
    client.com.atproto.repo.create_record(
        repo=client.me.did,
        collection='app.bsky.feed.post',
        record=record
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
