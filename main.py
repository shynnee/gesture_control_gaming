import face_recognition
import cv2
import pickle
import os
import numpy as np
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import glob
import threading
import subprocess
import sqlite3
from datetime import datetime

class FaceUnlockSystem:
    def __init__(self):
        try:
            with open('user_labels.pickle', 'rb') as self.label_file:
                self.original_labels = pickle.load(self.label_file)
            print(self.original_labels)
        except FileNotFoundError:
            print("No user_labels.pickle file detected, will create required pickle files")

        self.current_user_id = 0
        self.user_labels_ids = {}
        self.base_directory = os.path.dirname(os.path.abspath(__file__))
        self.image_directory = os.path.join(self.base_directory, 'user_images')
        for self.root_dir, self.dir_list, self.file_list in os.walk(self.image_directory):
            for self.file_name in self.file_list:
                if self.file_name.endswith('png') or self.file_name.endswith('jpg'):
                    self.file_path = os.path.join(self.root_dir, self.file_name)
                    self.user_label = os.path.basename(os.path.dirname(self.file_path)).replace(' ', '-').lower()
                    if self.user_label not in self.user_labels_ids:
                        self.user_labels_ids[self.user_label] = self.current_user_id
                        self.current_user_id += 1
                        self.user_id = self.user_labels_ids[self.user_label]

        print(self.user_labels_ids)
        self.original_labels = 0
        if self.user_labels_ids != self.original_labels:
            with open('user_labels.pickle', 'wb') as self.label_file:
                pickle.dump(self.user_labels_ids, self.label_file)

            self.known_face_encodings = []
            for self.label in self.user_labels_ids:
                number_of_images = len([filename for filename in os.listdir('user_images/' + self.label)
                                if os.path.isfile(os.path.join('user_images/' + self.label, filename))])
                print(number_of_images)
                for image_number in range(1, (number_of_images + 1)):
                    self.image_path = os.path.join(self.image_directory, self.label, str(image_number) + '.png')
                    self.image = face_recognition.load_image_file(self.image_path)
                    self.image_encoding = face_recognition.face_encodings(self.image)[0]
                    self.known_face_encodings.append([self.label, self.image_encoding])
            print(self.known_face_encodings)
            print("Total Number of Images: " + str(len(self.known_face_encodings)))
            with open('KnownFaces.pickle', 'wb') as self.known_faces_file:
                pickle.dump(self.known_face_encodings, self.known_faces_file)
        else:
            with open('KnownFaces.pickle', 'rb') as self.faces_file:
                self.known_face_encodings = pickle.load(self.faces_file)
            print(self.known_face_encodings)

    def identify_user(self):
        self.video_capture = cv2.VideoCapture(0)
        self.continue_running = True
        self.detected_user_names = []
        while self.continue_running:
            self.ret, self.frame = self.video_capture.read()
            self.small_frame = cv2.resize(self.frame, (0, 0), fx=0.5, fy=0.5)
            self.rgb_small_frame = self.small_frame[:, :, ::-1]
            if self.continue_running:
                self.face_locations = face_recognition.face_locations(self.frame)
                self.face_encodings = face_recognition.face_encodings(self.frame, self.face_locations)
                self.detected_user_names = []
                for self.face_encoding in self.face_encodings:
                    for self.known_face in self.known_face_encodings:
                        self.matches = face_recognition.compare_faces([self.known_face[1]], self.face_encoding)
                        print(self.matches)
                        self.name = 'Unknown'
                        self.face_distances = face_recognition.face_distance([self.known_face[1]], self.face_encoding)
                        self.best_match_index = np.argmin(self.face_distances)
                        print(self.best_match_index)
                        print('Match found:', self.matches[self.best_match_index])
                        if self.matches[self.best_match_index]:
                            self.continue_running = False
                            self.detected_user_names.append(self.known_face[0])
                            break
                        next
            print("Best match(es): " + str(self.detected_user_names))
            self.video_capture.release()
            cv2.destroyAllWindows()
            break
        return self.detected_user_names


def register_user():
    if not (full_name_var.get() and username_var.get() and password_var.get()):
        messagebox.showerror("Error", "All fields are required!")
        return

    if not os.path.exists("user_images"):
        os.makedirs("user_images")

    user_image_dir = os.path.join("user_images", username_var.get())
    Path(user_image_dir).mkdir(parents=True, exist_ok=True)

    number_of_files = len([filename for filename in os.listdir(user_image_dir)
                        if os.path.isfile(os.path.join(user_image_dir, filename))])
    number_of_files += 1

    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Capture Image")

    while True:
        ret, frame = cam.read()
        cv2.imshow("Capture Image", frame)
        if not ret:
            break
        key_press = cv2.waitKey(1)

        if key_press % 256 == 27:
            print("Escape hit, closing...")
            cam.release()
            cv2.destroyAllWindows()
            return
        elif key_press % 256 == 32:
            img_name = os.path.join(user_image_dir, f"{number_of_files}.png")
            cv2.imwrite(img_name, frame)
            print(f"{img_name} saved!")
            cam.release()
            cv2.destroyAllWindows()
            break

    try:
        conn = sqlite3.connect('face_recognition.db')
        c = conn.cursor()

        c.execute('INSERT INTO users (full_name, username, password) VALUES (?, ?, ?)',
                  (full_name_var.get(), username_var.get(), password_var.get()))

        c.execute('INSERT INTO face_images (username, image_path) VALUES (?, ?)',
                  (username_var.get(), img_name))

        registration_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('INSERT INTO registration_times (username, registration_time) VALUES (?, ?)',
                  (username_var.get(), registration_time))

        conn.commit()
        conn.close()

    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists!")
        return

    raise_frame(login_frame)


def login_user():
    print("Login button clicked")
    face_unlock_system = FaceUnlockSystem()
    user = face_unlock_system.identify_user()
    if not user:
        messagebox.showerror("Alert", "Face Not Recognised")
        return

    username = user[0]
    logged_in_user.set(username)

    conn = sqlite3.connect('face_recognition.db')
    c = conn.cursor()

    c.execute('SELECT login_count FROM login_attempts WHERE username = ?', (username,))
    result = c.fetchone()

    login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if result:
        login_count = result[0] + 1
        c.execute('UPDATE login_attempts SET login_count = ?, last_login_time = ? WHERE username = ?',
                  (login_count, login_time, username))
    else:
        c.execute('INSERT INTO login_attempts (username, login_count, last_login_time) VALUES (?, 1, ?)',
                  (username, login_time))

    conn.commit()
    conn.close()

    user_menu_frame.destroy()
    run_additional_threads()


def run_additional_threads():
    def run_window():
        subprocess.run(["python", "window.py"])

    def run_game():
        subprocess.run(["python", "newgame/game.py"])

    window_thread = threading.Thread(target=run_window)
    game_thread = threading.Thread(target=run_game)

    window_thread.start()
    game_thread.start()

    window_thread.join()
    game_thread.join()


app = tk.Tk()
app.title("Face Login System")

login_frame = tk.Frame(app)
registration_frame = tk.Frame(app)
user_menu_frame = tk.Frame(app)

frame_list = [login_frame, registration_frame, user_menu_frame]
for frame in frame_list:
    frame.grid(row=0, column=0, sticky='news')
    frame.configure(bg='white')

def raise_frame(frame):
    frame.tkraise()

def raise_registration_frame():
    raise_frame(registration_frame)

def raise_login_frame():
    raise_frame(login_frame)

full_name_var = tk.StringVar()
username_var = tk.StringVar()
password_var = tk.StringVar()
logged_in_user = tk.StringVar()

tk.Label(login_frame, text="Face Recognition", font=("Courier", 60), bg="white").grid(row=1, column=1, columnspan=5)
tk.Button(login_frame, text="Login", bg="white", font=("Arial", 30), command=login_user).grid(row=2, column=5)
tk.Button(login_frame, text="Register", command=raise_registration_frame, bg="white", font=("Arial", 30)).grid(row=2, column=1)

tk.Label(registration_frame, text="Register", font=("Courier", 60), bg="white").grid(row=1, column=1, columnspan=5)
tk.Label(registration_frame, text="Full Name: ", font=("Arial", 30), bg="white").grid(row=2, column=1)
tk.Entry(registration_frame, textvariable=full_name_var, font=("Arial", 30)).grid(row=2, column=2)

tk.Label(registration_frame, text="Username: ", font=("Arial", 30), bg="white").grid(row=3, column=1)
tk.Entry(registration_frame, textvariable=username_var, font=("Arial", 30)).grid(row=3, column=2)

tk.Label(registration_frame, text="Password: ", font=("Arial", 30), bg="white").grid(row=4, column=1)
tk.Entry(registration_frame, textvariable=password_var, font=("Arial", 30), show='*').grid(row=4, column=2)

tk.Button(registration_frame, text="Register", command=register_user, bg="white", font=("Arial", 30)).grid(row=5, column=2)

tk.Label(user_menu_frame, text="Hello, ", font=("Courier", 60), bg="white").grid(row=1, column=1)
tk.Label(user_menu_frame, textvariable=logged_in_user, font=("Courier", 60), bg="white", fg="red").grid(row=1, column=2)
tk.Button(user_menu_frame, text="Back", font=("Arial", 30), command=raise_login_frame).grid(row=2, column=1)

raise_frame(login_frame)
app.mainloop()
