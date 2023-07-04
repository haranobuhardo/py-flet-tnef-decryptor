import flet as ft
from datetime import datetime as dt
import os
import tnef
import tempfile
import re
import copy

def make_safe_filename(filename):
    # Replace or remove unsafe characters
    safe_filename = re.sub(r'[<>:"/\\|?*]', '', filename)

    return safe_filename

def main(page: ft.Page):
    global save_file_details
    save_file_details = {
        'title': '',
        'data': '',
        'metadata': ''
    }

    # Configure app (main page/the only page) initial properties
    page.title='PCMS WINMAIL.DAT Decryptor'
    page.window_width=400
    page.window_height=600
    page.window_resizable=False
    page.window_maximizable=False
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_center()
    page.scroll = 'AUTO'

    parse_result = None

    dlg = ft.AlertDialog(
        title=ft.Text("To be implemented! Work on progress..."), on_dismiss=lambda e: print("Open file Dialog dismissed!")
    )

    def parse_file(file_loc: str):
        with open(file_loc, 'rb') as f:
            parse_result = tnef.parse_tnef(f)

        file_result_buttons_row.clean()  
        EncryptedFilesTiles = []
        # for k, v in enumerate(parse_result[1]):
        #     EncryptedFilesTiles.append(
                
        #     )
            
        file_result_buttons_row.controls.extend(
            # [
            #     ft.ListTile(title=ft.Text('test'), trailing=ft.PopupMenuButton(items=[ft.PopupMenuItem(text='test', on_click=lambda _: print('test'))])),
            #     ft.ListTile(title=ft.Text('test2'), trailing=ft.PopupMenuButton(items=[ft.PopupMenuItem(text='test2', on_click=lambda _: print('test2'))]))
            # ]
            [ft.ListTile(
                title=ft.Text(make_safe_filename(v.decode('Big5'))), # use 'Big5' for common traditional chinese characters support
                on_click=lambda _, v=v, k=k: open_file_temp(make_safe_filename(v.decode('Big5')), parse_result[2][k], parse_result[3][k]),
                trailing=ft.PopupMenuButton(
                        icon=ft.icons.MORE_VERT,
                        items=
                        [
                            ft.PopupMenuItem(icon=ft.icons.FILE_OPEN, text="Open File",
                                    on_click = lambda _, v=v, k=k: open_file_temp(make_safe_filename(copy.deepcopy(v).decode('Big5')), parse_result[2][k], parse_result[3][k])
                                ),
                            ft.PopupMenuItem(icon=ft.icons.DOWNLOAD_FOR_OFFLINE, text="Download File", 
                                    on_click = lambda _, v=v, k=k: save_file(make_safe_filename(copy.deepcopy(v).decode('Big5')), parse_result[2][k], parse_result[3][k])
                                ),
                        ],
                    )
                ) for k, v in enumerate(parse_result[1])]
        )
        file_result_buttons_row.update()
    
    # Open Notification Dialog
    def open_dlg(e):
        page.dialog = dlg
        dlg.open = True 
        page.update()

    # Get source winmail.dat file
    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files == None:
            print('None file selected!')
            return
        selected_files.value = e.files[0].path
        selected_files.update()
        file_change(selected_files_details, {
            'filename': e.files[0].name,
            'filesize': e.files[0].size,
            'modifiedon': os.path.getmtime(e.files[0].path),
            'createdon': os.path.getctime(e.files[0].path),
        })
        file_result_buttons_row.clean() 

    # Saving file after picking the save location (save_file)
    def on_save_result(e: ft.FilePickerResultEvent):
        # if e.path == None:
        #     print('None file selected!')
        #     return
        save_file_loc = e.path
        if e.path != None:
            tnef.save_data(save_file_details['title'], save_file_details['data'], save_file_details['metadata'], e.path)
            return True
        
        pass

    # call on each file change -> updating the file details label field
    def file_change(textField: ft.Text, data):
        textField.value = f"• Filename:\t{data['filename']}\n• Filesize:\t{data['filesize']:,d} bytes\n• Last Modified:\t{dt.fromtimestamp(data['modifiedon'])}\n• Created On:\t{dt.fromtimestamp(data['createdon'])}\n"
        parse_file_button.disabled = False
        parse_file_button.update()
        textField.update()

    def save_file(filename: str, data, metadata):
        print('nama file', filename)
        # save_file_details = {
        #     'title': filename,
        #     'data': data,
        #     'metadata': metadata
        # }
        save_file_details['title'] = filename
        save_file_details['data'] = data
        save_file_details['metadata'] = metadata
        if save_file_dialog.save_file(file_name = filename) == True:
            print("berhasil!")

    def open_file_temp(filename, data, metadata):
        _temp_file_loc = os.path.join(tempfile.gettempdir(), filename)
        save_file_details['title'] = filename
        save_file_details['data'] = data
        save_file_details['metadata'] = metadata
        tnef.save_data(save_file_details['title'], save_file_details['data'], save_file_details['metadata'], _temp_file_loc)
        os.system(f'start "" "{_temp_file_loc}" > nul 2>&1')

    # Initialize app's controls
    parse_file_button = ft.ElevatedButton("Parse File", on_click=lambda _: parse_file(selected_files.value), col=12, disabled=True)
    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    save_file_dialog = ft.FilePicker(on_result=on_save_result)
    selected_files = ft.TextField(read_only=True, label='File to encrypt path:')
    selected_files_details = ft.Text(f"• Filename:\n• Filesize: bytes\n• Last Modified:\n• Created On:\n", selectable=True)
    file_result_buttons_row = ft.ResponsiveRow([])

    # add file picker control dialog (required to open a file dialog)
    page.overlay.append(pick_files_dialog)
    page.overlay.append(save_file_dialog)

    # add all app's controls to page
    page.add(
        ft.Row(
            [
                ft.Container(selected_files, padding=5, col=6),
                ft.Container(
                    ft.IconButton(
                        icon=ft.icons.UPLOAD_FILE,
                        bgcolor=ft.colors.LIGHT_BLUE_100,
                        on_click=lambda _: pick_files_dialog.pick_files(
                            allow_multiple=False,
                            allowed_extensions=['dat']
                        ),
                    ), 
                    padding=5, 
                    col=6
                )
            ]
        ),
        ft.Container(
            ft.Column(
                [
                    ft.Text('File details:', style=ft.TextThemeStyle.TITLE_MEDIUM),
                    selected_files_details,
                ],  
            ),
        padding=5
        ),
        ft.ResponsiveRow(
            [
                parse_file_button,
            ],
        ),
        ft.Container(ft.Column([ft.Text('File contents:', text_align='center', style=ft.TextThemeStyle.TITLE_MEDIUM, col=12),
                        file_result_buttons_row]), 
                        padding=10),
    )

ft.app(target=main)

# 1. Select File (TextBox + Button) (DONE)
# 2. Selected File Details (Filename, Size, Date, ...) (DONE)
# 3. Select Output Folder (TextBox + Button) (DONE, but still per file)
# 4. List all decrpyted TNEF files (ListBox) (DONE)
# 5. Add a MsgBox notification (on success, ask to open the directory directly)

# Next thing to do:
# - Fix saving file (DONE)
# - "Open File" feature, by saving it temporary and open it (DONE)