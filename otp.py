import base64
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import string
import secrets
from itertools import cycle

KEY_LETTERS = tuple(string.ascii_letters + string.punctuation + string.digits)
APP_TITLE = 'OTP'

class Entry(tk.Entry):

    def __init__(self,master = None ,defaulttext = '', defaultfg='#3e3e3e', *args, **kwargs):
        super().__init__(master,*args, **kwargs)
        self.defaultfg = defaultfg
        self.mainfg = self['fg']
        self.defaulttext = defaulttext
        if not self['textvariable']:
            self.insert(0, defaulttext)
            self.config(fg=defaultfg)

        self.bind('<FocusIn>', self._focus_in_handler)
        self.bind('<FocusOut>', self._focus_out_handler)

    def _focus_in_handler(self, event=None):
        if self.get() == self.defaulttext and self['fg'] == self.defaultfg:
            self.delete(0, tk.END)
            self.config(fg=self.mainfg)

    def _focus_out_handler(self, event=None):
        if not self.get() or (self.get() == self.defaulttext and self['fg'] == self.defaultfg):
            self.insert(0, self.defaulttext)
            self.config(fg=self.defaultfg)


class Text(tk.Text):

    def __init__(self,master = None ,defaulttext = '', defaultfg='#3e3e3e', *args, **kwargs):
        super().__init__(master,*args, **kwargs)
        self.defaultfg = defaultfg
        self.mainfg = self['fg']
        self.defaulttext = defaulttext
        self.insert('1.0', defaulttext)
        self.config(fg=defaultfg)

        self.bind('<FocusIn>', self._focus_in_handler)
        self.bind('<FocusOut>', self._focus_out_handler)

    def _focus_in_handler(self, event=None):
        if self.get('1.0', tk.END)[:-1] == self.defaulttext and self['fg'] == self.defaultfg:
            self.delete('1.0', tk.END)
            self.config(fg=self.mainfg)

    def _focus_out_handler(self, event=None):
        if not self.get('1.0', tk.END)[:-1] or (self.get('1.0', tk.END)[:-1] == self.defaulttext and self['fg'] == self.defaultfg):
            self.insert('1.0', self.defaulttext)
            self.config(fg=self.defaultfg)

def decode_text(encrypted_text):
    try:
        return base64.b64decode(encrypted_text).decode()
    except:
        messagebox.showerror(title = APP_TITLE, message = 'You should enter a base64 text to decrypt it')
        return

def convert_hex(key):
    try:
        return bytes.fromhex(key)
    except:
        messagebox.showerror(title = APP_TITLE, message = 'Your key is not hexadecimal')
        return

def encrypt(text,key):
    if use_hex_var.get():
        key = convert_hex(key)
        if not key:
            return
    key = cycle(key)
    encrypted_text = ''
    if use_hex_var.get():
        for char in text:
            encrypted_text += chr(ord(char)+next(key))
    else:
        for char in text:
            encrypted_text += chr(ord(char)+ord(next(key)))
    return base64.b64encode(encrypted_text.encode())

def decrypt(encrypted_text,key):
    if use_hex_var.get():
        key = convert_hex(key)
        if not key:
            return
    encrypted_text = decode_text(encrypted_text)
    if not encrypted_text:
        return
    
    key = cycle(key)
    decrypted_text = ''
    if use_hex_var.get():
        for char in encrypted_text:
            decrypted_text += chr(ord(char)-next(key))
    else:
        for char in encrypted_text:
            decrypted_text += chr(ord(char)-ord(next(key)))
    return decrypted_text

def check():
    try:
        if var.get():
            data = encrypt(input_text.get('1.0','end'), key_entry.get())
        else:
            data = decrypt(input_text.get('1.0','end'), key_entry.get())
        if data:
            output_text.delete('1.0','end')
            output_text.insert('1.0', data)
    except:
        messagebox.showerror(title=APP_TITLE, message='An error occured while decrypting. Your key is probably wrong')

def create_random_key():
    key_entry.delete(0, 'end')
    key = ''
    text_length = len(input_text.get('1.0', 'end')[:-1])
    if not use_hex_var.get():
        for i in range(text_length):
            key += secrets.choice(KEY_LETTERS)
    else:
        key = secrets.token_hex(text_length)
    key_entry.insert(0, key)

def copy_entry():
    window.clipboard_clear()
    window.clipboard_append(key_entry.get())

def copy_text(widget):
    window.clipboard_clear()
    window.clipboard_append(widget.get('1.0', 'end'))

def create_context_menu(is_entry):
    context_menu = tk.Menu(tearoff=0)
    context_menu.add_command(label='Select All', accelerator='Ctrl+A')
    context_menu.add_command(label='Copy', accelerator='Ctrl+C')
    context_menu.add_command(label='Paste', accelerator='Ctrl+V')
    context_menu.add_command(label='Cut', accelerator='Ctrl+X')
    context_menu.add_separator()
    if is_entry:
        context_menu.add_command(label='Copy Key', command=lambda : copy_entry())
        context_menu.add_command(label='Delete Key', command=lambda : key_entry.delete(0,'end'))
    if not is_entry:
        context_menu.add_command()
        context_menu.add_command()
    return context_menu

def configure_menu(event, context_menu):
    if isinstance(event.widget, Text):
        if event.widget == input_text:
            context_menu.entryconfigure(5, label='Copy Input')
            context_menu.entryconfigure(6, label='Clear Input')
            context_menu.entryconfigure(5, command=lambda: copy_text(event.widget))
            context_menu.entryconfigure(6, command=lambda: event.widget.delete('1.0', 'end'))
        elif event.widget == output_text:
            context_menu.entryconfigure(5, label='Copy Output')
            context_menu.entryconfigure(6, label='Clear Output')
            context_menu.entryconfigure(5, command=lambda: copy_text(event.widget))
            context_menu.entryconfigure(6, command=lambda: event.widget.delete('1.0', 'end'))

    if window.focus_get() == event.widget:
        for i in range(4):
            context_menu.entryconfigure(i, state='normal')
        if isinstance(event.widget, Text):
            context_menu.entryconfigure(0, command=lambda: event.widget.tag_add('sel', '1.0', 'end'))
        else:
            context_menu.entryconfigure(0, command=lambda: event.widget.select_range(0, 'end'))

        context_menu.entryconfigure(1, command=lambda: event.widget.event_generate('<<Copy>>'))
        context_menu.entryconfigure(2, command=lambda: event.widget.event_generate('<<Paste>>'))
        context_menu.entryconfigure(3, command=lambda: event.widget.event_generate('<<Cut>>'))
    else:
        for i in range(4):
            context_menu.entryconfigure(i, state='disabled')

    return context_menu

def show_menu(event, context_menu):
    context_menu = configure_menu(event, context_menu)
    context_menu.tk_popup(event.x_root, event.y_root)

window = tk.Tk()

text_menu = create_context_menu(False)
key_entry_menu = create_context_menu(True)

window.title(APP_TITLE)

var = tk.IntVar(value=1)
frm1 = tk.Frame(bd=5)
encrypt_rb = ttk.Radiobutton(frm1,text='Encrypt', variable=var, value=1, command = lambda : btn_convert.config(text='Encrypt'))
decrypt_rb = ttk.Radiobutton(frm1,text='Decrypt', variable=var, value=0, command = lambda : btn_convert.config(text='Decrypt'))
encrypt_rb.pack(side='left',padx=(0,10))
decrypt_rb.pack(side='left',padx=(10,0))
frm1.pack()

frm3 = tk.Frame(bd=5)
frm_text1 = tk.Frame(frm3)
frm_text2 = tk.Frame(frm3)
yscroll_text1 = tk.Scrollbar(frm_text1)
yscroll_text2 = tk.Scrollbar(frm_text2)
input_text = Text(frm_text1,yscrollcommand=yscroll_text1.set, width=35, height=10, defaulttext='Enter the text here', font = 'TkTextFont', defaultfg='#3a3a3a')
output_text = Text(frm_text2,yscrollcommand=yscroll_text2.set, width=35, height=10, defaulttext='The output will be shown here', font = 'TkTextFont', defaultfg='#3a3a3a')
yscroll_text1.config(command=input_text.yview)
yscroll_text2.config(command=output_text.yview)
btn_convert = ttk.Button(frm3,text='Encrypt', command=check)

input_text.pack(side='left', fill='both', expand=1)
yscroll_text1.pack(side='left', fill='y')
output_text.pack(side='left', fill='both', expand=1)
yscroll_text2.pack(side='left', fill='y')

frm2 = tk.Frame(bd = 5)
key_entry = Entry(frm2, defaulttext='Enter the key here')
random_btn = ttk.Button(frm2,text='random', command=create_random_key)
use_hex_var = tk.IntVar()
use_hex_cb = ttk.Checkbutton(frm2,text='Use hex key', variable=use_hex_var)

use_hex_cb.grid(row = 0,column = 0)
key_entry.grid(row=1, column=0, sticky='w', pady=5)
random_btn.grid(row=1,column=1, padx=5)

frm_text1.pack(side='left', fill='both', expand=1)
btn_convert.pack(side='left', padx=10)
frm_text2.pack(side='left',fill='both', expand=1)

window.bind_class('Text','<Button-3>', lambda event : show_menu(event, text_menu))
key_entry.bind('<Button-3>', lambda event : show_menu(event, key_entry_menu))

frm2.pack(anchor='w')
frm3.pack(fill='both', expand=1)

window.mainloop()