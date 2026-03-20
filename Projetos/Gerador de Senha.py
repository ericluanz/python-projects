import random
from tkinter import *
from tkinter import messagebox
import pyperclip

gui = Tk()
gui.title('Password Generator')
gui.geometry('250x200')
gui.resizable(0,0)

def process():
    try:
        length = int(string_pass.get())
    except:
        messagebox.showerror("Erro", "Digite um número válido")
        return

    lower = list('abcdefghijklmnopqrstuvwxyz')
    upper = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    num = list('0123456789')
    special = list('@#$%&*')

    chars = lower + upper + num + special

    password = "".join(random.choices(chars, k=length))

    messagebox.showinfo('Result', f'Your password {password}\n\nPassword copied to clipboard')
    pyperclip.copy(password)

string_pass = StringVar()

Label(text="Password Length").pack(pady=10)

txt = Entry(textvariable=string_pass)
txt.pack()

Button(text="Generator", command=process).pack(pady=10)

gui.mainloop()
