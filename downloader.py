import os
import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog, QSpinBox, QProgressBar, QRadioButton, QButtonGroup
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PIL import Image
from io import BytesIO
import urllib.parse as urlparse

class DownloaderThread(QThread):
    update_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()

    def __init__(self, base_url, output_folder, start_index, token, prefix):
        QThread.__init__(self)
        self.base_url = base_url
        self.output_folder = output_folder
        self.start_index = start_index
        self.token = token
        self.prefix = prefix
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

    def run(self):
        self.download_files_from_cdn()
        self.finished_signal.emit()

    def download_files_from_cdn(self):
        os.makedirs(self.output_folder, exist_ok=True)
        session = requests.Session()

        consecutive_failures = 0
        index = self.start_index
        total_downloaded = 0
        image_formats = ['.jpg', '.jpeg', '.webp', '.png']  # Supported formats

        while consecutive_failures < 8:  # Stop after 8 consecutive failures
            file_name = f"{self.prefix}-{index:03d}"

            successful_download = False

            for ext in image_formats:
                url = f"{self.base_url}/{file_name}{ext}?{self.token}"
                save_path = os.path.join(self.output_folder, f"{file_name}{ext}")
                self.update_signal.emit(f"Attempting to download: {url}")

                try:
                    response = session.get(url, headers=self.headers, timeout=10)
                    response.raise_for_status()

                    # Handle image conversion
                    if ext != '.jpg' and ext != '.jpeg':
                        self.update_signal.emit(f"Converting {ext} to .jpg")
                        img = Image.open(BytesIO(response.content))
                        save_path_jpg = os.path.join(self.output_folder, f"{file_name}.jpg")
                        img.convert('RGB').save(save_path_jpg, 'JPEG')
                        self.update_signal.emit(f"Converted and saved: {save_path_jpg}")
                    else:
                        with open(save_path, 'wb') as file:
                            file.write(response.content)
                        self.update_signal.emit(f"Downloaded: {save_path}")

                    successful_download = True
                    consecutive_failures = 0  # Reset failure count after successful download
                    total_downloaded += 1
                    break  # Exit the loop if one format succeeds
                except requests.exceptions.RequestException as e:
                    self.update_signal.emit(f"Failed to download: {url} (Format: {ext})")
                    self.update_signal.emit(f"Error: {str(e)}")

            if not successful_download:
                consecutive_failures += 1

            index += 1
            # Update progress (Optional since the end is unknown, update based on attempts)
            self.progress_signal.emit(index)

class CDNDownloaderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('CDN File Downloader')
        self.setGeometry(300, 300, 500, 500)

        layout = QVBoxLayout()

        # Radio buttons for choosing mode (Manual or Full Link)
        self.mode_label = QLabel('Choose Mode:')
        layout.addWidget(self.mode_label)

        self.manual_radio = QRadioButton('Manual (Base URL, Token, Prefix)')
        self.full_link_radio = QRadioButton('Full Link (auto-extract)')
        self.manual_radio.setChecked(True)

        self.button_group = QButtonGroup()
        self.button_group.addButton(self.manual_radio)
        self.button_group.addButton(self.full_link_radio)

        layout.addWidget(self.manual_radio)
        layout.addWidget(self.full_link_radio)

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

        self.download_button = QPushButton('Start Download')
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

        # Set visibility of full link vs manual fields based on selection
        self.full_link_radio.toggled.connect(self.toggle_mode)

    def toggle_mode(self):
        # Toggle visibility based on the selected mode
        if self.full_link_radio.isChecked():
            self.full_link_label.setVisible(True)
            self.full_link_input.setVisible(True)
            self.url_label.setVisible(False)
            self.url_input.setVisible(False)
            self.token_label.setVisible(False)
            self.token_input.setVisible(False)
            self.prefix_label.setVisible(False)
            self.prefix_input.setVisible(False)
        else:
            self.full_link_label.setVisible(False)
            self.full_link_input.setVisible(False)
            self.url_label.setVisible(True)
            self.url_input.setVisible(True)
            self.token_label.setVisible(True)
            self.token_input.setVisible(True)
            self.prefix_label.setVisible(True)
            self.prefix_input.setVisible(True)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.folder_input.setText(folder)

    def extract_url_parts(self, full_link):
        parsed_url = urlparse.urlparse(full_link)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path.rsplit('/', 1)[0]}"
        token = parsed_url.query
        file_name = parsed_url.path.rsplit('/', 1)[-1]
        prefix = file_name[:file_name.rfind('-')]
        return base_url, token, prefix

    def start_download(self):
        if self.full_link_radio.isChecked():
            full_link = self.full_link_input.text()
            if not full_link:
                self.log_output.append("Please enter a full link.")
                return
            cdn_url, token, prefix = self.extract_url_parts(full_link)
        else:
            cdn_url = self.url_input.text()
            token = self.token_input.text()
            prefix = self.prefix_input.text()

        output_folder = self.folder_input.text()
        start_index = self.start_index_input.value()

        if not cdn_url or not output_folder or not token or not prefix:
            self.log_output.append("Please complete all fields.")
            return

        self.download_button.setEnabled(False)
        self.log_output.clear()

        self.downloader_thread = DownloaderThread(cdn_url, output_folder, start_index, token, prefix)
        self.downloader_thread.update_signal.connect(self.log_output.append)
        self.downloader_thread.progress_signal.connect(self.update_progress)
        self.downloader_thread.finished_signal.connect(self.download_finished)
        self.downloader_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def download_finished(self):
        self.log_output.append("Download finished.")
        self.download_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    downloader = CDNDownloaderGUI()
    downloader.show()
    sys.exit(app.exec_())
