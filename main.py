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

    
    source = random.choice(sources)
# ... (keep imports, Flask routes, post_to_bluesky function start) ...

    # Heavily biased to Rule34 (has real porn + hentai/futa/femboy)
    sources = ["rule34"] * 8 + ["e621", "rule34"]  # More variety, no realbooru

    # Tags focused on real or realistic explicit (Rule34 has real uploads too)
    rule34_tags = [
        "rating:explicit",
        "real_porn rating:explicit",  # Forces real if available
        "pornstar rating:explicit",
        "blowjob rating:explicit",
        "anal rating:explicit",
        "milf rating:explicit",
        "amateur rating:explicit",
        "big_breasts rating:explicit",
        "cumshot rating:explicit",
        "futanari rating:explicit",
        "femboy rating:explicit",
    ]
    anime_tags = [  # For e621 furry
        "rating:explicit",
        "furry anthro rating:explicit",
        "futanari rating:explicit",
        "femboy rating:explicit",
    ]
    tags = random.choice(rule34_tags if source == "rule34" else anime_tags)

    # Fetch – remove realbooru entirely
    tags_str = tags.replace(' ', '+')
    image_url = None
    if source == "e621":
        url = f"https://e621.net/posts.json?tags={tags_str}+rating:explicit&limit=100"
        headers = {'User-Agent': 'BlueskyBot/1.0'}
        resp = requests.get(url, headers=headers)
        if resp.ok and resp.json().get('posts'):
            image_url = random.choice(resp.json()['posts'])['file']['url']
    else:  # rule34 only now
        base = "https://api.rule34.xxx/index.php"
        url = f"{base}?page=dapi&s=post&q=index&json=1&tags={tags_str}&limit=100"
        resp = requests.get(url)
        if resp.ok and resp.json():
            image_url = random.choice(resp.json())['file_url']

    # ... (rest of embed/post code stays the same)

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
