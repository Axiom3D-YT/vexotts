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

### Pulling from GHCR

If you don't want to build the image locally, you can pull the pre-built AMD64 image from the GitHub Container Registry:

1. Authenticate with GHCR (if the repository is private):
   ```bash
   echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
   ```

2. Pull the latest image:
   ```bash
   docker pull ghcr.io/axiom3d-yt/vexotts:latest
   ```

3. Update your `docker-compose.yml` to use the image and run:
   ```bash
   docker-compose up -d
   ```
