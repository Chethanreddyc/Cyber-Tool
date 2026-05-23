"""
╔══════════════════════════════════════════════════════════╗
║       CYBER TOOL — Password Cracker                      ║
║   Hash cracking via Dictionary & Brute-Force attacks     ║
║   For AUTHORISED security testing ONLY                   ║
╚══════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
import hashlib
import threading
import itertools
import string
import time
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import stats_tracker
from datetime import timedelta

# ── Palette ────────────────────────────────────────────────────
BG_DARK    = "#0a0f1e"
PANEL_BG   = "#0d1526"
CARD_BG    = "#0f1c35"
ACCENT     = "#ff6b35"       # orange theme for cracker
ACCENT2    = "#00d4ff"
TEXT_MAIN  = "#e8f4fd"
TEXT_MUTED = "#4a6fa5"
BORDER     = "#1e3a5f"
ERROR_C    = "#ff4d6d"
SUCCESS_C  = "#00e5a0"
WARN_C     = "#f0b429"
ENTRY_BG   = "#070e1c"

# ── Hash algorithms supported ──────────────────────────────────
HASH_ALGORITHMS = {
    32:  "MD5",
    40:  "SHA-1",
    56:  "SHA-224",
    64:  "SHA-256",
    96:  "SHA-384",
    128: "SHA-512",
}

HASH_FUNCTIONS = {
    "MD5":     lambda p: hashlib.md5(p.encode()).hexdigest(),
    "SHA-1":   lambda p: hashlib.sha1(p.encode()).hexdigest(),
    "SHA-224": lambda p: hashlib.sha224(p.encode()).hexdigest(),
    "SHA-256": lambda p: hashlib.sha256(p.encode()).hexdigest(),
    "SHA-384": lambda p: hashlib.sha384(p.encode()).hexdigest(),
    "SHA-512": lambda p: hashlib.sha512(p.encode()).hexdigest(),
}

# ── Built-in common password wordlist ──────────────────────────
BUILTIN_WORDLIST = [
    "123456","password","123456789","12345678","12345","1234567","1234567890",
    "qwerty","abc123","football","iloveyou","admin","letmein","monkey","1234",
    "shadow","master","666666","qwertyuiop","123321","mustang","michael",
    "superman","batman","dragon","pass1234","pass123","password1","password123",
    "hunter2","sunshine","princess","welcome","login","test","user","admin123",
    "root","toor","linux","windows","cisco","oracle","mysql","secret","alpine",
    "123abc","abc1234","qwerty123","azerty","123qwe","1q2w3e","zxcvbn","asdfgh",
    "111111","222222","333333","444444","555555","777777","888888","999999",
    "000000","112233","121212","123123","131313","232323","654321","987654321",
    "q1w2e3r4","pass@123","P@ssw0rd","P@ssword1","Admin@123","Admin1234",
    "Welcome1","Welcome!","Summer2023","Winter2023","Spring2024","Autumn2023",
    "January1","February2","March123","April123","Hello123","hello123",
    "computer","superman1","batman123","starwars","trustno1","qazwsx",
    "whatever","nothing","football1","baseball","basketball","soccer",
    "iloveyou1","iloveu","sexy","love123","lovely","mylove","loveme",
    "password!","passw0rd","p@ssword","pa$$word","p@$$word","pa$$w0rd",
    "Michael1","Jessica","Ashley","Jennifer","Amanda","Daniel","Matthew",
    "joshua","andrew","george","charlie","thomas","robert","william",
    "thomas1","charlie1","jordan","harley","ranger","dakota","maverick",
    "tiger","flower","cheese","butter","soccer1","hockey","guitar",
    "internet","computer1","keyboard","windows1","linux123","ubuntu",
    "raspberry","python","django","flask","javascript","reactjs","nodejs",
    "summer","winter","spring","autumn","rainbow","sunshine1","moonlight",
    "midnight","shadow1","ghost","phantom","falcon","eagle","hawk","cobra",
    "alpha","bravo","delta","echo","foxtrot","golf","hotel","india",
    "kilo","lima","mike","november","oscar","papa","quebec","romeo","sierra",
    "tango","uniform","victor","whiskey","xray","yankee","zulu",
    "abc","abcd","abcde","abcdef","abcdefg","abc123456","aaaaaa","bbbbbb",
    "cccccc","dddddd","eeeeee","ffffff","aabbcc","abcabc","aababc",
    "pass","passwd","password2","password3","password4","password5",
    "qwerty1","qwerty12","qwerty123","qwerty1234","qwerty12345",
    "1234abcd","abcd1234","pass1","pass12","pass123456",
    "welcome1","welcome12","welcome123","hello","hell0","he110",
    "mypassword","mypass","mypwd","newpass","newpassword","changeme",
    "temporary","temp123","test1","test12","test123","test1234","testing",
    "demo","demo123","sample","example","guest","guest123","user123",
    "admin1","admin12","admin1234","admin12345","administrator",
    "superuser","superadmin","sysadmin","syspass","system",
    "mysql","mysql123","oracle","oracle123","postgres","postgresql",
    "mongodb","redis","elastic","kibana","grafana","jenkins","gitlab",
    "github","docker","kubernetes","ansible","terraform","vagrant",
    "1Password","LastPass","bitwarden","keepass","dashlane",
    "P@$$w0rd","Adm1n","R00t","T00r","l33th4x0r","hackme","crackme",
    "letmein1","opensesame","alohomora","expelliarmus","lumos","nox",
    "matrix","neo123","trinity","morpheus","keymaker","oracle1",
    "ninja","samurai","pirate","assassin","hacker","cracker","h4cker",
    "bl4ck","wh1te","r3d","blu3","gr33n","y3ll0w","purpl3","0r4ng3",
    "0000","1111","2222","3333","4444","5555","6666","7777","8888","9999",
    "00000000","11111111","22222222","33333333","44444444","55555555",
    "12341234","43214321","12344321","43211234","11223344","44332211",
    "password@1","password@12","password@123","P@ssw0rd1","Pa$$w0rd",
    "India@123","India123","London123","Paris123","Delhi@123","Mumbai123",
    "NewYork1","Texas123","California","Florida1","Dallas123","Houston1",
    "!@#$%^&*","pass!@#","qwerty!","hello!","abc!","123!@#",
    "myname123","lastname1","firstname","name1234","name@123",
    "0987654321","9876543210","13579","24680","11235813","fibonacci",
    "monkey1","monkey123","donkey","donkey123","horse","horse123",
    "batman1","ironman1","thor1234","hulk123","spiderman","superman123",
    "pokemon","pikachu","charizard","bulbasaur","squirtle","mewtwo",
    "minecraft","roblox123","fortnite","valorant","csgo","gta5","pubg",
    "dragon1","dragon123","fire123","water123","earth123","wind123",
    "crystal","silver","golden","diamond","platinum","emerald","ruby",
    "qazxsw","plmokn","asdzxc","qweasd","qscesz","zsedcq",
]

# ── Auto-locate rockyou.txt from common paths ──────────────────
ROCKYOU_PATHS = [
    r"C:\Users\{}\Cyber Tool\rockyou.txt".format(os.getenv("USERNAME", "")),
    r"C:\Tools\wordlists\rockyou.txt",
    r"C:\wordlists\rockyou.txt",
    r"C:\rockyou.txt",
    r"D:\rockyou.txt",
    "/usr/share/wordlists/rockyou.txt",    # Kali Linux
    "/usr/share/wordlists/rockyou.txt.gz",
]

def _find_rockyou():
    """Return path to rockyou.txt if found, else None."""
    for p in ROCKYOU_PATHS:
        if os.path.isfile(p):
            return p
    return None

class PasswordCrackerPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG_DARK, corner_radius=0)
        self._running      = False
        self._stop_event   = threading.Event()
        self._attempts     = 0
        self._start_time   = 0
        self._result       = None
        self._build_ui()

    # ══════════════════════════════════════════════════════════
    #  UI Construction
    # ══════════════════════════════════════════════════════════
    def _build_ui(self):
        # ── Header ───────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=PANEL_BG, corner_radius=0, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="  💀  Password Cracker",
            font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
            text_color=ACCENT,
            anchor="w",
        ).pack(side="left", padx=24, pady=14)

        ctk.CTkLabel(
            header,
            text="⚠  Authorised Testing Only",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color=WARN_C,
        ).pack(side="right", padx=24)

        # ── Body ─────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=16)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_left(body)
        self._build_right(body)

    # ── LEFT — Input & Config ──────────────────────────────────
    def _build_left(self, parent):
        left = ctk.CTkFrame(parent, fg_color=PANEL_BG, corner_radius=14,
                             border_width=1, border_color=BORDER)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        inner = ctk.CTkScrollableFrame(left, fg_color="transparent",
                                        scrollbar_fg_color=PANEL_BG)
        inner.pack(fill="both", expand=True, padx=2, pady=2)

        # ── Section: Hash Input ───────────────────────────────
        self._section(inner, "HASH INPUT")

        ctk.CTkLabel(
            inner,
            text="Paste the hash value you want to crack",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_MUTED, anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 8))

        self.hash_entry = ctk.CTkEntry(
            inner,
            placeholder_text="e.g.  5f4dcc3b5aa765d61d8327deb882cf99",
            placeholder_text_color=TEXT_MUTED,
            fg_color=ENTRY_BG, border_color=BORDER, border_width=1,
            text_color=ACCENT2,
            font=ctk.CTkFont(family="Consolas", size=12),
            height=44, corner_radius=10,
        )
        self.hash_entry.pack(fill="x", padx=16)
        self.hash_entry.bind("<KeyRelease>", self._auto_detect_hash)

        # Hash type detection badge
        self.hash_type_label = ctk.CTkLabel(
            inner,
            text="🔍  Enter a hash above to auto-detect type",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=TEXT_MUTED, anchor="w",
        )
        self.hash_type_label.pack(fill="x", padx=16, pady=(6, 0))

        # Hash algo selector
        self._label(inner, "HASH ALGORITHM")
        self.algo_var = ctk.StringVar(value="MD5")
        self.algo_menu = ctk.CTkOptionMenu(
            inner,
            values=list(HASH_FUNCTIONS.keys()),
            variable=self.algo_var,
            fg_color=ENTRY_BG,
            button_color=ACCENT,
            button_hover_color="#cc4a1f",
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(family="Consolas", size=12),
            corner_radius=8,
            height=36,
        )
        self.algo_menu.pack(fill="x", padx=16, pady=(4, 0))

        # ── Section: Attack Mode ──────────────────────────────
        self._section(inner, "ATTACK MODE")

        self.attack_var = ctk.StringVar(value="Dictionary")
        modes = [
            ("📖 Dictionary Attack",   "Dictionary",     "Use wordlist of common passwords"),
            ("⚡ Brute-Force Attack",  "BruteForce",     "Try all character combinations"),
            ("🔗 Custom Wordlist",     "Custom",         "Load your own .txt wordlist file"),
            ("🧠 AI Smart Attack",     "AISmartAttack",  "OSINT-based targeted guessing with mutation rules"),
        ]

        self.mode_frames = {}
        for label, value, desc in modes:
            self._radio_card(inner, label, value, desc)

        # ── Dictionary sub-options ────────────────────────────
        self.dict_frame = ctk.CTkFrame(inner, fg_color=CARD_BG, corner_radius=10)
        self.dict_frame.pack(fill="x", padx=16, pady=(6, 0))

        dict_inner = ctk.CTkFrame(self.dict_frame, fg_color="transparent")
        dict_inner.pack(fill="x", padx=14, pady=10)

        # rockyou status label
        self.rockyou_status = ctk.CTkLabel(
            dict_inner, text="🔍  Searching for rockyou.txt…",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=WARN_C, anchor="w",
        )
        self.rockyou_status.pack(fill="x")

        # rockyou path entry + browse
        ry_row = ctk.CTkFrame(dict_inner, fg_color="transparent")
        ry_row.pack(fill="x", pady=(6, 0))

        self.rockyou_path_entry = ctk.CTkEntry(
            ry_row,
            placeholder_text="Path to rockyou.txt (auto-detected or browse)",
            fg_color=ENTRY_BG, border_color=BORDER, border_width=1,
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(family="Consolas", size=10),
            height=32, corner_radius=8,
        )
        self.rockyou_path_entry.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            ry_row, text="Browse",
            width=70, height=32,
            fg_color=ACCENT, hover_color="#cc4a1f",
            text_color="#fff",
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=8,
            command=self._browse_rockyou,
        ).pack(side="left", padx=(6, 0))

        self.dict_fallback_label = ctk.CTkLabel(
            dict_inner,
            text=f"📋  Fallback: built-in {len(BUILTIN_WORDLIST):,} passwords",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=TEXT_MUTED, anchor="w",
        )
        self.dict_fallback_label.pack(fill="x", pady=(4, 0))

        # Auto-detect rockyou on load
        self.after(100, self._detect_rockyou)

        # ── Brute-force sub-options ───────────────────────────
        self.bf_frame = ctk.CTkFrame(inner, fg_color=CARD_BG, corner_radius=10)
        self.bf_frame.pack(fill="x", padx=16, pady=(6, 0))

        bf_inner = ctk.CTkFrame(self.bf_frame, fg_color="transparent")
        bf_inner.pack(fill="x", padx=14, pady=10)

        ctk.CTkLabel(
            bf_inner, text="CHARACTER SET",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED, anchor="w",
        ).pack(fill="x")

        # Charset checkboxes
        self._checks = {}
        charsets = [
            ("Lowercase  a–z",   "lower",   True),
            ("Uppercase  A–Z",   "upper",   True),
            ("Digits  0–9",      "digits",  True),
            ("Symbols  !@#…",   "symbols", False),
        ]
        ck_grid = ctk.CTkFrame(bf_inner, fg_color="transparent")
        ck_grid.pack(fill="x", pady=(6, 0))

        for i, (lbl, key, default) in enumerate(charsets):
            var = ctk.BooleanVar(value=default)
            cb = ctk.CTkCheckBox(
                ck_grid, text=lbl, variable=var,
                font=ctk.CTkFont(family="Consolas", size=11),
                text_color=TEXT_MUTED,
                fg_color=ACCENT, hover_color="#cc4a1f",
                border_color=BORDER, checkmark_color="#fff",
            )
            cb.grid(row=i // 2, column=i % 2, sticky="w", padx=4, pady=2)
            self._checks[key] = var

        # Max length
        len_row = ctk.CTkFrame(bf_inner, fg_color="transparent")
        len_row.pack(fill="x", pady=(10, 0))

        ctk.CTkLabel(
            len_row, text="MAX LENGTH:",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=TEXT_MUTED,
        ).pack(side="left")

        self.max_len_slider = ctk.CTkSlider(
            len_row, from_=1, to=8, number_of_steps=7,
            button_color=ACCENT, button_hover_color="#cc4a1f",
            progress_color=ACCENT, fg_color=BORDER,
            command=self._update_len_label,
            width=120,
        )
        self.max_len_slider.set(4)
        self.max_len_slider.pack(side="left", padx=10)

        self.len_label = ctk.CTkLabel(
            len_row, text="4",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color=ACCENT,
        )
        self.len_label.pack(side="left")

        # ── Custom wordlist sub-options ───────────────────────
        self.custom_frame = ctk.CTkFrame(inner, fg_color=CARD_BG, corner_radius=10)
        self.custom_frame.pack(fill="x", padx=16, pady=(6, 0))

        cus_inner = ctk.CTkFrame(self.custom_frame, fg_color="transparent")
        cus_inner.pack(fill="x", padx=14, pady=10)

        ctk.CTkLabel(
            cus_inner, text="WORDLIST FILE PATH",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED, anchor="w",
        ).pack(fill="x")

        file_row = ctk.CTkFrame(cus_inner, fg_color="transparent")
        file_row.pack(fill="x", pady=(4, 0))

        self.wordlist_path = ctk.CTkEntry(
            file_row,
            placeholder_text="C:\\path\\to\\wordlist.txt",
            fg_color=ENTRY_BG, border_color=BORDER, border_width=1,
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(family="Consolas", size=11),
            height=34, corner_radius=8,
        )
        self.wordlist_path.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            file_row, text="Browse",
            width=70, height=34,
            fg_color=ACCENT, hover_color="#cc4a1f",
            text_color="#fff",
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=8,
            command=self._browse_wordlist,
        ).pack(side="left", padx=(6, 0))

        self.wordlist_count_label = ctk.CTkLabel(
            cus_inner, text="",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=TEXT_MUTED, anchor="w",
        )
        self.wordlist_count_label.pack(fill="x", pady=(4, 0))

        # ── AI Smart Attack sub-options ───────────────────────
        self.ai_frame = ctk.CTkFrame(inner, fg_color=CARD_BG, corner_radius=10,
                                     border_width=1, border_color="#2a1060")
        self.ai_frame.pack(fill="x", padx=16, pady=(6, 0))

        ai_header = ctk.CTkFrame(self.ai_frame, fg_color="#12043a", corner_radius=8)
        ai_header.pack(fill="x", padx=8, pady=(8, 0))
        ctk.CTkLabel(
            ai_header,
            text="🧠  OSINT PROFILE  — enter target's personal data",
            font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
            text_color="#b49cff", anchor="w",
        ).pack(fill="x", padx=10, pady=6)

        ai_inner = ctk.CTkFrame(self.ai_frame, fg_color="transparent")
        ai_inner.pack(fill="x", padx=10, pady=(4, 10))

        def _ai_field(label, placeholder, attr):
            ctk.CTkLabel(
                ai_inner, text=label,
                font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
                text_color="#7b5fff", anchor="w",
            ).pack(fill="x", pady=(6, 1))
            e = ctk.CTkEntry(
                ai_inner,
                placeholder_text=placeholder,
                placeholder_text_color=TEXT_MUTED,
                fg_color=ENTRY_BG, border_color="#2a1060", border_width=1,
                text_color=TEXT_MAIN,
                font=ctk.CTkFont(family="Consolas", size=11),
                height=32, corner_radius=8,
            )
            e.pack(fill="x")
            setattr(self, attr, e)

        _ai_field("FIRST NAME",          "e.g.  john",              "ai_fname")
        _ai_field("LAST NAME",           "e.g.  smith",             "ai_lname")
        _ai_field("DATE OF BIRTH",       "e.g.  1990, 19900415",    "ai_dob")
        _ai_field("PET / NICKNAME",      "e.g.  fluffy, bro",       "ai_pet")
        _ai_field("COMPANY / SCHOOL",    "e.g.  google, mit",       "ai_company")
        _ai_field("KEYWORDS / HOBBIES",  "e.g.  cricket, gaming",   "ai_keywords")
        _ai_field("FAVOURITE NUMBER",    "e.g.  7, 42, 99",         "ai_number")

        # Mutation rule toggles
        ctk.CTkLabel(
            ai_inner, text="MUTATION RULES",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color="#7b5fff", anchor="w",
        ).pack(fill="x", pady=(10, 4))

        self._ai_checks = {}
        ai_rules = [
            ("Leet speak  (a→4, e→3)",    "leet",    True),
            ("Year suffix  (2020–2025)",   "years",   True),
            ("Capitalise variants",         "caps",    True),
            ("Common suffixes  (!,@,#,1)", "suffixes", True),
            ("Reversal",                   "reverse",  False),
            ("Combine fields",             "combine",  True),
        ]
        ck_grid2 = ctk.CTkFrame(ai_inner, fg_color="transparent")
        ck_grid2.pack(fill="x")
        for i, (lbl, key, default) in enumerate(ai_rules):
            var = ctk.BooleanVar(value=default)
            cb = ctk.CTkCheckBox(
                ck_grid2, text=lbl, variable=var,
                font=ctk.CTkFont(family="Consolas", size=10),
                text_color=TEXT_MUTED,
                fg_color="#7b2ff7", hover_color="#5a1fc7",
                border_color="#2a1060", checkmark_color="#fff",
            )
            cb.grid(row=i // 2, column=i % 2, sticky="w", padx=4, pady=2)
            self._ai_checks[key] = var

        # Preview / generate button
        self.ai_preview_btn = ctk.CTkButton(
            ai_inner,
            text="  🔍  Preview Generated Wordlist",
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="transparent", border_width=1, border_color="#7b2ff7",
            hover_color="#1a0840", text_color="#b49cff",
            height=32, corner_radius=8,
            command=self._preview_smart_wordlist,
        )
        self.ai_preview_btn.pack(fill="x", pady=(10, 0))

        self.ai_count_label = ctk.CTkLabel(
            ai_inner, text="",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color="#7b5fff", anchor="w",
        )
        self.ai_count_label.pack(fill="x", pady=(4, 0))

        # ── Show only relevant frame ──────────────────────────
        self.attack_var.trace_add("write", self._on_mode_change)
        self._on_mode_change()

        # ── Buttons ───────────────────────────────────────────
        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(20, 12))

        self.crack_btn = ctk.CTkButton(
            btn_frame,
            text="  💀  Start Cracking",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            fg_color=ACCENT, hover_color="#cc4a1f",
            text_color="#fff",
            height=48, corner_radius=10,
            command=self._start_cracking,
        )
        self.crack_btn.pack(fill="x")

        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="  ⛔  Stop",
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color="transparent", border_width=1, border_color=ERROR_C,
            hover_color="#1a0008",
            text_color=ERROR_C,
            height=38, corner_radius=10,
            state="disabled",
            command=self._stop_cracking,
        )
        self.stop_btn.pack(fill="x", pady=(8, 0))

    # ── RIGHT — Progress & Results ─────────────────────────────
    def _build_right(self, parent):
        right = ctk.CTkFrame(parent, fg_color=PANEL_BG, corner_radius=14,
                              border_width=1, border_color=BORDER)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # ── Result banner ─────────────────────────────────────
        self.result_banner = ctk.CTkFrame(right, fg_color=CARD_BG, corner_radius=12)
        self.result_banner.pack(fill="x", padx=16, pady=(16, 0))

        banner_inner = ctk.CTkFrame(self.result_banner, fg_color="transparent")
        banner_inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(
            banner_inner, text="RESULT",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED, anchor="w",
        ).pack(fill="x")

        self.result_label = ctk.CTkLabel(
            banner_inner,
            text="—  Awaiting crack attempt",
            font=ctk.CTkFont(family="Consolas", size=18, weight="bold"),
            text_color=TEXT_MUTED, anchor="w",
        )
        self.result_label.pack(fill="x", pady=(4, 0))

        # ── Live stats grid ───────────────────────────────────
        stats_frame = ctk.CTkFrame(right, fg_color=CARD_BG, corner_radius=12)
        stats_frame.pack(fill="x", padx=16, pady=(10, 0))

        stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_grid.pack(fill="x", padx=16, pady=14)
        stats_grid.columnconfigure((0, 1, 2, 3), weight=1, uniform="col")

        stat_defs = [
            ("Attempts",  "stat_attempts",  "0"),
            ("Speed",     "stat_speed",     "0/s"),
            ("Elapsed",   "stat_elapsed",   "00:00"),
            ("Progress",  "stat_progress",  "—"),
        ]

        for col, (name, attr, default) in enumerate(stat_defs):
            cell = ctk.CTkFrame(stats_grid, fg_color="transparent")
            cell.grid(row=0, column=col, padx=8, sticky="w")

            ctk.CTkLabel(
                cell, text=name,
                font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
                text_color=TEXT_MUTED,
            ).pack(anchor="w")

            lbl = ctk.CTkLabel(
                cell, text=default,
                font=ctk.CTkFont(family="Consolas", size=16, weight="bold"),
                text_color=ACCENT,
            )
            lbl.pack(anchor="w")
            setattr(self, attr, lbl)

        # ── Progress bar ──────────────────────────────────────
        prog_frame = ctk.CTkFrame(right, fg_color="transparent")
        prog_frame.pack(fill="x", padx=16, pady=(10, 0))

        self.progress_bar = ctk.CTkProgressBar(
            prog_frame,
            height=12,
            corner_radius=6,
            progress_color=ACCENT,
            fg_color=CARD_BG,
            border_color=BORDER,
            border_width=1,
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x")

        self.progress_label = ctk.CTkLabel(
            prog_frame, text="",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=TEXT_MUTED, anchor="w",
        )
        self.progress_label.pack(fill="x", pady=(4, 0))

        # ── Hash generator tool ───────────────────────────────
        ctk.CTkFrame(right, height=1, fg_color=BORDER).pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            right, text="🔧  HASH GENERATOR  (generate a test hash)",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED, anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 6))

        gen_row = ctk.CTkFrame(right, fg_color="transparent")
        gen_row.pack(fill="x", padx=16)

        self.gen_input = ctk.CTkEntry(
            gen_row,
            placeholder_text="Type plain-text password to hash…",
            fg_color=ENTRY_BG, border_color=BORDER, border_width=1,
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(family="Consolas", size=12),
            height=36, corner_radius=8,
        )
        self.gen_input.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            gen_row, text="Hash →",
            width=80, height=36,
            fg_color=ACCENT, hover_color="#cc4a1f",
            text_color="#fff",
            font=ctk.CTkFont(family="Consolas", size=12),
            corner_radius=8,
            command=self._generate_hash,
        ).pack(side="left", padx=(6, 0))

        self.gen_result = ctk.CTkTextbox(
            right,
            fg_color=ENTRY_BG, border_color=BORDER, border_width=1,
            text_color=ACCENT2,
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=8, height=70, wrap="none",
            state="disabled",
        )
        self.gen_result.pack(fill="x", padx=16, pady=(6, 0))

        # ── Activity log ──────────────────────────────────────
        ctk.CTkFrame(right, height=1, fg_color=BORDER).pack(fill="x", padx=16, pady=10)

        ctk.CTkLabel(
            right, text="ACTIVITY LOG",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED, anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 4))

        self.log_box = ctk.CTkTextbox(
            right,
            fg_color=ENTRY_BG, border_color=BORDER, border_width=1,
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(family="Consolas", size=10),
            corner_radius=8, wrap="word",
            state="disabled",
        )
        self.log_box.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    # ══════════════════════════════════════════════════════════
    #  UI Helpers
    # ══════════════════════════════════════════════════════════
    def _section(self, parent, title):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=16, pady=(18, 6))
        ctk.CTkLabel(
            frame, text=title,
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(side="left")
        ctk.CTkFrame(frame, height=1, fg_color=BORDER).pack(
            side="left", fill="x", expand=True, padx=(8, 0), pady=1
        )

    def _label(self, parent, text):
        ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED, anchor="w",
        ).pack(fill="x", padx=16, pady=(12, 4))

    def _radio_card(self, parent, label, value, desc):
        frame = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=10)
        frame.pack(fill="x", padx=16, pady=3)

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=8)

        ctk.CTkRadioButton(
            inner, text=label,
            variable=self.attack_var, value=value,
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color=TEXT_MAIN,
            fg_color=ACCENT, hover_color="#cc4a1f",
            border_color=BORDER,
        ).pack(anchor="w")

        ctk.CTkLabel(
            inner, text=f"   {desc}",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_MUTED, anchor="w",
        ).pack(fill="x")

    def _on_mode_change(self, *_):
        mode = self.attack_var.get()
        self.dict_frame.pack_forget()
        self.bf_frame.pack_forget()
        self.custom_frame.pack_forget()
        self.ai_frame.pack_forget()

        if mode == "Dictionary":
            self.dict_frame.pack(fill="x", padx=16, pady=(6, 0))
        elif mode == "BruteForce":
            self.bf_frame.pack(fill="x", padx=16, pady=(6, 0))
        elif mode == "Custom":
            self.custom_frame.pack(fill="x", padx=16, pady=(6, 0))
        elif mode == "AISmartAttack":
            self.ai_frame.pack(fill="x", padx=16, pady=(6, 0))

    def _update_len_label(self, val):
        self.len_label.configure(text=str(int(val)))

    # ══════════════════════════════════════════════════════════
    #  Hash auto-detection
    # ══════════════════════════════════════════════════════════
    def _auto_detect_hash(self, _=None):
        h = self.hash_entry.get().strip()
        if not h:
            self.hash_type_label.configure(text="🔍  Enter a hash above to auto-detect type", text_color=TEXT_MUTED)
            return

        # Only hex chars = standard hash
        clean = h.replace(" ", "").lower()
        if not all(c in "0123456789abcdef" for c in clean):
            self.hash_type_label.configure(text="⚠  Non-standard hash — may be bcrypt/argon2", text_color=WARN_C)
            return

        detected = HASH_ALGORITHMS.get(len(clean))
        if detected:
            self.hash_type_label.configure(
                text=f"✅  Detected: {detected}  ({len(clean)} hex chars)",
                text_color=SUCCESS_C,
            )
            self.algo_var.set(detected)
        else:
            self.hash_type_label.configure(
                text=f"❓  Unknown hash length ({len(clean)} chars)",
                text_color=WARN_C,
            )

    # ══════════════════════════════════════════════════════════
    #  Hash Generator
    # ══════════════════════════════════════════════════════════
    def _generate_hash(self):
        pw    = self.gen_input.get().strip()
        if not pw:
            return
        algo  = self.algo_var.get()
        fn    = HASH_FUNCTIONS.get(algo, HASH_FUNCTIONS["MD5"])
        h     = fn(pw)

        self.gen_result.configure(state="normal")
        self.gen_result.delete("1.0", "end")
        self.gen_result.insert("1.0",
            f"Algorithm : {algo}\n"
            f"Hash      : {h}"
        )
        self.gen_result.configure(state="disabled")

        # Auto-paste into hash field
        self.hash_entry.delete(0, "end")
        self.hash_entry.insert(0, h)
        self._auto_detect_hash()
        self._log(f"Generated {algo} hash for testing")

    # ══════════════════════════════════════════════════════════
    #  Browse wordlist
    # ══════════════════════════════════════════════════════════
    def _browse_wordlist(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Select Wordlist File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path:
            self.wordlist_path.delete(0, "end")
            self.wordlist_path.insert(0, path)
            try:
                with open(path, "r", errors="ignore") as f:
                    lines = f.readlines()
                self.wordlist_count_label.configure(
                    text=f"✅  {len(lines):,} words loaded",
                    text_color=SUCCESS_C,
                )
                self._log(f"Loaded wordlist: {os.path.basename(path)} ({len(lines):,} words)")
            except Exception as e:
                self.wordlist_count_label.configure(text=f"⚠  {e}", text_color=ERROR_C)

    # ══════════════════════════════════════════════════════════
    #  Start / Stop Cracking
    # ══════════════════════════════════════════════════════════
    def _start_cracking(self):
        target_hash = self.hash_entry.get().strip().lower()
        if not target_hash:
            self._log("⚠  Please enter a hash value to crack.")
            return

        self._stop_event.clear()
        self._running   = True
        self._attempts  = 0
        self._result    = None
        self._start_time= time.time()

        self.progress_bar.set(0)
        self.progress_bar.configure(progress_color=ACCENT)
        self.result_label.configure(text="⚙  Cracking…", text_color=ACCENT)
        self.stat_attempts.configure(text="0")
        self.stat_speed.configure(text="0/s")
        self.stat_elapsed.configure(text="00:00")
        self.stat_progress.configure(text="—")

        self.crack_btn.configure(state="disabled", text="  ⏳  Running…")
        self.stop_btn.configure(state="normal")

        mode = self.attack_var.get()
        algo = self.algo_var.get()

        self._log(f"▶  Starting {mode} attack on {algo} hash")
        self._log(f"   Hash: {target_hash[:32]}{'…' if len(target_hash) > 32 else ''}")

        # Start stats updater
        self._update_stats_loop()

        # Start cracking thread
        if mode == "Dictionary":
            t = threading.Thread(target=self._dict_attack, args=(target_hash, algo), daemon=True)
        elif mode == "BruteForce":
            t = threading.Thread(target=self._brute_force_attack, args=(target_hash, algo), daemon=True)
        elif mode == "Custom":
            t = threading.Thread(target=self._custom_wordlist_attack, args=(target_hash, algo), daemon=True)
        elif mode == "AISmartAttack":
            t = threading.Thread(target=self._ai_smart_attack, args=(target_hash, algo), daemon=True)
        else:
            self._log("⚠  Unknown attack mode.")
            self._reset_buttons()
            return
        t.start()

    def _stop_cracking(self):
        self._stop_event.set()
        self._running = False
        self._log("⛔  Cracking stopped by user.")
        self.crack_btn.configure(state="normal", text="  💀  Start Cracking")
        self.stop_btn.configure(state="disabled")
        self.result_label.configure(text="⛔  Stopped", text_color=WARN_C)

    # ══════════════════════════════════════════════════════════
    #  rockyou.txt auto-detect & browse
    # ══════════════════════════════════════════════════════════
    def _detect_rockyou(self):
        path = _find_rockyou()
        if path:
            self._set_rockyou_path(path)
        else:
            self.rockyou_status.configure(
                text="⚠  rockyou.txt not found — browse to locate it or use fallback",
                text_color=WARN_C,
            )

    def _set_rockyou_path(self, path):
        size_mb = os.path.getsize(path) / (1024 * 1024)
        self.rockyou_path_entry.delete(0, "end")
        self.rockyou_path_entry.insert(0, path)
        self.rockyou_status.configure(
            text=f"✅  rockyou.txt found  ({size_mb:.1f} MB)",
            text_color=SUCCESS_C,
        )
        self._log(f"rockyou.txt detected: {path} ({size_mb:.1f} MB)")

    def _browse_rockyou(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Select rockyou.txt or any wordlist",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path:
            self._set_rockyou_path(path)

    # ══════════════════════════════════════════════════════════
    #  Attack Implementations
    # ══════════════════════════════════════════════════════════
    def _dict_attack(self, target_hash, algo):
        fn   = HASH_FUNCTIONS[algo]
        path = self.rockyou_path_entry.get().strip()

        # ── Stream rockyou.txt line-by-line (memory efficient) ──
        if path and os.path.isfile(path):
            file_size = os.path.getsize(path)
            self.after(0, lambda: self._log(f"   Using rockyou.txt ({file_size/(1024*1024):.1f} MB) — streaming…"))
            bytes_read = 0

            try:
                with open(path, "r", errors="ignore", buffering=1024*1024) as f:
                    for i, line in enumerate(f):
                        if self._stop_event.is_set():
                            return
                        word = line.strip()
                        if not word:
                            continue
                        self._attempts += 1
                        bytes_read += len(line.encode("utf-8", errors="ignore"))

                        if fn(word) == target_hash:
                            self.after(0, lambda w=word: self._on_cracked(w))
                            return

                        if i % 10000 == 0:
                            prog = min(bytes_read / file_size, 1.0)
                            self.after(0, lambda p=prog: self.progress_bar.set(p))
                            self.after(0, lambda a=self._attempts: self.stat_progress.configure(
                                text=f"{a:,} tried"
                            ))
            except Exception as e:
                self.after(0, lambda: self._log(f"⚠  Error reading rockyou.txt: {e}"))
                self.after(0, self._on_not_found)
                return
        else:
            # ── Fallback: built-in wordlist ──────────────────────
            self.after(0, lambda: self._log(f"   rockyou.txt not set — using built-in {len(BUILTIN_WORDLIST):,} passwords"))
            total = len(BUILTIN_WORDLIST)
            for i, word in enumerate(BUILTIN_WORDLIST):
                if self._stop_event.is_set():
                    return
                self._attempts += 1
                if fn(word) == target_hash:
                    self.after(0, lambda w=word: self._on_cracked(w))
                    return
                if i % 50 == 0:
                    prog = (i + 1) / total
                    self.after(0, lambda p=prog: self.progress_bar.set(p))
                    self.after(0, lambda p=i+1, t=total: self.stat_progress.configure(
                        text=f"{p}/{t}"
                    ))

        self.after(0, self._on_not_found)

    def _brute_force_attack(self, target_hash, algo):
        fn       = HASH_FUNCTIONS[algo]
        max_len  = int(self.max_len_slider.get())

        # Build charset
        charset = ""
        if self._checks["lower"].get():  charset += string.ascii_lowercase
        if self._checks["upper"].get():  charset += string.ascii_uppercase
        if self._checks["digits"].get(): charset += string.digits
        if self._checks["symbols"].get(): charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        if not charset:
            self.after(0, lambda: self._log("⚠  Select at least one character set."))
            self.after(0, self._reset_buttons)
            return

        # Estimate total combinations
        total = sum(len(charset) ** length for length in range(1, max_len + 1))
        self.after(0, lambda: self._log(f"   Charset size: {len(charset)}, Max combos: {total:,}"))

        count = 0
        for length in range(1, max_len + 1):
            if self._stop_event.is_set():
                return
            for combo in itertools.product(charset, repeat=length):
                if self._stop_event.is_set():
                    return
                word = "".join(combo)
                self._attempts += 1
                count += 1

                if fn(word) == target_hash:
                    self.after(0, lambda w=word: self._on_cracked(w))
                    return

                if count % 5000 == 0:
                    progress = min(count / total, 1.0)
                    self.after(0, lambda p=progress: self.progress_bar.set(p))
                    self.after(0, lambda c=count, t=total: self.stat_progress.configure(
                        text=f"{c:,}/{t:,}"
                    ))

        self.after(0, self._on_not_found)

    # ══════════════════════════════════════════════════════════
    #  AI Smart Attack — OSINT-powered targeted mutation engine
    # ══════════════════════════════════════════════════════════
    def _generate_smart_wordlist(self):
        """
        Build a targeted wordlist from the user's OSINT profile fields.
        Returns a list of (password, rule_description) tuples.
        """
        # ── Collect profile fields ────────────────────────────
        fname   = self.ai_fname.get().strip().lower()
        lname   = self.ai_lname.get().strip().lower()
        dob_raw = self.ai_dob.get().strip()
        pet     = self.ai_pet.get().strip().lower()
        company = self.ai_company.get().strip().lower()
        kw_raw  = self.ai_keywords.get().strip().lower()
        number  = self.ai_number.get().strip()

        keywords_raw = kw_raw.replace(",", " ").split()

        # All base tokens
        bases = []
        if fname:   bases.append((fname,   "first name"))
        if lname:   bases.append((lname,   "last name"))
        if pet:     bases.append((pet,     "pet/nickname"))
        if company: bases.append((company, "company/school"))
        for kw in keywords_raw:
            if kw: bases.append((kw, f"keyword '{kw}'"))

        # Parse date-of-birth tokens
        dob_tokens = []
        digits_only = "".join(c for c in dob_raw if c.isdigit())
        if len(digits_only) >= 4:
            dob_tokens.append(digits_only[:4])          # year e.g. 1995
        if len(digits_only) >= 8:
            dob_tokens.append(digits_only[2:8])         # YYMMDD
            dob_tokens.append(digits_only[4:8])         # MMDD
            dob_tokens.append(digits_only[6:8])         # DD
            dob_tokens.append(digits_only[:8])          # full YYYYMMDD

        common_years = ["2020", "2021", "2022", "2023", "2024", "2025",
                        "1990", "1991", "1992", "1993", "1994", "1995",
                        "1996", "1997", "1998", "1999", "2000", "2001"]
        year_suffixes = list(dict.fromkeys(dob_tokens[:1] + common_years))
        if dob_tokens:
            year_suffixes = list(dict.fromkeys(dob_tokens + common_years))

        common_suffixes = ["1", "12", "123", "!", "@", "#", "@123", "!123",
                           "321", "007", "666", "777", "999", "000"]
        if number:
            common_suffixes = [number] + common_suffixes

        # ── Leet speak substitution map ───────────────────────
        leet_map = {
            "a": "4", "e": "3", "i": "1", "o": "0",
            "s": "5", "t": "7", "b": "8", "g": "9",
            "l": "1", "z": "2",
        }

        def leet(word):
            return "".join(leet_map.get(c, c) for c in word)

        def leet_partial(word):
            """Replace only first occurrence of each leet char."""
            result = list(word)
            for i, c in enumerate(result):
                if c in leet_map:
                    result[i] = leet_map[c]
                    break
            return "".join(result)

        wordlist = []   # (password, rule)
        seen     = set()

        def add(pw, rule):
            if pw and 4 <= len(pw) <= 20 and pw not in seen:
                seen.add(pw)
                wordlist.append((pw, rule))

        do_leet     = self._ai_checks["leet"].get()
        do_years    = self._ai_checks["years"].get()
        do_caps     = self._ai_checks["caps"].get()
        do_suffixes = self._ai_checks["suffixes"].get()
        do_reverse  = self._ai_checks["reverse"].get()
        do_combine  = self._ai_checks["combine"].get()

        # ── Phase 1: Single-token mutations ──────────────────
        for base, origin in bases:
            add(base, f"plain  [{origin}]")

            if do_caps:
                add(base.capitalize(), f"capitalised  [{origin}]")
                add(base.upper(),      f"ALL CAPS  [{origin}]")
                add(base.capitalize() + base.capitalize(), f"doubled-cap  [{origin}]")

            if do_leet:
                add(leet(base),         f"full leet  [{origin}]")
                add(leet_partial(base), f"partial leet  [{origin}]")
                if do_caps:
                    add(leet(base).capitalize(), f"leet+cap  [{origin}]")

            if do_reverse:
                add(base[::-1], f"reversed  [{origin}]")
                if do_caps:
                    add(base[::-1].capitalize(), f"reversed+cap  [{origin}]")

            if do_years:
                for yr in year_suffixes:
                    add(base + yr,              f"[{origin}] + year {yr}")
                    add(yr + base,              f"year {yr} + [{origin}]")
                    if do_caps:
                        add(base.capitalize() + yr, f"cap+year  [{origin}]+{yr}")
                    if do_leet:
                        add(leet(base) + yr,    f"leet+year  [{origin}]+{yr}")

            if do_suffixes:
                for sfx in common_suffixes:
                    add(base + sfx,              f"[{origin}] + suffix '{sfx}'")
                    add(base.capitalize() + sfx, f"cap+suffix  [{origin}]+'{sfx}'")
                    if do_leet:
                        add(leet(base) + sfx,   f"leet+suffix  [{origin}]+'{sfx}'")

        # ── Phase 2: Field combinations ───────────────────────
        if do_combine and len(bases) >= 2:
            combos = [
                (bases[0], bases[1]),
            ]
            if len(bases) >= 3:
                combos.append((bases[0], bases[2]))
            if fname and lname:
                fl = fname + lname
                lf = lname + fname
                add(fl, "first+last")
                add(lf, "last+first")
                add(fl.capitalize(), "First+last cap")
                add(fname[0] + lname, "initial+last")
                add(fname + lname[0], "first+initial")
                if do_years:
                    for yr in year_suffixes[:4]:
                        add(fl + yr,             f"first+last+{yr}")
                        add(fl.capitalize() + yr, f"First+last+{yr}")
                if do_suffixes:
                    for sfx in common_suffixes[:6]:
                        add(fl + sfx,             f"first+last+'{sfx}'")
                if do_leet:
                    add(leet(fl), "leet(first+last)")

            for (b1, o1), (b2, o2) in combos:
                add(b1 + b2, f"[{o1}]+[{o2}]")
                if do_years:
                    for yr in year_suffixes[:3]:
                        add(b1 + b2 + yr, f"[{o1}]+[{o2}]+{yr}")
                if do_suffixes:
                    for sfx in common_suffixes[:4]:
                        add(b1 + b2 + sfx, f"[{o1}]+[{o2}]+'{sfx}'")

        # ── Phase 3: DOB-specific patterns ───────────────────
        for dtok in dob_tokens:
            add(dtok, f"bare DOB token '{dtok}'")
            for base, origin in bases:
                add(base + dtok, f"[{origin}]+DOB '{dtok}'")
                if do_caps:
                    add(base.capitalize() + dtok, f"cap+DOB [{origin}]+'{dtok}'")

        # ── Phase 4: Keyboard patterns + base ────────────────
        keyboard_appends = ["qwerty", "1234", "12345", "abcd"]
        for ka in keyboard_appends:
            for base, origin in bases:
                add(base + ka, f"[{origin}]+keyboard '{ka}'")

        return wordlist

    def _preview_smart_wordlist(self):
        """Show first 30 entries of the generated wordlist in the log box."""
        wl = self._generate_smart_wordlist()
        if not wl:
            self._log("⚠  Fill in at least one profile field first.")
            return
        self._log(f"🧠  Generated {len(wl):,} targeted candidates. Preview (first 30):")
        for pw, rule in wl[:30]:
            self._log(f"   • {pw:<22}  ← {rule}")
        self._log(f"   …and {max(0, len(wl)-30):,} more")
        self.ai_count_label.configure(
            text=f"✅  {len(wl):,} candidates ready",
        )

    def _ai_smart_attack(self, target_hash, algo):
        """Run the AI Smart Attack using the generated targeted wordlist."""
        fn = HASH_FUNCTIONS[algo]
        wordlist = self._generate_smart_wordlist()

        if not wordlist:
            self.after(0, lambda: self._log(
                "⚠  No profile data entered!\n"
                "   Fill in at least one field in the OSINT Profile."
            ))
            self.after(0, self._reset_buttons)
            return

        total = len(wordlist)
        self.after(0, lambda: self._log(
            f"🧠  AI Smart Attack: {total:,} targeted candidates generated"
        ))
        self.after(0, lambda: self._log(
            "   Applying OSINT mutations: leet, years, caps, combos…"
        ))

        for i, (word, rule) in enumerate(wordlist):
            if self._stop_event.is_set():
                return

            self._attempts += 1

            if fn(word) == target_hash:
                # Log the winning rule before calling _on_cracked
                self.after(0, lambda r=rule: self._log(
                    f"🎯  Matched via rule: {r}"
                ))
                self.after(0, lambda w=word: self._on_cracked(w))
                return

            # Every 50 attempts, show progress + last tried word
            if i % 50 == 0:
                prog = (i + 1) / total
                self.after(0, lambda p=prog: self.progress_bar.set(p))
                self.after(0, lambda p=i+1, t=total: self.stat_progress.configure(
                    text=f"{p}/{t}"
                ))
                self.after(0, lambda w=word, r=rule: self.result_label.configure(
                    text=f"⚙  Trying:  {w}  [{r}]",
                    text_color=ACCENT,
                ))

        # ── If not cracked, also try built-in wordlist as fallback ──
        self.after(0, lambda: self._log(
            "   Profile exhausted — falling back to built-in common list…"
        ))
        for i, word in enumerate(BUILTIN_WORDLIST):
            if self._stop_event.is_set():
                return
            self._attempts += 1
            if fn(word) == target_hash:
                self.after(0, lambda r="common password list (fallback)": self._log(
                    f"🎯  Matched via rule: {r}"
                ))
                self.after(0, lambda w=word: self._on_cracked(w))
                return

        self.after(0, self._on_not_found)

    def _custom_wordlist_attack(self, target_hash, algo):
        path = self.wordlist_path.get().strip()
        if not path or not os.path.exists(path):
            self.after(0, lambda: self._log("⚠  Wordlist file not found."))
            self.after(0, self._reset_buttons)
            return

        fn = HASH_FUNCTIONS[algo]
        try:
            with open(path, "r", errors="ignore") as f:
                words = [line.strip() for line in f if line.strip()]
        except Exception as e:
            self.after(0, lambda: self._log(f"⚠  Error reading file: {e}"))
            self.after(0, self._reset_buttons)
            return

        total = len(words)
        self.after(0, lambda: self._log(f"   Testing {total:,} passwords from wordlist…"))

        for i, word in enumerate(words):
            if self._stop_event.is_set():
                return
            self._attempts += 1

            if fn(word) == target_hash:
                self.after(0, lambda w=word: self._on_cracked(w))
                return

            if i % 100 == 0:
                prog = (i + 1) / total
                self.after(0, lambda p=prog: self.progress_bar.set(p))
                self.after(0, lambda p=i+1, t=total: self.stat_progress.configure(
                    text=f"{p:,}/{t:,}"
                ))

        self.after(0, self._on_not_found)

    # ══════════════════════════════════════════════════════════
    #  Result handlers
    # ══════════════════════════════════════════════════════════
    def _on_cracked(self, password):
        elapsed = time.time() - self._start_time
        self._running = False
        self.progress_bar.set(1)
        self.progress_bar.configure(progress_color=SUCCESS_C)
        self.result_label.configure(
            text=f"✅  CRACKED!   →   {password}",
            text_color=SUCCESS_C,
        )
        self._log(f"✅  PASSWORD FOUND: '{password}'")
        self._log(f"   Attempts: {self._attempts:,}  |  Time: {elapsed:.2f}s")
        self._reset_buttons()

        # Record to stats
        try:
            stats_tracker.record_password_cracked(password, self.algo_var.get())
        except Exception:
            pass

        # Copy to clipboard
        try:
            import pyperclip
            pyperclip.copy(password)
            self._log("   ✔ Copied to clipboard")
        except Exception:
            pass

    def _on_not_found(self):
        self._running = False
        self.progress_bar.set(1)
        self.progress_bar.configure(progress_color=ERROR_C)
        self.result_label.configure(
            text="❌  Password NOT found in this attack",
            text_color=ERROR_C,
        )
        elapsed = time.time() - self._start_time
        self._log(f"❌  Not found after {self._attempts:,} attempts ({elapsed:.2f}s)")
        self._log("   Try a different attack mode or wordlist.")
        self._reset_buttons()

    def _reset_buttons(self):
        self.crack_btn.configure(state="normal", text="  💀  Start Cracking")
        self.stop_btn.configure(state="disabled")

    # ══════════════════════════════════════════════════════════
    #  Live stats updater
    # ══════════════════════════════════════════════════════════
    def _update_stats_loop(self):
        if not self._running:
            return
        elapsed = time.time() - self._start_time
        speed   = int(self._attempts / elapsed) if elapsed > 0 else 0
        td      = str(timedelta(seconds=int(elapsed)))[2:]  # mm:ss

        self.stat_attempts.configure(text=f"{self._attempts:,}")
        self.stat_speed.configure(text=f"{speed:,}/s")
        self.stat_elapsed.configure(text=td)

        self.after(300, self._update_stats_loop)

    # ── Helpers ───────────────────────────────────────────────
    def _log(self, msg):
        ts = time.strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{ts}] {msg}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
