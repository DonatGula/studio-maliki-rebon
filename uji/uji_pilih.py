import sys, threading, time, runpy
sys.argv = ["studio.py"]
import webview
from webview import window as W
W.Window.create_file_dialog = lambda self, *a, **k: [r"C:\Users\uji\Video Saya\podcast panjang.mp4"]
asli_start = webview.start
def start(func=None, *a, **k):
    def uji():
        if func: func()
        w = webview.windows[0]
        for _ in range(60):
            time.sleep(1)
            try:
                if w.evaluate_js("!!(window.pywebview && window.pywebview.api && window.pywebview.api.pilih_video)"): break
            except Exception: pass
        w.evaluate_js("document.querySelector('#tblFile').click()")
        time.sleep(2)
        print("SUMBER =", w.evaluate_js("document.querySelector('#sumber').value"), flush=True)
        print("FILE INPUT DIBUKA?", w.evaluate_js("document.querySelector('#pilihFile').files.length"), flush=True)
        w.destroy()
    return asli_start(uji, *a, **k)
webview.start = start
runpy.run_path("studio.py", run_name="__main__")
