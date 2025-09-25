import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
import time
import requests
from app.events import get_event_bus, Event, run_consumer_loop


class MainGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("V3.1 - Scaffold GUI")
        self.root.geometry("800x600")

        self.bus = get_event_bus()
        self.stop_event = threading.Event()

        # build UI first (widgets needed by consumer callbacks)
        self._build()

        # start consumer in background thread to update GUI
        self.consumer_thread = threading.Thread(
            target=run_consumer_loop,
            args=(self._on_event, self.stop_event),
            daemon=True,
        )
        self.consumer_thread.start()
        # enable start button only after consumer has started to ensure listeners are registered
        try:
            self.start_btn.config(state=tk.NORMAL)
        except Exception:
            pass

    def _build(self):
        nb = ttk.Notebook(self.root)
        nb.pack(fill=tk.BOTH, expand=True)

        # Keywords tab
        tab1 = ttk.Frame(nb)
        nb.add(tab1, text="Keywords")
        ttk.Label(tab1, text="Keywords (Etapa 1)").pack(anchor=tk.W)

        # Ads tab
        tab2 = ttk.Frame(nb)
        nb.add(tab2, text="Anúncios")
        ttk.Label(tab2, text="Anúncios (Etapa 2/3)").pack(anchor=tk.W)
        self._build_ads_tab(tab2)

        # Metrics tab
        tab3 = ttk.Frame(nb)
        nb.add(tab3, text="Métricas")
        ttk.Label(tab3, text="Métricas (Etapa 4)").pack(anchor=tk.W)
        self._build_metrics_tab(tab3)

        # Status/logs
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.X)
        # start disabled until consumer thread is up (prevents publishing before listeners ready)
        self.start_btn = ttk.Button(
            frame, text="Start Mock Run", command=self._start_run, state=tk.DISABLED
        )
        self.start_btn.pack(side=tk.LEFT, padx=4, pady=4)
        self.stop_btn = ttk.Button(
            frame, text="Stop", command=self._stop_run, state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=4, pady=4)

        self.log = scrolledtext.ScrolledText(self.root, height=12, state=tk.DISABLED)
        self.log.pack(fill=tk.BOTH, expand=False)
        # configure error tag (red)
        try:
            self.log.tag_config("error", foreground="red")
        except Exception:
            pass

    def _start_run(self):
        # publish an intent to start a job; JobManager should listen
        self.bus.publish(
            Event(type="intent.start_run", payload={"keywords": ["python", "tkinter"]})
        )
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self._log("Published start intent")

    def _stop_run(self):
        self.bus.publish(Event(type="intent.stop_run", payload={}))
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self._log("Published stop intent")

    def _on_event(self, ev: Event):
        # run in background thread; schedule GUI updates via after
        self.root.after(0, lambda: self._handle_ui_event(ev))

    def _handle_ui_event(self, ev: Event):
        # colored error logs when job.error
        timestamp = f"[{time.strftime('%H:%M:%S')}]"
        text = f"{timestamp} {ev.type} - {ev.payload}"
        if ev.type == "job.error":
            # insert with error tag
            self.log.config(state=tk.NORMAL)
            self.log.insert(tk.END, text + "\n", "error")
            self.log.see(tk.END)
            self.log.config(state=tk.DISABLED)
        else:
            self._log(text)

        # optional: update ads/metrics views when job finishes
        if ev.type == "job.finished":
            # refresh ads display if present
            try:
                if hasattr(self, "ads_text"):
                    # run update in background to avoid blocking
                    threading.Thread(target=self._fetch_ads, daemon=True).start()
            except Exception:
                pass

    def _log(self, text: str):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

    # ------------------ Ads tab helpers ------------------
    def _build_ads_tab(self, parent):
        """Create UI elements for the Anúncios tab."""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=4)

        btn = ttk.Button(toolbar, text="Atualizar", command=lambda: threading.Thread(target=self._fetch_ads, daemon=True).start())
        btn.pack(side=tk.LEFT, padx=4)

        self.ads_text = scrolledtext.ScrolledText(parent, height=20, state=tk.NORMAL)
        self.ads_text.pack(fill=tk.BOTH, expand=True)

        # initial empty state
        self.ads_text.insert(tk.END, "Clique em Atualizar para carregar anúncios...\n")

    # ------------------ Metrics tab helpers ------------------
    def _build_metrics_tab(self, parent):
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=4)
        # Atualizar button with reference so we can disable while loading
        self.metrics_update_btn = ttk.Button(
            toolbar,
            text="Atualizar",
            command=lambda: threading.Thread(target=self._fetch_metrics, daemon=True).start(),
        )
        self.metrics_update_btn.pack(side=tk.LEFT, padx=4)

        self.metrics_text = scrolledtext.ScrolledText(parent, height=20, state=tk.NORMAL)
        self.metrics_text.pack(fill=tk.BOTH, expand=True)
        self.metrics_text.insert(tk.END, "Clique em Atualizar para carregar métricas...\n")
        # hidden progress bar (spinner) to show while loading
        self.metrics_spinner = ttk.Progressbar(toolbar, mode='indeterminate')

    def _fetch_metrics(self):
        url = "http://127.0.0.1:8000/metrics"
        # show loading UI: disable button and start spinner
        def show_loading():
            try:
                self.metrics_update_btn.config(state=tk.DISABLED)
            except Exception:
                pass
            try:
                self.metrics_spinner.pack(side=tk.LEFT, padx=6)
                self.metrics_spinner.start(10)  # interval in ms
            except Exception:
                pass

        self.root.after(0, show_loading)
        try:
            resp = requests.get(url, timeout=3)
            resp.raise_for_status()
            metrics = resp.json()
        except Exception as e:
            self._log(f"Erro ao buscar métricas: {e}")

            def show_err():
                self.metrics_text.config(state=tk.NORMAL)
                self.metrics_text.delete("1.0", tk.END)
                self.metrics_text.insert(tk.END, f"Erro ao buscar métricas: {e}\n")
                self.metrics_text.config(state=tk.DISABLED)
                try:
                    self.metrics_update_btn.config(state=tk.NORMAL)
                except Exception:
                    pass
                try:
                    self.metrics_spinner.stop()
                    self.metrics_spinner.pack_forget()
                except Exception:
                    pass

            self.root.after(0, show_err)
            return

        def render():
            self.metrics_text.config(state=tk.NORMAL)
            self.metrics_text.delete("1.0", tk.END)
            # pretty print basic aggregates with formatting
            def fmt_num(x):
                try:
                    if x is None:
                        return "-"
                    # show integers without decimals, floats with 2 decimals
                    if isinstance(x, int):
                        return str(x)
                    return f"{float(x):.2f}"
                except Exception:
                    return str(x)

            self.metrics_text.insert(tk.END, f"total_ads: {fmt_num(metrics.get('total_ads'))}\n")
            self.metrics_text.insert(tk.END, f"total_runs: {fmt_num(metrics.get('total_runs'))}\n")
            self.metrics_text.insert(tk.END, f"avg_duration: {fmt_num(metrics.get('avg_duration'))}\n")
            self.metrics_text.insert(tk.END, f"p50_duration: {fmt_num(metrics.get('p50_duration'))}\n")
            self.metrics_text.insert(tk.END, f"p95_duration: {fmt_num(metrics.get('p95_duration'))}\n\n")
            # per-keyword
            per = metrics.get('per_keyword') or {}
            if not per:
                self.metrics_text.insert(tk.END, "Nenhum dado por keyword.\n")
            else:
                self.metrics_text.insert(tk.END, "Per keyword:\n")
                for k, v in per.items():
                    runs = fmt_num(v.get('runs'))
                    ads = fmt_num(v.get('ads'))
                    avg_d = fmt_num(v.get('avg_duration'))
                    self.metrics_text.insert(tk.END, f"  {k}: runs={runs} ads={ads} avg_duration={avg_d}\n")
            self.metrics_text.config(state=tk.DISABLED)
            try:
                self.metrics_update_btn.config(state=tk.NORMAL)
            except Exception:
                pass
            try:
                self.metrics_spinner.stop()
                self.metrics_spinner.pack_forget()
            except Exception:
                pass

        self.root.after(0, render)

    def _fetch_ads(self):
        """Fetch /ads and populate the ads_text widget. Run in background thread."""
        url = "http://127.0.0.1:8000/ads"
        try:
            resp = requests.get(url, timeout=3)
            resp.raise_for_status()
            ads = resp.json()
        except Exception as e:
            # show error in GUI log
            self._log(f"Erro ao buscar anúncios: {e}")
            # also show brief message in ads area
            def show_err():
                self.ads_text.config(state=tk.NORMAL)
                self.ads_text.delete("1.0", tk.END)
                self.ads_text.insert(tk.END, f"Erro ao buscar anúncios: {e}\n")
                self.ads_text.config(state=tk.DISABLED)

            self.root.after(0, show_err)
            return

        # render results in the ads_text area on the main thread
        def render():
            self.ads_text.config(state=tk.NORMAL)
            self.ads_text.delete("1.0", tk.END)
            if not ads:
                self.ads_text.insert(tk.END, "Nenhum anúncio encontrado.\n")
            else:
                for ad in ads:
                    line = f"[{ad.get('keyword')}] {ad.get('title')} - {ad.get('domain')}\n"
                    self.ads_text.insert(tk.END, line)
            self.ads_text.config(state=tk.DISABLED)

        self.root.after(0, render)

    def run(self):
        try:
            self.root.protocol("WM_DELETE_WINDOW", self._on_close)
            self.root.mainloop()
        finally:
            self.stop_event.set()

    def _on_close(self):
        # safe-to-close: publish stop and wait briefly
        self.bus.publish(Event(type="intent.stop_run", payload={}))
        self._log("Closing GUI, stopping workers...")
        self.stop_event.set()
        self.root.after(200, self.root.destroy)


def main():
    gui = MainGUI()
    gui.run()


if __name__ == "__main__":
    main()
