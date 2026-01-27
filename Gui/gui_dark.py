import tkinter as tk
from tkinter import messagebox

# Function to update label text
def update_label(text):
    label.config(text=text)

# Function to show a message box
def show_message():
    messagebox.showinfo("Info", "Button Clicked!")

# Create the main window
root = tk.Tk()
root.title("Dark Mode GUI")
root.geometry("300x200")

# Set Dark Mode Colors
bg_color = "#2E2E2E"  # Dark Gray Background
fg_color = "#FFFFFF"  # White Text
btn_color = "#555555"  # Darker Buttons
btn_text_color = "#FFFFFF"

root.configure(bg=bg_color)

# Create a label
label = tk.Label(root, text="Click a button", font=("Arial", 14), fg=fg_color, bg=bg_color)
label.pack(pady=10)

# Create buttons
button1 = tk.Button(root, text="Say Hello", command=lambda: update_label("Hello!"),
                    bg=btn_color, fg=btn_text_color)
button1.pack(pady=5)

button2 = tk.Button(root, text="Say Goodbye", command=lambda: update_label("Goodbye!"),
                    bg=btn_color, fg=btn_text_color)
button2.pack(pady=5)

button3 = tk.Button(root, text="Show Message", command=show_message,
                    bg=btn_color, fg=btn_text_color)
button3.pack(pady=5)

# Run the Tkinter event loop
root.mainloop()

