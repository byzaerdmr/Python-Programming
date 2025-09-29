#Lab-3, Variant 4 (tkinter keygen)

import random
import string
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

try:
    from PIL import Image, ImageTk
    _HAVE_PIL = True
except Exception:
    _HAVE_PIL = False

# ---------------- Keygen core ----------------

LETTERS = string.ascii_uppercase           # A..Z
DIGITS  = string.digits                    # 0..9
ALPHABET = LETTERS + DIGITS
INTERVAL_MIN, INTERVAL_MAX = 30, 35        # inclusive
BLOCKS = 3
BLOCK_LEN = 4

def weight(ch: str) -> int:
    """Return weight: A=1..Z=26, digits 0..9."""
    if ch.isdigit():
        return int(ch)
    return ord(ch) - ord('A') + 1

def block_sum(block: str) -> int:
    return sum(weight(c) for c in block)

def generate_block() -> str:

    while True:
        first_three = [random.choice(ALPHABET) for _ in range(3)]
        s3 = sum(weight(c) for c in first_three)
        T = random.randint(INTERVAL_MIN, INTERVAL_MAX)
        need = T - s3

        # Pick the 4th char to match 'need'
        if 0 <= need <= 9:
            last_char = str(need)
        elif 1 <= need <= 26:
            last_char = chr(ord('A') + need - 1)
        else:
            continue  # try again

        block = ''.join(first_three) + last_char
        # Safety check
        if INTERVAL_MIN <= block_sum(block) <= INTERVAL_MAX:
            return block

def generate_key() -> str:
    """Generate XXXX-XXXX-XXXX with each block satisfying the rule."""
    return "-".join(generate_block() for _ in range(BLOCKS))

def validate_key(k: str):

    parts = k.split("-")
    if len(parts) != BLOCKS or any(len(p) != BLOCK_LEN for p in parts):
        return False, [], "Invalid format"
    sums = []
    for p in parts:
        if not all(c in ALPHABET for c in p):
            return False, [], "Invalid characters"
        s = block_sum(p)
        sums.append(s)
        if not (INTERVAL_MIN <= s <= INTERVAL_MAX):
            return False, sums, "Block sum out of bounds"
    return True, sums, None

# ---------------- Tkinter App ----------------

class KeygenApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Key Generator — Variant 4")
        self.geometry("720x420")
        self.resizable(False, False)

        self._set_background_if_exists()
        self._build_ui()

    def _set_background_if_exists(self):

        base = Path(__file__).parent
        candidates = [base / "bg_pic.png"]

        bg_path = next((p for p in candidates if p.exists()), None)
        print("[BG] cwd           :", Path.cwd())
        print("[BG] script dir    :", base)
        print("[BG] candidates    :", [str(p) for p in candidates])
        print("[BG] chosen        :", str(bg_path) if bg_path else "None (no background)")

        self._bg_label = None
        self._bg_imgtk = None
        self._bg_src_pil = None

        if not bg_path:
            return  # nothing to show

        try:
            if bg_path.suffix.lower() == ".png" and not _HAVE_PIL:

                self._bg_imgtk = tk.PhotoImage(file=str(bg_path))
                self._bg_label = tk.Label(self, image=self._bg_imgtk)
                self._bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                self._bg_label.lower()
            else:
                if not _HAVE_PIL:
                    print("[BG] Pillow not installed; PNG is recommended if you need background.")
                    return

                self._bg_src_pil = Image.open(bg_path)
                self._bg_label = tk.Label(self)
                self._bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                self._bg_label.lower()

                def redraw(_=None):
                    w = max(self.winfo_width(), 1)
                    h = max(self.winfo_height(), 1)
                    img = self._bg_src_pil.resize((w, h), Image.LANCZOS)
                    self._bg_imgtk = ImageTk.PhotoImage(img)
                    self._bg_label.configure(image=self._bg_imgtk)

                self.bind("<Configure>", redraw)
                self.after(0, redraw)
        except Exception as e:
            print("[BG] load failed:", e)

    def _build_ui(self):
        # Foreground frame
        self.frame = ttk.Frame(self, padding=18)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        title_lbl = ttk.Label(self.frame, text="Key Generator", font=("Arial", 16, "bold"))
        title_lbl.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # Key output (readonly)
        ttk.Label(self.frame, text="Key:").grid(row=2, column=0, sticky="e", padx=(0, 8))
        self.key_var = tk.StringVar()
        self.key_entry = ttk.Entry(self.frame, textvariable=self.key_var, width=34, state="readonly", justify="center")
        self.key_entry.grid(row=2, column=1, columnspan=2, sticky="we", pady=6)

        # Buttons
        gen_btn = ttk.Button(self.frame, text="Generate", command=self.on_generate)
        gen_btn.grid(row=3, column=1, sticky="we", pady=6)
        copy_btn = ttk.Button(self.frame, text="Copy", command=self.on_copy)
        copy_btn.grid(row=3, column=2, sticky="we", padx=(8, 0), pady=6)

        # Sums label
        self.sums_var = tk.StringVar(value="Sums: ––")
        self.sums_lbl = ttk.Label(self.frame, textvariable=self.sums_var)
        self.sums_lbl.grid(row=4, column=0, columnspan=3, pady=(4, 0))

        # Key bindings
        self.bind("<Return>", lambda e: self.on_generate())
        self.bind("<Escape>", lambda e: self.destroy())

        # Initial key
        self.on_generate()

    def on_generate(self):
        k = generate_key()
        self.key_var.set(k)
        ok, sums, err = validate_key(k)
        if ok:
            self.sums_var.set(f"Sums: {sums[0]} - {sums[1]} - {sums[2]} ")
        else:
            self.sums_var.set(f"Sums: {sums}  (Invalid: {err})")

    def on_copy(self):
        k = self.key_var.get()
        if not k:
            messagebox.showinfo("Copy", "Nothing to copy.")
            return
        self.clipboard_clear()
        self.clipboard_append(k)
        self.update()  # keep clipboard content after app closes
        messagebox.showinfo("Copy", "Key copied to clipboard.")

if __name__ == "__main__":
    random.seed()  # fresh seed each run
    app = KeygenApp()
    app.mainloop()
