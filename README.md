# 🎓 Multi-User Flashcard Quiz App

A real-time multiplayer quiz application built with Python socket programming. Multiple clients can connect simultaneously, choose topics, answer questions, and compete on a live leaderboard.

## ✨ Features

- **Multi-client support**: Multiple users can connect and play simultaneously
- **Real-time gameplay**: Live leaderboard updates after each question
- **Multiple topics**: Math, History, Science, and Geography
- **Multiple game rounds**: Play continuous quizzes without reconnecting
- **Enhanced user experience**: Improved menus and game flow
- **Username management**: Change usernames between sessions
- **Session statistics**: Track your performance across rounds
- **Interactive terminal UI**: Clean, colorful interface with emojis
- **Cross-platform**: Works on Windows, Linux, and macOS
- **No external dependencies**: Uses only Python standard library

## 📁 Project Structure

```
cn/
├── server.py          # Quiz server implementation
├── client.py          # Basic quiz client implementation
├── client_enhanced.py # Enhanced client with multiple rounds
├── questions.json     # Question database
├── requirements.txt   # Dependencies (Python stdlib only)
└── README.md         # This file
```

## 🚀 Quick Start

### 1. Start the Server

Open a terminal and run:

```bash
# Windows
python server.py

# Linux/macOS
python3 server.py
```

The server will start on `localhost:12345` by default and display:
- Available topics
- Connection status
- Player activities
- Quiz progress

### 2. Connect Clients

Open additional terminal windows/tabs for each player:

```bash
# Basic Client (single quiz per session)
# Windows
python client.py

# Enhanced Client (multiple rounds, better UX)
# Windows  
python client_enhanced.py

# Linux/macOS
python3 client.py
# OR
python3 client_enhanced.py
```

**Enhanced Client Features:**
- 🔄 Play multiple quiz rounds without reconnecting
- 👤 Change username between sessions
- 📊 View session statistics
- 🎮 Improved game menus and flow
- 🎯 Better post-quiz options

Each client will:
1. Connect to the server
2. Enter a username
3. Access the game menu (enhanced client)
4. Select a quiz topic
5. Answer 5 random questions
6. See real-time leaderboard updates
7. View final results
8. Choose to play again or exit (enhanced client)

### 3. Play the Quiz

1. **Registration**: Enter a unique username
2. **Topic Selection**: Choose from Math, History, Science, or Geography
3. **Answer Questions**: Select from multiple choice options (1-4)
4. **View Results**: See if your answer was correct and current score
5. **Leaderboard**: Check your ranking against other players
6. **Final Results**: View your final score and performance rating

## 🔄 Post-Quiz Options

### Enhanced Client Features (client_enhanced.py)
After completing a quiz, players can:

1. **🔄 Play Another Quiz**
   - Choose the same or different topic
   - Keep the same username
   - Continue competing on the leaderboard

2. **👤 Change Username**
   - Switch to a new identity
   - Fresh start with new username
   - Previous scores reset

3. **📊 View Session Statistics**
   - See current score and accuracy
   - Track performance across rounds
   - Get improvement tips

4. **🎮 Enhanced Game Menu**
   - User-friendly navigation
   - Clear options and feedback
   - Smooth game flow

### Basic Client (client.py)
- Single quiz session per connection
- Manual restart required (run `python client.py` again)
- Simple and straightforward experience

## 🎮 How to Play

### Server Side
- The server loads questions from `questions.json`
- Accepts multiple client connections
- Manages quiz sessions for each client
- Broadcasts leaderboard updates in real-time
- Handles client disconnections gracefully

### Client Side
- Connect with a unique username
- Choose your preferred topic
- Answer 5 multiple-choice questions
- Compete for the highest score
- View live leaderboard after each question

## 📊 Question Format

Questions are stored in `questions.json`:

```json
{
  "Math": [
    {
      "q": "What is 2 + 2?",
      "a": "4",
      "choices": ["2", "3", "4", "5"]
    }
  ]
}
```

## 🔧 Configuration

### Server Settings
Edit `server.py` to modify:
- `host` and `port` (default: localhost:12345)
- `max_questions` (default: 5 per quiz)
- `questions_file` path

### Client Settings
The client will prompt for server details on startup, or modify `client.py`:
- Default host: localhost
- Default port: 12345

## 🌐 Network Protocol

Messages are sent as JSON objects:

```json
{
  "type": "register|topic|question|answer|result|leaderboard",
  "username": "player_name",
  "data": "message_specific_data"
}
```

## 🎯 Game Rules

- **5 questions per quiz** (configurable)
- **Multiple choice answers** (4 options each)
- **1 point per correct answer**
- **Real-time leaderboard** sorted by score
- **No time limit** per question
- **Multiple rounds support** (enhanced client)
- **Graceful disconnection** handling
- **Username switching** between rounds

## 🏆 Scoring System

- ✅ Correct answer: +1 point
- ❌ Wrong answer: 0 points
- 🏆 Leaderboard: Sorted by total score
- 📊 Final percentage: (score/total) × 100

## 🛠 Technical Implementation

### Technologies Used
- **Python 3.x**: Core programming language
- **socket**: TCP networking
- **threading**: Multi-client handling
- **json**: Message serialization
- **random**: Question selection

### Key Features
- **Thread-safe operations**: Using locks for shared data
- **Error handling**: Graceful connection management
- **Cross-platform**: Works on all major operating systems
- **Clean separation**: Server and client responsibilities

## 🧪 Testing

### Single Machine Testing
1. Start the server: `python server.py`
2. Open multiple terminals
3. Run `python client.py` or `python client_enhanced.py` in each terminal
4. Use different usernames for each client
5. Test multiple rounds with the enhanced client

### Enhanced Client Testing
1. Complete a quiz and test post-quiz options
2. Try changing usernames between rounds
3. Play multiple topics in one session
4. Check session statistics display

### Network Testing
1. Run server on one machine
2. Connect clients from different machines
3. Use the server's IP address in client connections
4. Test both basic and enhanced clients over network

## 🎨 Sample Gameplay

```
🎓 Quiz Server started on localhost:12345
📚 Available topics: Math, History, Science, Geography
⏳ Waiting for clients to connect...
🔗 New connection from ('127.0.0.1', 50234)
👤 Alice registered from ('127.0.0.1', 50234)
📖 Alice selected topic: Math
❓ Sent question 1 to Alice
✅ Correct! Alice answered: 4 (correct: 4)
```

## 🚨 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Change port in server.py or wait for port to be released
```

**Connection refused:**
- Ensure server is running first
- Check firewall settings
- Verify host/port configuration

**JSON decode errors:**
- Usually indicates network issues
- Check connection stability

## 📝 Future Enhancements

- [ ] Timed questions with countdown
- [ ] Custom question sets upload
- [ ] Player statistics dashboard
- [ ] Admin controls and moderation
- [ ] GUI interface with modern frameworks
- [ ] Question difficulty levels (Easy/Medium/Hard)
- [ ] Team play mode and tournaments
- [ ] Voice chat integration
- [ ] Question categories expansion
- [ ] Achievement system and badges

## 🤝 Contributing

Feel free to enhance the quiz app:
1. Add more question categories
2. Implement time limits
3. Add colorful terminal output
4. Create a web interface
5. Add sound effects

## 📄 License

This project is open source and available under the MIT License.

---

**Ready to test your knowledge? Start the server and challenge your friends! 🎓🏆**
