# SmartHeart Bot

A robust and flexible Telegram bot designed for content publishing and user activity tracking. This bot serves as a content distribution platform for a creative agency, enabling seamless material sharing, user engagement tracking, and automated mailing management.

## Project Overview

SmartHeart Bot provides a comprehensive solution for:
- **Content Publishing**: Manage and distribute materials, products, and events to users
- **User Activity Tracking**: Monitor user interactions, material views, and profile completion
- **Automated Mailings**: Schedule and send targeted messages to users
- **CRM Integration**: Sync user data with AmoCRM for lead management
- **Admin Panel**: Full administrative control through Telegram interface

## Architecture

The project follows a clean, modular structure:

```
SmartHeart/
├── app/
│   ├── bot/
│   │   ├── admin_handlers/      # Admin command and callback handlers
│   │   ├── user_handlers/       # User-facing command and callback handlers
│   │   ├── services/            # Business logic layer
│   │   │   ├── amocrm_service.py
│   │   │   ├── file_service.py
│   │   │   ├── mailing_service.py
│   │   │   ├── material_service.py
│   │   │   └── user_service.py
│   │   ├── messages.py          # Centralized message templates
│   │   ├── scheduler.py         # Mailing scheduler
│   │   ├── mailing_sender.py    # Mailing execution logic
│   │   ├── utils.py             # Utility functions
│   │   └── validators.py        # Input validation
│   ├── db/
│   │   ├── models.py            # SQLAlchemy models
│   │   └── database.py          # Database connection and session management
│   └── config.py                # Configuration and environment variables
├── main.py                       # Application entry point
└── requirements.txt              # Python dependencies
```

## Key Features

### Content Management
- **Materials**: Categorize and publish educational materials with media support
- **File Management**: Store and retrieve files (documents, images, videos)
- **View Tracking**: Record and analyze user interactions with materials

### User Management
- **Profile System**: Collect and manage user profiles (name, company, position, phone)
- **Consent Management**: Track user consent for data processing
- **User Statistics**: Export user data with material viewing history

### Mailing System
- **Scheduled Mailings**: Plan and schedule messages for future delivery
- **Progress Tracking**: Real-time monitoring of mailing progress
- **Multiple Formats**: Support for text, photo, and video messages
- **Error Handling**: Automatic tracking of blocked users and delivery errors

### CRM Integration
- **AmoCRM Sync**: Create leads and sync user data with AmoCRM
- **Lead Management**: Link Telegram users to CRM leads

## Database Models

- **User**: Stores user profiles, consent status, and CRM lead IDs
- **Material**: Content items with categories, media, and document attachments
- **UserMaterialView**: Tracks which materials users have viewed
- **File**: Manages uploaded files and their Telegram file IDs
- **Mailing**: Stores mailing campaigns with scheduling and statistics

## Technology Stack

- **Python 3.10+**
- **pyTelegramBotAPI**: Telegram Bot API wrapper
- **SQLAlchemy 2.0**: ORM for database operations
- **Loguru**: Logging framework
- **python-dotenv**: Environment variable management
- **openpyxl**: Excel file generation for statistics export

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with the following variables:
```
BOT_TOKEN=your_telegram_bot_token
ADMIN_GROUP_ID=your_admin_group_id
MAIN_TOPIC_ID=your_main_topic_id
MAILING_TOPIC_ID=your_mailing_topic_id
EVENTS_TOPIC_ID=your_events_topic_id
AMOCRM_URL=your_amocrm_url
AMOCRM_ACCESS_TOKEN=your_amocrm_token
AMOCRM_PIPELINE_ID=your_pipeline_id
```

3. Run the bot:
```bash
python main.py
```

## Project Goals

The primary goal of this project is to create a **reliable and flexible structure** for:
- Publishing content efficiently
- Tracking user actions and engagement
- Managing automated communications
- Integrating with external CRM systems

The architecture emphasizes clean code, maintainability, and scalability while keeping the codebase minimal and focused on core functionality.

