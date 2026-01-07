import os

from flask import Flask, jsonify, render_template, request

from dotenv import load_dotenv

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


load_dotenv()


app = Flask(__name__)


def _get_openai_api_key() -> str | None:
    return os.getenv("OPEN_AI_API_KEY") or os.getenv("OPENAI_API_KEY")


def _get_openai_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-5.2")


@app.post("/api/chat")
def api_chat():
    if OpenAI is None:
        return (
            jsonify(
                ok=False,
                error="Библиотека openai не установлена. Выполните: pip install -r requirements.txt",
            ),
            500,
        )

    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify(ok=False, error="Пустой запрос"), 400

    api_key = _get_openai_api_key()
    if not api_key:
        return (
            jsonify(
                ok=False,
                error="Не найден ключ OPEN_AI_API_KEY (или OPENAI_API_KEY) в .env/переменных окружения",
            ),
            500,
        )

    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(model=_get_openai_model(), input=prompt)
        answer = getattr(response, "output_text", "") or ""
        return jsonify(ok=True, answer=answer)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@app.get("/")
def index():
    return render_template(
        "index.html",
        page_title="Главная",
        sample_text="Версия 0.2. Это пример текста на главной странице. Здесь может быть ваше приветствие или описание проекта.",
    )


@app.get("/page2")
def page2():
    return render_template(
        "page2.html",
        page_title="Вторая страница",
        sample_text="Форма ниже отправляет запрос в ChatGPT через /api/chat и показывает полный ответ (без посимвольного вывода).",
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


