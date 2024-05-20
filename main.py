from newgame import game
from window import *

if __name__ == '__main__':
    game = game.Game()
    game.run()
    sys.exit(app.exec())
    app = QApplication()
    window = PoseDetectionWindow()
    window.show()
    sys.exit(app.exec())