import logging

def setup_logging():
    logging.basicConfig(
        stream=sys.stdout,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG if os.environ.get('DEBUG') == "TRUE" else logging.INFO,
    )
