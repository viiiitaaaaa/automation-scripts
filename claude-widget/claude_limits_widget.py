"""
Виджет лимитов Claude над панелью задач Windows.

Показывает, сколько израсходовано из лимита 5-часовой сессии и недельного лимита,
и когда они сбросятся. Данные — те же, что в /usage в Claude Code.
Токен входа берётся из ~/.claude/.credentials.json (его обновляет сам Claude Code)
и отправляется только на api.anthropic.com.

Запуск без чёрного окна:  pythonw claude_limits_widget.py
Перетащить — левой кнопкой мыши. Правая кнопка — меню «Обновить / Закрыть».
"""
import ctypes
import json
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path

import requests

CRED = Path.home() / ".claude" / ".credentials.json"
URL = "https://api.anthropic.com/api/oauth/usage"
REFRESH_MS = 3 * 60 * 1000
W, H = 250, 92

BG, FG, MUTED, TRACK = "#1E1F1C", "#ECEAE0", "#9B9A8B", "#34352F"
GOOD, WARN, BAD = "#6CC49A", "#E0A857", "#E5876F"
DAYS = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]


def fetch():
    tok = json.loads(CRED.read_text(encoding="utf-8"))["claudeAiOauth"]["accessToken"]
    r = requests.get(URL, timeout=20, headers={"Authorization": f"Bearer {tok}",
                                               "anthropic-beta": "oauth-2025-04-20"})
    if r.status_code == 401:
        raise RuntimeError("вход устарел — откройте Claude Code")
    r.raise_for_status()
    return r.json()


def when(iso, with_day):
    if not iso:
        return ""
    t = datetime.fromisoformat(iso).astimezone()
    return f"{DAYS[t.weekday()]} {t:%H:%M}" if with_day else f"{t:%H:%M}"


def color(p):
    return GOOD if p < 60 else WARN if p < 85 else BAD


def work_area():
    """Прямоугольник рабочего стола без панели задач (SPI_GETWORKAREA)."""
    class RECT(ctypes.Structure):
        _fields_ = [("l", ctypes.c_long), ("t", ctypes.c_long), ("r", ctypes.c_long), ("b", ctypes.c_long)]
    rc = RECT()
    ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rc), 0)
    return rc.r, rc.b


class Widget:
    def __init__(self):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            pass
        self.root = tk.Tk()
        global W, H
        self.s = s = self.root.winfo_fpixels("1i") / 96   # масштаб экрана Windows (200% -> 2.0)
        W, H = round(250 * s), round(92 * s)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=BG)
        right, bottom = work_area()
        self.root.geometry(f"{W}x{H}+{right - W - round(12 * s)}+{bottom - H - round(8 * s)}")

        self.c = tk.Canvas(self.root, width=W, height=H, bg=BG, highlightthickness=0)
        self.c.pack()
        self.c.bind("<ButtonPress-1>", self._start_drag)
        self.c.bind("<B1-Motion>", self._drag)
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Обновить", command=self.refresh)
        menu.add_command(label="Закрыть", command=self.root.destroy)
        self.c.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))

        self.draw_text("Claude · загрузка…")
        self._tick()
        self._keep_on_top()

    def _keep_on_top(self):
        """Развёрнутые окна иногда перекрывают topmost-окно Tk — раз в 5 с поднимаем себя снова."""
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id()) or self.root.winfo_id()
        # HWND_TOPMOST=-1, SWP_NOSIZE|SWP_NOMOVE|SWP_NOACTIVATE = 0x1|0x2|0x10
        ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x13)
        self.root.after(5000, self._keep_on_top)

    def _tick(self):
        self.refresh()
        self.root.after(REFRESH_MS, self._tick)

    def _start_drag(self, e):
        self._dx, self._dy = e.x, e.y

    def _drag(self, e):
        self.root.geometry(f"+{e.x_root - self._dx}+{e.y_root - self._dy}")

    def draw_text(self, msg):
        self.c.delete("all")
        self.c.create_text(12 * self.s, H // 2, text=msg, fill=MUTED, anchor="w", font=("Segoe UI", 9))

    def bar(self, y, label, p, reset):
        s = self.s   # координаты заданы для масштаба 100% и умножаются на масштаб экрана
        p = max(0, min(100, round(p)))
        self.c.create_text(12 * s, y * s, text=label, fill=FG, anchor="w", font=("Segoe UI Semibold", 9))
        self.c.create_text(W - 12 * s, y * s, text=f"{p}%  · сброс {reset}", fill=MUTED, anchor="e", font=("Segoe UI", 8))
        x0, x1, yb = 12 * s, W - 12 * s, (y + 12) * s
        self.c.create_rectangle(x0, yb, x1, yb + 5 * s, fill=TRACK, width=0)
        if p:
            self.c.create_rectangle(x0, yb, x0 + (x1 - x0) * p / 100, yb + 5 * s, fill=color(p), width=0)

    def show(self, d):
        self.c.delete("all")
        s, w = d.get("five_hour") or {}, d.get("seven_day") or {}
        self.bar(14, "Сессия 5 ч", s.get("utilization") or 0, when(s.get("resets_at"), False))
        self.bar(46, "Неделя", w.get("utilization") or 0, when(w.get("resets_at"), True))
        self.c.create_text(W - 12 * self.s, H - 9 * self.s, text=f"обновлено {datetime.now():%H:%M}",
                           fill=MUTED, anchor="e", font=("Segoe UI", 7))

    def refresh(self):
        def work():
            try:
                d = fetch()
                self.root.after(0, self.show, d)
            except Exception as e:  # сеть, файл, 401 — показываем текстом, не падаем
                msg = str(e) if isinstance(e, RuntimeError) else "нет связи — повторю позже"
                self.root.after(0, self.draw_text, f"Claude · {msg}")
        threading.Thread(target=work, daemon=True).start()


if __name__ == "__main__":
    Widget().root.mainloop()
