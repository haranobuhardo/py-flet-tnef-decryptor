# WINMAIL.DAT Decryptor

WINMAIL.DAT Decryptor is a Python application for encrypting `winmail.dat` files. It's particularly useful if you're experiencing issues with `winmail.dat` files in your mailing client. This is my personal side project since I've encountered this problem many times, and takes time to decrypt it from online decryptor (also a little bit cautious about our privacy).

This project was built with Python and Flet Py. It allows the user to pick a `winmail.dat` file from their file system, which is then parsed and decrypted. The resulting files can be saved in a location chosen by the user.

## Features
1. File selection: User can pick a `winmail.dat` file to parse.
2. File details: Displays details about the selected file including filename, size, and date of creation/last modification.
3. File decryption: Decrypts the content of the `winmail.dat` file, showing the list of decrypted files.
4. File saving: User can save the decrypted files in their desired location.
5. File opening: Option to directly open decrypted files from the application.

## Installation
This project requires Python 3, Flet Py (for front-end) and compressed_rtf (for decrypting the winmail.dat). Before running the application, you will need to install the necessary dependencies from the `requirements.txt` file. You can do this by running the following command in your terminal:

```bash
pip install -r requirements.txt
```

## Usage
To use the PCMS WINMAIL.DAT Decryptor:
1. Clone this repository to your local machine.
2. Navigate to the cloned repository directory.
3. Run `python main.py` (or `python3 main.py` if you have both Python 2 and Python 3 installed).
4. The application window will appear. Select a winmail.dat file and the application will decrypt it and show the details.
5. Save the decrypted files to your desired location.

## Contributing
Contributions are welcome! Please feel free to submit a pull request.