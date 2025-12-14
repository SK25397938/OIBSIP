import tkinter as tk
from tkinter import messagebox
import secrets
import string

def generate_password():
    try:
        length = int(length_entry.get())
        if length < 8:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Input", "Password length must be at least 8")
        return
    use_upper = upper_var.get()
    use_lower = lower_var.get()
    use_digits = digit_var.get()
    use_symbols = symbol_var.get()
    if not (use_upper or use_lower or use_digits or use_symbols):
        messagebox.showerror("Selection Error", "Select at least one character type")
        return
    exclude_chars = exclude_entry.get()
    char_pool = ""
    if use_upper:
        char_pool += string.ascii_uppercase
    if use_lower:
        char_pool += string.ascii_lowercase
    if use_digits:
        char_pool += string.digits
    if use_symbols:
        char_pool += string.punctuation
    for ch in exclude_chars:
        char_pool = char_pool.replace(ch, "")
    if not char_pool:
        messagebox.showerror("Error", "Character pool is empty after exclusions")
        return
    password = []
    if use_upper:
        password.append(secrets.choice(string.ascii_uppercase))
    if use_lower:
        password.append(secrets.choice(string.ascii_lowercase))
    if use_digits:
        password.append(secrets.choice(string.digits))
    if use_symbols:
        password.append(secrets.choice(string.punctuation))
    while len(password) < length:
        password.append(secrets.choice(char_pool))
    secrets.SystemRandom().shuffle(password)
    password_entry.delete(0, tk.END)
    password_entry.insert(0, "".join(password))

def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(password_entry.get())
    messagebox.showinfo("Copied", "Password copied to clipboard!")

root = tk.Tk()
root.title("SecurePass - Password Generator")
root.geometry("420x420")
root.resizable(False, False)
tk.Label(root, text="Password Length", font=("Arial", 10)).pack(pady=5)
length_entry = tk.Entry(root)
length_entry.pack()
length_entry.insert(0, "12")
upper_var = tk.BooleanVar(value=True)
lower_var = tk.BooleanVar(value=True)
digit_var = tk.BooleanVar(value=True)
symbol_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Uppercase Letters", variable=upper_var).pack(anchor="w", padx=40)
tk.Checkbutton(root, text="Lowercase Letters", variable=lower_var).pack(anchor="w", padx=40)
tk.Checkbutton(root, text="Numbers", variable=digit_var).pack(anchor="w", padx=40)
tk.Checkbutton(root, text="Symbols", variable=symbol_var).pack(anchor="w", padx=40)
tk.Label(root, text="Exclude Characters (optional)").pack(pady=5)
exclude_entry = tk.Entry(root)
exclude_entry.pack()
tk.Button(root, text="Generate Password", command=generate_password, bg="#4CAF50", fg="white").pack(pady=10)
password_entry = tk.Entry(root, width=30, font=("Arial", 12))
password_entry.pack(pady=5)
tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard).pack()

root.mainloop()
