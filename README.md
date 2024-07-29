# Telebox Telegram Bot

This repository contains a Telegram bot that interacts with the Telebox API to upload and download files. The bot automatically uploads files sent via Telegram to Telebox and can download files from Telebox to Telegram when a valid link is provided.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
  - [Configuration](#configuration)
  - [Installation](#installation)
  - [Deployment](#deployment)
- [Usage](#usage)
- [License](#license)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
- [Troubleshooting](#troubleshooting)

## Features

- **Upload to Telebox**: Automatically upload files received in Telegram to Telebox.
- **Download from Telebox**: Download files from Telebox using a link and send them back to the Telegram user.
- **Concurrent Uploads**: Supports multiple file uploads concurrently for efficient performance.

## Prerequisites

Before setting up this bot, ensure you have the following:

- **Telegram Bot API Token**: Create a bot using [BotFather](https://core.telegram.org/bots#botfather) on Telegram to get the API token.
- **Telebox API Token and Base Folder ID**: Register on [Telebox](https://www.linkbox.to/) and obtain the necessary API credentials.
- **Docker**: Install Docker on your system by following the official [Docker installation guide](https://docs.docker.com/get-docker/).

## Setup

### Configuration

1. **Edit the configuration file:**  
   Update `app/config.py` with your Telegram API token, Telebox API token, and base folder ID.

   ```python
   class Config:
       TELEGRAM_API_TOKEN = 'YOUR_TELEGRAM_BOT_API_TOKEN'
       TELEBOX_API = 'YOUR_TELEBOX_API_TOKEN'
       TELEBOX_BASEFOLDER = 'YOUR_TELEBOX_BASE_FOLDER_ID'
       TELEBOX_BASE_URI = 'https://www.linkbox.to/'
       USR_LIMIT_CONCURRENT = 5


### INSTALLATION

```git clone https://github.com/yourusername/telebox-telegram-bot.git
cd telebox-telegram-bot

docker build -t telebox-bot 

docker run -d --name telebox-bot -p 5000:5000 telebox-bot