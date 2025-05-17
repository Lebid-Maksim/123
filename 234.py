from customtkinter import *
from socket import *
import threading


class LogiTalkApp(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('800x600')
        self.title('LogiTalk - Чат')

        self.username = None

        # Кольори
        self.bg_color = '#e0f7fa'
        self.menu_color = '#00bcd4'
        self.chat_bg_color = '#ffffff'
        self.user_msg_color = '#a7ffeb'
        self.other_msg_color = '#d1c4e9'

        self.configure(fg_color=self.bg_color)
        self.frame_width = 0
        self.is_show_menu = False

        self.init_registration_ui()

        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect(('127.0.0.1', 5555))
        threading.Thread(target=self.recv_message, daemon=True).start()

    def init_registration_ui(self):
        self.registration_frame = CTkFrame(self)
        self.registration_frame.pack(expand=True)

        label = CTkLabel(self.registration_frame, text="Введіть ваше ім'я:", font=("Arial", 18))
        label.pack(pady=10)

        self.name_entry = CTkEntry(self.registration_frame, placeholder_text="Ваше ім'я")
        self.name_entry.pack(pady=10)

        start_btn = CTkButton(self.registration_frame, text="Почати чат", command=self.start_chat)
        start_btn.pack(pady=10)

    def start_chat(self):
        name = self.name_entry.get().strip()
        if name:
            self.username = name
            self.registration_frame.destroy()
            self.init_chat_ui()

    def init_chat_ui(self):
        self.frame = CTkFrame(self, width=0, fg_color=self.menu_color, corner_radius=0)
        self.frame.pack_propagate(False)
        self.frame.place(x=0, y=0, relheight=1)

        self.btn_menu = CTkButton(self, text='≡', command=self.toggle_menu, width=40, height=40,
                                  fg_color='#006064', text_color='white', corner_radius=20)
        self.btn_menu.place(x=10, y=10)

        self.messages_frame = CTkScrollableFrame(self, fg_color=self.chat_bg_color, corner_radius=20)
        self.entry = CTkEntry(self, placeholder_text='Напишіть щось...', height=40, corner_radius=20)
        self.btn_send = CTkButton(self, text='➤', width=40, height=40, corner_radius=20,
                                  command=self.send_message)

        self.entry.bind("<Return>", lambda event: self.send_message())
        self.entry.focus_set()

        self.update_ui()

    def update_ui(self):
        win_w = self.winfo_width()
        win_h = self.winfo_height()
        menu_w = self.frame.winfo_width()
        padding = 20
        input_height = 50

        self.messages_frame.place(x=menu_w + padding, y=padding + 50)
        self.messages_frame.configure(width=win_w - menu_w - 2 * padding, height=win_h - input_height - 3 * padding - 50)

        self.entry.place(x=menu_w + padding, y=win_h - input_height - padding)
        self.entry.configure(width=win_w - menu_w - 3 * padding - 50)

        self.btn_send.place(x=win_w - padding - 50, y=win_h - input_height - padding)

        self.after(50, self.update_ui)

    def toggle_menu(self):
        self.is_show_menu = not self.is_show_menu
        if self.is_show_menu:
            self.show_menu()
        else:
            self.hide_menu()

    def show_menu(self):
        if self.frame_width < 220:
            self.frame_width += 5
            self.frame.configure(width=self.frame_width)
            self.after(10, self.show_menu)

    def hide_menu(self):
        if self.frame_width > 0:
            self.frame_width -= 5
            self.frame.configure(width=self.frame_width)
            self.after(10, self.hide_menu)

    def send_message(self):
        text = self.entry.get().strip()
        if text:
            full_message = f"{self.username}: {text}"
            self.create_message_bubble(full_message, sender='user')
            self.entry.delete(0, END)
            self.socket.sendall(full_message.encode())

    def recv_message(self):
        while True:
            data = self.socket.recv(1024).decode()
            if ':' in data:
                sender_name, message = data.split(':', 1)
                sender_name = sender_name.strip()
                message = message.strip()
                sender = 'user' if sender_name == self.username else 'other'
                self.create_message_bubble(f"{sender_name}: {message}", sender=sender)

    def create_message_bubble(self, text, sender='user'):
        bubble_color = self.user_msg_color if sender == 'user' else self.other_msg_color
        align = 'e' if sender == 'user' else 'w'

        msg_frame = CTkFrame(self.messages_frame, fg_color=bubble_color, corner_radius=15)
        msg_label = CTkLabel(msg_frame, text=text, wraplength=300, justify=LEFT, text_color='#000000')
        msg_label.pack(padx=10, pady=5)
        msg_frame.pack(anchor=align, pady=5, padx=10)


if __name__ == '__main__':
    app = LogiTalkApp()
    app.mainloop()