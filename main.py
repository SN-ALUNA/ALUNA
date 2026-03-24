import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.main_window import AlunaApp

if __name__ == "__main__":
    app = AlunaApp()
    app.mainloop()
