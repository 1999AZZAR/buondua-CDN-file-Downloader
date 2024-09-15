import os
import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog, QSpinBox, QRadioButton, QButtonGroup
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PIL import Image
from io import BytesIO
import urllib.parse as urlparse

class DownloaderThread(QThread):
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, base_url, output_folder, start_index, token, prefix, mode, number_format):
        QThread.__init__(self)
        self.base_url = base_url
        self.output_folder = output_folder
        self.start_index = start_index
        self.token = token
        self.prefix = prefix
        self.mode = mode
        self.number_format = number_format
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://buondua.com/'
        }
        self.session = requests.Session()
        self.image_formats = [
            '.jpg', '.jpeg', '.webp', '.png', '.gif', '.bmp',
            '.tiff', '.tif', '.heic', '.heif', '.avif'
        ]

    def run(self):
        self.download_files()
        self.finished_signal.emit()

    def download_file(self, url, save_path, file_name, ext=None):
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            # Always save as .jpeg
            save_path_jpeg = os.path.join(self.output_folder, f"{file_name}.jpeg")

            # For all formats, including .jpg and .jpeg, process through PIL
            self.update_signal.emit(f"Processing {ext} to .jpeg")
            img = Image.open(BytesIO(response.content))

            # Convert to RGB mode if the image is not already in RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')

            img.save(save_path_jpeg, 'JPEG', quality=95)
            self.update_signal.emit(f"Saved as .jpeg: {save_path_jpeg}")
            return True
        except requests.exceptions.RequestException as e:
            self.update_signal.emit(f"Failed to download: {url} (Format: {ext})")
            self.update_signal.emit(f"Error: {str(e)}")
            return False
        except Exception as e:
            self.update_signal.emit(f"Failed to process image: {url} (Format: {ext})")
            self.update_signal.emit(f"Error: {str(e)}")
            return False

    def download_files(self):
        os.makedirs(self.output_folder, exist_ok=True)

        consecutive_failures = 0
        index = self.start_index

        while consecutive_failures < 5:
            file_name = f"{self.prefix}-{index:0{self.number_format}d}"
            success = False

            for ext in self.image_formats:
                if self.mode == 'cdn':
                    url = f"{self.base_url}/{file_name}{ext}?{self.token}"
                else:  # mitaku mode
                    url = f"{self.base_url}/{file_name}{ext}"

                save_path = os.path.join(self.output_folder, f"{file_name}{ext}")
                self.update_signal.emit(f"Attempting to download: {url}")

                if self.download_file(url, save_path, file_name, ext):
                    success = True
                    break  # Stop trying other formats if one succeeds

            if success:
                consecutive_failures = 0
            else:
                consecutive_failures += 1
                self.update_signal.emit(f"Failed to download any format for {file_name}")

            index += 1

        self.update_signal.emit(f"Download finished. Stopped after {consecutive_failures} consecutive failures.")

class CDNDownloaderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('CDN File Downloader')
        self.setGeometry(300, 300, 500, 500)

        layout = QVBoxLayout()

        self.mode_label = QLabel('Choose Mode:')
        layout.addWidget(self.mode_label)

        self.manual_radio = QRadioButton('Manual (Base URL, Token, Prefix)')
        self.full_link_radio = QRadioButton('Full Link (auto-extract)')
        self.mitaku_radio = QRadioButton('Mitaku Link')
        self.manual_radio.setChecked(True)

        self.button_group = QButtonGroup()
        self.button_group.addButton(self.manual_radio)
        self.button_group.addButton(self.full_link_radio)
        self.button_group.addButton(self.mitaku_radio)

        layout.addWidget(self.manual_radio)
        layout.addWidget(self.full_link_radio)
        layout.addWidget(self.mitaku_radio)

        self.full_link_label = QLabel('Enter Full Link:')
        layout.addWidget(self.full_link_label)

        self.full_link_input = QLineEdit()
        layout.addWidget(self.full_link_input)

        self.url_label = QLabel('Enter CDN base URL:')
        layout.addWidget(self.url_label)

        self.url_input = QLineEdit()
        self.url_input.setText('https://i0.buondua.com/cdn/38706')
        layout.addWidget(self.url_input)

        self.token_label = QLabel('Enter token:')
        layout.addWidget(self.token_label)

        self.token_input = QLineEdit()
        self.token_input.setText('84f3676c9b5c14f49df3d50daa19df41')
        layout.addWidget(self.token_input)

        self.prefix_label = QLabel('Enter file prefix:')
        layout.addWidget(self.prefix_label)

        self.prefix_input = QLineEdit()
        self.prefix_input.setText('XR-Uncensored-Shen-Siyi-MissKON.com-')
        layout.addWidget(self.prefix_input)

        self.folder_label = QLabel('Select Output Folder:')
        layout.addWidget(self.folder_label)

        self.folder_input = QLineEdit()
        layout.addWidget(self.folder_input)

        self.browse_button = QPushButton('Browse')
        self.browse_button.clicked.connect(self.browse_folder)
        layout.addWidget(self.browse_button)

        self.start_index_label = QLabel('Start Index:')
        layout.addWidget(self.start_index_label)

        self.start_index_input = QSpinBox()
        self.start_index_input.setMinimum(1)
        self.start_index_input.setMaximum(9999)
        self.start_index_input.setValue(1)
        layout.addWidget(self.start_index_input)

        self.number_format_label = QLabel('Number Format (digits):')
        layout.addWidget(self.number_format_label)

        self.number_format_input = QSpinBox()
        self.number_format_input.setMinimum(1)
        self.number_format_input.setMaximum(8)
        self.number_format_input.setValue(3)
        layout.addWidget(self.number_format_input)

        self.download_button = QPushButton('Start Download')
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

        self.full_link_radio.toggled.connect(self.toggle_mode)
        self.mitaku_radio.toggled.connect(self.toggle_mode)
        self.manual_radio.toggled.connect(self.toggle_mode)

        self.toggle_mode()  # Initialize visibility

    def toggle_mode(self):
        full_link_mode = self.full_link_radio.isChecked() or self.mitaku_radio.isChecked()
        self.full_link_label.setVisible(full_link_mode)
        self.full_link_input.setVisible(full_link_mode)
        self.url_label.setVisible(not full_link_mode)
        self.url_input.setVisible(not full_link_mode)
        self.token_label.setVisible(not full_link_mode)
        self.token_input.setVisible(not full_link_mode)
        self.prefix_label.setVisible(not full_link_mode)
        self.prefix_input.setVisible(not full_link_mode)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.folder_input.setText(folder)

    def extract_url_parts(self, full_link):
        parsed_url = urlparse.urlparse(full_link)
        if 'mitaku.net' in parsed_url.netloc:
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/wp-content/uploads/{parsed_url.path.split('/')[3]}/{parsed_url.path.split('/')[4]}"
            file_name = parsed_url.path.split('/')[-1]
            prefix = '-'.join(file_name.split('-')[:-1])
            return base_url, '', prefix, 'mitaku'
        else:
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path.rsplit('/', 1)[0]}"
            token = parsed_url.query
            file_name = parsed_url.path.rsplit('/', 1)[-1]
            prefix = file_name[:file_name.rfind('-')]
            return base_url, token, prefix, 'cdn'

    def start_download(self):
        if self.full_link_radio.isChecked() or self.mitaku_radio.isChecked():
            full_link = self.full_link_input.text()
            if not full_link:
                self.log_output.append("Please enter a full link.")
                return
            cdn_url, token, prefix, mode = self.extract_url_parts(full_link)
        else:
            cdn_url = self.url_input.text()
            token = self.token_input.text()
            prefix = self.prefix_input.text()
            mode = 'cdn'

        output_folder = self.folder_input.text()
        start_index = self.start_index_input.value()
        number_format = self.number_format_input.value()

        if not cdn_url or not output_folder or (mode == 'cdn' and not token) or not prefix:
            self.log_output.append("Please complete all fields.")
            return

        self.download_button.setEnabled(False)
        self.log_output.clear()

        self.downloader_thread = DownloaderThread(cdn_url, output_folder, start_index, token, prefix, mode, number_format)
        self.downloader_thread.update_signal.connect(self.log_output.append)
        self.downloader_thread.finished_signal.connect(self.download_finished)
        self.downloader_thread.start()

    def download_finished(self):
        self.download_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    downloader = CDNDownloaderGUI()
    downloader.show()
    sys.exit(app.exec_())
