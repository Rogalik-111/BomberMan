import tkinter as tk

from tkinter import *

from config import load_settings, save_settings
from sprites import ASSETS_DIR
from sound import sound_manager
from savegame import has_save, clear_save
from ui_widgets import create_styled_button, style_menubutton_outline, NAVY, YELLOW

MENU_BG = "#050a12"
PANEL_BG = "#ffffff"

RESOLUTIONS = ("1280x720", "1600x900", "1920x1080")
DIFFICULTY_OPTIONS = ("Новичок", "Нормальный", "Сложный")
_LEGACY_DIFFICULTY = {"Лёгкий": "Новичок"}

REF_MENU_W = 1280
REF_MENU_H = 720


def _normalize_difficulty_ui(stored):
    return _LEGACY_DIFFICULTY.get(stored, stored)


def _menu_scale(w, h):
    return max(0.55, min(w / REF_MENU_W, h / REF_MENU_H, 1.85))


def show_settings_overlay(parent, on_change=None, on_close=None, apply_geometry=None):
    current = load_settings()
    res = current.get("resolution", "1920x1080")
    if res not in RESOLUTIONS:
        res = "1920x1080"
    diff = _normalize_difficulty_ui(current.get("difficulty", "Нормальный"))
    if diff not in DIFFICULTY_OPTIONS:
        diff = "Нормальный"

    res_var = tk.StringVar(value=res)
    diff_var = tk.StringVar(value=diff)

    overlay = tk.Frame(parent, bg=PANEL_BG, highlightthickness=0)
    overlay.place(x=0, y=0, relwidth=1, relheight=1)
    overlay.lift()
    overlay.focus_set()
    parent.update_idletasks()

    try:
        ow = max(parent.winfo_width(), overlay.winfo_width(), 520)
        oh = max(parent.winfo_height(), overlay.winfo_height(), 400)
    except tk.TclError:
        ow, oh = 700, 550
    sc = max(0.55, min(ow / 700.0, oh / 550.0, 1.7))

    inner = tk.Frame(overlay, bg=PANEL_BG)
    inner.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        inner,
        text="Настройки",
        font=("Segoe UI", max(16, int(28 * sc)), "bold"),
        fg=NAVY,
        bg=PANEL_BG,
    ).pack(pady=(0, int(16 * sc)))

    tk.Label(
        inner,
        text="Уровень громкости",
        font=("Segoe UI", max(9, int(11 * sc)), "bold"),
        fg="#111111",
        bg=PANEL_BG,
    ).pack(anchor="w", pady=(8, 4))

    vol = tk.Scale(
        inner,
        from_=0,
        to=100,
        orient=tk.HORIZONTAL,
        length=int(340 * sc),
        showvalue=True,
        troughcolor=NAVY,
        bg=PANEL_BG,
        fg=NAVY,
        highlightthickness=0,
        bd=0,
        activebackground=YELLOW,
    )
    vol.set(int(current.get("volume", 50)))
    vol.pack(pady=(0, int(12 * sc)))

    tk.Label(
        inner,
        text="Разрешение экрана",
        font=("Segoe UI", max(9, int(11 * sc)), "bold"),
        fg="#111111",
        bg=PANEL_BG,
    ).pack(anchor="w", pady=(6, 4))

    mb_res = tk.Menubutton(
        inner,
        textvariable=res_var,
        font=("Segoe UI", max(11, int(17 * sc)), "bold"),
        fg=YELLOW,
        bg=NAVY,
        activeforeground=YELLOW,
        activebackground="#152a40",
        bd=0,
        indicatoron=True,
        width=max(18, int(17 * sc)),
        pady=int(10 * sc),
    )
    menu_r = tk.Menu(
        mb_res,
        tearoff=0,
        bg=NAVY,
        fg=YELLOW,
        activebackground="#152a40",
        activeforeground=YELLOW,
        font=("Segoe UI", max(9, int(11 * sc)), "bold"),
    )
    for v in RESOLUTIONS:
        menu_r.add_command(label=v, command=lambda val=v: res_var.set(val))
    mb_res["menu"] = menu_r
    style_menubutton_outline(mb_res)
    mb_res.pack(pady=(0, int(10 * sc)))

    tk.Label(
        inner,
        text="Уровень сложности",
        font=("Segoe UI", max(9, int(11 * sc)), "bold"),
        fg="#111111",
        bg=PANEL_BG,
    ).pack(anchor="w", pady=(6, 4))

    mb_d = tk.Menubutton(
        inner,
        textvariable=diff_var,
        font=("Segoe UI", max(11, int(17 * sc)), "bold"),
        fg=YELLOW,
        bg=NAVY,
        activeforeground=YELLOW,
        activebackground="#152a40",
        bd=0,
        indicatoron=True,
        width=max(18, int(17 * sc)),
        pady=int(10 * sc),
    )
    menu_d = tk.Menu(
        mb_d,
        tearoff=0,
        bg=NAVY,
        fg=YELLOW,
        activebackground="#152a40",
        activeforeground=YELLOW,
        font=("Segoe UI", max(9, int(11 * sc)), "bold"),
    )
    for v in DIFFICULTY_OPTIONS:
        menu_d.add_command(label=v, command=lambda val=v: diff_var.set(val))
    mb_d["menu"] = menu_d
    style_menubutton_outline(mb_d)
    mb_d.pack(pady=(0, int(16 * sc)))

    def save_and_close():
        new_settings = {
            "volume": int(vol.get()),
            "resolution": res_var.get(),
            "difficulty": diff_var.get(),
        }
        save_settings(new_settings)
        sound_manager.set_volume(new_settings["volume"] / 100)
        if apply_geometry:
            apply_geometry(new_settings["resolution"])
        if on_change:
            on_change(new_settings)
        overlay.destroy()
        if on_close:
            on_close()

    def discard(_event=None):
        if overlay.winfo_exists():
            overlay.destroy()
        if on_close:
            on_close()

    bw = int(370 * sc)
    bh = int(52 * sc)
    fs = max(11, int(17 * sc))
    create_styled_button(
        inner,
        "Сохранить",
        save_and_close,
        width=bw,
        height=bh,
        font_size=fs,
    ).pack(pady=6)

    overlay.bind("<Escape>", discard)

    parent.wait_window(overlay)


def show_menu(root):
    result = {"v": "quit"}
    frame = tk.Frame(root, bg=MENU_BG)
    frame.pack(fill="both", expand=True)

    c = tk.Canvas(frame, highlightthickness=0, bd=0, bg=MENU_BG)
    c.pack(fill="both", expand=True)

    photo_holder = [None]
    win_items = []

    layout_timer = [None]

    def do_layout(_event=None):
        if layout_timer[0]:
            try:
                root.after_cancel(layout_timer[0])
            except tk.TclError:
                pass
        layout_timer[0] = root.after(70, layout_buttons)

    def layout_buttons():
        layout_timer[0] = None
        w = max(c.winfo_width(), 2)
        h = max(c.winfo_height(), 2)
        sc = _menu_scale(w, h)

        c.delete("all")
        for wid in win_items:
            try:
                c.delete(wid)
            except tk.TclError:
                pass
        win_items.clear()

        path = ASSETS_DIR / "MenuBack.png"
        if path.exists():
            try:
                photo_holder[0] = PhotoImage(file = f"{path}", master=root)
                c.create_image(w // 2, h // 2, image=photo_holder[0])
            except OSError:
                c.create_rectangle(0, 0, w, h, fill=MENU_BG, outline="")
                c.create_text(
                    int(32 * sc),
                    int(40 * sc),
                    text="BOMBERMAN",
                    anchor="nw",
                    fill=YELLOW,
                    font=("Segoe UI", max(20, int(32 * sc)), "bold"),
                )

        bw = int(280 * sc)
        bh = int(64 * sc)
        fs = max(11, int(17 * sc))
        gap = int(14 * sc)
        n = 4
        total_h = n * bh + (n - 1) * gap
        y0 = (h - total_h) / 2 - 32
        x0 = int(256 * sc)

        def add_window(btn_widget, yi):
            iid = c.create_window(x0, yi, window=btn_widget, anchor="nw")
            win_items.append(iid)

        def on_continue():
            if not has_save():
                return
            result["v"] = "continue"
            frame.destroy()

        def on_new():
            clear_save()
            result["v"] = "new"
            frame.destroy()

        def open_settings():
            show_settings_overlay(root, apply_geometry=root.geometry)

        y = y0
        cont = create_styled_button(
            frame,
            "Продолжить",
            on_continue,
            width=bw,
            height=bh,
            font_size=fs,
            state=tk.NORMAL if has_save() else tk.DISABLED,
        )
        add_window(cont, y)
        y += bh + gap

        new_b = create_styled_button(
            frame,
            "Новая игра",
            on_new,
            width=bw,
            height=bh,
            font_size=fs,
        )
        add_window(new_b, y)
        y += bh + gap

        set_b = create_styled_button(
            frame,
            "Настройки",
            open_settings,
            width=bw,
            height=bh,
            font_size=fs,
        )
        add_window(set_b, y)
        y += bh + gap

        ex_b = create_styled_button(
            frame,
            "Выход",
            root.destroy,
            width=bw,
            height=bh,
            font_size=fs,
        )
        add_window(ex_b, y)

    c.bind("<Configure>", do_layout)
    root.after_idle(do_layout)

    old_close = root.protocol("WM_DELETE_WINDOW")

    def on_user_close():
        result["v"] = "quit"
        frame.destroy()

    root.protocol("WM_DELETE_WINDOW", on_user_close)

    try:
        root.wait_window(frame)
    finally:
        try:
            root.protocol("WM_DELETE_WINDOW", old_close)
        except tk.TclError:
            pass

    return result["v"]
