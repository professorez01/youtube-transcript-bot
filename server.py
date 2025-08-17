import threading
import http.server
import socketserver
import os

# Import the main function from our Telegram bot
from main import main as start_telegram_bot


def run_telegram_bot():
    """
    Start the Telegram bot in a separate thread using the existing
    main() function from the main module. This will block inside
    application.run_polling(), so running it in a thread keeps our
    HTTP server responsive.
    """
    try:
        start_telegram_bot()
    except Exception as e:
        # If the bot encounters an error, log it to stdout. Render
        # captures stdout and stderr so you can debug from the logs.
        print(f"Telegram bot exited with error: {e}")


def run_http_server():
    """
    Start a simple HTTP server to satisfy Render's health check. This
    server responds with a basic message for any GET request. You can
    customize the response as needed.
    """
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"YouTube Transcript Bot is running.\n")

    # Determine the port to listen on. Render sets the PORT environment
    # variable for web services. Default to 8080 for local testing.
    port = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"HTTP server listening on port {port}")
        httpd.serve_forever()


def main():
    # Start the Telegram bot in a daemon thread so it doesn't block
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()

    # Run the HTTP server in the main thread
    run_http_server()


if __name__ == "__main__":
    main()
