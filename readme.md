# KazLabs AutoClicker

A dead simple auto-clicking tool with customizable intervals and turbo mode (look it just clicks fast okay...).

## Features

- Customizable clicking intervals
- Turbo mode for somewhat fast clicking
- Configurable hotkeys
- Error handling and logging
- Clean simple interface

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
- Theme colors #KindaWorks

## Logs

Logs are stored in `C:\Logs\AutoClicker\main.log`
- Includes all clicks, errors, and status changes
- Formatted for easy parsing
- Automatic log directory creation

## Requirements

- Python 3.x
- pyautogui
- keyboard
- pyinstaller
- pywin32

## Building Executable

To create a portable executable:

1. Install Requirements: `pip install -r requirements.txt`
2. Run: `python build.py`
3. Find the executable in the `dist` folder

## Notes

- Turbo mode may cause high CPU usage
- Moving mouse to any corner will trigger failsafe
- Config file is auto-created if missing

## Known Issues

- Turbo mode isn't as fast as advertised (Windows is mean) - I'm working on it. I really want to hit 1,000 CPS.
- Some antivirus software may flag the auto-clicker (it's the nature of auto-clickers)
- Theme might look weird on some Windows versions (because Windows)

© 2025 Kazlabs - Made with ♥️ by Liam Sorensen

