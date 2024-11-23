from unidecode import unidecode


def slugify(text):
    text = unidecode(text.lower())
    text = "".join(char if char.isalnum() else " " for char in text)
    text = "-".join(text.split())
    return text
