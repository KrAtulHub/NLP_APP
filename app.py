from tkinter import *
from tkinter import messagebox
import threading
from mydb import Database
from myapi import API, APIError


class NLP_App:

    def __init__(self):

        self.db = Database()
        self.api = API()

        self.root = Tk()
        self.root.title("NLP App")
        self.root.geometry("400x600")
        self.root.config(bg="#f0f0f0")

        self.login_gui()

        self.root.mainloop()

    def clear(self):

        for widget in self.root.pack_slaves():
            widget.destroy()

    def login_gui(self):

        self.clear()

        Label(
            self.root,
            text="Welcome to NLP App",
            font=("Arial", 20, "bold"),
            bg="#f0f0f0",
        ).pack(pady=20)

        Label(self.root, text="Enter Email", font=("Arial", 12), bg="#f0f0f0").pack(
            pady=10
        )

        self.email_input = Entry(self.root, font=("Arial", 12))
        self.email_input.pack(pady=10)

        Label(self.root, text="Enter Password", font=("Arial", 12), bg="#f0f0f0").pack(
            pady=10
        )

        self.password_input = Entry(self.root, font=("Arial", 12), show="*")
        self.password_input.pack(pady=10)

        Button(
            self.root,
            text="Login",
            font=("Arial", 12, "bold"),
            bg="#80B782",
            fg="white",
            command=self.perform_login,
        ).pack(pady=20)

        Label(
            self.root, text="Don't have an account?", font=("Arial", 11), bg="#f0f0f0"
        ).pack(pady=10)

        Button(
            self.root,
            text="Sign Up",
            font=("Arial", 10, "bold"),
            bg="#80B782",
            fg="white",
            command=self.Register_gui,
        ).pack()

    def Register_gui(self):

        self.clear()

        Label(
            self.root,
            text="Create New Account",
            font=("Arial", 20, "bold"),
            bg="#f0f0f0",
        ).pack(pady=20)

        Label(self.root, text="Enter Email", font=("Arial", 12), bg="#f0f0f0").pack(
            pady=10
        )

        self.email_input = Entry(self.root, font=("Arial", 12))
        self.email_input.pack(pady=10)

        Label(self.root, text="Enter Password", font=("Arial", 12), bg="#f0f0f0").pack(
            pady=10
        )

        self.password_input = Entry(self.root, font=("Arial", 12), show="*")
        self.password_input.pack(pady=10)

        Button(
            self.root,
            text="Register",
            font=("Arial", 12, "bold"),
            bg="#80B782",
            fg="white",
            command=self.perform_registration,
        ).pack(pady=20)

        Button(
            self.root,
            text="Back to Login",
            font=("Arial", 10, "bold"),
            bg="#80B782",
            fg="white",
            command=self.login_gui,
        ).pack()

    def perform_registration(self):

        email = self.email_input.get()
        password = self.password_input.get()

        success = self.db.add_data(email, password)

        if success:

            messagebox.showinfo("Success", "Registration Successful")

            self.login_gui()

        else:

            messagebox.showerror("Error", "Email already exists")

    def perform_login(self):

        email = self.email_input.get()
        password = self.password_input.get()

        success = self.db.validate_login(email, password)

        if success:

            messagebox.showinfo("Success", "Login Successful")

            self.home_gui()

        else:

            messagebox.showerror("Error", "Invalid Email or Password")

    def home_gui(self):

        self.clear()

        Label(
            self.root, text="NLP Features", font=("Arial", 20, "bold"), bg="#f0f0f0"
        ).pack(pady=20)

        Button(
            self.root,
            text="Named Entity Recognition",
            font=("Arial", 12, "bold"),
            width=25,
            bg="#80B782",
            fg="white",
            command=self.perform_ner,
        ).pack(pady=10)

        Button(
            self.root,
            text="Emotion Detection",
            font=("Arial", 12, "bold"),
            width=25,
            bg="#80B782",
            fg="white",
            command=self.perform_emotion_detection,
        ).pack(pady=10)

        Button(
            self.root,
            text="Logout",
            font=("Arial", 12, "bold"),
            width=25,
            bg="red",
            fg="white",
            command=self.login_gui,
        ).pack(pady=30)

    def perform_ner(self):

        self.clear()

        Label(
            self.root,
            text="Named Entity Recognition",
            font=("Arial", 20, "bold"),
            bg="#f0f0f0",
        ).pack(pady=20)

        self.ner_input = Entry(self.root, font=("Arial", 12), width=35)
        self.ner_input.pack(pady=20)

        Button(
            self.root,
            text="Analyze",
            font=("Arial", 12, "bold"),
            bg="#80B782",
            fg="white",
            command=self.analyze_ner,
        ).pack(pady=10)

        self.ner_result = Label(
            self.root,
            text="",
            font=("Arial", 12),
            bg="#f0f0f0",
            wraplength=350,
            justify="left",
        )
        self.ner_result.pack(pady=20)

        self.ner_status = Label(
            self.root,
            text="",
            font=("Arial", 11, "italic"),
            bg="#f0f0f0",
            fg="#555555",
        )
        self.ner_status.pack(pady=(0, 10))

        Button(self.root, text="Go Back", command=self.home_gui).pack()

    def analyze_ner(self):

        text = self.ner_input.get()

        if text.strip() == "":
            messagebox.showerror("Error", "Please enter text")
            return

        self.ner_status.config(text="Processing...")
        self.ner_result.config(text="")

        def worker():
            try:
                result = self.api.perform_ner(text)

                def on_success():
                    self.ner_result.config(text=result)
                    self.ner_status.config(text="")

                self.root.after(0, on_success)
            except APIError as e:

                def on_error():
                    self.ner_result.config(text=str(e))
                    self.ner_status.config(text="")

                self.root.after(0, on_error)
            except Exception:

                def on_error():
                    self.ner_result.config(
                        text="Something went wrong while analyzing text. Please try again."
                    )
                    self.ner_status.config(text="")

                self.root.after(0, on_error)

        threading.Thread(target=worker, daemon=True).start()

    def perform_emotion_detection(self):

        self.clear()

        Label(
            self.root,
            text="Emotion Detection",
            font=("Arial", 20, "bold"),
            bg="#f0f0f0",
        ).pack(pady=20)

        self.emotion_input = Entry(self.root, font=("Arial", 12), width=35)
        self.emotion_input.pack(pady=20)

        Button(
            self.root,
            text="Analyze",
            font=("Arial", 12, "bold"),
            bg="#80B782",
            fg="white",
            command=self.analyze_emotion,
        ).pack(pady=10)

        self.emotion_result = Label(
            self.root, text="", font=("Arial", 12), bg="#f0f0f0"
        )
        self.emotion_result.pack(pady=20)

        self.emotion_status = Label(
            self.root,
            text="",
            font=("Arial", 11, "italic"),
            bg="#f0f0f0",
            fg="#555555",
        )
        self.emotion_status.pack(pady=(0, 10))

        Button(self.root, text="Go Back", command=self.home_gui).pack()

    def analyze_emotion(self):

        text = self.emotion_input.get()

        if text.strip() == "":
            messagebox.showerror("Error", "Please enter text")
            return

        self.emotion_status.config(text="Processing...")
        self.emotion_result.config(text="")

        def worker():
            try:
                result = self.api.perform_emotion_detection(text)
                emotion = result.get("emotion", "unknown")
                confidence = result.get("confidence", 0.0)

                def on_success():
                    self.emotion_result.config(
                        text=f"Emotion : {emotion}\nConfidence : {confidence}"
                    )
                    self.emotion_status.config(text="")

                self.root.after(0, on_success)
            except APIError as e:

                def on_error():
                    self.emotion_result.config(text=str(e))
                    self.emotion_status.config(text="")

                self.root.after(0, on_error)
            except Exception:

                def on_error():
                    self.emotion_result.config(
                        text="Something went wrong while analyzing text. Please try again."
                    )
                    self.emotion_status.config(text="")

                self.root.after(0, on_error)

        threading.Thread(target=worker, daemon=True).start()


nlp = NLP_App()
