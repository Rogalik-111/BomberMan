import random
import tkinter as tk

from settings import (
    BG,
    BOMB_DELAY,
    COLS,
    EXIT_TILE,
    EXPLOSION_TIME,
    MAX_BOMBS,
    RADIUS,
    ROWS,
    TILE,
    WIDTH,
)
from Level import generate_level
from Walls import Wall
from Player import Player
from Enemy import Enemy
from Bomb import Bomb
from Explosion import Explosion
from Exit import Exit
from Bonus import Bonus
from menu import show_settings_overlay, PANEL_BG
from ui_widgets import create_styled_button, NAVY
from config import load_settings
from sound import sound_manager
from savegame import save_from_game, load_save, has_save, clear_save

LAST_LEVEL = 3


class Game:
    def __init__(self, root, canvas, hud_frame, continue_game=False):
        self.root = root
        self.canvas = canvas
        self.hud = hud_frame

        self.session_var = tk.IntVar(value=0)
        self.quit_app = False

        self.active = True
        self.cleaned_up = False
        self.scheduled_jobs = []
        self.hud_resize_job = None

        self.paused = False
        self.game_over = False
        self.leaving_to_menu = False

        settings = load_settings()
        self.difficulty = settings.get("difficulty", "Нормальный")
        if self.difficulty in ("Лёгкий", "Новичок"):
            self.level_time_sec = 180
            self.enemy_delay_ms = 700
        elif self.difficulty == "Сложный":
            self.level_time_sec = 90
            self.enemy_delay_ms = 300
        else:
            self.level_time_sec = 120
            self.enemy_delay_ms = 500

        self.walls = {}
        self.exit_obj = None
        self.exit_cell = None
        self.bombs = []
        self.bonuses = {}
        self.enemies = []

        if continue_game and has_save():
            self.load_from_save(load_save())
        else:
            self.level_num = 1
            self.score = 0
            self.time_left = self.level_time_sec
            self.grid = generate_level()
            self.max_bombs = MAX_BOMBS
            self.blast_radius = RADIUS
            self.redraw_field()
            self.player = Player(canvas)
            self.spawn_enemies(self.enemy_count_for_level(1))

        self.view_w = self.canvas.winfo_width() or WIDTH
        self.view_h = self.canvas.winfo_height() or HEIGHT
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.root.bind("<Configure>", self.on_root_resize, add="+")

        self.label_lives = tk.Label(self.hud, fg="white", bg=BG, font=("Arial", 12))
        self.label_time = tk.Label(self.hud, fg="white", bg=BG, font=("Arial", 12))
        self.label_level = tk.Label(self.hud, fg="white", bg=BG, font=("Arial", 12))
        self.label_score = tk.Label(self.hud, fg="white", bg=BG, font=("Arial", 12))
        for lb in (
            self.label_lives,
            self.label_time,
            self.label_level,
            self.label_score,
        ):
            lb.pack(side="left", padx=10)

        self.update_hud()
        self.resize_hud_fonts()

        root.bind("<Key>", self.on_key_press)
        root.bind("<Escape>", self.toggle_pause)

        self.schedule_after(self.enemy_delay_ms, self.tick_enemies)
        self.schedule_after(1000, self.tick_timer)
        self.scroll_to_player()

    def end_session(self):
        self.session_var.set(self.session_var.get() + 1)

    def schedule_after(self, ms, func):
        if not self.active:
            return

        def run():
            if self.active:
                func()

        job = self.root.after(ms, run)
        self.scheduled_jobs.append(job)

    def base_enemy_count(self):
        if self.difficulty in ("Новичок", "Лёгкий"):
            return 3
        if self.difficulty == "Сложный":
            return 6
        return 4

    def enemy_count_for_level(self, n):
        b = self.base_enemy_count()
        return max(1, int(round(b * (1.5 ** (n - 1)))))

    def spawn_cells(self, count):
        blocked = {(1, 1), (2, 1), (1, 2)}
        if self.exit_cell:
            blocked.add(self.exit_cell)
        free = []
        for y in range(ROWS):
            for x in range(COLS):
                if self.grid[y][x] == 0 and (x, y) not in blocked:
                    free.append((x, y))
        random.shuffle(free)
        return free[:count]

    def spawn_enemies(self, count):
        for x, y in self.spawn_cells(count):
            self.enemies.append(Enemy(self.canvas, x, y))

    def load_from_save(self, data):
        self.level_num = int(data["level_number"])
        self.score = int(data["score"])
        self.max_bombs = int(data["max_bombs"])
        self.blast_radius = int(data["radius"])
        self.time_left = int(data["time_left"])
        self.grid = [list(row) for row in data["level"]]
        px = int(data.get("player_x", 1))
        py = int(data.get("player_y", 1))
        self.redraw_field()
        self.player = Player(self.canvas, px, py, int(data["lives"]))
        for ex, ey in data.get("enemies", []):
            ex, ey = int(ex), int(ey)
            if 0 <= ex < COLS and 0 <= ey < ROWS and self.grid[ey][ex] == 0:
                self.enemies.append(Enemy(self.canvas, ex, ey))
        for b in data.get("bonuses", []):
            x, y, kind = int(b["x"]), int(b["y"]), b["kind"]
            if 0 <= x < COLS and 0 <= y < ROWS and self.grid[y][x] == 0:
                self.bonuses[(x, y)] = Bonus(self.canvas, x, y, kind)

    def cleanup(self):
        if self.cleaned_up:
            return
        self.cleaned_up = True
        self.active = False
        for job in self.scheduled_jobs:
            try:
                self.root.after_cancel(job)
            except tk.TclError:
                pass
        self.scheduled_jobs.clear()
        if self.hud_resize_job:
            try:
                self.root.after_cancel(self.hud_resize_job)
            except tk.TclError:
                pass
            self.hud_resize_job = None
        try:
            self.root.unbind("<Key>")
            self.root.unbind("<Escape>")
        except tk.TclError:
            pass

    def on_root_resize(self, event):
        if event.widget != self.root:
            return
        if self.hud_resize_job:
            try:
                self.root.after_cancel(self.hud_resize_job)
            except tk.TclError:
                pass
        self.hud_resize_job = self.root.after(100, self.resize_hud_fonts)

    def resize_hud_fonts(self):
        self.hud_resize_job = None
        if not self.active:
            return
        try:
            sw = max(self.root.winfo_width(), 400)
        except tk.TclError:
            return
        scale = max(0.7, min(sw / 1920.0, 1.6))
        size = max(9, int(12 * scale))
        font = ("Arial", size)
        for lb in (
            self.label_lives,
            self.label_time,
            self.label_level,
            self.label_score,
        ):
            try:
                lb.config(font=font)
            except tk.TclError:
                pass

    def update_hud(self):
        self.label_lives.config(text=f"Жизни: {self.player.lives}")
        self.label_time.config(text=f"Время: {self.time_left} c")
        self.label_level.config(text=f"Уровень: {self.level_num}")
        self.label_score.config(text=f"Очки: {self.score}")

    def redraw_field(self):
        for w in self.walls.values():
            w.destroy()
        self.walls.clear()
        if self.exit_obj:
            self.exit_obj.destroy()
            self.exit_obj = None
        self.exit_cell = None
        for y in range(ROWS):
            for x in range(COLS):
                cell = self.grid[y][x]
                if cell == 1:
                    self.walls[(x, y)] = Wall(
                        self.canvas, x * TILE, y * TILE, False
                    )
                elif cell == 2:
                    self.walls[(x, y)] = Wall(
                        self.canvas, x * TILE, y * TILE, True
                    )
                elif cell == EXIT_TILE:
                    self.exit_obj = Exit(self.canvas, x, y)
                    self.exit_cell = (x, y)

    def on_key_press(self, event):
        if not self.active or self.leaving_to_menu or self.paused or self.game_over:
            return
        g = self.grid
        if event.keysym == "Left":
            self.player.move(-1, 0, g)
        if event.keysym == "Right":
            self.player.move(1, 0, g)
        if event.keysym == "Up":
            self.player.move(0, -1, g)
        if event.keysym == "Down":
            self.player.move(0, 1, g)
        if event.keysym == "space":
            self.try_place_bomb()
        self.collect_bonus_here()
        self.update_hud()
        self.check_exit_or_win()
        self.scroll_to_player()

    def try_place_bomb(self):
        if (
            not self.active
            or self.leaving_to_menu
            or len(self.bombs) >= self.max_bombs
            or self.paused
            or self.game_over
        ):
            return
        bomb = Bomb(self.canvas, self.player.x, self.player.y)
        self.bombs.append(bomb)
        self.schedule_after(BOMB_DELAY, lambda b=bomb: self.fire_bomb(b))

    def fire_bomb(self, bomb):
        if self.active:
            self.do_explosion(bomb)

    def do_explosion(self, bomb):
        if not self.active or bomb not in self.bombs or self.game_over:
            return
        enemies_before = len(self.enemies)
        tiles = [(bomb.x, bomb.y)]
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            for i in range(1, self.blast_radius + 1):
                nx, ny = bomb.x + dx * i, bomb.y + dy * i
                if self.grid[ny][nx] == 1:
                    break
                tiles.append((nx, ny))
                if self.grid[ny][nx] == 2:
                    break
        explosion = Explosion(self.canvas, tiles)
        sound_manager.play_sound("explosion")
        for x, y in tiles:
            if self.grid[y][x] == 2:
                self.grid[y][x] = 0
                self.walls[(x, y)].destroy()
                del self.walls[(x, y)]
                self.score += 10
                self.maybe_drop_bonus(x, y)
            if self.player.x == x and self.player.y == y:
                self.player.hit()
                sound_manager.play_sound("hit")
                self.check_player_dead()
            for enemy in self.enemies[:]:
                if enemy.x == x and enemy.y == y:
                    enemy.destroy()
                    self.enemies.remove(enemy)
                    self.score += 100
        if enemies_before > 0 and len(self.enemies) == 0:
            sound_manager.play_sound("door")
        self.update_hud()
        self.schedule_after(EXPLOSION_TIME, lambda: self.clear_bomb_fx(explosion, bomb))

    def clear_bomb_fx(self, explosion, bomb):
        if not self.active:
            return
        explosion.destroy()
        if bomb in self.bombs:
            bomb.destroy()
            self.bombs.remove(bomb)

    def tick_enemies(self):
        if not self.active:
            return
        if not self.paused and not self.game_over:
            for enemy in self.enemies:
                enemy.move(self.grid)
                if enemy.x == self.player.x and enemy.y == self.player.y:
                    self.player.hit()
                    sound_manager.play_sound("hit")
                    self.check_player_dead()
            self.update_hud()
            self.check_exit_or_win()
        self.schedule_after(self.enemy_delay_ms, self.tick_enemies)

    def tick_timer(self):
        if not self.active:
            return
        if not self.paused and not self.game_over and self.time_left > 0:
            self.time_left -= 1
            self.update_hud()
        if self.time_left <= 0 and not self.game_over:
            self.time_left = 0
            self.update_hud()
            self.show_end_screen(False, "Время вышло")
        elif not self.game_over:
            self.schedule_after(1000, self.tick_timer)

    def toggle_pause(self, event=None):
        if not self.active or self.leaving_to_menu or self.game_over:
            return
        if self.paused:
            self.paused = False
            overlay = getattr(self, "pause_overlay", None)
            if overlay and overlay.winfo_exists():
                overlay.destroy()
        else:
            self.paused = True
            self.open_pause_menu()

    def overlay_scale(self):
        try:
            w = max(self.root.winfo_width(), 480)
            h = max(self.root.winfo_height(), 360)
        except tk.TclError:
            return 1.0
        return max(0.65, min(w / 1280.0, h / 720.0, 1.6))

    def open_pause_menu(self):
        sc = self.overlay_scale()
        self.pause_overlay = tk.Frame(self.root, bg=PANEL_BG, highlightthickness=0)
        self.pause_overlay.place(x=0, y=0, relwidth=1, relheight=1)
        self.pause_overlay.lift()
        box = tk.Frame(self.pause_overlay, bg=PANEL_BG)
        box.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(
            box,
            text="Пауза",
            font=("Segoe UI", max(18, int(28 * sc)), "bold"),
            fg=NAVY,
            bg=PANEL_BG,
        ).pack(pady=(0, int(24 * sc)))
        bw, bh = int(260 * sc), int(52 * sc)
        fs = max(11, int(17 * sc))
        create_styled_button(
            box, "Возобновить", self.toggle_pause, width=bw, height=bh, font_size=fs
        ).pack(pady=int(10 * sc))
        create_styled_button(
            box,
            "Настройки",
            lambda: show_settings_overlay(
                self.root,
                on_change=self.apply_volume_from_settings,
                apply_geometry=self.root.geometry,
            ),
            width=bw,
            height=bh,
            font_size=fs,
        ).pack(pady=int(10 * sc))
        create_styled_button(
            box,
            "Выход",
            self.return_to_main_menu,
            width=bw,
            height=bh,
            font_size=fs,
        ).pack(pady=int(10 * sc))

    def apply_volume_from_settings(self, st):
        sound_manager.set_volume(st.get("volume", 50) / 100)

    def return_to_main_menu(self):
        if self.leaving_to_menu:
            return
        self.leaving_to_menu = True
        try:
            save_from_game(self)
        except Exception:
            pass
        try:
            overlay = getattr(self, "pause_overlay", None)
            if overlay and overlay.winfo_exists():
                overlay.destroy()
            self.paused = False
            self.cleanup()
        finally:
            self.end_session()

    def maybe_drop_bonus(self, x, y):
        if (x, y) in self.bonuses:
            return
        if random.random() >= 0.1:
            return
        kinds = ["life"]
        if (self.max_bombs - MAX_BOMBS) < 3:
            kinds.append("bomb")
        if (self.blast_radius - RADIUS) < 3:
            kinds.append("radius")
        kind = random.choice(kinds)
        self.bonuses[(x, y)] = Bonus(self.canvas, x, y, kind)

    def collect_bonus_here(self):
        pos = (self.player.x, self.player.y)
        bonus = self.bonuses.pop(pos, None)
        if not bonus:
            return
        if bonus.kind == "bomb":
            self.max_bombs += 1
        elif bonus.kind == "radius":
            self.blast_radius += 1
        elif bonus.kind == "life":
            self.player.lives += 1
        self.score += 50
        bonus.destroy()
        sound_manager.play_sound("bonus")
        self.update_hud()

    def check_player_dead(self):
        if self.player.lives <= 0 and not self.game_over:
            self.show_end_screen(False, "Игрок потерял все жизни")

    def check_exit_or_win(self):
        if self.enemies:
            return
        if self.exit_cell and (self.player.x, self.player.y) == self.exit_cell:
            if self.level_num >= LAST_LEVEL:
                self.show_end_screen(True, "Все уровни пройдены")
            else:
                sound_manager.play_sound("next_level")
                self.level_num += 1
                self.load_next_level()
                self.scroll_to_player()

    def load_next_level(self):
        for w in self.walls.values():
            w.destroy()
        self.walls.clear()
        if self.exit_obj:
            self.exit_obj.destroy()
            self.exit_obj = None
        self.exit_cell = None
        for e in self.enemies:
            e.destroy()
        self.enemies.clear()
        for b in self.bombs:
            b.destroy()
        self.bombs.clear()
        self.grid = generate_level()
        self.redraw_field()
        self.player.reset_position()
        self.spawn_enemies(self.enemy_count_for_level(self.level_num))
        self.time_left = self.level_time_sec
        self.update_hud()

    def on_canvas_resize(self, event):
        self.view_w = event.width
        self.view_h = event.height
        self.scroll_to_player()

    def scroll_to_player(self):
        map_w, map_h = COLS * TILE, ROWS * TILE
        cx = self.player.x * TILE + TILE / 2
        cy = self.player.y * TILE + TILE / 2
        x0 = max(0, min(cx - self.view_w / 2, max(0, map_w - self.view_w)))
        y0 = max(0, min(cy - self.view_h / 2, max(0, map_h - self.view_h)))
        fx = x0 / (map_w - self.view_w) if map_w > self.view_w else 0.0
        fy = y0 / (map_h - self.view_h) if map_h > self.view_h else 0.0
        self.canvas.xview_moveto(fx)
        self.canvas.yview_moveto(fy)

    def show_end_screen(self, won, message):
        self.game_over = True
        self.paused = True
        overlay = getattr(self, "pause_overlay", None)
        if overlay and overlay.winfo_exists():
            overlay.destroy()
        sound_manager.play_sound("win" if won else "lose")
        sc = self.overlay_scale()
        end = tk.Frame(self.root, bg=PANEL_BG, highlightthickness=0)
        end.place(x=0, y=0, relwidth=1, relheight=1)
        end.lift()
        box = tk.Frame(end, bg=PANEL_BG)
        box.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(
            box,
            text="Победа!" if won else "Поражение",
            font=("Segoe UI", max(18, int(28 * sc)), "bold"),
            fg=NAVY,
            bg=PANEL_BG,
        ).pack(pady=(0, 12))
        tk.Label(
            box,
            text=message,
            font=("Segoe UI", max(10, int(11 * sc)), "bold"),
            fg=NAVY,
            bg=PANEL_BG,
        ).pack(pady=6)
        tk.Label(
            box,
            text=f"Уровень: {self.level_num}, Очки: {self.score}",
            font=("Segoe UI", max(10, int(11 * sc)), "bold"),
            fg=NAVY,
            bg=PANEL_BG,
        ).pack(pady=(0, 20))
        bw, bh = int(260 * sc), int(52 * sc)
        fs = max(11, int(17 * sc))

        def go_menu():
            if self.leaving_to_menu:
                return
            self.leaving_to_menu = True
            end.destroy()
            clear_save()
            self.cleanup()
            self.end_session()

        def quit_game():
            if self.leaving_to_menu:
                return
            self.leaving_to_menu = True
            end.destroy()
            clear_save()
            self.quit_app = True
            self.cleanup()
            self.end_session()

        create_styled_button(
            box, "Выход", go_menu, width=bw, height=bh, font_size=fs
        ).pack(pady=8)
        create_styled_button(
            box, "Выход из игры", quit_game, width=bw, height=bh, font_size=fs
        ).pack(pady=8)
