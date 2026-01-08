from playwright_controller import PlaywrightController


def main() -> None:
    pw = PlaywrightController()
    try:
        print("Initial open pages:", pw.get_open_pages_count())
        print("Open 1:", pw.open_url("https://example.com"))
        print("After 1:", pw.get_open_pages_count())
        print("Open 2:", pw.open_url("https://example.org"))
        print("After 2:", pw.get_open_pages_count())
        # Don't forget to stop to close browser/pages.
    finally:
        pw.stop()
        print("Stopped.")


if __name__ == "__main__":
    main()


