import asyncio
import threading
import time
from typing import Optional


class PlaywrightController:
    """
    Один headless Chromium + одна вкладка (Page) на всё приложение.
    Flask-эндпойнты дергают async-логику через отдельный event-loop в фоне.
    """

    def __init__(self) -> None:
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._ready = threading.Event()
        self._init_error: Optional[str] = None

        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._op_lock = None

        self._last_screenshot_ts: float = 0.0
        self._last_screenshot: Optional[bytes] = None
        self._cache_ttl_sec = 1.0

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        self._ready.clear()
        self._init_error = None

        t = threading.Thread(target=self._thread_main, name="playwright-loop", daemon=True)
        self._thread = t
        t.start()

        # Подождём инициализацию, чтобы ошибки были понятны сразу.
        if not self._ready.wait(timeout=60):
            raise RuntimeError("Playwright не успел инициализироваться за 60 секунд")
        if self._init_error:
            raise RuntimeError(self._init_error)

    def _thread_main(self) -> None:
        try:
            loop = asyncio.new_event_loop()
            self._loop = loop
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._async_init())
            self._ready.set()
            loop.run_forever()
        except Exception as e:  # pragma: no cover
            self._init_error = str(e)
            self._ready.set()

    async def _async_init(self) -> None:
        from playwright.async_api import async_playwright

        self._playwright = await async_playwright().start()

        # В Docker часто нужно отключать sandbox.
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
        )
        self._context = await self._browser.new_context(
            viewport={"width": 1280, "height": 720},
            device_scale_factor=1,
        )
        self._page = await self._context.new_page()
        self._op_lock = asyncio.Lock()

    def _run(self, coro, timeout: float = 60):
        self.start()
        if not self._loop:
            raise RuntimeError("Playwright loop не инициализирован")
        fut = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return fut.result(timeout=timeout)

    @staticmethod
    def _normalize_url(url: str) -> str:
        url = (url or "").strip()
        if not url:
            raise ValueError("Пустой адрес")
        if "://" not in url:
            url = "https://" + url
        return url

    async def _open_async(self, url: str) -> str:
        if not self._page:
            raise RuntimeError("Playwright page не инициализирован")

        if not self._op_lock:
            raise RuntimeError("Playwright lock не инициализирован")

        async with self._op_lock:
            url = self._normalize_url(url)
            resp = await self._page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            # Иногда resp может быть None (например, about:blank), но это ок.
            _ = resp
            return self._page.url

    def open_url(self, url: str) -> str:
        final_url = self._run(self._open_async(url), timeout=70)
        # Сброс кэша скрина, чтобы следующий запрос сразу перерисовал.
        self._last_screenshot = None
        self._last_screenshot_ts = 0.0
        return final_url

    async def _screenshot_async(self) -> bytes:
        if not self._page:
            raise RuntimeError("Playwright page не инициализирован")
        if not self._op_lock:
            raise RuntimeError("Playwright lock не инициализирован")

        async with self._op_lock:
            return await self._page.screenshot(type="png", full_page=True)

    def get_screenshot_png(self) -> bytes:
        now = time.time()
        if self._last_screenshot and (now - self._last_screenshot_ts) < self._cache_ttl_sec:
            return self._last_screenshot

        data = self._run(self._screenshot_async(), timeout=70)
        self._last_screenshot = data
        self._last_screenshot_ts = now
        return data


