# Healing Guru AI App

An AI-powered healing guru application that helps users identify behavioral patterns, work through emotional dysregulation, and access personalized coping tools.

## Features

✨ **Behavioral Pattern Recognition**
- Automatically detects patterns like perfectionism, people-pleasing, catastrophizing, avoidance, self-criticism, and control issues
- Tracks frequency and timing of patterns
- Provides insights into recurring behavioral themes

💚 **Emotion Regulation Support**
- Daily emotional check-ins with intensity tracking
- Body sensation awareness
- Trigger identification

🌟 **Personalized Affirmations**
- Context-aware affirmations based on emotions and detected patterns
- Curated library covering anxiety, sadness, anger, stress, and overwhelm

🛠️ **Coping Tools Toolbox**
- 5-4-3-2-1 Grounding technique
- Box Breathing exercises
- Body Scan meditation
- Progressive Muscle Relaxation
- Emotional Journaling prompts
- Cold Water Reset technique

📊 **Progress Tracking**
- Log effectiveness of different tools
- View historical patterns and trends
- Track emotional journey over time

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Navigate to the project directory**
```bash
cd ~/healing_guru_app
```

2. **Create a virtual environment** (recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

5. **Open in browser**
Navigate to: `http://127.0.0.1:5001`

## Usage

### Daily Check-In
1. Enter your name (optional)
2. Select your current emotion
3. Rate the intensity (1-10)
4. Describe what triggered the feeling
5. Note any body sensations
6. Share your thoughts
7. Click "Get Guidance"

### View Patterns
- Switch to the "Patterns" tab to see detected behavioral patterns
- Patterns are automatically identified from your check-in text
- Frequency and timing are tracked

### Track Progress
- After trying a coping tool, log its effectiveness
- View your progress history in the "Progress" tab
- See which tools work best for you

### Explore Tools
- Browse all available coping tools in the "All Tools" tab
- Each tool includes description, duration, and best use cases

## Data Storage

All data is stored locally in `healing_guru.db` (SQLite database) including:
- User profiles
- Check-ins with emotions, triggers, and thoughts
- Detected behavioral patterns
- Progress logs with tool effectiveness

## Project Structure

```
healing_guru_app/
├── app.py                  # Flask backend with API endpoints
├── templates/
│   └── index.html         # Frontend UI
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── healing_guru.db       # SQLite database (created on first run)
```

## API Endpoints

- `GET /` - Main application page
- `POST /api/checkin` - Submit daily check-in
- `GET /api/patterns` - Get user's behavioral patterns
- `GET /api/progress` - Get progress history
- `POST /api/log_tool` - Log tool effectiveness
- `GET /api/affirmations/<emotion>` - Get affirmations for emotion
- `GET /api/tools` - Get all coping tools

## Pattern Detection

The app detects the following patterns from user input:

- **Perfectionism**: "perfect", "not good enough", "should", "must", "failure"
- **People-Pleasing**: "say no", "disappointing", "others think", "approval"
- **Catastrophizing**: "worst case", "disaster", "terrible", "always", "never"
- **Avoidance**: "ignore", "later", "can't face", "escape", "distract"
- **Self-Criticism**: "stupid", "useless", "worthless", "failure", "wrong"
- **Control**: "control", "need to know", "can't handle", "uncertainty"

## Customization

### Add More Affirmations
Edit the `AFFIRMATIONS` dictionary in `app.py`:
```python
AFFIRMATIONS = {
    'anxiety': [
        "Your custom affirmation here",
        # ... more affirmations
    ]
}
```

### Add More Coping Tools
Edit the `COPING_TOOLS` dictionary in `app.py`:
```python
COPING_TOOLS = {
    'your_tool': {
        'name': 'Tool Name',
        'description': 'Description',
        'duration': '5 minutes',
        'when_to_use': 'Specific situations'
    }
}
```

### Modify Pattern Detection
Edit the `PATTERN_KEYWORDS` dictionary in `app.py` to adjust pattern recognition.

## Future Enhancements

- [ ] AI-powered insights using OpenAI API
- [ ] Export progress reports
- [ ] Mood trends visualization
- [ ] Guided meditation audio
- [ ] Mobile app version
- [ ] Multi-user authentication
- [ ] Therapist collaboration features
- [ ] Integration with wearables for biometric data

## Privacy & Security

- All data stored locally on your device
- No data transmitted to external servers
- Session-based user tracking
- Delete data by removing `healing_guru.db`

## Troubleshooting

**Port already in use:**
```bash
# Change port in app.py (last line):
app.run(debug=True, port=5002)  # Use different port
```

**Database errors:**
```bash
# Delete and recreate database:
rm healing_guru.db
python app.py  # Will create fresh database
```

**Module not found:**
```bash
# Reinstall dependencies:
pip install -r requirements.txt --force-reinstall
```

## Support

For questions or issues, contact: hello@rootedlightwithin.co.uk

## License

This project is for personal wellness use. Feel free to customize and extend for your own needs.

---

Built with ❤️ for healing and growth
