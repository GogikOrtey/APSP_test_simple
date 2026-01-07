## Flask + Jinja: 3 страницы

Минимальный пример Flask-приложения с тремя страницами на Jinja и общей шапкой-навигацией.

### Установка

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Запуск

```bash
python app.py
```

Откройте в браузере:
- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/page2`
- `http://127.0.0.1:5000/page3`

### Запуск в Docker (Linux/Windows/macOS)

В проект добавлены файлы: `Dockerfile`, `.dockerignore`, `docker-compose.yml`.

#### Вариант A: через docker compose (рекомендую)

1) Установите Docker Engine + Docker Compose plugin на Linux.
2) Скопируйте проект на Linux (через `git clone ...` или просто zip/флешку).
3) В папке проекта выполните:

```bash
docker compose up --build -d
```

Открывайте в браузере:
- `http://<IP_вашего_Linux>:8000/`
- `http://<IP_вашего_Linux>:8000/page2`
- `http://<IP_вашего_Linux>:8000/page3`

Остановить:

```bash
docker compose down
```

#### Вариант B: без compose (ручные команды)

Сборка образа:

```bash
docker build -t apsp-test-simple:latest .
```

Запуск контейнера:

```bash
docker run --rm -p 8000:8000 --name apsp-web apsp-test-simple:latest
```

---

### Можно собрать контейнер на основной машине с проектом, и далее переместить и запустить его на Linux:

На Windows (в папке проекта):
```
docker build -t apsp-test-simple:latest .
docker save -o apsp-test-simple.tar apsp-test-simple:latest
```

> apsp-test-simple:latest - это будет image  
>
> apsp-test-simple.tar - это будет упакованный image, который мы отправляем на сервер

Перенеси apsp-test-simple.tar на Linux, затем на Linux:

```
docker load -i apsp-test-simple.tar
docker run --rm -p 8000:8000 --name apsp-web apsp-test-simple:latest
```