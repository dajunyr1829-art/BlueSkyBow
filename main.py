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
        return "Posted to Bluesky successfully!"
    except Exception as e:
        return f"Error: {str(e)}"

def post_to_bluesky():
    client = Client()
    client.login(os.environ['HANDLE'], os.environ['APP_PASSWORD'])

    sources = ["realbooru"] * 8 + ["rule34", "e621"]
    source = random.choice(sources)

    real_tags = [
        "rating:explicit",
        "blowjob rating:explicit",
        "anal rating:explicit",
        "milf rating:explicit",
        "amateur rating:explicit",
        "big_breasts rating:explicit",
        "cumshot rating:explicit",
    ]
    anime_tags = [
        "futanari solo rating:explicit",
        "femboy anal rating:explicit",
        "furry anthro rating:explicit",
        "hentai futanari rating:explicit",
    ]
    tags = random.choice(real_tags if source == "realbooru" else anime_tags)

    captions = [
        "Real heat you can't handle 🥵 #nsfw #porn #adult\n\nJoin my community: https://discord.com/invite/NuP2QQvsQM\nPremium = more exclusive NSFW channels + free promo (X links only)!",
        "Fresh real action dropping 🔥 #realporn #nsfw #explicit\n\nDiscord: https://discord.com/invite/NuP2QQvsQM\nUpgrade to Premium for extra channels!",
        "Authentic spice incoming 😏 #porn #hot #nsfw\n\nInvite: https://discord.com/invite/NuP2QQvsQM\nPremium members get free self-promo perks.",
    ]
    caption = random.choice(captions)

    tags_str = tags.replace(' ', '+')
    image_url = None
    if source == "e621":
        url = f"https://e621.net/posts.json?tags={tags_str}+rating:explicit&limit=100"
        headers = {'User-Agent': 'BlueskyBot/1.0'}
        resp = requests.get(url, headers=headers)
        if resp.ok and resp.json().get('posts'):
            image_url = random.choice(resp.json()['posts'])['file']['url']
    else:
        base = "https://api.realbooru.com/index.php" if source == "realbooru" else "https://api.rule34.xxx/index.php"
        url = f"{base}?page=dapi&s=post&q=index&json=1&tags={tags_str}&limit=100"
        resp = requests.get(url)
        if resp.ok and resp.json():
            image_url = random.choice(resp.json())['file_url']

    embed = None
    if image_url:
        try:
            img_data = requests.get(image_url, timeout=30).content
            blob = client.upload_blob(img_data).blob
            embed = models.AppBskyEmbedImages.Main(
                images=[models.AppBskyEmbedImages.Image(alt='Explicit adult content', image=blob)]
            )
        except Exception as e:
            print(f"Image failed: {e}")

    post = models.AppBskyFeedPost.Main(
        text=caption,
        created_at=client.get_current_time_iso(),
        labels=models.ComAtprotoLabelDefs.SelfLabels(
            values=[models.ComAtprotoLabelDefs.LabelValue(value='porn')]
        ),
        embed=embed,
    )

    client.com.atproto.repo.create_record(
        repo=client.me.did,
        collection='app.bsky.feed.post',
        record=post
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
