import threading
import subprocess

def run_window():
    subprocess.run(["python", "window.py"])

def run_game():
    subprocess.run(["python", "newgame/game.py"])

if __name__ == "__main__":
    window_thread = threading.Thread(target=run_window)
    game_thread = threading.Thread(target=run_game)

    window_thread.start()
    game_thread.start()

    window_thread.join()
    game_thread.join()
