from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import sqlite3
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize database
def init_db():
    conn = sqlite3.connect('healing_guru.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Check-ins table
    c.execute('''CREATE TABLE IF NOT EXISTS checkins
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  emotion TEXT,
                  intensity INTEGER,
                  trigger TEXT,
                  body_sensations TEXT,
                  thoughts TEXT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    # Patterns table
    c.execute('''CREATE TABLE IF NOT EXISTS patterns
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  pattern_type TEXT,
                  description TEXT,
                  frequency INTEGER DEFAULT 1,
                  first_noticed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  last_occurred TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    # Progress table
    c.execute('''CREATE TABLE IF NOT EXISTS progress
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  tool_used TEXT,
                  effectiveness INTEGER,
                  notes TEXT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    conn.commit()
    conn.close()

init_db()

# Affirmations database
AFFIRMATIONS = {
    'anxiety': [
        "I am safe in this moment",
        "My breath anchors me to the present",
        "This feeling will pass, I am resilient",
        "I trust my body to regulate itself",
        "I am stronger than my anxiety"
    ],
    'sadness': [
        "My emotions are valid and temporary",
        "I allow myself to feel and heal",
        "I am worthy of love and care",
        "This too shall pass",
        "I honor my feelings without judgment"
    ],
    'anger': [
        "I acknowledge my anger and choose my response",
        "My feelings are valid, my actions are my choice",
        "I release what I cannot control",
        "I am in charge of my emotional reactions",
        "I express my needs with clarity and respect"
    ],
    'stress': [
        "I can handle one moment at a time",
        "I release tension with each exhale",
        "I prioritize my wellbeing",
        "I am doing my best, and that is enough",
        "I give myself permission to pause"
    ],
    'overwhelm': [
        "I break challenges into manageable steps",
        "I ask for help when I need it",
        "I am capable and resourceful",
        "One thing at a time, one breath at a time",
        "I trust my ability to navigate this"
    ]
}

# Coping tools database
COPING_TOOLS = {
    'grounding': {
        'name': '5-4-3-2-1 Grounding',
        'description': 'Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste',
        'duration': '2-3 minutes',
        'when_to_use': 'Anxiety, panic, dissociation'
    },
    'breathing': {
        'name': 'Box Breathing',
        'description': 'Inhale 4 counts, hold 4, exhale 4, hold 4. Repeat 4 times.',
        'duration': '2-5 minutes',
        'when_to_use': 'Stress, anxiety, overwhelm'
    },
    'body_scan': {
        'name': 'Body Scan',
        'description': 'Slowly scan from head to toe, noticing sensations without judgment',
        'duration': '5-10 minutes',
        'when_to_use': 'Tension, disconnect, before sleep'
    },
    'progressive_relaxation': {
        'name': 'Progressive Muscle Relaxation',
        'description': 'Tense each muscle group for 5 seconds, then release. Start with feet, move up.',
        'duration': '10-15 minutes',
        'when_to_use': 'Physical tension, anxiety, insomnia'
    },
    'journaling': {
        'name': 'Emotional Journaling',
        'description': 'Write freely about your feelings without editing or judgment',
        'duration': '10-20 minutes',
        'when_to_use': 'Processing emotions, confusion, overwhelm'
    },
    'cold_water': {
        'name': 'Cold Water Reset',
        'description': 'Splash cold water on face or hold ice cube to activate vagus nerve',
        'duration': '30-60 seconds',
        'when_to_use': 'Panic, intense emotion, need quick reset'
    }
}

# Pattern recognition keywords
PATTERN_KEYWORDS = {
    'perfectionism': ['perfect', 'not good enough', 'should', 'must', 'failure'],
    'people_pleasing': ['say no', 'disappointing', 'others think', 'everyone else', 'approval'],
    'catastrophizing': ['worst case', 'disaster', 'terrible', 'always', 'never'],
    'avoidance': ['ignore', 'later', 'cant face', 'escape', 'distract'],
    'self_criticism': ['stupid', 'useless', 'worthless', 'failure', 'wrong'],
    'control': ['control', 'need to know', 'cant handle', 'uncertainty', 'plan']
}

def analyze_patterns(text):
    """Analyze text for behavioral patterns"""
    text_lower = text.lower()
    detected_patterns = []
    
    for pattern, keywords in PATTERN_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_patterns.append(pattern)
    
    return detected_patterns

def get_personalized_affirmations(emotion, patterns):
    """Get affirmations based on emotion and patterns"""
    affirmations = AFFIRMATIONS.get(emotion.lower(), AFFIRMATIONS['stress'])
    
    # Add pattern-specific affirmations
    pattern_affirmations = {
        'perfectionism': "Progress over perfection. I am enough as I am.",
        'people_pleasing': "My needs matter. I can say no with love.",
        'catastrophizing': "I focus on what I can control right now.",
        'avoidance': "I face challenges with courage and self-compassion.",
        'self_criticism': "I speak to myself with kindness and understanding.",
        'control': "I release the need to control. I trust the process."
    }
    
    for pattern in patterns:
        if pattern in pattern_affirmations:
            affirmations.append(pattern_affirmations[pattern])
    
    return affirmations

def recommend_tools(emotion, intensity):
    """Recommend coping tools based on emotion and intensity"""
    tools = []
    
    if intensity >= 8:
        # High intensity - immediate regulation
        tools.extend(['grounding', 'breathing', 'cold_water'])
    elif intensity >= 5:
        # Medium intensity
        tools.extend(['breathing', 'body_scan', 'progressive_relaxation'])
    else:
        # Low intensity - processing
        tools.extend(['journaling', 'body_scan'])
    
    return [COPING_TOOLS[tool] for tool in tools]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/checkin', methods=['POST'])
def checkin():
    data = request.json
    
    # Get or create user
    user_id = session.get('user_id')
    if not user_id:
        conn = sqlite3.connect('healing_guru.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (name) VALUES (?)", (data.get('name', 'Anonymous'),))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        session['user_id'] = user_id
    
    # Save check-in
    conn = sqlite3.connect('healing_guru.db')
    c = conn.cursor()
    c.execute("""INSERT INTO checkins 
                 (user_id, emotion, intensity, trigger, body_sensations, thoughts)
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (user_id, data['emotion'], data['intensity'], 
               data.get('trigger', ''), data.get('body_sensations', ''),
               data.get('thoughts', '')))
    conn.commit()
    conn.close()
    
    # Analyze patterns
    all_text = f"{data.get('trigger', '')} {data.get('thoughts', '')}"
    patterns = analyze_patterns(all_text)
    
    # Save detected patterns
    if patterns:
        conn = sqlite3.connect('healing_guru.db')
        c = conn.cursor()
        for pattern in patterns:
            # Check if pattern exists
            c.execute("SELECT id, frequency FROM patterns WHERE user_id=? AND pattern_type=?",
                     (user_id, pattern))
            existing = c.fetchone()
            
            if existing:
                # Update frequency
                c.execute("UPDATE patterns SET frequency=?, last_occurred=? WHERE id=?",
                         (existing[1] + 1, datetime.now(), existing[0]))
            else:
                # Create new pattern
                c.execute("INSERT INTO patterns (user_id, pattern_type, description) VALUES (?, ?, ?)",
                         (user_id, pattern, f"Detected {pattern} pattern"))
        conn.commit()
        conn.close()
    
    # Get personalized recommendations
    affirmations = get_personalized_affirmations(data['emotion'], patterns)
    tools = recommend_tools(data['emotion'], data['intensity'])
    
    return jsonify({
        'success': True,
        'patterns': patterns,
        'affirmations': affirmations,
        'tools': tools,
        'message': 'Check-in recorded. Here are your personalized recommendations.'
    })

@app.route('/api/patterns')
def get_patterns():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'patterns': []})
    
    conn = sqlite3.connect('healing_guru.db')
    c = conn.cursor()
    c.execute("""SELECT pattern_type, description, frequency, 
                 first_noticed, last_occurred 
                 FROM patterns WHERE user_id=? ORDER BY frequency DESC""",
              (user_id,))
    patterns = c.fetchall()
    conn.close()
    
    return jsonify({
        'patterns': [
            {
                'type': p[0],
                'description': p[1],
                'frequency': p[2],
                'first_noticed': p[3],
                'last_occurred': p[4]
            } for p in patterns
        ]
    })

@app.route('/api/progress')
def get_progress():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'progress': []})
    
    conn = sqlite3.connect('healing_guru.db')
    c = conn.cursor()
    c.execute("""SELECT tool_used, effectiveness, notes, timestamp 
                 FROM progress WHERE user_id=? ORDER BY timestamp DESC LIMIT 20""",
              (user_id,))
    progress = c.fetchall()
    conn.close()
    
    return jsonify({
        'progress': [
            {
                'tool': p[0],
                'effectiveness': p[1],
                'notes': p[2],
                'timestamp': p[3]
            } for p in progress
        ]
    })

@app.route('/api/log_tool', methods=['POST'])
def log_tool():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'User not found'})
    
    data = request.json
    
    conn = sqlite3.connect('healing_guru.db')
    c = conn.cursor()
    c.execute("""INSERT INTO progress (user_id, tool_used, effectiveness, notes)
                 VALUES (?, ?, ?, ?)""",
              (user_id, data['tool'], data['effectiveness'], data.get('notes', '')))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/affirmations/<emotion>')
def get_affirmations(emotion):
    return jsonify({
        'affirmations': AFFIRMATIONS.get(emotion.lower(), AFFIRMATIONS['stress'])
    })

@app.route('/api/tools')
def get_tools():
    return jsonify({'tools': COPING_TOOLS})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
