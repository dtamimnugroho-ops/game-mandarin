import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
from collections import deque

# ======================================
#           DATA LEVEL SOAL
# ======================================

LEVEL_1 = [
    {"hanzi": "我", "pinyin": "wǒ", "arti": "saya"},
    {"hanzi": "你", "pinyin": "nǐ", "arti": "kamu"},
    {"hanzi": "他", "pinyin": "tā", "arti": "dia (laki-laki)"},
    {"hanzi": "水", "pinyin": "shuǐ", "arti": "air"},
    {"hanzi": "火", "pinyin": "huǒ", "arti": "api"}
]

LEVEL_2 = [
    {"hanzi": "你好", "pinyin": "nǐ hǎo", "arti": "halo"},
    {"hanzi": "谢谢", "pinyin": "xièxie", "arti": "terima kasih"},
    {"hanzi": "朋友", "pinyin": "péngyǒu", "arti": "teman"},
    {"hanzi": "老师", "pinyin": "lǎoshī", "arti": "guru"},
    {"hanzi": "学生", "pinyin": "xuéshēng", "arti": "murid"}
]

LEVEL_3 = [
    {"hanzi": "你好吗？", "pinyin": "nǐ hǎo ma?", "arti": "apa kabar?"},
    {"hanzi": "我喜欢吃饭。", "pinyin": "wǒ xǐhuān chīfàn.", "arti": "saya suka makan."},
    {"hanzi": "她是老师。", "pinyin": "tā shì lǎoshī.", "arti": "dia adalah guru."},
    {"hanzi": "我们是朋友。", "pinyin": "wǒmen shì péngyǒu.", "arti": "kita teman."},
    {"hanzi": "他在学习中文。", "pinyin": "tā zài xuéxí zhōngwén.", "arti": "dia sedang belajar Mandarin."}
]

# ======================================
#        NEON THEME (A2: MAGENTA)
# ======================================
BG_COLOR = "#000010"            # background (near black)
PANEL_BG = "#0B0B16"           # panel dirty black-blue
NEON_COLOR = "#FF00CC"         # magenta neon
NEON_LIGHT = "#FF66D9"         # lighter magenta for glow/hover
TEXT_COLOR = "#EAE6FF"         # pale text

# Neon button helper (tk.Button with hover)
class NeonButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        self.base_bg = kwargs.pop("bg", PANEL_BG)
        self.fg = kwargs.pop("fg", TEXT_COLOR)
        self.border = kwargs.pop("bd", 0)
        super().__init__(master, bg=self.base_bg, fg=self.fg, bd=self.border, activebackground=self.base_bg, **kwargs)
        self.default_bg = self.base_bg
        self.neon = NEON_COLOR
        self.neon_light = NEON_LIGHT
        self.configure(relief="flat", highlightthickness=0, padx=12, pady=6, font=("Segoe UI", 10, "bold"))
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        try:
            self.configure(bg=self.neon_light, fg="black")
        except Exception:
            pass

    def on_leave(self, e):
        try:
            self.configure(bg=self.default_bg, fg=self.fg)
        except Exception:
            pass

# ======================================
#           GAME MANDARIN (Adaptive)
# ======================================
class GameMandarin:
    def __init__(self, root):
        self.root = root
        self.root.title("Mandarin — Neon TRON (A2) — Adaptive")
        self.root.configure(bg=BG_COLOR)
        # session state
        self.skor = 0
        self.level = 1
        self.soal_ke = 0
        self.xp = 0

        self.timer = 15
        self.running_timer = False

        # adaptive: recent results (True/False)
        self.recent_results = deque(maxlen=5)  # track last up to 5 answers
        # pool for the session
        self.soal_pool = []

        # style for progressbar
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Neon.Horizontal.TProgressbar", troughcolor="#071024", background=NEON_COLOR, thickness=12)

        self.frame_awal()

    # ------------------------
    # helpers
    # ------------------------
    def clear(self):
        self.running_timer = False
        for w in self.root.winfo_children():
            w.destroy()

    def center_panel_place(self, panel, w=540, h=520):
        panel.place(relx=0.5, rely=0.5, anchor="center", width=w, height=h)

    # ------------------------
    # initial screen (menu)
    # ------------------------
    def frame_awal(self):
        self.clear()

        # shadow / glow layers (3 layers for neon effect)
        shadow_outer = tk.Frame(self.root, bg="#220018")
        self.center_panel_place(shadow_outer, w=580, h=560)
        shadow_mid = tk.Frame(self.root, bg="#2a0022")
        self.center_panel_place(shadow_mid, w=560, h=540)
        panel = tk.Frame(self.root, bg=PANEL_BG, bd=0)
        self.center_panel_place(panel, w=540, h=520)

        # title
        title = tk.Label(panel, text="⭑ MANDARIN TRON — ADAPTIVE", bg=PANEL_BG, fg=NEON_LIGHT,
                         font=("Orbitron", 20, "bold"))
        title.pack(pady=(24,6))

        subtitle = tk.Label(panel, text="Adaptive Learning — AI menyesuaikan soal untukmu",
                            bg=PANEL_BG, fg=TEXT_COLOR, font=("Segoe UI", 10))
        subtitle.pack(pady=(0,12))

        # name entry
        lbl_name = tk.Label(panel, text="Masukkan Nama", bg=PANEL_BG, fg=TEXT_COLOR, font=("Segoe UI", 10))
        lbl_name.pack(pady=(6,2))
        self.entry_name = tk.Entry(panel, bg="#08080b", fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                                   relief="flat", font=("Segoe UI", 11))
        self.entry_name.pack(ipadx=60, ipady=6)

        # level selection (start preference)
        lbl_lvl = tk.Label(panel, text="Pilih Level Awal (opsional)", bg=PANEL_BG, fg=TEXT_COLOR, font=("Segoe UI", 10))
        lbl_lvl.pack(pady=(12,4))
        self.level_var = tk.IntVar(value=1)
        lvl_frame = tk.Frame(panel, bg=PANEL_BG)
        lvl_frame.pack()
        for v, txt in [(1, "Level 1 — Huruf"), (2, "Level 2 — Kata"), (3, "Level 3 — Kalimat")]:
            rb = tk.Radiobutton(lvl_frame, text=txt, variable=self.level_var, value=v,
                                bg=PANEL_BG, fg=NEON_COLOR, selectcolor="#081018",
                                activeforeground=NEON_LIGHT, font=("Segoe UI", 10), relief="flat", indicatoron=0,
                                padx=8, pady=6)
            rb.pack(side="left", padx=6)

        # start button
        btn_start = NeonButton(panel, text="MULAI", command=self.start_from_menu)
        btn_start.pack(pady=(18,6))

        info = tk.Label(panel, text="AI akan menyesuaikan level berdasarkan 5 jawaban terakhir.",
                        bg=PANEL_BG, fg="#9a8aa8", font=("Segoe UI", 9))
        info.pack(side="bottom", pady=12)

    def start_from_menu(self):
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showwarning("Nama kosong", "Masukkan namamu dulu.")
            return
        self.player_name = name
        self.level = int(self.level_var.get())
        # reset adaptives
        self.recent_results.clear()
        self.prepare_question_pool()
        self.soal_ke = 0
        self.skor = 0
        self.xp = 0
        self.tampilkan_soal()

    # ------------------------
    # adaptive pool creation
    # ------------------------
    def prepare_question_pool(self):
        """
        Build a pool of unique questions for the session (5 items).
        Pool is adaptive: majority from current level, a few from neighbors for variety.
        """
        # map levels to data
        level_map = {1: LEVEL_1.copy(), 2: LEVEL_2.copy(), 3: LEVEL_3.copy()}

        # weights: current level gets heavier weight
        # we'll collect candidates with duplication allowed, then sample unique
        candidates = []

        # add many copies of current level items to increase chance
        curr = level_map[self.level]
        candidates += curr * 4  # amplify

        # add some neighbors
        if self.level - 1 in level_map:
            candidates += level_map[self.level - 1] * 1
        if self.level + 1 in level_map:
            candidates += level_map[self.level + 1] * 1

        # fallback: if candidates too small, combine all
        if not candidates:
            candidates = LEVEL_1 + LEVEL_2 + LEVEL_3

        # now pick unique questions up to 5
        unique = []
        attempts = 0
        while len(unique) < 5 and attempts < 200:
            q = random.choice(candidates)
            if q not in unique:
                unique.append(q)
            attempts += 1

        # if still fewer (rare), fill from current level list without duplication
        if len(unique) < 5:
            pool = self.ambil_level().copy()
            random.shuffle(pool)
            for it in pool:
                if it not in unique:
                    unique.append(it)
                    if len(unique) >= 5:
                        break

        self.soal_pool = unique

    def ambil_level(self):
        return {1: LEVEL_1, 2: LEVEL_2, 3: LEVEL_3}[self.level]

    # ------------------------
    # display question
    # ------------------------
    def tampilkan_soal(self):
        self.clear()
        # neon panels background layers
        shadow_outer = tk.Frame(self.root, bg="#220018")
        self.center_panel_place(shadow_outer, w=660, h=600)
        shadow_mid = tk.Frame(self.root, bg="#2a0022")
        self.center_panel_place(shadow_mid, w=640, h=580)
        panel = tk.Frame(self.root, bg=PANEL_BG)
        self.center_panel_place(panel, w=620, h=560)

        # update question index and check finish
        self.soal_ke += 1
        if not self.soal_pool or self.soal_ke > len(self.soal_pool):
            self.tampilkan_hasil()
            return

        q = self.soal_pool[self.soal_ke - 1]

        # header: show adaptive status (recent accuracy)
        acc = self.compute_recent_accuracy()
        hdr_text = f"Soal {self.soal_ke}/{len(self.soal_pool)}  •  Adaptive Level: {self.level}  •  Acc: {acc:.0%}"
        hdr = tk.Label(panel, text=hdr_text, bg=PANEL_BG, fg=NEON_LIGHT, font=("Segoe UI", 11, "bold"))
        hdr.pack(pady=(14,6))

        # hanzi display
        hanzi = tk.Label(panel, text=q["hanzi"], bg=PANEL_BG, fg=NEON_COLOR, font=("Orbitron", 56, "bold"))
        hanzi.pack(pady=(6,4))
        pinyin = tk.Label(panel, text=q["pinyin"], bg=PANEL_BG, fg=TEXT_COLOR, font=("Segoe UI", 12, "italic"))
        pinyin.pack(pady=(0,10))

        # build choices
        self.var_jawab = tk.StringVar()
        choices_frame = tk.Frame(panel, bg=PANEL_BG)
        choices_frame.pack(pady=(6,8))

        pilihan = [q["arti"]]
        pool = self.ambil_level().copy()
        other_artis = [it["arti"] for it in pool if it["arti"] not in pilihan]
        random.shuffle(other_artis)
        while len(pilihan) < 3 and other_artis:
            pilihan.append(other_artis.pop())
        random.shuffle(pilihan)

        for opt in pilihan:
            btn = tk.Radiobutton(choices_frame, text=opt, variable=self.var_jawab, value=opt,
                                 bg="#061018", fg=NEON_COLOR, selectcolor="#081018",
                                 activeforeground=NEON_LIGHT, activebackground="#061018",
                                 font=("Segoe UI", 11), indicatoron=0, width=36, padx=6, pady=8, relief="flat")
            btn.pack(pady=6)

        # xp bar
        self.xp_bar = ttk.Progressbar(panel, style="Neon.Horizontal.TProgressbar", length=420, maximum=100)
        self.xp_bar.pack(pady=(12,6))
        self.xp_bar['value'] = max(0, min(self.xp, 100))

        # controls
        ctl_frame = tk.Frame(panel, bg=PANEL_BG)
        ctl_frame.pack(pady=(6,16))
        self.label_timer = tk.Label(ctl_frame, text="", bg=PANEL_BG, fg=NEON_LIGHT, font=("Segoe UI", 11))
        self.label_timer.grid(row=0, column=0, padx=8)
        submit = NeonButton(ctl_frame, text="Kirim Jawaban", command=self.periksa_jawaban)
        submit.grid(row=0, column=1, padx=8)

        # animate + start timer
        self.animate_slide(panel)
        self.start_timer()

    # ------------------------
    # timer
    # ------------------------
    def start_timer(self):
        self.running_timer = True
        self.timer = 15
        self.update_timer()

    def update_timer(self):
        if not self.running_timer:
            return
        try:
            self.label_timer.config(text=f"⏳ {self.timer} detik")
        except Exception:
            pass
        if self.timer <= 0:
            self.running_timer = False
            messagebox.showerror("Waktu Habis", "Kamu kehabisan waktu!")
            self.periksa_jawaban(timeout=True)
            return
        self.timer -= 1
        self.root.after(1000, self.update_timer)

    # ------------------------
    # compute recent accuracy
    # ------------------------
    def compute_recent_accuracy(self):
        if not self.recent_results:
            return 0.0
        return sum(1 for x in self.recent_results if x) / len(self.recent_results)

    # ------------------------
    # check answer and adapt
    # ------------------------
    def periksa_jawaban(self, timeout=False):
        self.running_timer = False
        if timeout:
            benar = False
        else:
            sel = self.var_jawab.get() if hasattr(self, "var_jawab") else ""
            benar = (sel == self.soal_pool[self.soal_ke - 1]["arti"])

        # record result
        self.recent_results.append(bool(benar))

        if benar:
            self.skor += 1
            self.xp += 15
            messagebox.showinfo("Benar", "Jawaban benar! 🎉")
        else:
            self.xp = max(0, self.xp - 5)
            correct = self.soal_pool[self.soal_ke - 1]["arti"]
            messagebox.showerror("Salah", f"Jawaban benar: {correct}")

        # check adaptive leveling rules
        self.adaptive_adjustment()

        # if level changed during adjustment, pool might be refreshed and soal_ke reset; handle inside
        # otherwise continue to next question
        # proceed to next question only if not already redirected
        if self.soal_ke <= len(self.soal_pool):
            self.tampilkan_soal()

    def adaptive_adjustment(self):
        """
        Decide whether to change level based on recent accuracy.
        Rules:
         - if recent accuracy >= 0.8 and level < 3 -> level up
         - if recent accuracy <= 0.4 and level > 1 -> level down
        After change, refresh pool and reset question counter to start new pool.
        """
        acc = self.compute_recent_accuracy()
        leveled = False
        if len(self.recent_results) >= 3:  # require at least 3 answers to start adapting
            if acc >= 0.8 and self.level < 3:
                self.level += 1
                leveled = True
                messagebox.showinfo("Adaptive AI", f"AI menilai kamu siap naik ke Level {self.level}!")
            elif acc <= 0.4 and self.level > 1:
                self.level -= 1
                leveled = True
                messagebox.showinfo("Adaptive AI", f"AI menilai kamu perlu turunkan ke Level {self.level} untuk latihan lebih baik.")

        if leveled:
            # refresh pool and reset counters for new pool
            self.prepare_question_pool()
            self.soal_ke = 0
            # do not clear recent_results (keep some memory), but you may optionally clear
            # self.recent_results.clear()

    # ------------------------
    # results
    # ------------------------
    def tampilkan_hasil(self):
        self.clear()
        # neon panels
        shadow_outer = tk.Frame(self.root, bg="#220018")
        self.center_panel_place(shadow_outer, w=660, h=560)
        shadow_mid = tk.Frame(self.root, bg="#2a0022")
        self.center_panel_place(shadow_mid, w=640, h=540)
        panel = tk.Frame(self.root, bg=PANEL_BG)
        self.center_panel_place(panel, w=620, h=520)

        lbl = tk.Label(panel, text="HASIL AKHIR", bg=PANEL_BG, fg=NEON_LIGHT, font=("Orbitron", 20, "bold"))
        lbl.pack(pady=(24,6))
        tk.Label(panel, text=f"Nama: {getattr(self, 'player_name', 'Guest')}", bg=PANEL_BG, fg=TEXT_COLOR,
                 font=("Segoe UI", 11)).pack()
        tk.Label(panel, text=f"Skor: {self.skor}/{len(self.soal_pool)}", bg=PANEL_BG, fg=TEXT_COLOR,
                 font=("Segoe UI", 14, "bold")).pack(pady=(8,8))

        ach = tk.Label(panel, text="Achievement:", bg=PANEL_BG, fg=NEON_COLOR, font=("Segoe UI", 10, "bold"))
        ach.pack(pady=(8,2))
        tk.Label(panel, text=self.cek_achievement(), bg=PANEL_BG, fg=TEXT_COLOR, font=("Segoe UI", 10)).pack()

        NeonButton(panel, text="Main Lagi", command=self.frame_awal).pack(pady=(18,6))
        NeonButton(panel, text="Keluar", command=self.root.quit).pack()

        # confetti
        self.confetti(panel)

    def cek_achievement(self):
        res = []
        if self.skor == len(self.soal_pool) and self.skor > 0:
            res.append("🏆 Semua Jawaban Benar!")
        if self.xp >= 50:
            res.append("🎖 Pengumpul XP")
        if self.level == 3:
            res.append("🌟 Level Maksimum")
        return "\n".join(res) if res else "Tidak ada achievement."

    # ------------------------
    # small animation helpers
    # ------------------------
    def animate_slide(self, frame):
        for i in range(10):
            frame.update()
            time.sleep(0.01)

    def confetti(self, frame):
        for _ in range(36):
            c = tk.Label(frame, text="✦", fg=random.choice([NEON_COLOR, NEON_LIGHT, "#9A4FFF", "#FF66D9"]),
                         bg=PANEL_BG, font=("Segoe UI", 12, "bold"))
            x = random.randint(20, 560)
            y = random.randint(40, 380)
            c.place(x=x, y=y)
            c.after(700 + random.randint(0, 400), c.destroy)

# ======================================
#                MAIN
# ======================================
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("980x720")
    GameMandarin(root)
    root.mainloop()
