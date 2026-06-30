# 🤝 CONTRIBUTING.md

## 📖 **English**

### 🌟 **Welcome Contributors!**

Thank you for your interest in contributing to **LudoBot**! This guide will help you get started with contributing to the project. Whether you're a beginner or an experienced developer, there are many ways to help.

---

## 🎯 **Ways to Contribute**

### 🐍 **Code Contributions**
- Implement new features
- Fix bugs and issues
- Improve performance
- Write unit tests
- Refactor code

### 📚 **Documentation**
- Improve README
- Write tutorials
- Create video guides
- Translate documentation
- Add code comments

### 🎨 **Design**
- Design board themes
- Create emojis
- Improve UI/UX
- Design marketing materials

### 🌍 **Translation**
- Translate to new languages
- Review existing translations
- Fix translation errors

### 🧪 **Testing**
- Test new features
- Report bugs
- Provide feedback
- Create test cases

---

## 🚀 **Getting Started**

### 1. **Fork the Repository**
```bash
# Click the Fork button on GitHub
# Then clone your fork
git clone https://github.com/VIDAKHOSHPEY22/LudoBot.git

cd LudoBot
```

### 2. **Set Up Development Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your BOT_TOKEN and OWNER_ID
```

### 3. **Create a Branch**
```bash
# Create a branch for your feature
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/your-bug-fix
```

### 4. **Make Your Changes**
- Write clean, readable code
- Add comments where needed
- Follow existing code style
- Write tests for new features

### 5. **Test Your Changes**
```bash
# Run the bot locally
python run.py

# Run tests (if available)
pytest
```

### 6. **Commit Your Changes**
```bash
# Add your changes
git add .

# Commit with a meaningful message
git commit -m "feat: add your feature description"

# Push to your fork
git push origin feature/your-feature-name
```

### 7. **Create a Pull Request**
- Go to the original repository
- Click "New Pull Request"
- Select your branch
- Describe your changes
- Submit the pull request

---

## 📝 **Commit Message Guidelines**

### **Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

### **Types:**

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style changes |
| `refactor` | Code refactoring |
| `perf` | Performance improvements |
| `test` | Adding tests |
| `chore` | Maintenance tasks |

### **Examples:**
```bash
# Good commit
git commit -m "feat(game): add dice rolling animation

- Add animated dice emoji
- Show rolling animation for 1.5 seconds
- Display final result with emoji"

# Bad commit (avoid)
git commit -m "updated stuff"
```

---

## 🎨 **Coding Standards**

### **Python Style**
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names

### **Docstrings**
```python
def calculate_score(player: Player) -> int:
    """
    Calculate the total score for a player.

    Args:
        player: Player object with tokens

    Returns:
        int: Total score based on finished tokens

    Example:
        >>> player = Player(user_id=123, username="John")
        >>> calculate_score(player)
        40
    """
    return player.wins * 10 + player.score
```

---

## 🐛 **Bug Reports**

When reporting bugs, please include:

1. **Description** - What happened?
2. **Steps to Reproduce** - How to reproduce it?
3. **Expected Behavior** - What should have happened?
4. **Screenshots** - If applicable
5. **Environment** - OS, Python version, etc.
6. **Logs** - Error messages or logs

### **Example:**
```markdown
## Bug Report

**Description:** Game crashes when rolling dice with no tokens on board.

**Steps to Reproduce:**
1. Start a new game
2. Roll dice
3. Game crashes

**Expected Behavior:** Should show "No tokens can move" message.

**Environment:**
- OS: Windows 11
- Python: 3.11
- Bot Version: v1.0.0
```

---

## 💡 **Feature Requests**

When suggesting features, please include:

1. **Description** - What feature would you like?
2. **Use Case** - Why is it useful?
3. **Examples** - How would it work?
4. **Mockups** - UI/UX design (if applicable)

---

## 🧪 **Testing**

### **Writing Tests**
```python
import pytest
from game.core.ludo_game import LudoGame

def test_dice_roll():
    """Test that dice roll returns a value between 1 and 6."""
    game = LudoGame("test_game")
    result = game.dice.roll()
    assert 1 <= result <= 6
```

### **Running Tests**
```bash
# Install testing dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run tests with coverage
pytest --cov=.
```

---

## 🌿 **Branch Naming Convention**

| Type | Format | Example |
|------|--------|---------|
| Feature | `feature/feature-name` | `feature/dice-animation` |
| Bug Fix | `fix/bug-description` | `fix/token-collision` |
| Documentation | `docs/doc-update` | `docs/update-readme` |
| Refactor | `refactor/component` | `refactor/game-engine` |

---

## 📋 **Pull Request Checklist**

- [ ] Code follows style guidelines
- [ ] Tests have been added/updated
- [ ] Documentation has been updated
- [ ] No breaking changes (or documented)
- [ ] Branch is up to date with main
- [ ] Commit messages are clear
- [ ] All tests pass

---

## 💬 **Community Guidelines**

1. **Be Respectful** - Treat everyone with respect
2. **Be Helpful** - Help others learn and grow
3. **Be Open** - Welcome new ideas and perspectives
4. **Be Patient** - Responses may take time
5. **Be Constructive** - Provide useful feedback

---

## 🎁 **Recognition**

Contributors will be:
- Added to the CONTRIBUTORS list
- Mentioned in release notes
- Given credit in documentation
- Invited to special events

---

## 📫 **Contact**

- **GitHub Issues:** [Report a bug](*https://github.com/VIDAKHOSHPEY22/LudoBot/issues)
- **Telegram:** [@LudoGoPlayBot](https://t.me/LudoGoPlayBot)
- **Email:** vviiddaa2@gmail.com

---

## 🎯 **Roadmap & Planned Features**

### 🚀 **Features Coming Soon**

We're constantly working to improve LudoBot! Here's what's on our roadmap:

---

### 🌟 **Phase 1: Core Enhancements**

#### 🎨 **Advanced UI/UX**
- [ ] **Custom Themes** - Choose from multiple color themes for the board
- [ ] **Animated Dice** - 3D dice roll animation with sound effects
- [ ] **Interactive Board** - Clickable board with token positions highlighted
- [ ] **Dark/Light Mode** - Toggle between dark and light themes
- [ ] **Custom Emojis** - Use custom emoji sets for tokens and board

#### 💬 **Chat & Social Features**
- [ ] **Voice Chat** - Integrated voice chat during gameplay
- [ ] **Sticker Support** - Send stickers during the game
- [ ] **Game Emojis** - Custom emoji reactions for game events
- [ ] **Message Translation** - Auto-translate messages between players
- [ ] **Group Chat** - Dedicated group chat for each game session

#### 🏆 **Competitive Features**
- [ ] **Tournament Mode** - Organize tournaments with brackets
- [ ] **Ranked Matches** - Competitive matchmaking based on skill
- [ ] **Leaderboard** - Global and friends leaderboard
- [ ] **Achievements** - Unlock achievements for milestones
- [ ] **Daily Challenges** - Complete daily challenges for rewards

---

### 🔥 **Phase 2: Advanced Features**

#### 🎮 **Game Modes**
- [ ] **Speed Mode** - Faster gameplay with 15-second turns
- [ ] **Classic Mode** - Traditional Ludo rules
- [ ] **Team Mode** - 2v2 team play
- [ ] **Battle Royale** - 4-player free-for-all
- [ ] **Practice Mode** - Play against AI bots

#### 🤖 **AI & Automation**
- [ ] **Bot Players** - Play with AI opponents when short on players
- [ ] **Auto-Roll** - Automatic dice rolling for faster play
- [ ] **Smart Suggestions** - AI-powered move suggestions
- [ ] **Game Analysis** - Post-game analysis and statistics

#### 📱 **Integration**
- [ ] **Web App** - Full web version with better graphics
- [ ] **Mobile App** - Native mobile app for Android/iOS
- [ ] **Desktop App** - Electron desktop application
- [ ] **Discord Integration** - Play via Discord bot
- [ ] **WebSocket** - Real-time updates without polling

---

### 🚀 **Phase 3: Premium Features**

#### 💎 **Monetization**
- [ ] **Premium Subscriptions** - Ad-free experience, exclusive themes
- [ ] **Virtual Currency** - Earn coins by playing, spend on cosmetics
- [ ] **NFT Integration** - Unique digital collectibles
- [ ] **Tournament Tickets** - Buy tickets for premium tournaments
- [ ] **Custom Bots** - Create and monetize AI bots

#### 🎯 **Social & Community**
- [ ] **Clan System** - Create and join gaming clans
- [ ] **Friend List** - Add friends and see their online status
- [ ] **Invite System** - Invite friends with referral bonuses
- [ ] **Live Streaming** - Stream games to YouTube/Twitch
- [ ] **Spectator Mode** - Watch live games

---

### 🌍 **Phase 4: Global Expansion**

#### 🌐 **Localization**
- [ ] **Persian Support** - Full Persian translation
- [ ] **Russian Support** - Full Russian translation
- [ ] **Turkish Support** - Full Turkish translation
- [ ] **German Support** - Full German translation
- [ ] **French Support** - Full French translation
- [ ] **Spanish Support** - Full Spanish translation
- [ ] **Hindi Support** - Full Hindi translation

#### 🌍 **Regional Features**
- [ ] **Regional Leaderboards** - Country-specific rankings
- [ ] **Cultural Themes** - Country-specific board designs
- [ ] **Holiday Events** - Special events for local holidays
- [ ] **Local Payments** - Regional payment gateways

---

### 🔧 **Technical Improvements**

#### 🛠️ **Development**
- [ ] **Docker Support** - Containerized deployment
- [ ] **CI/CD Pipeline** - Automated testing and deployment
- [ ] **API Documentation** - Full API reference
- [ ] **Plugin System** - Extend functionality with plugins
- [ ] **WebSocket API** - Real-time API for external apps

#### 📊 **Analytics**
- [ ] **Game Statistics** - Detailed game analytics
- [ ] **User Behavior** - Heat maps and user journey analysis
- [ ] **Performance Monitoring** - Real-time performance metrics
- [ ] **Error Tracking** - Automatic error reporting

#### 🔒 **Security**
- [ ] **2FA for Admins** - Two-factor authentication
- [ ] **Anti-Cheat** - Cheat detection and prevention
- [ ] **Rate Limiting** - API rate limiting
- [ ] **Data Encryption** - End-to-end encryption for sensitive data

---

### 🗓️ **Timeline**

| Phase | Estimated Completion | Status |
|-------|---------------------|--------|
| **Phase 1** | Q1 2025 | 🟡 In Progress |
| **Phase 2** | Q2 2025 | ⚪ Planned |
| **Phase 3** | Q3 2025 | ⚪ Planned |
| **Phase 4** | Q4 2025 | ⚪ Planned |

---

### 📊 **Success Metrics**

We track these metrics to measure success:

| Metric | Target | Current |
|--------|--------|---------|
| **Monthly Active Users** | 10,000+ | 📊 Tracking |
| **Games Played per Day** | 1,000+ | 📊 Tracking |
| **User Retention** | 60%+ | 📊 Tracking |
| **Average Play Time** | 15+ mins | 📊 Tracking |
| **Community Growth** | 20% monthly | 📊 Tracking |

---

### 🎯 **Vision**

To create the **best multiplayer board game experience on Telegram** where players from around the world can connect, compete, and have fun together.

---

## 🙏 **Thank You!**

Your contributions make LudoBot better for everyone!

---

**[⭐ Star this repository if you like it!]**

**[🤝 Contributions are always welcome!]**

**[🎲 Have fun playing Ludo!]**