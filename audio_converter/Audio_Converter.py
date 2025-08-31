import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout,
    QPushButton, QFileDialog, QAction, QSizePolicy
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Converter")
        self.resize(300, 100)
        self.setup_menu()
        self.setup_layout()

    def setup_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("파일")
        exit_action = QAction("종료", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def setup_layout(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        self.file_button = QPushButton("파일")
        self.file_button.setMaximumSize(100, 25)
        self.file_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.file_button.clicked.connect(self.handle_file_button)
        layout.addWidget(self.file_button)

        self.folder_button = QPushButton("폴더")
        self.folder_button.setMaximumSize(100, 25)
        self.folder_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.folder_button.clicked.connect(self.handle_folder_button)
        layout.addWidget(self.folder_button)

    def convert_to_wav_and_pcm(self, input_path: Path, wav_path: Path, pcm_path: Path):
        os.system(f'ffmpeg -y -loglevel quiet -nostats -hide_banner -i "{input_path}" "{wav_path}"')
        self.extract_pcm_from_wav(wav_path, pcm_path)

    def extract_pcm_from_wav(self, wav_path: Path, pcm_path: Path):
        with open(wav_path, "rb") as f:
            data = f.read()
        with open(pcm_path, "wb") as f:
            f.write(data[44:])  # Skip WAV header

    def handle_file_button(self):
        file_path_str, _ = QFileDialog.getOpenFileName(self, "파일 선택", "", "Audio Files (*.mp3 *.wav *.m4a)")
        if not file_path_str:
            return

        input_path = Path(file_path_str)
        working_dir = Path.cwd()
        temp_dir = working_dir / "temp"
        pcm_dir = working_dir / "pcm"
        temp_dir.mkdir(exist_ok=True)
        pcm_dir.mkdir(exist_ok=True)

        base_name = input_path.stem.replace(" ", "_")
        wav_path = temp_dir / f"{base_name}.wav"
        pcm_path = pcm_dir / f"{base_name}.pcm"

        if input_path.suffix.lower() in [".mp3", ".m4a"]:
            self.convert_to_wav_and_pcm(input_path, wav_path, pcm_path)
        elif input_path.suffix.lower() == ".wav":
            self.extract_pcm_from_wav(input_path, pcm_path)

    def handle_folder_button(self):
        dir_path_str = QFileDialog.getExistingDirectory(self, "폴더 선택")
        if not dir_path_str:
            return

        base_dir = Path(dir_path_str)
        sound_files = list(base_dir.rglob("*"))
        for file in sound_files:
            if file.suffix.lower() not in [".mp3", ".wav", ".m4a"]:
                continue

            working_dir = Path.cwd()
            temp_dir = working_dir / "temp"
            pcm_dir = working_dir / "pcm"
            temp_dir.mkdir(exist_ok=True)
            pcm_dir.mkdir(exist_ok=True)

            base_name = file.stem.replace(" ", "_")
            wav_path = temp_dir / f"{base_name}.wav"
            pcm_path = pcm_dir / f"{base_name}.pcm"

            if file.suffix.lower() in [".mp3", ".m4a"]:
                self.convert_to_wav_and_pcm(file, wav_path, pcm_path)
            elif file.suffix.lower() == ".wav":
                self.extract_pcm_from_wav(file, pcm_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
