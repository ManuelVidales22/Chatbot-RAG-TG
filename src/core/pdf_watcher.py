import os
import time
import threading

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

MICROCURRICULOS_PDF_FOLDER = os.path.join("data", "pdfs", "microcurriculos")
MICROCURRICULOS_TEXT_FOLDER = os.path.join("data", "texts", "microcurriculos")
SEMESTER_RANGE = range(2, 11)

_observer = None
_observer_lock = threading.Lock()


def ensure_microcurriculos_folders():
    """Crea las carpetas de semestres 2-10 en pdfs y texts si no existen."""
    for semester in SEMESTER_RANGE:
        folder_name = f"Semestre {semester}"
        os.makedirs(os.path.join(MICROCURRICULOS_PDF_FOLDER, folder_name), exist_ok=True)
        os.makedirs(os.path.join(MICROCURRICULOS_TEXT_FOLDER, folder_name), exist_ok=True)


class _PDFEventHandler(FileSystemEventHandler):
    """Detecta PDFs nuevos o movidos dentro de data/pdfs/microcurriculos/ y los procesa."""

    def __init__(self):
        self._processing_lock = threading.Lock()

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(".pdf"):
            self._handle(event.src_path)

    def on_moved(self, event):
        if not event.is_directory and event.dest_path.lower().endswith(".pdf"):
            self._handle(event.dest_path)

    def _handle(self, pdf_path):
        # Pequeña pausa para asegurar que el archivo esté completamente escrito
        time.sleep(2)
        with self._processing_lock:
            import core.pdf_processor as pdf_processor
            print(f"[Watcher] Nuevo PDF detectado: {pdf_path}")
            try:
                pdf_processor.process_pdfs()
                print(f"[Watcher] Procesamiento completado para: {pdf_path}")
            except Exception as exc:
                print(f"[Watcher] Error al procesar {pdf_path}: {exc}")


def start_watcher():
    """Inicia el observador de archivos en background. Idempotente: solo crea uno."""
    global _observer

    with _observer_lock:
        if _observer is not None and _observer.is_alive():
            return _observer

        ensure_microcurriculos_folders()
        abs_folder = os.path.abspath(MICROCURRICULOS_PDF_FOLDER)
        os.makedirs(abs_folder, exist_ok=True)

        handler = _PDFEventHandler()
        _observer = Observer()
        _observer.schedule(handler, abs_folder, recursive=True)
        _observer.daemon = True
        _observer.start()
        print(f"[Watcher] Vigilante iniciado — monitoreando: {abs_folder}")

    return _observer


def stop_watcher():
    """Detiene el observador si está activo."""
    global _observer
    with _observer_lock:
        if _observer is not None and _observer.is_alive():
            _observer.stop()
            _observer.join()
            _observer = None
            print("[Watcher] Vigilante detenido.")
