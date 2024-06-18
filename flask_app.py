from __future__ import annotations
from dataclasses import dataclass
import typing as tp
from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)


@dataclass
class Emotion(db.Model):
    __tablename__ = "emotion"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String, unique=True)


@dataclass
class Texture(db.Model):
    __tablename__ = "texture"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String, unique=True)


@dataclass
class Shape(db.Model):
    __tablename__ = "shape"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String, unique=True)


emotion_dish = db.Table(
    "emotion_dish",
    Column("left_id", ForeignKey("dish.id")),
    Column("right_id", ForeignKey("emotion.id")),
)

texture_dish = db.Table(
    "texture_dish",
    Column("left_id", ForeignKey("dish.id")),
    Column("right_id", ForeignKey("texture.id")),
)

shape_dish = db.Table(
    "shape_dish",
    Column("left_id", ForeignKey("dish.id")),
    Column("right_id", ForeignKey("shape.id")),
)


@dataclass
class Menu(db.Model):
    __tablename__ = "menu"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    dishes: Mapped[tp.List[Dish]] = relationship()


@dataclass
class Dish(db.Model):
    __tablename__ = "dish"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu.id"))
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    section: Mapped[str] = mapped_column(String)
    # menu: Mapped[Menu] = relationship(back_populates="dishes")
    # emotions
    emotions: Mapped[tp.List[Emotion]] = relationship(secondary=emotion_dish)
    # basic tastes
    bitter: Mapped[tp.Optional[int]] = mapped_column(Integer, nullable=True)
    salty: Mapped[tp.Optional[int]] = mapped_column(Integer, nullable=True)
    sour: Mapped[tp.Optional[int]] = mapped_column(Integer, nullable=True)
    sweet: Mapped[tp.Optional[int]] = mapped_column(Integer, nullable=True)
    umami: Mapped[tp.Optional[int]] = mapped_column(Integer, nullable=True)
    # other tastes
    fat: Mapped[tp.Optional[int]] = mapped_column(Integer, nullable=True)
    piquant: Mapped[tp.Optional[int]] = mapped_column(Integer, nullable=True)
    temperature: Mapped[tp.Optional[int]] = mapped_column(Integer, nullable=True)
    # textures
    textures: Mapped[tp.List[Texture]] = relationship(secondary=texture_dish)
    # colors
    color1: Mapped[tp.Optional[str]] = mapped_column(String, nullable=True)
    color2: Mapped[tp.Optional[str]] = mapped_column(String, nullable=True)
    color3: Mapped[tp.Optional[str]] = mapped_column(String, nullable=True)
    # shapes
    shapes: Mapped[tp.List[Shape]] = relationship(secondary=shape_dish)


@app.route("/")
def index():
    return jsonify({"message": "SoundFood menu API"})


@app.get("/api/menus")
def get_menu():
    menus = db.session.execute(db.select(Menu)).scalars().all()
    return jsonify(menus)


@app.post("/api/menus")
def create_menu():
    request_data = request.json
    assert request_data is not None
    print(request_data)

    new_menu = Menu(
        title=request_data["title"],
        description=request_data["description"],
    )

    for dish in request_data["dishes"]:
        basic_tastes = dish["tastes"]["basic"]
        other_tastes = dish["tastes"]["other"]

        new_dish = Dish(
            name=dish["name"],
            description=dish["description"],
            section=dish["section"],
            sour=basic_tastes["sour"],
            sweet=basic_tastes["sweet"],
            salty=basic_tastes["salty"],
            bitter=basic_tastes["bitter"],
            umami=basic_tastes["umami"],
            fat=other_tastes["fat"],
            piquant=other_tastes["piquant"],
            temperature=other_tastes["temperature"],
        )

        for emotion in dish["emotions"]:
            emotion_obj = db.session.execute(
                db.select(Emotion).where(Emotion.description == emotion)
            ).scalar()
            if emotion_obj:
                new_dish.emotions.append(emotion_obj)

        for texture in dish["textures"]:
            texture_obj = db.session.execute(
                db.select(Texture).where(Texture.description == texture)
            ).scalar()
            if texture_obj:
                new_dish.textures.append(texture_obj)

        for shape in dish["vision"]["shapes"]:
            shape_obj = db.session.execute(
                db.select(Shape).where(Shape.description == shape)
            ).scalar()
            if shape_obj:
                new_dish.shapes.append(shape_obj)

        for i, color in enumerate(dish["vision"]["colors"]):
            match i:
                case 0:
                    new_dish.color1 = color
                case 1:
                    new_dish.color2 = color
                case 2:
                    new_dish.color3 = color
                case _:
                    pass

        new_menu.dishes.append(new_dish)

    db.session.add(new_menu)
    db.session.commit()

    res = make_response(jsonify({"message": "Menu created"}), 201)
    return res


@app.get("/api/menus/<int:menu_id>")
def get_menu_by_id(menu_id: int):
    menu = db.session.execute(db.select(Menu).where(Menu.id == menu_id)).scalar()
    return jsonify(menu)


@app.delete("/api/menus/<int:menu_id>")
def delete_menu(menu_id: int):
    menu = db.session.execute(db.select(Menu).where(Menu.id == menu_id)).scalar()
    db.session.delete(menu)
    db.session.commit()
    return jsonify({"message": "Menu deleted"})


@app.get("/api/dishes")
def get_dishes():
    dishes = db.session.execute(db.select(Dish)).scalars().all()
    return jsonify(dishes)


@app.get("/api/dishes/<int:dish_id>")
def get_dish_by_id(dish_id: int):
    dish = db.session.execute(db.select(Dish).where(Dish.id == dish_id)).scalar()
    return jsonify(dish)


@app.delete("/api/dishes/<int:dish_id>")
def delete_dish(dish_id: int):
    dish = db.session.execute(db.select(Dish).where(Dish.id == dish_id)).scalar()
    db.session.delete(dish)
    db.session.commit()
    return jsonify({"message": "Dish deleted"})


@app.get("/api/emotions")
def get_emotions():
    emotions = db.session.execute(db.select(Emotion)).scalars().all()
    return jsonify(emotions)


@app.post("/api/emotions")
def create_emotion():
    request_data = request.json
    assert request_data is not None

    new_emotion = Emotion(
        description=request_data["description"],
    )

    db.session.add(new_emotion)
    db.session.commit()

    res = make_response(jsonify({"message": "Emotion created"}), 201)
    return res


@app.delete("/api/emotions/<int:emotion_id>")
def delete_emotion(emotion_id: int):
    emotion = db.session.execute(
        db.select(Emotion).where(Emotion.id == emotion_id)
    ).scalar()
    db.session.delete(emotion)
    db.session.commit()
    return jsonify({"message": "Emotion deleted"})


@app.get("/api/textures")
def get_textures():
    textures = db.session.execute(db.select(Texture)).scalars().all()
    return jsonify(textures)


@app.post("/api/textures")
def create_texture():
    request_data = request.json
    assert request_data is not None

    new_texture = Texture(
        description=request_data["description"],
    )

    db.session.add(new_texture)
    db.session.commit()

    res = make_response(jsonify({"message": "Texture created"}), 201)
    return res


@app.delete("/api/textures/<int:texture_id>")
def delete_texture(texture_id: int):
    texture = db.session.execute(
        db.select(Texture).where(Texture.id == texture_id)
    ).scalar()
    db.session.delete(texture)
    db.session.commit()
    return jsonify({"message": "Texture deleted"})


@app.get("/api/shapes")
def get_shapes():
    shapes = db.session.execute(db.select(Shape)).scalars().all()
    return jsonify(shapes)


@app.post("/api/shapes")
def create_shape():
    request_data = request.json
    assert request_data is not None

    new_shape = Shape(
        description=request_data["description"],
    )

    db.session.add(new_shape)
    db.session.commit()

    res = make_response(jsonify({"message": "Shape created"}), 201)
    return res


@app.delete("/api/shapes/<int:shape_id>")
def delete_shape(shape_id: int):
    shape = db.session.execute(db.select(Shape).where(Shape.id == shape_id)).scalar()
    db.session.delete(shape)
    db.session.commit()
    return jsonify({"message": "Shape deleted"})


if __name__ == "__main__":
    app.run(debug=True)
