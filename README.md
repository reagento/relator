# Relator <a href="https://github.com/marketplace/actions/reagento-relator">🔔</a>

![GitHub Actions](https://shieldcn.dev/badge/GitHub%20Actions-077124.svg?size=xs&font=geist&logo=githubactions)
![Requires Python](https://shieldcn.dev/badge/requires%20python-3.10+-3775A9.svg?size=xs&mode=light&logo=python&logoColor=ffffff)
![Telegram Bot](https://shieldcn.dev/badge/Telegram-Bot-abcde3.svg?font=geist&size=xs&logo=ri%3AFaTelegramPlane&color=26a4e2&valueColor=ffffff)
![Discord](https://shieldcn.dev/badge/Discord-Webhook-5865F2.svg?logo=discord&size=xs)
<a href="https://github.com/reagento/relator/actions/workflows/codeql.yml"><picture><source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/github/ci/reagento/relator.svg?workflow=codeql.yml&amp;variant=ghost&amp;size=xs&amp;theme=zinc&amp;logo=ri%3AFiGithub&amp;label=CodeQL&amp;mode=dark"><img alt="badge" src="https://shieldcn.dev/github/ci/reagento/relator.svg?workflow=codeql.yml&amp;variant=ghost&amp;size=xs&amp;theme=zinc&amp;logo=ri%3AFiGithub&amp;label=CodeQL&amp;mode=light"></picture></a>

**Relator** (Latin _referre_ - "to report") - delivers beautifully formatted GitHub notifications to Telegram and Discord. Get instant alerts for issues and PRs with smart labeling and clean formatting, keeping your team informed in real-time.

## ✨ Features

- **Multi-Platform**: Send notifications to Telegram, Discord, or both simultaneously
- **Instant Notifications**: Get real-time alerts for new events
- **Rich Formatting**: HTML for Telegram, rich embeds for Discord
- **Label Support**: Automatically converts GitHub labels to hashtags
- **Customizable**: Multiple configuration options for different needs
- **Reliable**: Built-in retry mechanism with exponential backoff

## 🚀 Quick Start

### Telegram Notifications

```yaml
name: Event Notifier

on:
  issues:
    types: [opened, reopened]
  pull_request_target:
    types: [opened, reopened]

permissions:
  issues: read
  pull-requests: read

jobs:
  notify:
    name: "Telegram notification"
    runs-on: ubuntu-latest
    steps:
      - name: Send Telegram notification for new issue or pull request
        uses: reagento/relator@v1.7.1
        with:
          tg-bot-token: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          tg-chat-id: ${{ vars.TELEGRAM_CHAT_ID }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

### Discord Notifications

```yaml
name: Event Notifier

on:
  issues:
    types: [opened, reopened]
  pull_request_target:
    types: [opened, reopened]

permissions:
  issues: read
  pull-requests: read

jobs:
  notify:
    name: "Discord notification"
    runs-on: ubuntu-latest
    steps:
      - name: Send Discord notification for new issue or pull request
        uses: reagento/relator@v1.7.1
        with:
          discord-webhook-url: ${{ secrets.DISCORD_WEBHOOK_URL }}
          discord-thread-id: ${{ vars.DISCORD_THREAD_ID }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

### Both Platforms Simultaneously

```yaml
- name: Send notification to Telegram and Discord
  uses: reagento/relator@v1.7.1
  with:
    tg-bot-token: ${{ secrets.TELEGRAM_BOT_TOKEN }}
    tg-chat-id: ${{ vars.TELEGRAM_CHAT_ID }}
    discord-webhook-url: ${{ secrets.DISCORD_WEBHOOK_URL }}
    github-token: ${{ secrets.GITHUB_TOKEN }}
```

> github-token it's not required for public projects and is unlikely to hit any [limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28#primary-rate-limit-for-unauthenticated-users). However, github actions uses IP-based limits, and since github actions has a limited pool of addresses, these limits are considered public, and you'll hit them very quickly.

### Advanced Configuration

```yaml
- name: Send Telegram notification for new issue
  uses: reagento/relator@v1.7.1
  with:
    tg-bot-token: ${{ secrets.TELEGRAM_BOT_TOKEN }}
    tg-chat-id: ${{ vars.TELEGRAM_CHAT_ID }}
    github-token: ${{ secrets.GITHUB_TOKEN }}
    base-url: "https://github.com/your-org/your-repo"
    python-version: "3.10"
    attempt-count: "5"
    # if you want to join the input with a list of labels
    join-input-with-list: "1"
    # if you have topics
    tg-message-thread-id: 2
    # by default templates exist, these parameters override them
    html-template: "<b>New issue by <a href=/{user}>@{user}</a> </b><br/><b>{title}</b> (<a href='{url}'>#{id}</a>)<br/>{body}{labels}<br/>{promo}"
    # Custom tags to add to every notification (comma-separated)
    custom-labels: "my_project,custom,etc"
```

Available inputs:

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `tg-bot-token` | No | — | Telegram bot token |
| `tg-chat-id` | No | — | Telegram numeric chat ID, or `"@chatname"` for a public chat |
| `tg-message-thread-id` | No | — | Telegram topic/thread ID |
| `discord-webhook-url` | No | — | Discord webhook URL |
| `discord-thread-id` | No | — | Discord thread ID to post in |
| `github-token` | No | — | GitHub token for API access |
| `base-url` | No | `https://github.com` | Base URL used when rendering links |
| `python-version` | No | `3.10` | Python version used by the action |
| `attempt-count` | No | `2` | Number of Telegram API attempts |
| `html-template` | No | — | Custom HTML template for Telegram messages |
| `join-input-with-list` | Yes | `0` | Render GitHub task-list inputs as a list |
| `custom-labels` | No | — | Comma-separated labels added to each notification |

## 🔧 Setup Instructions

### Telegram Setup

1. Create a Telegram Bot

- Message `@BotFather` on [Telegram](https://t.me/botfather)
- Create a new bot with `/newbot`
- Save the bot token

2. Get Chat ID

- For a public chat, use its username directly: `tg-chat-id: "@chatname"`
- For a private chat, add your bot to the chat and send a message
- Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
- Find the private chat's `chat.id` in the response

3. Configure GitHub Secrets
   Add these secrets in your repository settings:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### Discord Setup

1. Create a Discord Webhook

- Go to your Discord server settings
- Navigate to **Integrations** → **Webhooks**
- Click **New Webhook**
- Customize the webhook name and select the target channel
- Copy the **Webhook URL**

2. Configure GitHub Secrets
   Add these secrets in your repository settings:

- `DISCORD_WEBHOOK_URL`
- `DISCORD_THREAD_ID` (optional)

## 📋 Example Output

### Telegram

Your Telegram notifications will look like this:

Issue:

```text
🚀 New issue by @username
📌 Bug in authentication module (#123)

[Issue description content here...]

#bug #high_priority #authentication
sent via relator
```

Pull requests:

```text
🎉 New Pull Request to test/repo by @username
✨ Update .gitignore (#3)
📊 +1/-0
🌿 Sehat1137:test → master

[Pull requests description content here...]

#bug #high_priority #authentication
sent via relator
```

### Discord

Discord notifications appear as rich embeds with:

- **Color-coded embeds**: Green for issues, purple for pull requests
- **User avatars**: GitHub profile picture displayed
- **Repository links**: Clickable links to repository and issue/PR
- **Organized fields**: Repository, issue/PR number, changes (for PRs), branch info (for PRs)
- **Markdown formatting**: Clean formatting with proper code blocks, bold, italic, and links
- **Labels as hashtags**: Same label format as Telegram

## 🤝 Acknowledgments

This action uses:
- [sulguk](https://github.com/Tishka17/sulguk) by `@Tishka17` for reliable Telegram message delivery
- [markdownify](https://github.com/matthewwithanm/python-markdownify) for HTML to Markdown conversion for Discord

## 🌟 Support

If you find this action useful, please consider:

- ⭐ Starring the repository on GitHub
- 🐛 Reporting issues if you find any bugs
- 💡 Suggesting features for future improvements
- 🔄 Sharing with your developer community

## 📝 License

This project is open source and available under the [MIT License](https://opensource.org/licenses/MIT).

## ⚙️ Used by

**Relator** is used by many open source projects here we highlight a few:

| Project                                                                        | Logo                                               | Description                                               |
| ------------------------------------------------------------------------------ | -------------------------------------------------- | --------------------------------------------------------- |
| [FastStream](https://github.com/ag2ai/faststream)                              | <img src=".static/faststream.png" width="45">      | FastStream is a powerful and easy-to-use Python framework |
| [Dishka](https://github.com/reagento/dishka)                                   | <img src=".static/reagento.png" width="45">        | Cute dependency injection (DI) framework for Python       |
| [easyp](https://github.com/easyp-tech/easyp)                                   | <img src=".static/easyp.png" width="45">           | Easyp is a cli tool for workflows with proto files        |
| [wemake.services](https://github.com/wemake-services/wemake-python-styleguide) | <img src=".static/wemake-services.png" width="45"> | The strictest and most opinionated python linter ever!    |
