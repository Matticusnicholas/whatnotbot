# Whatnot Giveaway Bot

A web-based automation tool that helps you enter giveaways on Whatnot live streams automatically.

## Features

- **Cross-Browser Support**: Works with Firefox (Windows/Mac/Linux) and Safari (Mac only)
- **Multiple Login Methods**: Support for email/password login or Google OAuth
- **Automatic Giveaway Detection**: Scans live streams for active giveaways
- **Smart Entry**: Automatically enters giveaways and waits for completion
- **Follow-up Detection**: Checks for consecutive giveaways before moving on
- **Real-time Status**: Live updates on bot activity, giveaways entered, and streams visited
- **Web Interface**: Easy-to-use browser-based control panel

## Requirements

- Python 3.8+
- Firefox browser with geckodriver OR Safari (macOS)
- A valid Whatnot account

## Quick Start

### Windows

1. Download or clone the repository
2. Double-click `setup.bat` to install dependencies
3. Double-click `run.bat` to start the bot
4. Open http://localhost:5000 in your browser

### macOS / Linux

1. Download or clone the repository
2. Open Terminal in the project folder
3. Run the setup script:
   ```bash
   chmod +x setup.sh run.sh
   ./setup.sh
   ```
4. Start the bot:
   ```bash
   ./run.sh
   ```
5. Open http://localhost:5000 in your browser

## Manual Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/whatnotbot.git
cd whatnotbot
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Browser Setup

#### Firefox (Recommended)
The bot uses `webdriver-manager` to automatically download and manage geckodriver. No additional setup required!

#### Safari (macOS only)
Enable Safari's WebDriver support:
```bash
safaridriver --enable
```

## Usage

### Start the Web Application

**Windows:** Double-click `run.bat`

**macOS/Linux:** Run `./run.sh`

**Or manually:**
```bash
python app.py
```

Then open your browser and navigate to: `http://localhost:5000`

### Configure the Bot

1. **Select Browser**: Choose Firefox or Safari
2. **Login Method**:
   - **Email & Password**: Enter your Whatnot credentials
   - **Google Login**: Complete Google OAuth manually in the browser window
3. **Advanced Settings** (optional):
   - Giveaway wait time
   - Stream check interval
   - Maximum streams per session
   - Headless mode (runs without visible browser)

### Start Hunting

Click "Start Bot" to begin. The bot will:
1. Open a browser window
2. Log into your Whatnot account
3. Navigate to live streams
4. Search for streams with giveaways
5. Enter each stream and look for active giveaways
6. Automatically enter giveaways found
7. Wait for giveaway completion
8. Check for follow-up giveaways
9. Move to the next stream when done

### Monitor Progress

- View real-time logs in the status panel
- Track giveaways entered and streams visited
- See the current stream being watched
- Monitor bot state (idle, hunting, etc.)

## Project Structure

```
whatnotbot/
├── app.py                 # Flask web application
├── requirements.txt       # Python dependencies
├── setup.bat              # Windows setup script
├── run.bat                # Windows run script
├── setup.sh               # macOS/Linux setup script
├── run.sh                 # macOS/Linux run script
├── bot/
│   ├── __init__.py
│   ├── config.py         # Bot configuration
│   └── whatnot_bot.py    # Main bot logic
├── templates/
│   └── index.html        # Web interface
└── static/               # Static assets (CSS/JS)
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `browser` | firefox | Browser to use (firefox/safari) |
| `login_method` | credentials | Login method (credentials/google) |
| `headless` | false | Run browser without visible window |
| `giveaway_wait_time` | 30 | Seconds to wait for giveaway completion |
| `stream_check_interval` | 5 | Seconds between stream refreshes |
| `max_streams` | 50 | Maximum streams to check per session |

## Troubleshooting

### Firefox Issues
- Ensure Firefox is installed
- The bot will automatically download geckodriver via webdriver-manager

### Safari Issues
- Safari WebDriver is macOS only
- Run `safaridriver --enable` before first use
- Allow automation in Safari preferences

### Login Issues
- If using Google login, complete the process in the browser window
- For credentials login, ensure email and password are correct
- Check for CAPTCHA or additional verification requirements

## Disclaimer

⚠️ **Use at your own risk!**

This bot is for educational purposes only. Automated actions may violate Whatnot's Terms of Service. The developers are not responsible for any account bans or other consequences from using this tool.

## License

MIT License - See LICENSE file for details
