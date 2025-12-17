# DungeonCrawler Bot 🤖

A [Probot](https://probot.github.io) app to automate DungeonCrawlerAI repository workflows.

## Features

- 🏷️ **Auto-labeling** - Labels issues/PRs based on content
- 👋 **Welcome messages** - Greets first-time contributors
- ⏰ **Stale management** - Marks and closes inactive issues
- 💝 **Reactions** - Reacts to thank-you comments
- 📝 **Release notes** - Enhances release descriptions

## Setup

### 1. Create a GitHub App

1. Go to https://github.com/settings/apps/new
2. Fill in the details:
   - **Name:** DungeonCrawler Bot
   - **Webhook URL:** Your server URL or smee.io proxy
   - **Webhook Secret:** Generate a random string
3. Set permissions:
   - Issues: Read & Write
   - Pull Requests: Read & Write
   - Contents: Read
   - Metadata: Read
4. Subscribe to events:
   - Issues
   - Issue comment
   - Pull request
   - Release
5. Generate a private key and download it

### 2. Install Dependencies

```bash
cd probot-app
npm install
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your App ID, Webhook Secret, and Private Key
```

### 4. Run Locally

```bash
# Start with smee.io for webhook forwarding
npx smee -u https://smee.io/YOUR_CHANNEL -t http://localhost:3000/api/github/webhooks

# In another terminal
npm start
```

### 5. Install on Repository

1. Go to your GitHub App settings
2. Click "Install App"
3. Select the DungeonCrawlerAI repository

## Deployment

### Vercel

```bash
npm i -g vercel
vercel
```

### Heroku

```bash
heroku create dungeoncrawler-bot
git push heroku main
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
CMD ["npm", "start"]
```

## Development

```bash
# Run with auto-reload
npm run dev

# Run tests
npm test
```

## License

MIT
