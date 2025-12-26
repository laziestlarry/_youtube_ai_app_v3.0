TOPICS = ["AI Business", "Startup Models", "Productivity Tools"]

for topic in TOPICS:
    ideas = generate_ideas(topic)
    for idea in ideas:
        script = generate_script(idea["title"], topic)
        audio = tts(script)
        image = generate_thumbnail(idea["title"])
        video = compose(audio, image)
        youtube_upload(idea["title"], video)