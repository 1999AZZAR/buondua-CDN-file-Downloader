# buondua CDN File Downloader

## Overview

The **CDN File Downloader** is a graphical application built using Python and PyQt5 that facilitates downloading files from a CDN server. It provides a flexible interface to either manually input the base URL, token, and file prefix, or automatically extract these details from a full link. The downloader supports multiple image formats, automatically converts non-JPEG formats to `.jpg`, and includes features like progress tracking, log updates, and the ability to browse for an output folder.

## Key Features

- **Manual or Full Link Mode**: Allows the user to either manually input the necessary details or paste a full link, with auto-extraction of key components.
- **Supported Image Formats**: The downloader attempts to download files in `.jpg`, `.jpeg`, `.webp`, and `.png` formats, converting non-JPEG formats to `.jpg` for consistency.
- **Retry Mechanism**: Retries up to 8 times for missing files before halting.
- **Progress Tracking**: Visual progress updates using a progress bar, based on the download attempts.
- **Log Output**: Real-time log of download attempts and outcomes.
- **Multi-threaded**: Downloads run on a separate thread to avoid freezing the GUI.

## Prerequisites

1. **Python 3.8+**
2. **PyQt5**
3. **Requests**
4. **Pillow**

To install the required dependencies, run:

```bash
pip install PyQt5 requests Pillow
```

## How to Use

1. **Launching the Application**:
    - Run the script using Python:
      ```bash
      python downloader.py
      ```

2. **Choosing the Mode**:
   - **Manual Mode**: Input the base CDN URL, token, and file prefix.
   - **Full Link Mode**: Input a full CDN link, and the downloader will extract the base URL, token, and file prefix automatically.

3. **Input Fields**:
   - **Base URL**: The base URL of the CDN.
   - **Token**: The authentication or session token required for the CDN.
   - **Prefix**: The file prefix before the index.
   - **Output Folder**: Select the folder where downloaded files will be saved.
   - **Start Index**: The index number from which to start downloading.

4. **Starting the Download**:
   - After inputting all necessary fields, click on **Start Download** to begin downloading files from the CDN.

5. **Progress and Logs**:
   - The application will show download progress via the progress bar and display real-time logs of each download attempt in the log output area.

## Image Conversion

Files in formats other than `.jpg` (such as `.webp` and `.png`) will be automatically converted to `.jpg` for easier compatibility and saved in the output folder.

## Error Handling

The application is designed to handle request exceptions (e.g., timeouts, unavailable files) and will retry downloading each file up to 8 times before stopping.

## Example Full Link Input

When using **Full Link Mode**, an example full link input might look like:

```
https://i0.buondua.com/cdn/38706/XR-Uncensored-Shen-Siyi-MissKON.com-001.jpg?84f3676c9b5c14f49df3d50daa19df41
```

The application will auto-extract:
- **Base URL**: `https://i0.buondua.com/cdn/38706`
- **Token**: `84f3676c9b5c14f49df3d50daa19df41`
- **Prefix**: `XR-Uncensored-Shen-Siyi-MissKON.com-`

## License

This project is licensed under the MIT License. You are free to use, modify, and distribute this software as per the terms of the license.

---

Feel free to modify the code and adapt it to your specific needs!
