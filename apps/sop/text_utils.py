import re
import json
from wordcloud import WordCloud
from unidecode import unidecode


def make_text_json_safe(text: str):
    json_safe_text = json.loads(json.dumps(unidecode(text)).replace("\n", "\\n"))
    return json_safe_text


def make_slug_from_text(title: str):
    title = make_text_json_safe(title.lower())
    title = re.sub(r"[^\w\s-]", "", title)
    title = re.sub(r"\s{1,}", "-", title)
    return title


def optimize_text_for_search(text: str):
    text = make_text_json_safe(text.lower())
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"[^\w\s-]", "", text)
    return text


def get_word_cloud_svg(text: str):
    wordcloud = WordCloud(width=600, height=400, background_color="white").generate(
        text
    )
    return wordcloud.to_svg()
