import tkinter as tk
from tkinter import messagebox

# Function to update label with user input
def update_label():
    text = entry0.get()
    if text:
        label.config(text=f"Hello, {text}!")
    else:
        label.config(text="Please enter a name!")

# Function to show message if toggle is ON
def show_message():
    if toggle_var.get():
        messagebox.showinfo("Info", "You have enabled the toggle!")
    else:
        messagebox.showwarning("Warning", "Toggle is OFF!")

# Function to update color theme
def update_theme():
    if theme_var.get() == "dark":
        root.configure(bg="#2E2E2E")
        label.config(bg="#2E2E2E", fg="white")
    else:
        root.configure(bg="white")
        label.config(bg="white", fg="black")

# Function to close the application
def exit_app():
    root.destroy()

# Create main window
root = tk.Tk()
root.title("Enhanced GUI")
root.geometry("350x300")
root.configure(bg="black")  # Default black mode

# Create a label
label = tk.Label(root, text="Enter your name:", font=("Arial", 14), bg="white")
label.pack(pady=5)

# Create an entry field with default text
entry0 = tk.Entry(root, font=("Arial", 12))
entry0.insert(0, "Your Name")  # Default value
entry0.pack(pady=5)

# Create an entry field with default text
entry1 = tk.Entry(root, font=("Arial", 12))
entry1.insert(0, "10000")  # Default value
entry1.pack(pady=5)


# Button to update label
btn_update = tk.Button(root, text="Greet Me", command=update_label)
btn_update.pack(pady=5)

# Toggle Checkbutton
toggle_var = tk.BooleanVar(value=False)
toggle_button = tk.Checkbutton(root, text="Enable Feature", variable=toggle_var, command=show_message)
toggle_button.pack(pady=5)

# Theme selection using Radiobuttons
theme_var = tk.StringVar(value="dark")  # Default theme
rb_light = tk.Radiobutton(root, text="Light Mode", variable=theme_var, value="light", command=update_theme)
rb_dark = tk.Radiobutton(root, text="Dark Mode", variable=theme_var, value="dark", command=update_theme)

rb_light.pack(pady=2)
rb_dark.pack(pady=2)

# Exit Button
exit_button = tk.Button(root, text="Exit", command=exit_app, bg="red", fg="white")
exit_button.pack(pady=10)

# Run Tkinter event loop
root.mainloop()
