import tkinter as tk
from tkinter import ttk, messagebox
import csv, os, time

# ══════════════════════════════════════════════════════════════════════════════
#  COLOUR PALETTE
# ══════════════════════════════════════════════════════════════════════════════
BG       = "#0B132B"
CARD     = "#1C2541"
TEAL     = "#00B4D8"
WHITE    = "#FFFFFF"
MUTED    = "#A5AEC0"
FIELD_BG = "#1A2E4A"
BORDER   = "#2A4A6A"
ACCENT2  = "#0096B7"
SIDEBAR  = "#111D35"
ACCENT_BLUE = "#3B82F6"

# ══════════════════════════════════════════════════════════════════════════════
#  CSV / AUTH HELPERS
# ══════════════════════════════════════════════════════════════════════════════
DB = "login.csv"

def setup_db():
    if os.path.exists(DB):
        return
    with open(DB, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["username", "password", "display_name"])
        writer.writeheader()
        writer.writerow({"username": "kevin", "password": "The best", "display_name": "Kevin"})

def check_logins(user, pw):
    try:
        with open(DB, newline="") as f:
            for row in csv.DictReader(f):
                if row["username"].strip() == user and row["password"].strip() == pw:
                    return row.get("display_name", user)
    except FileNotFoundError:
        messagebox.showerror("Oops", "Login database is missing.")
    return None

def save_new_user(name, user, pw):
    with open(DB, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=["username", "password", "display_name"]).writerow(
            {"username": user, "password": pw, "display_name": name}
        )

# ══════════════════════════════════════════════════════════════════════════════
#  SHARED FIELD BUILDER (for Login / Register)
# ══════════════════════════════════════════════════════════════════════════════
def expected_entry(parent, label, hidden=False):
    tk.Label(parent, text=label, font=("Arial", 9), fg=MUTED, bg=CARD).pack(anchor="w", pady=(12, 2))
    e = tk.Entry(parent, font=("Arial", 11), bg=FIELD_BG, fg=WHITE, insertbackground=WHITE,
                 relief="flat", bd=0, highlightthickness=1,
                 highlightbackground=BORDER, highlightcolor=TEAL)
    if hidden:
        e.config(show="*")
    e.pack(fill="x", ipady=7)
    return e

def build_card(win, height):
    f = tk.Frame(win, bg=CARD, bd=0, highlightthickness=1, highlightbackground=BORDER)
    f.place(relx=0.5, rely=0.5, anchor="center", width=370, height=height)
    return f

# ══════════════════════════════════════════════════════════════════════════════
#  SPLASH / LOADING SCREEN
# ══════════════════════════════════════════════════════════════════════════════
class SplashScreen:
    def __init__(self, root, on_done):
        self.root = root
        self.on_done = on_done
        self.root.title("PeerSphere")
        self.root.geometry("700x400")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.geometry(f"700x400+{(sw-700)//2}+{(sh-400)//2}")

        tk.Label(root, text="PeerSphere", bg=BG, fg=WHITE,
                 font=("Georgia", 28, "bold")).pack(pady=(110, 8))
        tk.Label(root, text="Connecting students everywhere", bg=BG, fg=MUTED,
                 font=("Arial", 12)).pack(pady=(0, 36))

        self.bar = ttk.Progressbar(root, orient="horizontal", length=340)
        self.bar.pack()
        root.after(500, self._tick)

    def _tick(self, val=0):
        if val <= 100:
            self.bar["value"] = val
            self.root.after(10, self._tick, val + 1)
        else:
            self.on_done()

# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class LoginWindow:
    def __init__(self, root, on_success):
        """
        root       – the hidden Tk root (we reuse it).
        on_success – callable(display_name, username) → launches the main app.
        """
        self.root = root
        self.on_success = on_success

        self.win = tk.Toplevel(root)
        self.win.title("PeerSphere")
        self.win.geometry("900x600")
        self.win.configure(bg=BG)
        self.win.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self._build()

    def _build(self):
        card = build_card(self.win, 415)
        body = tk.Frame(card, bg=CARD)
        body.pack(fill="both", expand=True, padx=34, pady=28)

        top = tk.Frame(body, bg=CARD)
        top.pack()
        tk.Label(top, text="❖ ", font=("Georgia", 20), fg=TEAL, bg=CARD).pack(side="left")

        info = tk.Frame(top, bg=CARD)
        info.pack(side="left")
        tk.Label(info, text="PeerSphere",       font=("Georgia", 17, "bold"), fg=WHITE, bg=CARD).pack(anchor="w")
        tk.Label(info, text="Connecting students worldwide", font=("Arial", 8), fg=MUTED, bg=CARD).pack(anchor="w")

        self.u_entry = expected_entry(body, "Username")
        self.p_entry = expected_entry(body, "Password", hidden=True)

        tk.Button(body, text="Log in  →", font=("Arial", 11, "bold"),
                  bg=TEAL, fg=WHITE, activebackground="#0096B7",
                  relief="flat", cursor="hand2",
                  command=self._try_login).pack(fill="x", pady=(20, 0), ipady=9)

        row = tk.Frame(body, bg=CARD)
        row.pack(pady=(11, 0))
        tk.Label(row, text="New here?  ", font=("Arial", 9), fg=MUTED, bg=CARD).pack(side="left")
        link = tk.Label(row, text="Create an account",
                        font=("Arial", 9, "underline"), fg=TEAL, bg=CARD, cursor="hand2")
        link.pack(side="left")
        link.bind("<Button-1>", lambda e: (self.win.withdraw(), RegisterWindow(self.win, self.on_success)))

    def _try_login(self):
        u = self.u_entry.get().strip()
        p = self.p_entry.get().strip()
        if not u or not p:
            messagebox.showwarning("Hold on", "Both fields are required.", parent=self.win)
            return
        display_name = check_logins(u, p)
        if display_name:
            self.win.destroy()
            self.on_success(display_name, u)
        else:
            messagebox.showerror("Login failed", "Invalid username or password.", parent=self.win)

# ══════════════════════════════════════════════════════════════════════════════
#  REGISTER WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class RegisterWindow:
    def __init__(self, login_win, on_success):
        self.login_win  = login_win
        self.on_success = on_success

        self.win = tk.Toplevel()
        self.win.title("PeerSphere — Sign Up")
        self.win.geometry("900x600")
        self.win.configure(bg=BG)
        self.win.protocol("WM_DELETE_WINDOW", self._go_back)
        self._build()

    def _build(self):
        card = build_card(self.win, 505)
        body = tk.Frame(card, bg=CARD)
        body.pack(fill="both", expand=True, padx=34, pady=24)

        tk.Label(body, text="✦  Create Account", font=("Georgia", 16, "bold"), fg=TEAL, bg=CARD).pack(anchor="w")
        tk.Label(body, text="Join thousands of students worldwide", font=("Arial", 9), fg=MUTED, bg=CARD).pack(anchor="w", pady=(2, 0))

        self.name_f = expected_entry(body, "Display Name")
        self.user_f = expected_entry(body, "Username")
        self.pass_f = expected_entry(body, "Password", hidden=True)
        self.conf_f = expected_entry(body, "Confirm Password", hidden=True)

        tk.Button(body, text="Create Account  →", font=("Arial", 11, "bold"),
                  bg=TEAL, fg=WHITE,
                  command=self._try_register).pack(fill="x", pady=(16, 0))

        row = tk.Frame(body, bg=CARD)
        row.pack(pady=(9, 0))
        tk.Label(row, text="Already a member?  ", font=("Arial", 9), fg=MUTED, bg=CARD).pack(side="left")
        back = tk.Label(row, text="Sign in", font=("Arial", 9, "underline"), fg=TEAL, bg=CARD, cursor="hand2")
        back.pack(side="left")
        back.bind("<Button-1>", lambda e: self._go_back())

    def _try_register(self):
        dn = self.name_f.get().strip()
        u  = self.user_f.get().strip()
        p  = self.pass_f.get()
        cp = self.conf_f.get()
        if not all([dn, u, p, cp]):
            messagebox.showwarning("Incomplete", "Please fill all fields.", parent=self.win)
            return
        if p != cp:
            messagebox.showerror("Mismatch", "Passwords don't match.", parent=self.win)
            return
        save_new_user(dn, u, p)
        messagebox.showinfo("Success", f"Account created! Welcome, {dn}!", parent=self.win)
        self._go_back()

    def _go_back(self):
        self.win.destroy()
        self.login_win.deiconify()

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: DASHBOARD  (from Dashboard.py — adapted as a tk.Frame page)
# ══════════════════════════════════════════════════════════════════════════════
class DashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller

    def refresh(self):
        """Call after login so display_name / username are available."""
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _build(self):
        dn = getattr(self.controller, "display_name", "User")

        content = tk.Frame(self, bg=BG, padx=30, pady=20)
        content.pack(fill="both", expand=True)

        # ── Welcome ──────────────────────────────────────────────────────────
        welcome = tk.Frame(content, bg=CARD, pady=22, padx=28)
        welcome.pack(fill="x")
        tk.Label(welcome, text="WORKSPACE ACTIVE", font=("Arial", 10, "bold"), fg=TEAL, bg=CARD).pack(anchor="w")

        row = tk.Frame(welcome, bg=CARD)
        row.pack(fill="x", pady=(10, 0))
        tk.Label(row, text=f"Welcome back, {dn}", font=("Georgia", 24, "bold"), fg=WHITE, bg=CARD).pack(side="left")
        tk.Button(row, text="▶ Quick Study Sprint", bg=ACCENT_BLUE, fg=WHITE,
                  font=("Arial", 11, "bold"), relief="flat", padx=18, pady=7).pack(side="right", padx=8)
        tk.Button(row, text="🌍 Explore Culture Map", bg=CARD, fg=WHITE,
                  font=("Arial", 11, "bold"), relief="flat",
                  highlightthickness=1, highlightbackground=BORDER).pack(side="right")

        # ── Stats row ────────────────────────────────────────────────────────
        stats = tk.Frame(content, bg=BG)
        stats.pack(fill="x", pady=25)
        for title, val in [("GLOBAL COLLABORATIONS","8 Regions"),
                           ("STUDY SPRINT TIME","14.5 Hrs"),
                           ("COLLABORATIVE STREAKS","9 Days")]:
            f = tk.Frame(stats, bg=CARD, width=260, height=120)
            f.pack(side="left", padx=10, fill="both", expand=True)
            f.pack_propagate(False)
            tk.Label(f, text=title, font=("Arial", 9),  fg=MUTED, bg=CARD).pack(anchor="w", padx=22, pady=(22,5))
            tk.Label(f, text=val,   font=("Arial", 26, "bold"), fg=TEAL, bg=CARD).pack(anchor="w", padx=22)

        # ── Peers + Clusters ─────────────────────────────────────────────────
        bottom = tk.Frame(content, bg=BG)
        bottom.pack(fill="both", expand=True)

        left = tk.Frame(bottom, bg=CARD, padx=22, pady=18)
        left.pack(side="left", fill="both", expand=True, padx=(0,15))
        tk.Label(left, text="RECOMMENDED GLOBAL PEERS",
                 font=("Arial", 13, "bold"), fg=WHITE, bg=CARD).pack(anchor="w", pady=(0,15))
        self._peer_card(left, "Kenji Sato",   "University of Tokyo",   "#14B8A6")
        self._peer_card(left, "Clara Dubois", "Sorbonne Université",   "#F87171")

        right = tk.Frame(bottom, bg=CARD, padx=22, pady=18)
        right.pack(side="left", fill="both", expand=True)
        tk.Label(right, text="POPULAR STUDY CLUSTERS",
                 font=("Arial", 13, "bold"), fg=WHITE, bg=CARD).pack(anchor="w", pady=(0,15))
        self._cluster_card(right, "Quantum Cryptography Hub", "142 members", "#4338CA")
        self._cluster_card(right, "Global Hackathon Circle",  "89 members",  "#2563EB")

    def _peer_card(self, parent, name, school, color):
        f = tk.Frame(parent, bg=CARD, pady=14, padx=16)
        f.pack(fill="x", pady=6)
        tk.Label(f, text="●", font=("Arial", 28), fg=color, bg=CARD).pack(side="left")
        info = tk.Frame(f, bg=CARD)
        info.pack(side="left", padx=14)
        tk.Label(info, text=name,   font=("Arial", 12, "bold"), fg=WHITE, bg=CARD).pack(anchor="w")
        tk.Label(info, text=school, font=("Arial", 10),         fg=MUTED, bg=CARD).pack(anchor="w")
        tk.Button(f, text="Chat Peer", bg=ACCENT_BLUE, fg=WHITE,
                  font=("Arial", 10, "bold"), relief="flat",
                  padx=16, pady=5).pack(side="right")

    def _cluster_card(self, parent, name, count, color):
        f = tk.Frame(parent, bg=color, pady=22, padx=22)
        f.pack(fill="x", pady=7)
        tk.Label(f, text=name,  font=("Arial", 14, "bold"), fg=WHITE,     bg=color).pack(anchor="w")
        tk.Label(f, text=count, font=("Arial", 11),         fg="#E0F2FE", bg=color).pack(anchor="w", pady=4)
        tk.Button(f, text="Join Cluster →", bg=WHITE, fg="#1E3A8A",
                  font=("Arial", 10, "bold"), relief="flat").pack(anchor="w", pady=(8,0))

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: USER PROFILE  (from user_profile.py — adapted as a tk.Frame page)
# ══════════════════════════════════════════════════════════════════════════════
class UserProfilePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self._built = False

    def refresh(self):
        if self._built:
            return
        self._built = True
        self._build()

    def _build(self):
        username = getattr(self.controller, "display_name", "User")

        # ── Page header ──────────────────────────────────────────────────────
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", pady=(0, 18), padx=20)
        tk.Label(header, text="User Profile",        font=("Georgia", 18, "bold"), fg=WHITE, bg=BG).pack(side="left")
        tk.Label(header, text="Manage your personal details",
                 font=("Arial", 9), fg=MUTED, bg=BG).pack(side="left", padx=(12,0), pady=(6,0))

        # ── Avatar card ──────────────────────────────────────────────────────
        top_card = tk.Frame(self, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        top_card.pack(fill="x", padx=20, pady=(0,14))
        inner_top = tk.Frame(top_card, bg=CARD)
        inner_top.pack(fill="x", padx=24, pady=20)

        av = tk.Frame(inner_top, bg=TEAL, width=64, height=64)
        av.pack(side="left")
        av.pack_propagate(False)
        initials = "".join(p[0].upper() for p in username.split()[:2])
        tk.Label(av, text=initials, font=("Georgia", 20, "bold"), fg=WHITE, bg=TEAL).place(relx=.5, rely=.5, anchor="center")

        nb = tk.Frame(inner_top, bg=CARD)
        nb.pack(side="left", padx=18)
        tk.Label(nb, text=username,              font=("Georgia", 16, "bold"), fg=WHITE, bg=CARD).pack(anchor="w")
        tk.Label(nb, text="● Online  •  Student", font=("Arial", 9),           fg=TEAL,  bg=CARD).pack(anchor="w", pady=(2,0))
        tk.Label(nb, text="Joined PeerSphere  •  Active in 3 clusters",
                 font=("Arial", 8), fg=MUTED, bg=CARD).pack(anchor="w")

        self._edit_mode = [False]
        self._edit_btn  = tk.Button(inner_top, text="✏  Edit Profile",
                                    font=("Arial", 9, "bold"), bg=FIELD_BG, fg=WHITE,
                                    activebackground=CARD, activeforeground=TEAL,
                                    relief="flat", bd=0, cursor="hand2",
                                    highlightthickness=1, highlightbackground=BORDER,
                                    padx=12, pady=6, command=self._toggle_edit)
        self._edit_btn.pack(side="right")

        # ── Two-column layout ────────────────────────────────────────────────
        cols = tk.Frame(self, bg=BG)
        cols.pack(fill="both", expand=True, padx=20)

        left_col  = tk.Frame(cols, bg=BG)
        right_col = tk.Frame(cols, bg=BG)
        left_col.pack(side="left",  fill="both", expand=True, padx=(0,12))
        right_col.pack(side="right", fill="both", expand=True)

        # Personal Info card
        self._fields = {}
        info_card  = tk.Frame(left_col, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        info_card.pack(fill="x", pady=(0,14))
        info_inner = tk.Frame(info_card, bg=CARD)
        info_inner.pack(fill="x", padx=20, pady=16)
        tk.Label(info_inner, text="PERSONAL INFO",
                 font=("Arial", 8, "bold"), fg=MUTED, bg=CARD).pack(anchor="w", pady=(0,10))

        for lbl, default in [
            ("Display Name", username),
            ("Username",     username.lower().replace(" ", "_")),
            ("Email",        "user@peersphere.io"),
            ("University",   "University of Lagos"),
            ("Country",      "Nigeria"),
        ]:
            self._add_field(info_inner, lbl, default)

        self._save_btn = tk.Button(info_inner, text="Save Changes",
                                   font=("Arial", 10, "bold"),
                                   bg=TEAL, fg=WHITE, activebackground=ACCENT2,
                                   relief="flat", bd=0, cursor="hand2",
                                   pady=8, command=self._save_changes)

        # Stats card
        stats_card  = tk.Frame(right_col, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        stats_card.pack(fill="x", pady=(0,14))
        stats_inner = tk.Frame(stats_card, bg=CARD)
        stats_inner.pack(fill="x", padx=20, pady=16)
        tk.Label(stats_inner, text="ACTIVITY STATS",
                 font=("Arial", 8, "bold"), fg=MUTED, bg=CARD).pack(anchor="w", pady=(0,10))
        for stat_lbl, val in [("Study Sprint Hours","14.5 hrs"),("Collaborative Streak","9 days"),
                               ("Clusters Joined","3"),("Peers Connected","12"),("Regions Reached","8")]:
            r = tk.Frame(stats_inner, bg=CARD); r.pack(fill="x", pady=4)
            tk.Label(r, text=stat_lbl, font=("Arial", 9),           fg=MUTED, bg=CARD).pack(side="left")
            tk.Label(r, text=val,      font=("Arial", 9, "bold"),   fg=TEAL,  bg=CARD).pack(side="right")

        # Badges card
        badges_card  = tk.Frame(right_col, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        badges_card.pack(fill="x")
        badges_inner = tk.Frame(badges_card, bg=CARD)
        badges_inner.pack(fill="x", padx=20, pady=16)
        tk.Label(badges_inner, text="BADGES",
                 font=("Arial", 8, "bold"), fg=MUTED, bg=CARD).pack(anchor="w", pady=(0,10))
        badge_row = tk.Frame(badges_inner, bg=CARD); badge_row.pack(anchor="w")
        for icon, tip in [("🌍","Global Collab"),("🔥","9-Day Streak"),
                          ("💡","Idea Starter"),("🏆","Top Contributor")]:
            b = tk.Frame(badge_row, bg=FIELD_BG, highlightthickness=1,
                         highlightbackground=BORDER, width=52, height=52)
            b.pack(side="left", padx=(0,8)); b.pack_propagate(False)
            tk.Label(b, text=icon, font=("Arial", 18), bg=FIELD_BG).place(relx=.5, rely=.38, anchor="center")
            tk.Label(b, text=tip,  font=("Arial", 6),  fg=MUTED, bg=FIELD_BG).place(relx=.5, rely=.82, anchor="center")

    def _add_field(self, parent, field_label, default):
        wrapper = tk.Frame(parent, bg=CARD); wrapper.pack(fill="x", pady=(0,8))
        tk.Label(wrapper, text=field_label, font=("Arial", 8), fg=MUTED, bg=CARD).pack(anchor="w")
        var = tk.StringVar(value=default)
        lbl = tk.Label(wrapper, textvariable=var, font=("Arial", 10), fg=WHITE, bg=CARD, anchor="w")
        lbl.pack(fill="x")
        ent = tk.Entry(wrapper, textvariable=var, font=("Arial", 10),
                       bg=FIELD_BG, fg=WHITE, insertbackground=WHITE,
                       relief="flat", bd=0, highlightthickness=1,
                       highlightbackground=BORDER, highlightcolor=TEAL)
        ent.config(state="disabled")
        self._fields[field_label] = (lbl, ent, var)

    def _toggle_edit(self):
        editing = not self._edit_mode[0]
        self._edit_mode[0] = editing
        for lbl, ent, var in self._fields.values():
            if editing:
                lbl.pack_forget()
                ent.config(state="normal")
                ent.pack(fill="x", ipady=6)
            else:
                ent.pack_forget()
                ent.config(state="disabled")
                lbl.pack(fill="x")
        if editing:
            self._edit_btn.config(text="✕  Cancel")
            self._save_btn.pack(fill="x", pady=(12,0), ipady=2)
        else:
            self._edit_btn.config(text="✏  Edit Profile")
            self._save_btn.pack_forget()

    def _save_changes(self):
        self._toggle_edit()
        messagebox.showinfo("Saved", "Your profile has been updated!")

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: EVENTS
# ══════════════════════════════════════════════════════════════════════════════
class EventsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        CAT_TECH     = "#2e1065"
        CAT_GLOBAL   = "#451a03"
        CAT_ACADEMIC = "#1e293b"
        CAT_SPRINT   = "#115e59"

        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", pady=(0,20), padx=20)
        tk.Label(header, text="PeerSphere Events",
                 font=("Georgia", 18, "bold"), fg=WHITE, bg=BG).pack(side="left")
        tk.Button(header, text="+ Global AI Events", font=("Arial", 9, "bold"),
                  bg=TEAL, fg=WHITE, activebackground=ACCENT2,
                  relief="flat", bd=0, cursor="hand2", padx=14, pady=6).pack(side="right")

        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True, padx=(20,0))
        sb = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        sb.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=sb.set)

        sc = tk.Frame(canvas, bg=BG)
        win = canvas.create_window((0,0), window=sc, anchor="nw")

        sc.bind("<Configure>",  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        categorized_events = {
            "💻 TECH & AI DEVELOPMENTS": [
                ("💻","Global AI & Ethics Summit",    CAT_TECH,"1,240 members","Starts in 5m","Discuss ethical implications of AI in modern education."),
                ("⚛","Quantum Computing Class",       CAT_TECH,"430 members","Join Session","Introductory masterclass on quantum algorithms."),
                ("🚀","Global Hackathon 2026",         CAT_TECH,"2,100 members","Starts Tomorrow","Build software solutions addressing global climate change."),
                ("🧬","Bioinformatics Workshop",       CAT_TECH,"275 members","Starts in 2h","Data science revolutionizing genetics and healthcare."),
            ],
            "🌍 GLOBAL & COMMUNITY FORUMS": [
                ("🌍","Pan-African Tech Forum",        CAT_GLOBAL,"850 members","Join Session","African students showcase innovative software solutions."),
                ("🗣️","Language Exchange Mixer",       CAT_GLOBAL,"1,850 members","In Progress","Practice your target language with native speakers."),
            ],
            "📚 ACADEMIC & FINANCE SYMPOSIUMS": [
                ("⚖","International Law Symposium",   CAT_ACADEMIC,"315 members","Join Session","Debate international treaties with law students worldwide."),
                ("📈","Global Economics Forum",        CAT_ACADEMIC,"620 members","Join Session","Analyze emerging market trends with finance majors."),
            ],
            "⏱️ FOCUS SPRINTS & PRACTICAL WORKSHOPS": [
                ("⏱","24-Hour Study Sprint",          CAT_SPRINT,"5,000+ members","In Progress","Focused continuous study session with Pomodoro breaks."),
                ("🎨","Digital Art & UX Masterclass", CAT_SPRINT,"940 members","Join Session","Modern UI/UX principles with industry pros."),
                ("🌿","Sustainability Hackathon",      CAT_SPRINT,"1,150 members","Starts Monday","Eco-friendly tech solutions for university campuses."),
                ("📝","Thesis Writing Retreat",        CAT_SPRINT,"890 members","In Progress","Quiet, accountable co-working space for deep writing."),
            ],
        }

        for heading, events in categorized_events.items():
            sf = tk.Frame(sc, bg=BG); sf.pack(fill="x", pady=(20,10), padx=10)
            tk.Label(sf, text=heading, font=("Arial", 11, "bold"), fg=WHITE, bg=BG).pack(anchor="w")
            tk.Frame(sc, bg="#1e293b", height=1).pack(fill="x", padx=10, pady=(0,10))
            gf = tk.Frame(sc, bg=BG); gf.pack(fill="x", padx=10, pady=(0,20))
            for i, data in enumerate(events):
                self._event_card(gf, data).grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")
                gf.grid_columnconfigure(i%3, weight=1)

    def _event_card(self, parent, data):
        icon, title, color, members, status, desc = data
        card  = tk.Frame(parent, bg=color, highlightthickness=1, highlightbackground=BORDER)
        inner = tk.Frame(card, bg=color); inner.pack(fill="both", expand=True, padx=16, pady=16)
        top   = tk.Frame(inner, bg=color); top.pack(fill="x")
        tk.Label(top, text=icon,   font=("Arial", 22), bg=color, fg=WHITE).pack(side="left", padx=(0,10))
        tk.Label(top, text=title,  font=("Arial", 10, "bold"), fg=WHITE, bg=color, wraplength=160, justify="left").pack(side="left", anchor="w")
        tk.Label(inner, text=desc, font=("Arial", 9),  fg=MUTED, bg=color, wraplength=200, justify="left").pack(anchor="w", pady=(10,0))
        foot = tk.Frame(inner, bg=color); foot.pack(fill="x", side="bottom", pady=(12,0))
        tk.Label(foot, text=f"⊙ {members}", font=("Arial", 8), fg=MUTED, bg=color).pack(side="left")
        tk.Label(foot, text=status,          font=("Arial", 8), fg=TEAL,  bg=color).pack(side="right")
        return card

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: GLOBAL CHAT
# ══════════════════════════════════════════════════════════════════════════════
class GlobalChatPage(tk.Frame):
    def __init__(self, parent, controller):
        CHAT_BG   = "#0b1120"
        BUBBLE_BG = "#1e293b"
        CHAT_BORDER = "#334155"
        CHAT_TEAL   = "#06b6d4"
        CHAT_MUTED  = "#94a3b8"

        super().__init__(parent, bg=CHAT_BG)

        header = tk.Frame(self, bg=CHAT_BG); header.pack(fill="x", pady=(0,20), padx=20)
        tk.Label(header, text="Global Chat", font=("Georgia", 18, "bold"), fg=WHITE, bg=CHAT_BG).pack(side="left")
        tk.Button(header, text="+ Global Chat", font=("Arial", 9, "bold"),
                  bg=CHAT_TEAL, fg=WHITE, relief="flat", bd=0,
                  cursor="hand2", padx=14, pady=6).pack(side="right")

        chat_box = tk.Frame(self, bg=CHAT_BG, highlightthickness=1, highlightbackground=CHAT_BORDER)
        chat_box.pack(fill="both", expand=True, padx=20, pady=(0,20))

        canvas = tk.Canvas(chat_box, bg=CHAT_BG, highlightthickness=0)
        sb = tk.Scrollbar(chat_box, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=CHAT_BG)
        sw = canvas.create_window((0,0), window=self.scroll_frame, anchor="nw")

        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        canvas.bind("<Configure>", lambda e: canvas.itemconfig(sw, width=e.width))
        self.scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        avatar_colors = {
            "Alexa Smith":    "#0ea5e9",
            "Ragnar Crimson": "#d97706",
            "Sasaki Kojiro":  "#8b5cf6",
            "Eren Jaeger":    "#14b8a6",
        }
        messages = [
            {"name":"Alexa Smith",    "initials":"AS","text":"Is everyone here joining the AI & Ethics Summit later?","is_me":False},
            {"name":"Ragnar Crimson", "initials":"RC","text":"I'm definitely going. The panel on algorithmic bias sounds fascinating.","is_me":False},
            {"name":"Sasaki Kojiro",  "initials":"SK","text":"Same! I'm hoping they discuss open-source constraints.","is_me":False},
            {"name":"Alexa Smith",    "initials":"AS","text":"If anyone wants to sync up afterwards for a debrief, let me know.","is_me":False},
            {"name":"Sasaki Kojiro",  "initials":"SK","text":"That's a great idea, count me in. I'll be in the lobby at 5.","is_me":False},
            {"name":"Eren Jaeger",    "initials":"EJ","text":"Perfect. I'll see you all there!","is_me":True},
        ]
        for msg in messages:
            self._build_message(self.scroll_frame, msg, BUBBLE_BG, avatar_colors, CHAT_TEAL, CHAT_MUTED)

        inp = tk.Frame(self, bg=CHAT_BG); inp.pack(fill="x", padx=20, pady=(0,20))
        eb  = tk.Frame(inp, bg=CHAT_BG, highlightthickness=1, highlightbackground=CHAT_BORDER)
        eb.pack(side="left", fill="both", expand=True)
        self._ph = "What do you want to say"
        self._entry = tk.Entry(eb, font=("Arial", 11), bg=CHAT_BG, fg=CHAT_MUTED,
                               bd=0, insertbackground=WHITE)
        self._entry.pack(fill="both", expand=True, padx=10, pady=12)
        self._entry.insert(0, self._ph)
        self._entry.bind("<FocusIn>",  self._clear_ph)
        self._entry.bind("<FocusOut>", self._add_ph)
        tk.Button(inp, text="Send >", font=("Arial", 10, "bold"),
                  bg=CHAT_BORDER, fg=WHITE, relief="flat", bd=0,
                  cursor="hand2").pack(side="right", fill="y", padx=(10,0))

    def _build_message(self, parent, msg, bubble_bg, avatar_colors, teal, muted):
        row = tk.Frame(parent, bg=parent["bg"]); row.pack(fill="x", pady=10)
        is_me = msg["is_me"]
        wrap  = tk.Frame(row, bg=parent["bg"])
        wrap.pack(side="right" if is_me else "left")
        av_color = avatar_colors.get(msg["name"], "#64748b")
        av = tk.Frame(wrap, bg=av_color, width=36, height=36); av.pack_propagate(False)
        tk.Label(av, text=msg["initials"], font=("Arial", 10, "bold"),
                 fg=WHITE, bg=av_color).place(relx=.5, rely=.5, anchor="center")
        bub = tk.Frame(wrap, bg=bubble_bg)
        if is_me:
            tk.Label(bub, text=msg["name"], font=("Arial",9,"bold"), fg=teal, bg=bubble_bg).pack(anchor="e", padx=12, pady=(8,2))
            tk.Label(bub, text=msg["text"], font=("Arial",10), fg=WHITE, bg=bubble_bg, justify="right").pack(anchor="e", padx=12, pady=(0,8))
            bub.pack(side="left", padx=(0,10)); av.pack(side="right")
        else:
            tk.Label(bub, text=msg["name"], font=("Arial",9,"bold"), fg=teal, bg=bubble_bg).pack(anchor="w", padx=12, pady=(8,2))
            tk.Label(bub, text=msg["text"], font=("Arial",10), fg=WHITE, bg=bubble_bg, justify="left").pack(anchor="w", padx=12, pady=(0,8))
            av.pack(side="left"); bub.pack(side="left", padx=(10,0))

    def _clear_ph(self, e):
        if self._entry.get() == self._ph:
            self._entry.delete(0, tk.END); self._entry.config(fg=WHITE)

    def _add_ph(self, e):
        if not self._entry.get():
            self._entry.insert(0, self._ph); self._entry.config(fg="#94a3b8")

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: STUDY GROUPS / CULTURE EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
class StudyGroupsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        header = tk.Frame(self, bg=BG); header.pack(fill="x", pady=(0,20), padx=20)
        tk.Label(header, text="PeerSphere Study Groups",
                 font=("Georgia", 18, "bold"), fg=WHITE, bg=BG).pack(side="left")

        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True, padx=(20,0))
        sb = tk.Scrollbar(self, orient="vertical", command=canvas.yview); sb.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=sb.set)
        sc = tk.Frame(canvas, bg=BG)
        win = canvas.create_window((0,0), window=sc, anchor="nw")
        sc.bind("<Configure>",    lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",lambda e: canvas.itemconfig(win, width=e.width-40))

        groups = [
            ("CS","Intro to Computer Science","Engineering","2,450 members"),
            ("BC","Principles of Biochemistry","Life Sciences","1,120 members"),
            ("ME","Macroeconomic Theory","Economics","890 members"),
            ("LA","Linear Algebra & Matrices","Mathematics","1,540 members"),
            ("SU","Sustainable Urbanism","Architecture","760 members"),
            ("MH","Modern European History","Humanities","430 members"),
            ("DS","Data Structures & Algos","Computer Science","3,200 members"),
            ("GH","Global Health Policy","Public Health","510 members"),
            ("UX","Digital Art & UX Theory","Design","940 members"),
            ("QC","Quantum Computing Basics","Physics","620 members"),
            ("CY","Cybersecurity Essentials","Engineering","1,850 members"),
            ("BE","Behavioral Economics","Social Science","480 members"),
            ("DM","Digital Marketing Strategy","Business","710 members"),
            ("MT","Music Theory & Composition","Arts","350 members"),
            ("RE","Renewable Energy Systems","Environmental Science","590 members"),
        ]
        gf = tk.Frame(sc, bg=BG); gf.pack(fill="both", expand=True, padx=10, pady=10)
        for i, d in enumerate(groups):
            self._group_card(gf, d).grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")
            gf.grid_columnconfigure(i%3, weight=1)

    def _group_card(self, parent, data):
        initials, title, subtitle, members = data
        card  = tk.Frame(parent, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        inner = tk.Frame(card, bg=CARD); inner.pack(fill="both", expand=True, padx=16, pady=16)
        top   = tk.Frame(inner, bg=CARD); top.pack(fill="x", anchor="w")
        tk.Label(top, text=initials, font=("Arial",9,"bold"), fg=CARD, bg=WHITE, width=3, height=1).pack(side="left", padx=(0,10))
        tk.Label(top, text=title, font=("Arial",10,"bold"), fg=WHITE, bg=CARD, wraplength=150, justify="left").pack(side="left", anchor="w")
        tk.Label(inner, text=subtitle, font=("Arial",9), fg=WHITE, bg=CARD).pack(anchor="w", pady=(12,0))
        foot = tk.Frame(inner, bg=CARD); foot.pack(fill="x", side="bottom", pady=(12,0))
        tk.Label(foot, text=members,       font=("Arial",8), fg=WHITE, bg=CARD).pack(side="left")
        tk.Label(foot, text="Join Group →",font=("Arial",8), fg=WHITE, bg=CARD, cursor="hand2").pack(side="right")
        return card

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APP  (launched after successful login)
# ══════════════════════════════════════════════════════════════════════════════
class PeerSphereApp(tk.Toplevel):
    def __init__(self, root, display_name, username):
        super().__init__(root)
        self.root         = root
        self.display_name = display_name
        self.username     = username

        self.title("PeerSphere — Workspace")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg=BG)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._clock_running = True
        self.active_nav_btn = None
        self.nav_buttons    = {}

        self._build_topbar()

        self.body = tk.Frame(self, bg=BG)
        self.body.pack(fill="both", expand=True)

        self._build_sidebar()

        self.main_container = tk.Frame(self.body, bg=BG)
        self.main_container.pack(side="left", fill="both", expand=True, padx=20, pady=16)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Instantiate all pages
        self.pages = {}
        for PageClass in (DashboardPage, EventsPage, GlobalChatPage, StudyGroupsPage, UserProfilePage):
            name  = PageClass.__name__
            frame = PageClass(parent=self.main_container, controller=self)
            self.pages[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Initialise pages that need post-login data
        self.pages["DashboardPage"].refresh()
        self.pages["UserProfilePage"].refresh()

        # Show dashboard by default
        self.show_page("DashboardPage", "Dashboard")

    # ── Top bar ───────────────────────────────────────────────────────────────
    def _build_topbar(self):
        topbar = tk.Frame(self, bg=SIDEBAR, height=54)
        topbar.pack(side="top", fill="x")
        topbar.pack_propagate(False)

        badge = tk.Frame(topbar, bg=TEAL, width=36, height=36)
        badge.pack(side="left", padx=(14,6), pady=9)
        badge.pack_propagate(False)
        tk.Label(badge, text="PS", font=("Georgia",11,"bold"), fg=WHITE, bg=TEAL).place(relx=.5, rely=.5, anchor="center")

        bw = tk.Frame(topbar, bg=SIDEBAR); bw.pack(side="left", pady=6)
        tk.Label(bw, text="PEERSPHERE",    font=("Georgia",12,"bold"), fg=WHITE, bg=SIDEBAR).pack(anchor="w")
        tk.Label(bw, text="UPLINK: ONLINE",font=("Arial",7),           fg=TEAL,  bg=SIDEBAR).pack(anchor="w")

        tk.Label(topbar, text=" v1.4.0-beta ", font=("Arial",8), fg=MUTED, bg=CARD,
                 relief="flat", bd=0, highlightthickness=1, highlightbackground=BORDER).pack(side="left", padx=10)

        sf = tk.Frame(topbar, bg=FIELD_BG, highlightthickness=1, highlightbackground=BORDER)
        sf.pack(side="left", padx=20, fill="y", pady=10, expand=True)
        tk.Label(sf, text="🔍", fg=MUTED, bg=FIELD_BG, font=("Arial",10)).pack(side="left", padx=(8,2))
        tk.Entry(sf, font=("Arial",10), bg=FIELD_BG, fg=MUTED, insertbackground=WHITE,
                 relief="flat", bd=0, width=38).pack(side="left", pady=6, ipady=2)

        self.clock_lbl = tk.Label(topbar, text="", font=("Arial",10,"bold"), fg=WHITE, bg=SIDEBAR)
        self.clock_lbl.pack(side="right", padx=(4,14))
        tk.Label(topbar, text="● 24ms ping", font=("Arial",9), fg=TEAL, bg=SIDEBAR).pack(side="right", padx=(4,0))
        self._tick_clock()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sidebar = tk.Frame(self.body, bg=SIDEBAR, width=190)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        nav_pad = tk.Frame(sidebar, bg=SIDEBAR); nav_pad.pack(fill="x", pady=(16,0))

        # label → (page_class_name)
        nav_items = [
            ("Dashboard",       "DashboardPage"),
            ("Global Chat",     "GlobalChatPage"),
            ("Culture Explorer","StudyGroupsPage"),
            ("User Profile",    "UserProfilePage"),
            ("Events",          "EventsPage"),
        ]

        for label, page_ref in nav_items:
            btn = tk.Button(nav_pad, text=f"  {label}", font=("Arial",10,"normal"),
                            bg=SIDEBAR, fg=WHITE, activebackground=CARD, activeforeground=TEAL,
                            relief="flat", bd=0, anchor="w", cursor="hand2", pady=10,
                            command=lambda p=page_ref, l=label: self.show_page(p, l))
            btn.pack(fill="x")
            self.nav_buttons[label] = btn
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=CARD)    if b is not self.active_nav_btn else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=SIDEBAR) if b is not self.active_nav_btn else None)

        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=14, pady=16)

        # Logout
        logout_btn = tk.Button(sidebar, text="  Logout", font=("Arial",10,"normal"),
                               bg=SIDEBAR, fg="#EF4444", activebackground="#1f1f1f",
                               relief="flat", bd=0, anchor="w", cursor="hand2", pady=10,
                               command=self._logout)
        logout_btn.pack(fill="x")

    def show_page(self, page_name, label_name):
        if self.active_nav_btn:
            self.active_nav_btn.config(bg=SIDEBAR, fg=WHITE, font=("Arial",10,"normal"))
        btn = self.nav_buttons.get(label_name)
        if btn:
            btn.config(bg=CARD, fg=TEAL, font=("Arial",10,"bold"))
            self.active_nav_btn = btn
        frame = self.pages.get(page_name)
        if frame:
            frame.tkraise()

    def _tick_clock(self):
        if not self._clock_running:
            return
        self.clock_lbl.config(text=time.strftime("%I:%M %p"))
        self.after(1000, self._tick_clock)

    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self._clock_running = False
            self.destroy()
            # Re-launch login over the hidden root
            LoginWindow(self.root, _launch_app)

    def _on_close(self):
        self._clock_running = False
        self.root.destroy()

# ══════════════════════════════════════════════════════════════════════════════
#  WIRING: splash → login → app
# ══════════════════════════════════════════════════════════════════════════════
def _launch_app(display_name, username):
    PeerSphereApp(root, display_name, username)

def _show_login():
    for w in root.winfo_children():
        w.destroy()
    root.withdraw()
    LoginWindow(root, _launch_app)

# ── Bootstrap ─────────────────────────────────────────────────────────────────
setup_db()

root = tk.Tk()
root.title("PeerSphere")
root.configure(bg=BG)
root.withdraw()   # hidden; splash uses a Toplevel equivalent (the root itself)
root.deiconify()

SplashScreen(root, on_done=_show_login)
root.mainloop()
