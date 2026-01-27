#!/usr/bin/python3

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
root.title("Simple GUI Example")
root.geometry("300x200")  # Set window size

# Create a label
label = tk.Label(root, text="Click a button", font=("Arial", 14))
label.pack(pady=10)

# Create buttons
button1 = tk.Button(root, text="Say Hello", command=lambda: update_label("Hello!"))
button1.pack(pady=5)

button2 = tk.Button(root, text="Say Goodbye", command=lambda: update_label("Goodbye!"))
button2.pack(pady=5)

button3 = tk.Button(root, text="Show Message", command=show_message)
button3.pack(pady=5)

# Run the Tkinter event loop
root.mainloop()
