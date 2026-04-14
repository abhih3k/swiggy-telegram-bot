# Good Times League - Telegram Bot

A Telegram bot for automating The Good Times League game with automatic random signup functionality.

## Features

- Automatic account creation with random details (name, age, state)
- Daily game automation
- Score submission
- Leaderboard tracking
- Profile status checking

## Commands

- `/start` - Start the bot and see available commands
- `/play` - Play today's game (optionally with score mode: /play 50, /play 90, /play 150)
- `/status` - Check your current profile and score
- `/leaderboard` - View top players
- `/cancel` - Cancel current operation

## Rewards

- Daily Swiggy Voucher ₹50 (50 pts required)
- Weekly Myntra Voucher ₹1500 (400 pts required)

## Installation

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/abhih3k/swiggy-telegram-bot.git
cd swiggy-telegram-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the bot:
```bash
python sm_swiggy.py
```

### Deploy on Railway

1. Fork this repository
2. Sign up at [Railway.app](https://railway.app)
3. Create a new project from GitHub repo
4. Railway will automatically detect the configuration
5. Your bot will be deployed and running!

## Configuration

The bot uses a hardcoded Telegram bot token. For production use, it's recommended to use environment variables:

1. Create a `.env` file (not included in repo)
2. Add your bot token: `BOT_TOKEN=your_token_here`
3. Update the code to read from environment variables

## How It Works

The bot automatically:
1. Accepts 10-digit mobile numbers
2. For new accounts: generates random name, age, and state
3. Handles OTP verification
4. Checks store proximity (with GPS spoofing for better coverage)
5. Submits scores automatically
6. Sends confirmation and voucher details

## Technical Details

- Built with `python-telegram-bot` (v20+)
- Uses The Good Times League public API
- Implements automatic GPS spoofing for store proximity
- Supports multiple scoring modes (50, 90, 150 points)

## Disclaimer

This bot is for educational purposes only. Use responsibly and in accordance with The Good Times League's terms of service.

## License

MIT License
