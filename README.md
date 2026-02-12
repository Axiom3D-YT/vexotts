# VexoTTS

A high-performance Discord TTS bot powered by FastAPI and gTTS.

## Features

- **FastAPI Backend**: Fast and efficient API to trigger TTS.
- **Discord Integration**: Joins voice channels and plays high-quality TTS audio.
- **Docker Support**: Easy deployment using Docker and Docker Compose.
- **Robust Audio Handling**: Uses locks to prevent overlapping audio and ensures proper file cleanup.

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- A Discord Bot Token (from the [Discord Developer Portal](https://discord.com/developers/applications))

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Axiom3D-YT/vexotts.git
   cd vexotts
   ```

2. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and paste your `DISCORD_TOKEN`.

3. Start the bot with Docker Compose:
   ```bash
   docker-compose up -d
   ```

## API Usage

The bot exposes a POST endpoint to trigger TTS:

**Endpoint**: `POST /speak`

**Payload**:
```json
{
  "guild_id": 123456789,
  "channel_id": 987654321,
  "message": "Hello from VexoTTS!",
  "voice": "en",
  "slow": false
}
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE)
