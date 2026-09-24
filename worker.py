import logging
import time

from app import app, process_due_once

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("autopost-worker")

if __name__ == "__main__":
    log.info("AutoPost worker started")
    while True:
        try:
            if process_due_once(app):
                log.info("Processed one due topic")
        except Exception:
            log.exception("Worker cycle failed")
        time.sleep(60)
