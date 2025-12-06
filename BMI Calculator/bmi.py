import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
from datetime import datetime

DB_FILENAME = "bmi_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()
    c.execute(""" CREATE TABLE IF NOT EXISTS bmi_entries (id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT,recorded_at TEXT,weight_kg REAL,height_cm REAL,bmi REAL,category TEXT);""")
    conn.commit()
    conn.close()

def get_bmi_data(bmi):
    if bmi < 18.5:
        return "Underweight", "#6A99D5"  
    elif bmi < 25:
        return "Normal", "#6DBC70"     
    elif bmi < 30:
        return "Overweight", "#FFD700"  
    else:
        return "Obese", "#E06666"       

class BMIResultDialog(tk.Toplevel):
    def __init__(self, parent, bmi_value, category, color):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        self.title("BMI Result")
        self.parent = parent
        self.bmi_value = bmi_value
        self.category = category
        self.color = color
        self.result_max = 40.0  
        self.bar_target_width = min(bmi_value / self.result_max, 1.0) 
        self.current_width = 0
        self.geometry("350x200")
        self.resizable(False, False)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.configure(bg="#F0F0F0")
        self.build_ui()
        self.animate_bar()

    def build_ui(self):
        ttk.Label(self, text=f"BMI: {self.bmi_value:.2f}", font=("Segoe UI Semibold", 16)).pack(pady=(15, 5))
        ttk.Label(self, text=f"Category: {self.category}", font=("Segoe UI", 14), foreground=self.color).pack(pady=(0, 10))
        bar_frame = ttk.Frame(self)
        bar_frame.pack(pady=10, padx=20, fill='x')
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Horizontal.TProgressbar", 
                        background=self.color, 
                        troughcolor="#EAEAEA", 
                        bordercolor="#CCCCCC",
                        thickness=15)
        self.progress_bar = ttk.Progressbar(bar_frame, style="Custom.Horizontal.TProgressbar", orient="horizontal", length=300, mode="determinate", maximum=self.result_max)
        self.progress_bar.pack(fill='x')
        ttk.Button(self, text="OK", command=self.destroy, width=10).pack(pady=15)
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.parent.winfo_screenwidth() // 2) - (width // 2)
        y = (self.parent.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def animate_bar(self):
        target_value = self.bmi_value
        if self.current_width < target_value:
            step = (target_value - self.current_width) / 10 + 0.1
            self.current_width += step
            if self.current_width > target_value:
                self.current_width = target_value  
            self.progress_bar["value"] = self.current_width
            self.after(30, self.animate_bar)
        else:
            self.progress_bar["value"] = target_value
            
class GradientFrame(tk.Canvas):
    def __init__(self, parent, color1, color2, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.bind("<Configure>", self._draw_gradient)

    def _draw_gradient(self, event=None):
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        (r1, g1, b1) = self.winfo_rgb(self.color1)
        (r2, g2, b2) = self.winfo_rgb(self.color2)
        r_ratio = (r2 - r1) / height
        g_ratio = (g2 - g1) / height
        b_ratio = (b2 - b1) / height
        for i in range(height):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = f"#{nr//256:02x}{ng//256:02x}{nb//256:02x}"
            self.create_line(0, i, width, i, tags=("gradient"), fill=color)
        self.lower("gradient")

class BMICalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BMI Calculator")
        self.geometry("650x650")
        self.resizable(False, False)
        init_db()
        self.style_widgets()
        self.bg = GradientFrame(self, "#74ebd5", "#ACB6E5")  
        self.bg.pack(fill="both", expand=True)
        self.build_ui()
        self.populate_user_list()
        if self.user_combobox["values"]:
             self.user_combobox.set(self.user_combobox["values"][0])
             self.load_statistics()

    def style_widgets(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Card.TFrame",
                        background="#FFFFFF",
                        borderwidth=0,
                        relief="flat")
        style.configure("TLabel",
                        background="#FFFFFF",
                        font=("Segoe UI", 11))
        style.configure("Title.TLabel",
                        background="#FFFFFF",
                        font=("Segoe UI Semibold", 16))
        style.configure("Glow.TButton",
                        font=("Segoe UI Semibold", 11),
                        padding=(12, 8),
                        background="#4D73FF", 
                        foreground="#FFFFFF") 
        style.map("Glow.TButton",
                  background=[("active", "#3A60E0")],
                  foreground=[("active", "#FFFFFF"), ("!active", "#FFFFFF")])

    def build_ui(self):
        self.input_row_counter = 1 
        input_card = ttk.Frame(self.bg, style="Card.TFrame", padding=20)
        input_card.place(relx=0.5, rely=0.25, anchor="center", width=460)
        ttk.Label(input_card, text="BMI Calculator", style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 10))
        self.entry_username = self._entry(input_card, "Username")
        self.entry_weight = self._entry(input_card, "Weight (kg)")
        self.entry_height = self._entry(input_card, "Height (cm)")
        calc_btn = ttk.Button(input_card,text="Calculate & Save",style="Glow.TButton",command=self.calculate_bmi)
        calc_btn.grid(row=self.input_row_counter, column=0, columnspan=2, pady=15) 
        self.input_row_counter += 1
        stats_card = ttk.Frame(self.bg, style="Card.TFrame", padding=20)
        stats_card.place(relx=0.5, rely=0.58, anchor="center", width=460)
        ttk.Label(stats_card, text="User Statistics", style="Title.TLabel").pack()
        ttk.Label(stats_card, text="Select User:").pack(pady=(10, 0))
        self.user_combobox = ttk.Combobox(stats_card, state="readonly", width=25)
        self.user_combobox.pack(pady=5)
        self.user_combobox.bind("<<ComboboxSelected>>", lambda e: self.load_statistics())
        self.stat_latest = ttk.Label(stats_card, text="Latest BMI: -")
        self.stat_trend = ttk.Label(stats_card, text="Trend: -")
        self.stat_latest.pack(pady=2)
        self.stat_trend.pack(pady=2)
        btn_frame = ttk.Frame(self.bg)
        btn_frame.place(relx=0.5, rely=0.88, anchor="center")
        ttk.Button(btn_frame, text="Delete History",
                   style="Glow.TButton",
                   command=self.delete_user_history).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Export CSV",
                   style="Glow.TButton",
                   command=self.export_history_csv).grid(row=0, column=1, padx=10)

    def _entry(self, parent, label):
        parent.grid_columnconfigure(0, weight=1) 
        parent.grid_columnconfigure(1, weight=1) 
        ttk.Label(parent, text=label).grid(row=self.input_row_counter, column=0, sticky="e", padx=(0, 10), pady=3)
        e = ttk.Entry(parent, width=25)
        e.grid(row=self.input_row_counter, column=1, pady=3, sticky="w")
        self.input_row_counter += 1
        return e

    def populate_user_list(self):
        conn = sqlite3.connect(DB_FILENAME)
        c = conn.cursor()
        c.execute("SELECT DISTINCT username FROM bmi_entries ORDER BY username")
        users = [u[0] for u in c.fetchall()]
        conn.close()
        self.user_combobox["values"] = users

    def calculate_bmi(self):
        username = self.entry_username.get().strip()
        weight = self.entry_weight.get().strip()
        height = self.entry_height.get().strip()
        if not username or not weight or not height:
            messagebox.showwarning("Missing Info", "Fill all fields.")
            return
        try:
            weight = float(weight)
            height = float(height)
        except:
            messagebox.showerror("Error", "Invalid numeric values.")
            return
        bmi = weight / ((height / 100) ** 2) 
        cat, color = get_bmi_data(bmi)
        conn = sqlite3.connect(DB_FILENAME)
        c = conn.cursor()
        c.execute(""" INSERT INTO bmi_entries (username, recorded_at, weight_kg, height_cm, bmi, category) VALUES (?, ?, ?, ?, ?, ?)""",
                  (username, datetime.now().isoformat(), weight, height, bmi, cat))
        conn.commit()
        conn.close()
        BMIResultDialog(self, bmi, cat, color)
        self.populate_user_list()
        self.user_combobox.set(username)
        self.load_statistics()

    def load_statistics(self):
        username = self.user_combobox.get()
        if not username:
            self.stat_latest.config(text="Latest BMI: -")
            self.stat_trend.config(text="Trend: -")
            return
        conn = sqlite3.connect(DB_FILENAME)
        c = conn.cursor()
        c.execute("SELECT bmi FROM bmi_entries WHERE username = ? ORDER BY recorded_at", (username,))
        bmis = [r[0] for r in c.fetchall()]
        conn.close()
        if not bmis:
            return
        latest = bmis[-1]
        trend_delta = latest - bmis[0]
        if abs(trend_delta) < 0.2:
            trend = "Stable"
        elif trend_delta > 0:
            trend = f"Increasing (+{trend_delta:.2f})"
        else:
            trend = f"Decreasing ({trend_delta:.2f})"
        self.stat_latest.config(text=f"Latest BMI: {latest:.2f} ({get_bmi_data(latest)[0]})")
        self.stat_trend.config(text=f"Trend: {trend}")

    def delete_user_history(self):
        username = self.user_combobox.get()
        if not username:
            messagebox.showinfo("Info", "No user selected.")
            return
        if messagebox.askyesno("Confirm", f"Delete all history for '{username}'?"):
            conn = sqlite3.connect(DB_FILENAME)
            c = conn.cursor()
            c.execute("DELETE FROM bmi_entries WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            self.populate_user_list()
            self.user_combobox.set("")
            self.load_statistics()
            messagebox.showinfo("Deleted", "History removed.")

    def export_history_csv(self):
        username = self.user_combobox.get()
        if not username:
            messagebox.showinfo("Info", "Select a user to export data.")
            return
        conn = sqlite3.connect(DB_FILENAME)
        c = conn.cursor()
        c.execute("""SELECT id, username, recorded_at, weight_kg, height_cm, bmi, category FROM bmi_entries WHERE username = ? ORDER BY recorded_at ASC """,
                  (username,))
        rows = c.fetchall()
        conn.close()
        if not rows:
            messagebox.showinfo("No Data", "No history to export.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=f"BMI_History_{username}.csv"
        )
        if not file_path:
            return
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Username", "Recorded At", "Weight (kg)", "Height (cm)", "BMI", "Category"])
            writer.writerows(rows)
        messagebox.showinfo("Exported", "CSV file saved successfully.")
if __name__ == "__main__":
    BMICalculatorApp().mainloop()