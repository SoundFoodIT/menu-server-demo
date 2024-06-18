from flask_app import app, db, Emotion, Texture, Shape

EMOTIONS = [
    "joy",
    "anger",
    "fear",
    "sadness",
    "surprise",
    "satisfaction",
    "gratitude",
    "hope",
    "love",
    "serenity",
    "euphoria",
    "conviviality",
    "playfulness",
]
SHAPES = [
    "sharp",
    "round",
    "smooth",
    "symmetric",
    "asymmetric",
    "compact",
    "loose",
]
TEXTURES = [
    "rough",
    "soft",
    "hard",
    "creamy",
    "crunchy",
    "liquid",
    "viscous",
    "solid",
    "hollow",
    "dense",
    "porous",
    "airy",
]

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        for e in EMOTIONS:
            emotion = Emotion(description=e)
            db.session.add(emotion)
        for t in TEXTURES:
            texture = Texture(description=t)
            db.session.add(texture)
        for s in SHAPES:
            shape = Shape(description=s)
            db.session.add(shape)

        try:
            db.session.commit()
            print("Database created")
        except Exception as e:
            print(e)
            db.session.rollback()
            print("Failed to create database")
