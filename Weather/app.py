from dotenv import load_dotenv
import os
import requests
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from io import BytesIO
from datetime import datetime
import threading

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except:
    MATPLOTLIB_AVAILABLE = False

load_dotenv()
API_KEY = os.getenv("WEATHERAPI_KEY")
if not API_KEY:
    raise ValueError("API key not found")

def fetch_json(url, params=None, timeout=10):
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()

def detect_location_by_ip():
    data = fetch_json("https://ipinfo.io/json")
    city = data.get("city")
    region = data.get("region")
    country = data.get("country")
    if city:
        return f"{city},{region},{country}"
    loc = data.get("loc")
    if loc:
        return loc
    raise RuntimeError("IP location failed")

def build_weatherapi_url(endpoint="forecast.json"):
    return f"https://api.weatherapi.com/v1/{endpoint}"

class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Weather App")
        self.geometry("760x520")
        self.resizable(False, False)
        self.create_gradient()
        self.create_theme()
        self.unit = tk.StringVar(value="C")
        self._icon_image = None
        self._hourly_chart_canvas = None
        self.create_widgets()

    def create_gradient(self):
        self.bg_canvas = tk.Canvas(self, width=760, height=520, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0)

        for i in range(520):
            r = int(20 + (i / 520) * 20)
            g = int(20 + (i / 520) * 40)
            b = int(40 + (i / 520) * 80)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.bg_canvas.create_line(0, i, 760, i, fill=color)

    def create_theme(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TFrame",
            background="#10131a"
        )
        style.configure(
            "TLabelframe",
            background="#10131a",
            foreground="#ffffff",
            borderwidth=1,
            relief="solid"
        )
        style.configure(
            "TLabelframe.Label",
            background="#10131a",
            foreground="#d0d0d0"
        )
        style.configure(
            "TLabel",
            background="#10131a",
            foreground="#e8e8e8"
        )
        style.configure(
            "TEntry",
            fieldbackground="#1a1d26",
            foreground="white",
            insertcolor="white"
        )
        style.configure(
            "TButton",
            background="#222632",
            foreground="white",
            padding=6
        )
        style.map("TButton", background=[("active", "#303646")])

    def create_widgets(self):
        top_frame = ttk.Frame(self, padding=10)
        top_frame.place(x=0, y=0, relwidth=1)
        ttk.Label(top_frame, text="Location:").pack(side="left")
        self.location_entry = ttk.Entry(top_frame, width=30)
        self.location_entry.pack(side="left", padx=(6, 4))
        self.location_entry.insert(0, "Mumbai")
        ttk.Button(top_frame, text="Get Weather", command=self.on_get_weather).pack(side="left", padx=4)
        ttk.Button(top_frame, text="Use my location", command=self.on_use_my_location).pack(side="left", padx=4)
        unit_frame = ttk.Frame(top_frame)
        unit_frame.pack(side="right")
        ttk.Radiobutton(unit_frame, text="°C", variable=self.unit, value="C", command=self.on_unit_change).pack(side="left")
        ttk.Radiobutton(unit_frame, text="°F", variable=self.unit, value="F", command=self.on_unit_change).pack(side="left")
        body = ttk.Frame(self, padding=10)
        body.place(y=60, relwidth=1, relheight=0.85)
        left = ttk.Frame(body)
        left.pack(side="left", fill="y", padx=(0,10))
        self.city_lbl = ttk.Label(left, text="City, Country", font=("Segoe UI", 14, "bold"))
        self.city_lbl.pack(anchor="w")
        self.updated_lbl = ttk.Label(left, text="Last updated:")
        self.updated_lbl.pack(anchor="w", pady=(2,8))
        icon_temp = ttk.Frame(left)
        icon_temp.pack(anchor="w")
        self.icon_label = ttk.Label(icon_temp)
        self.icon_label.pack(side="left", padx=(0,10))
        temp_frame = ttk.Frame(icon_temp)
        temp_frame.pack(side="left")
        self.temp_lbl = ttk.Label(temp_frame, text="--°", font=("Segoe UI", 28))
        self.temp_lbl.pack(anchor="w")
        self.cond_lbl = ttk.Label(temp_frame, text="")
        self.cond_lbl.pack(anchor="w")
        details = ttk.Frame(left)
        details.pack(anchor="w", pady=(10,0))
        self.feels_lbl = ttk.Label(details, text="Feels like:")
        self.feels_lbl.pack(anchor="w")
        self.wind_lbl = ttk.Label(details, text="Wind:")
        self.wind_lbl.pack(anchor="w")
        self.humidity_lbl = ttk.Label(details, text="Humidity:")
        self.humidity_lbl.pack(anchor="w")
        right = ttk.Frame(body)
        right.pack(side="left", fill="both", expand=True)
        hourly_frame = ttk.LabelFrame(right, text="Hourly (today)")
        hourly_frame.pack(fill="x", pady=(0,8))
        self.hourly_list = tk.Listbox(hourly_frame, height=6, bg="#1a1d26", fg="white")
        self.hourly_list.pack(fill="x", padx=4, pady=4)
        forecast_frame = ttk.LabelFrame(right, text="3-day Forecast")
        forecast_frame.pack(fill="x")
        self.forecast_tree = ttk.Treeview(
            forecast_frame,
            columns=("date","maxt","mint","condition"),
            show="headings",
            height=3
        )
        self.forecast_tree.heading("date", text="Date")
        self.forecast_tree.heading("maxt", text="Max")
        self.forecast_tree.heading("mint", text="Min")
        self.forecast_tree.heading("condition", text="Condition")
        self.forecast_tree.column("date", width=120)
        self.forecast_tree.column("maxt", width=70, anchor="center")
        self.forecast_tree.column("mint", width=70, anchor="center")
        self.forecast_tree.column("condition", width=200)
        self.forecast_tree.pack(fill="x", padx=4, pady=4)
        if MATPLOTLIB_AVAILABLE:
            chart_frame = ttk.LabelFrame(right, text="Hourly Temperature Chart")
            chart_frame.pack(fill="both", expand=True, pady=(8,0))
            self.chart_container = chart_frame
        self.status_lbl = ttk.Label(self, text="Ready", relief="sunken", anchor="w")
        self.status_lbl.place(x=0, y=498, relwidth=1)

    def on_get_weather(self):
        location = self.location_entry.get().strip()
        if not location:
            return
        threading.Thread(target=self.fetch_and_display, args=(location,), daemon=True).start()

    def on_use_my_location(self):
        self.status("Detecting location...")
        def run():
            try:
                q = detect_location_by_ip()
                self.location_entry.delete(0, tk.END)
                self.location_entry.insert(0, q)
                self.fetch_and_display(q)
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.status("Ready")
        threading.Thread(target=run, daemon=True).start()

    def on_unit_change(self):
        loc = self.location_entry.get().strip()
        if loc:
            threading.Thread(target=self.fetch_and_display, args=(loc,), daemon=True).start()

    def status(self, text):
        self.status_lbl.config(text=text)

    def fetch_and_display(self, location_query):
        self.status("Fetching...")
        try:
            params = {"key": API_KEY, "q": location_query, "days": 3, "aqi": "no", "alerts": "no"}
            data = fetch_json(build_weatherapi_url(), params=params)
            self.after(0, lambda: self.update_ui(data))
            self.status("Ready")
        except Exception as e:
            self.status("Error")
            messagebox.showerror("Error", str(e))

    def update_ui(self, data):
        location = data["location"]
        current = data["current"]
        forecast = data["forecast"]
        self.city_lbl.config(text=f"{location['name']}, {location['country']}")
        self.updated_lbl.config(text=f"Last updated: {current['last_updated']}")
        if self.unit.get() == "C":
            temp = current["temp_c"]
            feels = current["feelslike_c"]
            max_key = "maxtemp_c"
            min_key = "mintemp_c"
        else:
            temp = current["temp_f"]
            feels = current["feelslike_f"]
            max_key = "maxtemp_f"
            min_key = "mintemp_f"
        self.temp_lbl.config(text=f"{temp:.1f}°{self.unit.get()}")
        self.cond_lbl.config(text=current["condition"]["text"])
        self.feels_lbl.config(text=f"Feels like: {feels:.1f}°{self.unit.get()}")
        self.wind_lbl.config(text=f"Wind: {current['wind_kph']} kph / {current['wind_mph']} mph")
        self.humidity_lbl.config(text=f"Humidity: {current['humidity']}%")
        icon_url = "https:" + current["condition"]["icon"]
        r = requests.get(icon_url)
        img = Image.open(BytesIO(r.content)).resize((64,64))
        self._icon_image = ImageTk.PhotoImage(img)
        self.icon_label.config(image=self._icon_image)
        today = forecast["forecastday"][0]["date"]
        hourly = next(fd["hour"] for fd in forecast["forecastday"] if fd["date"] == today)
        self.hourly_list.delete(0, tk.END)
        times = []
        temps = []
        for h in hourly:
            tstr = h["time"].split(" ")[1]
            if self.unit.get() == "C":
                t = h["temp_c"]
            else:
                t = h["temp_f"]
            self.hourly_list.insert(tk.END, f"{tstr} — {t:.1f}°{self.unit.get()} — {h['condition']['text']}")
            times.append(tstr)
            temps.append(t)
        for i in self.forecast_tree.get_children():
            self.forecast_tree.delete(i)
        for fd in forecast["forecastday"][:3]:
            d = fd["date"]
            day = fd["day"]
            ma = day[max_key]
            mi = day[min_key]
            cond = day["condition"]["text"]
            self.forecast_tree.insert("", tk.END, values=(
                d,
                f"{ma:.1f}°{self.unit.get()}",
                f"{mi:.1f}°{self.unit.get()}",
                cond,
            ))
        if MATPLOTLIB_AVAILABLE:
            self.draw_chart(times, temps)
    def draw_chart(self, times, temps):
        if hasattr(self, "_chart_widget") and self._chart_widget:
            self._chart_widget.get_tk_widget().destroy()
            self._chart_widget = None
        fig, ax = plt.subplots(figsize=(6,2.5), dpi=100)
        ax.plot(range(len(temps)), temps, marker="o")
        ax.set_xticks(range(len(times)))
        labels = [t if i % max(1, len(times)//8) == 0 else "" for i, t in enumerate(times)]
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_ylabel(f"Temp (°{self.unit.get()})")
        ax.set_title("Hourly Temperature")
        fig.patch.set_facecolor("#10131a")
        ax.set_facecolor("#151821")
        ax.tick_params(axis="x", colors="white")
        ax.tick_params(axis="y", colors="white")
        ax.title.set_color("white")
        ax.yaxis.label.set_color("white")
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        self._chart_widget = canvas
        canvas.get_tk_widget().pack(fill="both", expand=True)

def main():
    app = WeatherApp()
    app.mainloop()
if __name__ == "__main__":
    main()
