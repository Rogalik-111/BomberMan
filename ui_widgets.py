import tkinter as tk

from sound import sound_manager

NAVY = "#0d1b2a"
YELLOW = "#f5e000"
DISABLED_FG = "#666666"
DISABLED_FILL = "#2a3544"
DISABLED_OUTLINE = "#777777"


def rounded_rect_points(width, height, corner):
    corner = min(corner, width // 4, height // 4, 20)
    return (
        corner,
        0,
        width - corner,
        0,
        width,
        0,
        width,
        corner,
        width,
        height - corner,
        width,
        height,
        width - corner,
        height,
        corner,
        height,
        0,
        height,
        0,
        height - corner,
        0,
        corner,
        0,
        0,
        corner,
        0,
    )


def create_styled_button(
    parent,
    text,
    command,
    font_family="Segoe UI",
    font_size=17,
    font_weight="bold",
    width=260,
    height=52,
    state=tk.NORMAL,
    corner_radius=14,
    outline_width=3,
    canvas_bg=None,
):
    try:
        if canvas_bg is None:
            canvas_bg = parent.cget("bg")
    except tk.TclError:
        canvas_bg = NAVY

    canvas = tk.Canvas(
        parent,
        width=width,
        height=height,
        highlightthickness=0,
        bd=0,
        bg=canvas_bg,
        cursor="hand2" if state == tk.NORMAL else "arrow",
    )

    pts = rounded_rect_points(width, height, corner_radius)
    fill = NAVY
    outline = YELLOW
    fg = YELLOW
    if state == tk.DISABLED:
        fill = DISABLED_FILL
        outline = DISABLED_OUTLINE
        fg = DISABLED_FG
        canvas.config(cursor="arrow")

    tag = "btn"
    canvas.create_polygon(
        pts,
        fill=fill,
        outline=outline,
        width=outline_width,
        smooth=True,
        tags=tag,
    )
    canvas.create_text(
        width // 2,
        height // 2,
        text=text,
        fill=fg,
        font=(font_family, font_size, font_weight),
        tags=tag,
    )

    def on_click(event=None):
        if state == tk.DISABLED:
            return
        try:
            sound_manager.play_sound("button")
        except Exception:
            pass
        command()

    canvas.tag_bind(tag, "<Button-1>", on_click)
    canvas.tag_bind(
        tag,
        "<Enter>",
        lambda e: canvas.config(
            cursor="hand2" if state == tk.NORMAL else "arrow"
        ),
    )
    canvas.tag_bind(tag, "<Leave>", lambda e: canvas.config(cursor=""))

    return canvas


def style_menubutton_outline(menubutton, outline_width=3):
    menubutton.config(
        highlightbackground=YELLOW,
        highlightcolor=YELLOW,
        highlightthickness=outline_width,
    )
