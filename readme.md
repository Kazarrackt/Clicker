# KazLabs AutoClicker

A dead simple auto-clicking tool with customizable intervals and turbo mode (look it just clicks fast okay...).

## Features

- Customizable clicking intervals
- Turbo mode for ultra-fast clicking
- Configurable hotkeys
- Error handling and logging
- Clean modern interface

## Usage

1. Run the application
2. Set your desired minimum and maximum intervals
3. Configure your hotkey
4. Enable/disable turbo mode as needed
5. Press Start or use the hotkey to begin auto-clicking

## Configuration

Edit `config.json` to customize:
- Default intervals
- Default hotkey
- Turbo mode settings
- Window title
- Theme colors #NotImplementedYet

## Logs

Logs are stored in `C:\Logs\AutoClicker\main.log`

## Requirements

- Python 3.x
- pyautogui
- keyboard

## Building Executable

To create a portable executable:

1. Install PyInstaller: `pip install pyinstaller`
2. Run: `pyinstaller --onefile app.py`
3. Find the executable in the `dist` folder

© 2024 Kazlabs - Made with ♥️ by Liam Sorensen

