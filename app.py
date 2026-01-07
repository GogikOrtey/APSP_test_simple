import os

from flask import Flask, render_template


app = Flask(__name__)


@app.get("/")
def index():
    return render_template(
        "index.html",
        page_title="Главная",
        sample_text="Это пример текста на главной странице. Здесь может быть ваше приветствие или описание проекта.",
    )


@app.get("/page2")
def page2():
    return render_template(
        "page2.html",
        page_title="Вторая страница",
        sample_text="Это пример текста на второй странице. Можно разместить здесь дополнительную информацию.",
    )


@app.get("/page3")
def page3():
    return render_template(
        "page3.html",
        page_title="Третья страница",
        sample_text="Это пример текста на третьей странице. Например, контакты или краткое резюме.",
    )


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true", "yes", "on")
    app.run(host=host, port=port, debug=debug)


