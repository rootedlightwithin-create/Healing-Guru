from flask import Flask, render_template, request, jsonify, session
import sqlite3
from datetime import datetime
import os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Database setup
def init_db():
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    
    # Chat messages table
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT,
                  role TEXT,
                  content TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # User insights table
    c.execute('''CREATE TABLE IF NOT EXISTS insights
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT,
                  pattern_type TEXT,
                  description TEXT,
                  detected_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # User journal entries
    c.execute('''CREATE TABLE IF NOT EXISTS journal
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT,
                  emotion TEXT,
                  intensity INTEGER,
                  content TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

init_db()

# AI Conversation Engine
class HealingGuruAI:
    def __init__(self):
        # Emotional states with detection patterns and responses
        self.emotional_states = {
            'overwhelmed_anxious': {
                'keywords': ['cant', 'too much', 'overwhelmed', 'racing', 'shaky', 'cant breathe', 'everything at once', 'drowning'],
                'physical_cues': ['heart racing', 'chest tight', 'shaking', 'trembling', 'cant catch my breath'],
                'responses': [
                    "I can sense your nervous system is running fast right now. Let's slow down together. Can you take one slow breath with me? Breathe in for 4... and out for 6. Just this moment.",
                    "Everything feels like too much right now. That's okay. We're going to take this one small piece at a time. Right now, can you place your hand on your heart and feel it beating? You're here. You're safe.",
                    "Your body is trying to keep up with a lot. Let's anchor you. Name one thing you can see right now. Then one thing you can touch. Just that. Nothing more.",
                    "I hear the overwhelm. Your nervous system needs grounding. Press your feet into the floor. Feel the solid ground beneath you. You don't have to do everything right now - just this breath."
                ]
            },
            'numb_disconnected': {
                'keywords': ['numb', 'disconnected', 'dont feel anything', 'empty', 'blank', 'nothing', 'cant feel', 'hollow'],
                'responses': [
                    "Sometimes our system shuts down to protect us from feeling too much. That numbness makes sense. You don't have to force feeling. Can you just notice - are you warm or cold right now? That's enough.",
                    "I hear that disconnection. Your body chose this to keep you safe. We can stay here together without pressure. What's one tiny sensation you notice - maybe the chair beneath you, or your breath moving?",
                    "Numbness is your nervous system saying 'I need a break.' That's valid. No pressure to feel more. Can you just notice if your jaw is clenched? Or if your shoulders are tense? Just observe, no need to change anything.",
                    "That flatness is real. You're not broken - you're protecting yourself. Let's just be present without pushing. Can you wiggle your toes? Sometimes the smallest movement can be a gentle way back."
                ]
            },
            'self_blame_shame': {
                'keywords': ['my fault', 'sorry', 'i should have', 'im a burden', 'bothering you', 'worthless', 'failure', 'always mess up', 'terrible person'],
                'responses': [
                    "I'm noticing a lot of harsh words toward yourself. What would happen if we paused that for just a moment? You're not a burden. Your pain matters. You matter.",
                    "That self-blame is so heavy. Can I reflect something back to you? You're human. Humans make mistakes, have limits, and need support. That doesn't make you less worthy - it makes you real.",
                    "I hear you apologizing for existing. Please know: you don't need to earn the right to be heard or helped. You're worthy of care simply because you're here.",
                    "Those words you're using about yourself are so harsh. Would you ever speak to someone you care about this way? What if we tried offering yourself the same gentleness you'd give a friend?"
                ]
            },
            'irritated_on_edge': {
                'keywords': ['irritated', 'annoyed', 'so done', 'everything annoys me', 'on edge', 'angry at everything', 'frustrated', 'cant stand'],
                'responses': [
                    "I can feel that restless energy. Something underneath is asking for your attention. Can you take a breath and ask yourself: what do I actually need right now that I'm not getting?",
                    "That irritation is a signal. Usually it's protecting something - maybe a boundary that needs honoring, or a need that's been ignored. What's underneath the 'done' feeling?",
                    "Everything feels grating right now. That makes sense when we're stretched too thin or our boundaries are being pushed. Can you soften your jaw? Let your shoulders drop? What's one thing that would give you relief right now?",
                    "Irritation often means we're carrying something we shouldn't have to carry. What would it feel like to put something down, even just for a moment?"
                ]
            },
            'avoidant_withdrawing': {
                'keywords': ['dont want to talk', 'leave me alone', 'not now', 'withdrawing', 'pulling away', 'hiding', 'cant face', 'too tired to share'],
                'responses': [
                    "I respect that you need space. You don't have to explain or share more than you're ready for. I'm here whenever you need, no pressure. Even this small connection counts.",
                    "Withdrawing makes sense when things feel like too much. There's no rush. If you need to just sit quietly for now, that's okay. I'll be here when you're ready.",
                    "I hear the exhaustion and the need to pull back. That's self-protection, and it's valid. You don't owe anyone your vulnerability. What would support feel like right now - presence, or true space?",
                    "Sometimes we need to retreat to restore. That's wisdom, not weakness. If you want to just breathe together in silence, that's enough. Or if you want to step away, that's okay too."
                ]
            },
            'overthinking': {
                'keywords': ['what if', 'keep thinking', 'cant stop', 'spiral', 'analysing', 'going in circles', 'need to figure out', 'need certainty'],
                'responses': [
                    "I can see your mind working hard to find certainty. But sometimes the more we think, the further we get from clarity. Can we pause the analysis for a moment and just feel your breath?",
                    "Those 'what if' loops are your brain trying to protect you by preparing for everything. But it's exhausting you. Let's ground back in what IS true right now. What's one thing you know for certain in this moment?",
                    "Your mind is tangled in possibilities. That makes sense - we think if we figure it all out, we'll feel safe. But maybe what you need isn't more answers, but less noise. Can you place your hand on your belly and just breathe?",
                    "I hear the spiral. Your intuition already knows something your mind is trying to logic its way to. What would happen if you listened to your gut instead of your thoughts for just a moment?"
                ]
            },
            'seeking_validation': {
                'keywords': ['is this okay', 'is that right', 'what do you think', 'should i', 'am i doing this right', 'tell me if', 'need to know if'],
                'responses': [
                    "I notice you're checking with me. But I'm curious - what does YOUR inner voice say? What feels true to you?",
                    "You're looking outside for permission. But you already have the answer inside. What would you do if you trusted yourself completely?",
                    "That question is really asking 'am I okay?' And the answer is yes. You don't need external validation to make your feelings or choices real. What do YOU think?",
                    "I hear you seeking reassurance. But your opinion of yourself matters more than anyone else's. When you quiet everyone else's voices, what does yours say?"
                ]
            },
            'people_pleasing_overgiving': {
                'keywords': ['dont want to upset', 'everyone else', 'their needs', 'cant say no', 'disappointing', 'letting them down', 'always helping', 'exhausted from'],
                'responses': [
                    "I'm noticing a pattern of putting everyone else first. What about YOUR needs? What about what YOU want? When was the last time you honored what you needed?",
                    "That exhaustion makes sense - you're pouring from an empty cup. People-pleasing is a survival pattern, not a character flaw. But you deserve to be on your own list of people who matter.",
                    "Your needs are just as important as everyone else's. Not more, not less - equal. What would it feel like to say 'no' and trust that people who truly care will understand?",
                    "I hear the fear of disappointing others. But what about disappointing yourself? What if the relationship with yourself is the most important one to honor? What do you need today?"
                ]
            },
            'high_functioning_distress': {
                'keywords': ['im fine', 'keeping it together', 'managing', 'functioning', 'doing everything right', 'maintaining', 'holding it together', 'appear normal'],
                'responses': [
                    "You say you're fine, but I'm sensing something underneath. It's exhausting to hold everything together all the time. What would it feel like to let the armor down, even for a moment?",
                    "You're doing so much, accomplishing so much - but how are you FEELING? Sometimes we perform strength when what we really need is permission to fall apart a little.",
                    "I see you keeping it all together. That takes so much energy. What if you didn't have to be strong right now? What if it was safe to let someone see the strain?",
                    "High-functioning doesn't mean not struggling. It often means struggling in silence. You don't have to earn care through achievement. You can be seen in your exhaustion too."
                ]
            },
            'change_resistance': {
                'keywords': ['not ready', 'scared to change', 'what if i fail', 'procrastinating', 'cant take the step', 'want to but', 'afraid to move forward'],
                'responses': [
                    "Fear of change is so normal. Growth doesn't require urgency or big leaps. What's one tiny step that feels manageable? Just one small thing.",
                    "That 'not ready' feeling makes sense. Change means losing something familiar, even if that familiar thing doesn't serve you. What are you afraid of losing if you move forward?",
                    "You don't have to be ready. You don't have to be fearless. You just have to take one small step while scared. What would that look like?",
                    "Resistance isn't weakness - it's your system trying to keep you safe. But sometimes safety means staying stuck. What would it feel like to honor the fear AND take a small step anyway?"
                ]
            }
        }
        
        # Legacy patterns for backward compatibility
        self.patterns = {
            'perfectionism': {
                'keywords': ['perfect', 'not good enough', 'should', 'must', 'flawed', 'mistake'],
                'response_intro': "I'm noticing some perfectionist thinking patterns here. ",
                'insight': "Perfectionism often stems from a deep fear of not being enough. But here's the truth: you are inherently worthy, regardless of your achievements or mistakes.",
                'questions': [
                    "What would you tell a friend who was being this hard on themselves?",
                    "Where did you learn that you had to be perfect to be valuable?",
                    "What would it feel like to give yourself permission to be human?"
                ]
            },
            'people_pleasing': {
                'keywords': ['say no', 'disappointing', 'others think', 'approval', 'let them down'],
                'response_intro': "It sounds like you're carrying the weight of others' expectations. ",
                'insight': "People-pleasing is often a survival strategy we developed to feel safe and accepted. But your needs matter just as much as anyone else's.",
                'questions': [
                    "What are you afraid will happen if you prioritize your own needs?",
                    "Whose voice is telling you that you need to please everyone?",
                    "What would setting a boundary look like in this situation?"
                ]
            },
            'catastrophizing': {
                'keywords': ['worst case', 'disaster', 'terrible', 'doomed', 'everything is terrible', 'everything is wrong', 'nothing works', 'nothing matters', 'always goes wrong', 'never works out', 'always fail', 'never succeed'],
                'response_intro': "I hear you spiraling into worst-case scenarios. ",
                'insight': "Catastrophic thinking is your brain's way of trying to protect you by preparing for the worst. But it's exhausting and often inaccurate.",
                'questions': [
                    "What's the most likely outcome, not the worst-case scenario?",
                    "Have you survived situations like this before?",
                    "What evidence do you have that contradicts this catastrophic thought?"
                ]
            },
            'self_criticism': {
                'keywords': ['stupid', 'useless', 'worthless', 'failure', 'wrong', 'idiot', 'hate myself', 'pathetic'],
                'response_intro': "The way you're speaking to yourself right now is really harsh. ",
                'insight': "Self-criticism might feel motivating, but research shows it actually undermines our wellbeing and progress. You deserve the same compassion you'd give others.",
                'questions': [
                    "Would you ever speak to someone you love this way?",
                    "What's beneath this self-criticism? What are you really afraid of?",
                    "Can you find even one compassionate thought to offer yourself right now?"
                ]
            },
            'avoidance': {
                'keywords': ['ignore', 'later', 'cant face', 'escape', 'distract', 'running from', 'put off', 'hide'],
                'response_intro': "It seems like you're trying to avoid something difficult. ",
                'insight': "Avoidance gives temporary relief but usually makes things harder in the long run. What we resist, persists.",
                'questions': [
                    "What are you really trying to avoid feeling?",
                    "What's one tiny step you could take toward facing this?",
                    "What would it feel like to stop running and just be with what is?"
                ]
            },
            'anxiety': {
                'keywords': ['anxious', 'worried', 'panic', 'scared', 'fear', 'nervous', 'overwhelmed', 'stressed'],
                'response_intro': "I can sense the anxiety you're experiencing. ",
                'insight': "Anxiety is your nervous system trying to protect you. It's not your enemy-it's just working overtime. Let's help it calm down.",
                'questions': [
                    "Where do you feel this anxiety in your body?",
                    "What do you need to feel safe right now?",
                    "Can you take three slow breaths with me before we continue?"
                ]
            },
            'sleep_difficulty': {
                'keywords': ['cant sleep', "can't sleep", 'insomnia', 'staying awake', 'trouble sleeping', 'hard to sleep', 'sleep problems', 'cant fall asleep', 'wide awake', 'racing mind at night', 'tossing and turning'],
                'response_intro': "Sleep struggles are so hard. When your mind won't quiet, it's exhausting. ",
                'insight': "Sleep difficulties are often your nervous system stuck in 'on' mode. Your body needs safety signals to let go into rest.",
                'questions': [
                    "What's your mind doing when you're trying to sleep? Racing? Worrying? Replaying things?",
                    "What does your body feel like? Restless? Tense? Wired?",
                    "What time are you usually trying to sleep, and how long have you been struggling with this?"
                ]
            },
            'being_bullied': {
                'keywords': ['bullying me', 'bullied', 'horrible to me', 'picked on', 'picking on me', 'nasty things', 'feel targeted', 'made me feel small', 'scared of how they treat', 'mistreated', 'won\'t leave me alone', 'keep saying mean', 'someone was mean', 'they said something cruel', 'won\'t stop messaging'],
                'response_intro': "I'm really sorry you were treated that way. No one deserves to feel unsafe or belittled. ",
                'insight': "That must have been painful. Your feelings make complete sense. What you feel is completely valid. You don't have to hold this alone-I'm right here with you.",
                'questions': [
                    "What part of this is sitting heaviest on your heart?",
                    "Where did you feel it most-in your body, or in your mind?",
                    "If this situation feels threatening or ongoing, reaching out to someone you trust or a professional can offer the support you deserve. Your safety matters."
                ]
            },
            'causing_harm': {
                'keywords': ['i hurt someone', 'i was mean', 'said something awful', 'feel guilty for how i acted', 'shouldn\'t have spoken', 'i lost control', 'i regret what i did', 'feel awful for how i acted', 'i hurt them', 'i was horrible', 'said something i shouldn\'t'],
                'response_intro': "Thank you for trusting me with this. Looking honestly at our actions is a strong, courageous step. ",
                'insight': "It sounds like you were dysregulated in that moment, and everything became too much. That doesn't make you a bad person-it shows you were in pain. Guilt often signals that your heart cares deeply.",
                'questions': [
                    "What happened in that moment?",
                    "What was going on inside you before you reacted? What part of you felt unheard or overwhelmed?",
                    "If you imagine the moment again, what would a calmer version of you do differently? You always get to choose differently going forward."
                ]
            },
            'emotional_dysregulation': {
                'keywords': ['i exploded', 'i snapped', 'i lost it', 'out of control', 'couldn\'t stop myself', 'reacted badly', 'didn\'t feel heard', 'i was overwhelmed', 'lost my temper', 'couldn\'t regulate', 'wasn\'t thinking clearly'],
                'response_intro': "That sounds overwhelming. Moments like that often come from deep stress or feeling unheard. ",
                'insight': "You're not alone-many people react this way when their system is overloaded. Feeling unheard can bring up strong reactions. It makes sense that everything felt intense.",
                'questions': [
                    "What do you think your body was trying to communicate in that moment?",
                    "Was there a boundary, fear, or need underneath the reaction?",
                    "You're allowed to grow from this-awareness is the beginning of change. What was your heart needing in that moment?"
                ]
            }
        }
        
        self.affirmations = {
            'anxiety': [
                "I am safe in this moment.",
                "I trust myself to handle whatever comes.",
                "My anxiety is uncomfortable, but it won't harm me.",
                "I choose to focus on what I can control.",
                "I am learning to calm my nervous system."
            ],
            'sadness': [
                "It's okay to feel sad. My emotions are valid.",
                "This feeling will pass. I have survived difficult feelings before.",
                "I deserve comfort and gentleness right now.",
                "My sadness doesn't define me-it's just a visitor.",
                "I am allowed to rest and heal."
            ],
            'anger': [
                "My anger is telling me something important.",
                "I can feel angry and still choose how I respond.",
                "My boundaries matter and deserve to be respected.",
                "I release the need to control what I cannot change.",
                "I am learning healthier ways to express my needs."
            ],
            'shame': [
                "I am not my mistakes. I am learning and growing.",
                "Shame thrives in secrecy. I choose to bring it into the light.",
                "I am worthy of love and belonging, just as I am.",
                "Everyone struggles. I am not alone in my imperfection.",
                "I forgive myself for not knowing what I hadn't yet learned."
            ],
            'overwhelm': [
                "I can only do what I can do, and that's enough.",
                "I give myself permission to take this one moment at a time.",
                "Not everything needs to be done right now.",
                "I am doing the best I can with what I have.",
                "It's okay to ask for help."
            ]
        }
        
        self.coping_tools = [
            # Original tools
            {
                'name': '5-4-3-2-1 Grounding',
                'description': 'Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste. This brings you back to the present moment.',
                'when': 'anxiety, panic, dissociation',
                'intensity_range': [4, 6],
                'states': ['overwhelmed_anxious', 'overthinking']
            },
            {
                'name': 'Box Breathing',
                'description': 'Breathe in for 4, hold for 4, out for 4, hold for 4. Repeat 4 times. This activates your parasympathetic nervous system.',
                'when': 'stress, anxiety, anger',
                'intensity_range': [4, 9],
                'states': ['overwhelmed_anxious', 'overthinking']
            },
            {
                'name': 'Butterfly Hug',
                'description': 'Cross your arms over your chest and gently tap alternating sides. This bilateral stimulation is calming for trauma responses.',
                'when': 'trauma activation, intense emotion',
                'intensity_range': [7, 10],
                'states': ['high_functioning_distress', 'self_blame_shame']
            },
            {
                'name': 'Cold Water Reset',
                'description': 'Splash cold water on your face or hold ice cubes. This activates the dive reflex and quickly calms your nervous system.',
                'when': 'panic, intense distress',
                'intensity_range': [6, 9],
                'states': ['overwhelmed_anxious']
            },
            {
                'name': 'Loving-Kindness Meditation',
                'description': 'Say to yourself: "May I be safe. May I be peaceful. May I be kind to myself. May I accept myself as I am."',
                'when': 'self-criticism, shame, loneliness',
                'intensity_range': [4, 8],
                'states': ['self_blame_shame', 'seeking_validation']
            },
            {
                'name': 'Body Scan',
                'description': 'Slowly notice sensations from head to toe without judgment. Just observe and breathe.',
                'when': 'disconnection from body, numbness',
                'intensity_range': [3, 6],
                'states': ['numb_disconnected', 'avoidant_withdrawing']
            },
            # NEW TOOLS
            {
                'name': 'Name the Need',
                'description': 'A soft invitation to recognise what your heart is asking for.\n\nDo you need:\n• Rest?\n• Understanding?\n• Comfort?\n• Choice?\n• Connection?\n\nNo pressure-just notice what resonates.',
                'when': 'confusion, mild stress, feeling lost',
                'intensity_range': [0, 4],
                'states': ['numb_disconnected', 'avoidant_withdrawing', 'people_pleasing_overgiving']
            },
            {
                'name': 'Physiological Sigh',
                'description': 'A proven nervous-system reset from somatic therapy.\n\n**Try this now:**\n1️⃣ Two quick inhales through your nose\n2️⃣ One long exhale through your mouth\n\nRepeat 2-3 times. This is powerful for panic, overwhelm, and tight chest sensations.',
                'when': 'panic, overwhelm, tight chest',
                'intensity_range': [5, 10],
                'states': ['overwhelmed_anxious', 'high_functioning_distress', 'overthinking']
            },
            {
                'name': 'Hand-on-Heart Regulation',
                'description': 'A tool for self-soothing when you feel lost, ashamed, or alone.\n\n**Right now:**\nPlace your hand on your chest. Feel the warmth. Breathe with it. Let your body remember safety.\n\nStay there for 5 breaths.',
                'when': 'shame, self-blame, loneliness, collapse',
                'intensity_range': [5, 9],
                'states': ['self_blame_shame', 'numb_disconnected', 'seeking_validation']
            },
            {
                'name': 'Thought Defusion (Clouds Passing)',
                'description': 'For when thoughts spiral and loop.\n\n**Imagine this:**\nEach thought is a cloud drifting across the sky. You\'re not the cloud - you\'re the sky watching it pass.\n\nNo fighting the thought. Just watching it drift by.',
                'when': 'overthinking, mental spirals, racing thoughts',
                'intensity_range': [3, 7],
                'states': ['overthinking', 'overwhelmed_anxious', 'change_resistance']
            },
            {
                'name': 'One Tiny Step',
                'description': 'For when you feel stuck, scared, or frozen.\n\n**Choose one small action that feels doable:**\n• One breath\n• One sentence\n• One minute pause\n• One small decision\n\nMovement without pressure. What\'s your one tiny step right now?',
                'when': 'stuck, overwhelmed, paralyzed',
                'intensity_range': [0, 6],
                'states': ['avoidant_withdrawing', 'overwhelmed_anxious', 'change_resistance']
            },
            {
                'name': 'Emotional Naming',
                'description': 'Name it to tame it-softly, not clinically.\n\nYou might be feeling:\n• Overwhelmed\n• Scared\n• Exhausted\n• Angry\n• Lost\n• Something close to these\n\nI\'m here with you. What feels closest?',
                'when': 'confusion, emotional fog, numbness',
                'intensity_range': [2, 6],
                'states': ['numb_disconnected', 'overwhelmed_anxious']
            },
            {
                'name': 'Co-Regulation Imagery',
                'description': 'For loneliness, hopelessness, or emotional collapse.\n\n**Close your eyes for a moment:**\nImagine someone steady sitting beside you. Not fixing anything. Not talking. Just being there. Breathing with you.\n\nFeel that presence. You\'re not alone.',
                'when': 'loneliness, hopelessness, collapse',
                'intensity_range': [6, 9],
                'states': ['numb_disconnected', 'seeking_validation', 'self_blame_shame']
            },
            {
                'name': 'Protective Boundaries Check-In',
                'description': 'For overwhelm, irritation, or people-pleasing.\n\n**A gentle question:**\nWhat part of you is asking for space right now?\n\nYou don\'t have to justify it. Just notice it.',
                'when': 'overwhelm, irritation, people-pleasing',
                'intensity_range': [3, 7],
                'states': ['people_pleasing_overgiving', 'irritated_on_edge', 'overwhelmed_anxious']
            },
            {
                'name': 'Tension Release Scan',
                'description': 'A micro-somatic reset. Just three key spots:\n\n**Right now:**\n• Jaw - relax it by 10%\n• Shoulders - drop them by 10%\n• Belly - soften it by 10%\n\nThat\'s it. Notice the shift.',
                'when': 'tension, irritation, physical stress',
                'intensity_range': [4, 7],
                'states': ['irritated_on_edge', 'overwhelmed_anxious', 'high_functioning_distress']
            },
            {
                'name': 'Safe Support Reflection',
                'description': 'A gentle bridge toward real-world help.\n\n**Reflect on this:**\n• Who in your life helps you feel steadier?\n• Is there a professional or place you trust?\n• What would reaching out look like?\n\nNo pressure. Just planting a seed.',
                'when': 'high distress, needing additional support',
                'intensity_range': [7, 9],
                'states': ['high_functioning_distress', 'numb_disconnected']
            },
            {
                'name': 'Sleep Preparation (Nervous System Reset)',
                'description': 'When your mind won\'t quiet for sleep.\n\n**30 minutes before bed:**\n1. **Body temperature drop** - Warm shower/bath, then cool room (65-68°F)\n2. **4-7-8 Breathing** - In for 4, hold for 7, out for 8 (repeat 4 times)\n3. **Progressive muscle relaxation** - Tense each muscle group for 5 seconds, then release\n\n**In bed:**\n• Keep eyes open in the dark (reverse psychology)\n• If awake after 20 min, leave room until drowsy\n• No clock watching\n\nYour body knows how to sleep. You\'re just helping it remember safety.',
                'when': 'sleep difficulty, racing mind, insomnia',
                'intensity_range': [3, 8],
                'states': ['overthinking', 'overwhelmed_anxious', 'high_functioning_distress']
            },
            {
                'name': 'Worry Time Container (For Sleep)',
                'description': 'Stop middle-of-the-night worry spirals.\n\n**Setup:**\nBefore bed, write down your worries. All of them. Then say: "I\'ll think about this tomorrow at [specific time]."\n\n**If worries come at night:**\n"Not now. Tomorrow at [time]." Redirect to breath.\n\nYour brain needs permission to let go. This gives it a plan.',
                'when': 'bedtime anxiety, racing thoughts at night',
                'intensity_range': [4, 7],
                'states': ['overthinking', 'overwhelmed_anxious', 'high_functioning_distress']
            },
            {
                'name': 'Repair Exercise (Choosing Differently)',
                'description': 'For when you\'re carrying guilt about how you acted.\n\n**Close your eyes and reimagine:**\n1. Picture the moment again\n2. See yourself responding with steadiness and care\n3. Notice how it feels to choose differently\n\n**Then ask yourself:**\nWhat would you say now if you could? What needs healing?\n\nYou always get to choose differently going forward.',
                'when': 'guilt, regret, shame about behavior',
                'intensity_range': [4, 8],
                'states': ['self_blame_shame', 'causing_harm', 'emotional_dysregulation']
            },
            {
                'name': 'Self-Forgiveness Prompt',
                'description': 'A gentle path toward releasing shame.\n\n**Say to yourself (out loud if you can):**\n"I was dysregulated. I was overwhelmed. I didn\'t have the tools in that moment that I have now.\n\nI forgive myself for not knowing what I hadn\'t yet learned.\n\nI choose to do better going forward."\n\n**Then place a hand on your chest and breathe.**',
                'when': 'shame, regret, self-criticism',
                'intensity_range': [5, 9],
                'states': ['self_blame_shame', 'causing_harm']
            },
            {
                'name': 'Safety Validation & Support Check',
                'description': 'For when you\'re being mistreated or feel unsafe.\n\n**Remember:**\n• What happened to you was not okay\n• Your feelings make complete sense\n• You deserve to feel safe and respected\n• This is not your fault\n\n**Reflection:**\nIs this situation ongoing? Do you have someone you trust who can support you?\n\nIf you ever feel at risk, reaching out to a counselor, trusted adult, or support service is really important.\n\n**Crisis Support:**\n🇺🇸 **US** - Crisis Text Line: Text HOME to 741741 | Call: 988\n🇬🇧 **UK** - Samaritans: 116 123 | Text: 85258\n🇦🇺 **Australia** - Lifeline: 13 11 14\n🇨🇦 **Canada** - Crisis Services: 1-833-456-4566\n🇮🇪 **Ireland** - Samaritans: 116 123\n🌍 **Worldwide** - findahelpline.com for your country',
                'when': 'bullying, mistreatment, feeling unsafe',
                'intensity_range': [5, 10],
                'states': ['being_bullied', 'overwhelmed_anxious', 'self_blame_shame']
            }
        ]
    
    def analyze_message(self, message, conversation_history):
        """Analyze user message and generate compassionate response"""
        import random
        message_lower = message.lower()
        
        # FIRST: Check for positive states to avoid false negatives on words like "everything" 
        positive_state = self.detect_positive_state(message_lower)
        if positive_state:
            # Route to positive state handling in generate_empathetic_response
            return self.generate_empathetic_response(message, conversation_history)
        
        # Assess emotional intensity (internal only - never shown to user)
        intensity_score = self.assess_emotional_intensity(message, conversation_history)
        
        # Get recent AI responses to avoid repetition
        recent_ai_messages = [msg[1] for msg in conversation_history if msg[0] == 'assistant'][:3]
        
        # CRITICAL: If intensity is 7+, prioritize crisis support
        if intensity_score >= 7:
            crisis_response = self.get_crisis_response(intensity_score)
            if crisis_response:
                # Also offer intelligent tools alongside crisis response
                emotion = self.detect_emotion(message_lower)
                
                # Detect emotional state for tool selection
                emotional_state = None
                for state_name, state_data in self.emotional_states.items():
                    matched_keywords = [kw for kw in state_data['keywords'] if kw in message_lower]
                    if matched_keywords:
                        emotional_state = state_name
                        break
                
                # Get intelligent tool recommendations
                selected_tools = self.select_intelligent_tool(intensity_score, emotional_state, conversation_history)
                tool_text = self.format_tool_offer(selected_tools, intensity_score)
                
                return {
                    'response': crisis_response + "\n\n" + tool_text,
                    'pattern': 'crisis_intervention',
                    'emotion': emotion,
                    'needs_tool': True,
                    'recommended_tools': selected_tools
                }
        
        # Check if user is questioning the AI's assessment
        questioning_assessment = any(phrase in message_lower for phrase in [
            'what makes you', 'why do you think', 'why do you say', 'how do you know',
            'what gave you', 'why would you', "i'm not", "i don't think i'm"
        ])
        
        if questioning_assessment and conversation_history:
            # Look at previous user messages to explain the reasoning
            previous_messages = [msg[1] for msg in conversation_history if msg[0] == 'user']
            if len(previous_messages) > 1:
                # Get the message before this question
                previous_msg = previous_messages[1] if len(previous_messages) > 1 else previous_messages[0]
                
                # Find which pattern was detected and explain with evidence
                for pattern_name, pattern_data in self.patterns.items():
                    matched_keywords = [kw for kw in pattern_data['keywords'] if kw in previous_msg.lower()]
                    if matched_keywords:
                        response = f"I heard that because you used phrases like "
                        # Quote the actual words they used
                        quotes = []
                        for keyword in matched_keywords[:3]:  # Show up to 3 examples
                            # Find the context around the keyword
                            idx = previous_msg.lower().find(keyword)
                            if idx != -1:
                                # Get a snippet around the keyword
                                start = max(0, idx - 20)
                                end = min(len(previous_msg), idx + len(keyword) + 20)
                                snippet = previous_msg[start:end].strip()
                                quotes.append(f'"{snippet}"')
                        
                        if quotes:
                            response += ", ".join(quotes[:2])
                        else:
                            response += f'"{", ".join(matched_keywords[:2])}"'
                        
                        response += f". These phrases often indicate {pattern_name.replace('_', ' ')} patterns.\n\n"
                        response += f"But you know yourself better than I do. What resonates with you about that? Or does it feel off?"
                        
                        return {
                            'response': response,
                            'pattern': None,
                            'emotion': self.detect_emotion(message_lower),
                            'needs_tool': False
                        }
        
        # First check for specific emotional states (new system)
        for state_name, state_data in self.emotional_states.items():
            matched_keywords = [kw for kw in state_data['keywords'] if kw in message_lower]
            
            # Check physical cues if present
            if 'physical_cues' in state_data:
                matched_keywords.extend([cue for cue in state_data['physical_cues'] if cue in message_lower])
            
            if matched_keywords:
                # Choose a response that hasn't been used recently
                available_responses = [r for r in state_data['responses'] if r not in str(recent_ai_messages)]
                if not available_responses:
                    available_responses = state_data['responses']
                
                response = random.choice(available_responses)
                
                # Add emotion-specific affirmation
                emotion = self.detect_emotion(message_lower)
                if emotion and emotion in self.affirmations:
                    affirmation = random.choice(self.affirmations[emotion])
                    response += f"\n\n✨ {affirmation}"
                
                # Add crisis resources if intensity is high (6-7 range)
                if intensity_score >= 6:
                    response += "\n\n💜 If you need immediate support, please reach out: Call/text 988 (crisis line) or text HOME to 741741."
                
                # Intelligently select and offer tools based on state and intensity
                should_offer_tools = (
                    state_name in ['overwhelmed_anxious', 'numb_disconnected', 'high_functioning_distress'] or
                    intensity_score >= 4
                )
                
                recommended_tools = []
                if should_offer_tools:
                    selected_tools = self.select_intelligent_tool(intensity_score, state_name, conversation_history)
                    tool_text = self.format_tool_offer(selected_tools, intensity_score)
                    response += "\n\n" + tool_text
                    recommended_tools = selected_tools
                
                return {
                    'response': response,
                    'pattern': state_name,
                    'emotion': emotion,
                    'needs_tool': should_offer_tools,
                    'recommended_tools': recommended_tools
                }
        
        # Fall back to legacy pattern detection
        detected_patterns = []
        for pattern_name, pattern_data in self.patterns.items():
            matched_keywords = [kw for kw in pattern_data['keywords'] if kw in message_lower]
            if matched_keywords:
                detected_patterns.append((pattern_name, pattern_data, matched_keywords))
        
        # Build response
        if detected_patterns:
            # Use the most relevant pattern
            pattern_name, pattern_data, matched_keywords = detected_patterns[0]
            
            # Vary the response structure to avoid repetition
            response_styles = [
                # Style 1: Direct observation
                lambda: f"I'm hearing {pattern_name.replace('_', ' ')} coming through in what you're saying. {pattern_data['insight']}\n\n{random.choice(pattern_data['questions'])}",
                
                # Style 2: Gentle reflection
                lambda: f"{pattern_data['insight']}\n\nI wonder: {random.choice(pattern_data['questions'])}",
                
                # Style 3: Empathetic naming
                lambda: f"It sounds like you're caught in {pattern_name.replace('_', ' ')}. {pattern_data['insight']}\n\n{random.choice(pattern_data['questions'])}",
                
                # Style 4: Direct with context
                lambda: f"When you say things like '{matched_keywords[0]}', it often points to {pattern_name.replace('_', ' ')}. {pattern_data['insight']}\n\n{random.choice(pattern_data['questions'])}"
            ]
            
            response = random.choice(response_styles)()
            
            # Add an affirmation if emotion detected
            emotion = self.detect_emotion(message_lower)
            if emotion and emotion in self.affirmations:
                affirmation = random.choice(self.affirmations[emotion])
                response += f"\n\n✨ Reminder: {affirmation}"
            
            return {
                'response': response,
                'pattern': pattern_name,
                'emotion': emotion,
                'needs_tool': intensity_score >= 5
            }
        else:
            # General empathetic response
            return self.generate_empathetic_response(message, conversation_history)
    
    def detect_emotion(self, message):
        """Detect primary emotion in message"""
        emotions = {
            'anxiety': ['anxious', 'worried', 'panic', 'scared', 'fear', 'nervous', 'overwhelmed'],
            'sadness': ['sad', 'depressed', 'hopeless', 'empty', 'lonely', 'hurt', 'grief'],
            'anger': ['angry', 'furious', 'frustrated', 'irritated', 'rage', 'mad'],
            'shame': ['ashamed', 'embarrassed', 'guilty', 'worthless', 'pathetic'],
            'overwhelm': ['overwhelmed', 'too much', 'cant cope', 'drowning', 'exhausted'],
            # POSITIVE EMOTIONS
            'joy': ['happy', 'joyful', 'excited', 'thrilled', 'delighted', 'elated'],
            'peace': ['peaceful', 'calm', 'serene', 'tranquil', 'settled', 'centered'],
            'gratitude': ['grateful', 'thankful', 'blessed', 'appreciate', 'fortunate'],
            'pride': ['proud', 'accomplished', 'achieved', 'succeeded'],
            'relief': ['relieved', 'lighter', 'lifted', 'unburdened', 'can breathe'],
            'hope': ['hopeful', 'optimistic', 'looking forward', 'better', 'improving']
        }
        
        for emotion, keywords in emotions.items():
            if any(keyword in message for keyword in keywords):
                return emotion
        return None
    
    def detect_positive_state(self, message_lower):
        """Detect if user is expressing genuine positive emotions (not just conversational agreements)"""
        
        # FIRST: Check for negations that invalidate positive words
        # e.g., "I'm not doing too good", "not feeling great", "don't feel good"
        negation_patterns = [
            'not doing', 'not feeling', 'not too', 'not very', 'not really',
            "don't feel", "dont feel", "doesn't feel", "doesnt feel",
            'not good', 'not great', 'not well', 'not okay', 'not ok',
            'hardly', 'barely', 'far from'
        ]
        
        if any(neg in message_lower for neg in negation_patterns):
            return None  # Negated positive words = not a positive state
        
        # Exclude short agreement responses that contain positive words but aren't emotional states
        # These are conversational fillers, not emotional expressions
        agreement_phrases = [
            'yeah', 'yh', 'yep', 'yes', 'ok', 'okay', 'sure', 'sounds good',
            'that works', 'makes sense', 'i understand', 'got it', 'alright'
        ]
        
        # If message is very short (under 8 words) AND contains agreement words, it's likely not a positive state
        word_count = len(message_lower.split())
        has_agreement = any(phrase in message_lower for phrase in agreement_phrases)
        
        # Short agreements with positive words are NOT positive states
        # e.g., "yh, great" or "yes, good idea" or "ok, sounds good"
        if word_count <= 8 and has_agreement:
            # Unless they explicitly say they FEEL good/great
            if not any(phrase in message_lower for phrase in ['feel good', 'feel great', 'feeling good', 'feeling great', 'i feel']):
                return None
        
        # Core positive keywords from requirements
        positive_keywords = [
            'good', 'great', 'calm', 'peaceful', 'happy', 'light', 
            'grateful', 'relieved', 'balanced', 'proud', 'settled', 'clear'
        ]
        
        # Check for basic positive keywords
        has_positive_keyword = any(word in message_lower for word in positive_keywords)
        
        # Enhanced detection for specific states
        positive_indicators = {
            'clear_positivity': [
                'feel so good', 'feel good', 'feel great', 'feeling good', 'feeling great',
                'really happy', 'so happy', 'feel happy', 'feel lighter', 'feel peaceful',
                'breakthrough', 'feel amazing', 'feeling amazing', 'going well', 'things are good'
            ],
            'gratitude': [
                'grateful', 'thankful', 'so grateful', 'heart feels full',
                'appreciate this', 'blessed', 'fortunate'
            ],
            'energy_momentum': [
                'feel motivated', 'feel energized', 'feel like myself',
                'feel proud', 'proud of myself', 'accomplished',
                'completed everything', 'finished everything', 'got everything done',
                'finished', 'completed', 'all done', 'made it through',
                'i did it', 'achieved', 'mission accomplished', 'checked off',
                'got it done', 'made progress', 'got through it'
            ],
            'relief': [
                'feel calmer', 'can breathe again', 'feel better',
                'lifted', 'weight lifted', 'feel lighter', 'relieved'
            ],
            'peace': [
                'peaceful', 'calm', 'settled', 'centered', 'balanced', 'clear'
            ],
            'self_care': [
                'going to rest', 'going to relax', 'take time', 'take a break',
                'need rest', 'need to rest', 'time to relax', 'going to take care',
                'prioritize myself', 'setting boundaries', 'saying no',
                'taking space', 'stepping back', 'going to unwind',
                'time for myself', 'focusing on me', 'self care'
            ]
        }
        
        # Check for specific positive states
        for category, phrases in positive_indicators.items():
            if any(phrase in message_lower for phrase in phrases):
                return category
        
        # If has positive keyword but no specific category, return general positive
        if has_positive_keyword:
            return 'general_positive'
        
        return None
    
    def detect_exit_intention(self, message_lower):
        """Detect if user is indicating they're done/good/exiting"""
        exit_phrases = [
            "i'm good", "im good", "i'm okay now", "im okay now",
            "all good", "no, i'm fine", "no im fine", "that's enough",
            "thats enough", "thank you", "thanks", "appreciate it",
            "i'm fine now", "im fine now", "feel better now"
        ]
        
        return any(phrase in message_lower for phrase in exit_phrases)
    
    def detect_farewell_intention(self, message_lower):
        """Detect if user is saying goodbye/leaving the conversation"""
        farewell_phrases = [
            'bye', 'goodbye', 'good bye', 'see you', 'talk soon', 'speak soon',
            'see you later', 'see you soon', 'talk to you later', 'talk later',
            'catch you later', 'ttyl', 'gotta go', 'got to go', 'have to go',
            'going to leave', 'going to go', 'will be back', "i'll be back",
            'ill be back', 'back later', 'back soon', 'leaving now',
            'time to go', 'heading out', 'signing off'
        ]
        
        return any(phrase in message_lower for phrase in farewell_phrases)
    
    def extract_time_period(self, message_lower):
        """Extract time period if user mentions how long something has been happening"""
        import re
        
        # Time period patterns
        time_patterns = [
            r'(for |past |last |about )?(a |the )?(few )?(\\d+|a|an|couple|several) ?(day|days|week|weeks|month|months|year|years)',
            r'(today|tonight|this morning|this afternoon|this evening)',
            r'(all day|all week|all month|all year)',
            r'(since )(yesterday|last week|last month|monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'(lately|recently|for a while|for ages|forever)',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, message_lower)
            if match:
                return match.group(0).strip()
        
        return None
    
    def detect_dysregulation_in_positivity(self, message):
        """Check if positive state shows signs of dysregulation"""
        dysregulation_signs = {
            'rapid_typing': len(message.split()) > 50 and '!' in message,
            'excessive_exclamation': message.count('!') >= 3,
            'buzzing_language': any(word in message.lower() for word in [
                'buzzing', "can't sit still", 'too energized', 'too much energy',
                'racing', 'wired', 'hyper'
            ]),
            'all_caps': sum(1 for c in message if c.isupper()) > len(message) * 0.3
        }
        
        return any(dysregulation_signs.values())
    
    def assess_emotional_intensity(self, message, conversation_history):
        """
        Internal emotional intensity scale (0-10) - NEVER shown to user
        Guides support level and intervention type
        """
        message_lower = message.lower()
        score = 0
        
        # Critical indicators (9-10)
        critical_phrases = [
            'want to die', 'kill myself', 'end it all', 'cant do this anymore', 
            "can't do this anymore", 'dont want to exist', "don't want to exist",
            'want everything to stop', 'hurt myself', 'no point in living',
            'better off dead', 'nothing matters', 'give up completely'
        ]
        if any(phrase in message_lower for phrase in critical_phrases):
            return 10
        
        # Severe distress (7-8)
        severe_phrases = [
            'cant cope', "can't cope", 'falling apart', 'unraveling', 
            'cant go on', "can't go on", 'no way out', 'dont see the point',
            "don't see the point", 'completely hopeless', 'breaking down',
            'cant take it', "can't take it", 'too much pain', 'hate myself',
            'im worthless', "i'm worthless", 'im stupid', "i'm stupid",
            'everything is my fault', 'no one cares about me', 'im the problem',
            "i'm the problem", 'im a bad person', "i'm a bad person"
        ]
        if any(phrase in message_lower for phrase in severe_phrases):
            score = max(score, 8)
        
        # High distress (7-8)
        high_distress = [
            'cant function', "can't function", 'losing it', 'cant breathe',
            'spiraling', 'collapsing', 'drowning', 'suffocating',
            'completely overwhelmed', 'cant handle', 'breaking'
        ]
        if any(phrase in message_lower for phrase in high_distress):
            score = max(score, 7)
        
        # Moderate-high distress (5-6)
        moderate_high = [
            'overwhelmed', 'too much', 'cant think', 'exhausted',
            'dont know what to do', 'feel lost', 'stuck', 'trapped',
            'panic', 'terrified', 'desperate', 'dont feel anything',
            "don't feel anything", 'im empty', "i'm empty", 'feel numb',
            'disconnected from myself', 'feel nothing', 'emotionally numb'
        ]
        if any(phrase in message_lower for phrase in moderate_high):
            score = max(score, 6)
        
        # Moderate distress (4-5)
        moderate = [
            'anxious', 'stressed', 'worried', 'scared', 'confused',
            'frustrated', 'upset', 'struggling', 'difficult'
        ]
        if any(phrase in message_lower for phrase in moderate):
            score = max(score, 4)
        
        # Tone and structure indicators
        # Fragmented (lots of short bursts)
        if len(message.split()) < 10 and any(char in message for char in ['...', '??', '!!']):
            score += 1
        
        # Repetitive hopeless phrases in history
        if conversation_history:
            recent_user_msgs = [msg[1].lower() for msg in conversation_history[:5] if msg[0] == 'user']
            hopeless_count = sum(1 for msg in recent_user_msgs if any(
                word in msg for word in ['hopeless', 'pointless', 'give up', 'cant', "can't", 'no point']
            ))
            if hopeless_count >= 2:
                score += 2
        
        # Escalating pattern (messages getting darker)
        if conversation_history and len(conversation_history) >= 4:
            recent_msgs = [msg[1].lower() for msg in conversation_history[:4] if msg[0] == 'user']
            if len(recent_msgs) >= 2:
                # Check if negative words increasing
                neg_words = ['worse', 'cant', "can't", 'hopeless', 'stuck', 'nothing', 'never']
                recent_neg = sum(1 for msg in recent_msgs[:2] for word in neg_words if word in msg)
                older_neg = sum(1 for msg in recent_msgs[2:] for word in neg_words if word in msg)
                if recent_neg > older_neg:
                    score += 1
        
        return min(score, 10)  # Cap at 10
    
    def get_crisis_response(self, intensity_level):
        """Generate appropriate crisis intervention based on intensity (7-10)"""
        if intensity_level >= 9:
            return (
                "I'm hearing a lot of pain in your words… and I need you to know: you don't have to carry this alone.\n\n"
                "Reaching out for support is a sign of strength — it shows you're ready for change. "
                "Feeling scared, confused, or overwhelmed is part of moving through difficult things. "
                "There are people trained to help carry this weight with you.\n\n"
                "🆘 **Crisis Support (24/7)**:\n"
                "🇺🇸 **US** - Crisis Text Line: Text HOME to 741741 | Call: 988\n"
                "🇬🇧 **UK** - Samaritans: 116 123 | Text: 85258\n"
                "🇦🇺 **Australia** - Lifeline: 13 11 14\n"
                "🇨🇦 **Canada** - Crisis Services: 1-833-456-4566\n"
                "🌍 **Worldwide** - findahelpline.com\n\n"
                "Your life has value. This pain is real, but it can change. You deserve care and support. Please let someone help you through this moment."
            )
        elif intensity_level >= 7:
            return (
                "I can feel how much you're struggling right now. This level of pain… it's a signal that you need more support than what I can offer here.\n\n"
                "Asking for help doesn't mean you're failing. It means you're brave enough to care for yourself. "
                "You're not meant to carry this alone — reaching out is a powerful act of strength.\n\n"
                "Please consider talking to:\n\n"
                "• A mental health professional or doctor who can provide ongoing care\n"
                "• A crisis counselor (24/7 support available)\n"
                "• A trusted friend, family member, or spiritual advisor\n\n"
                "You deserve care that can hold this with you. You're worthy of support. What would feel most accessible right now?"
            )
        return None
    
    def select_intelligent_tool(self, intensity_score, emotional_state, conversation_history):
        """
        Emotional Decision Tree for Tool Selection
        Automatically chooses the right grounding tool based on:
        - Emotional intensity (0-10)
        - Emotional state category
        - User's language patterns
        """
        import random
        
        # Get tools that match intensity range and emotional state
        matching_tools = []
        
        for tool in self.coping_tools:
            intensity_min, intensity_max = tool['intensity_range']
            
            # Check if intensity is in range
            if intensity_min <= intensity_score <= intensity_max:
                # Check if emotional state matches
                if emotional_state and emotional_state in tool['states']:
                    matching_tools.append(tool)
        
        # If no exact match, fall back to intensity-only matching
        if not matching_tools:
            for tool in self.coping_tools:
                intensity_min, intensity_max = tool['intensity_range']
                if intensity_min <= intensity_score <= intensity_max:
                    matching_tools.append(tool)
        
        # If still no match, use defaults based on intensity
        if not matching_tools:
            if intensity_score <= 3:
                matching_tools = [t for t in self.coping_tools if t['name'] in ['Name the Need', 'One Tiny Step', 'Thought Defusion (Clouds Passing)']]
            elif intensity_score <= 6:
                matching_tools = [t for t in self.coping_tools if t['name'] in ['Box Breathing', '5-4-3-2-1 Grounding', 'Physiological Sigh']]
            elif intensity_score <= 8:
                matching_tools = [t for t in self.coping_tools if t['name'] in ['Hand-on-Heart Regulation', 'Butterfly Hug', 'Co-Regulation Imagery']]
            else:
                matching_tools = [t for t in self.coping_tools if t['name'] in ['Physiological Sigh', 'Hand-on-Heart Regulation', 'Butterfly Hug']]
        
        # Return 1-2 most relevant tools
        if matching_tools:
            return random.sample(matching_tools, min(2, len(matching_tools)))
        
        # Absolute fallback
        return [self.coping_tools[7]]  # Box Breathing (index adjusted for new list)
    
    def format_tool_offer(self, tools, intensity_score):
        """Format tool offerings based on intensity level"""
        if intensity_score >= 7:
            # High distress: gentle, directive
            intro = "Let me offer something that might help ground you right now:\n\n"
        elif intensity_score >= 4:
            # Moderate: balanced offering
            intro = "Here are some tools that might help:\n\n"
        else:
            # Low: exploratory
            intro = "You might find one of these helpful:\n\n"
        
        tool_text = ""
        for i, tool in enumerate(tools, 1):
            tool_text += f"**{i}. {tool['name']}**\n{tool['description']}\n\n"
        
        if intensity_score >= 7:
            closing = "Would you like me to guide you through one of these?"
        else:
            closing = "Let me know if you'd like to try one, or if you want to talk more first."
        
        return intro + tool_text + closing
    
    def generate_empathetic_response(self, message, history):
        """Generate context-aware empathetic response"""
        import random
        message_lower = message.lower()
        
        # Get recent AI responses to avoid repetition
        recent_ai_messages = [msg[1] for msg in history if msg[0] == 'assistant'][:3]
        
        # FIRST: Check for positive emotional states
        positive_state = self.detect_positive_state(message_lower)
        
        if positive_state:
            emotion = self.detect_emotion(message_lower)
            
            # Check for farewell intention FIRST (\"bye\", \"see you later\", etc.)
            is_farewell = self.detect_farewell_intention(message_lower)
            if is_farewell:
                farewell_responses = [
                    "Take care of yourself. I'll be right here whenever you need me.",
                    "Rest well. I'm here anytime you want to talk.",
                    "See you soon. You know where to find me.",
                    "Go gently. I'll be here waiting when you're ready.",
                    "Take good care. Come back whenever you need.",
                    "I'll be here. Rest, recharge, and return when you're ready."
                ]
                return {
                    'response': random.choice(farewell_responses),
                    'pattern': 'farewell',
                    'emotion': emotion,
                    'needs_tool': False
                }
            
            is_dysregulated = self.detect_dysregulation_in_positivity(message)
            
            # Check if user is indicating they're done
            is_exiting = self.detect_exit_intention(message_lower)
            
            if is_exiting:
                exit_responses = [
                    "Beautiful. I'll stay right here. Come back anytime you need me.",
                    "I'm glad you're feeling steady. I'm here whenever you want to check in again.",
                    "Wonderful. Take care of that good feeling. I'm always here when you need support.",
                    "I love that you're in this space. Come back whenever you'd like to talk."
                ]
                response = random.choice(exit_responses)
                
                return {
                    'response': response,
                    'pattern': 'positive_exit',
                    'emotion': emotion,
                    'needs_tool': False
                }
            
            # Dysregulated joy - offer gentle grounding
            if is_dysregulated:
                responses = [
                    "I can feel that excitement! It has a real spark to it.\n\nIf you'd like, take one steady breath with me - just to help your body hold all that good energy without losing balance. In for 4... out for 4.\n\nWhat's fueling this bright feeling?",
                    
                    "That energy is electric! I love it.\n\nLet's ground it just a little so you can savor it fully. One slow breath - in through your nose, out through your mouth.\n\nNow tell me: where do you feel this joy in your body?",
                    
                    "I hear the buzz in your words - that's beautiful! Sometimes big feelings need a soft landing.\n\nTake a moment with me: breathe in slowly, breathe out even slower. Let your body catch up to your heart.\n\nWhat opened this up for you?"
                ]
            
            # Grounded positive state - use reflective and celebratory responses
            elif positive_state == 'clear_positivity':
                reflective = [
                    "That's beautiful to hear. What part of your day or moment feels especially good right now?",
                    "I'm really glad you're feeling this way. What do you want to savour about it?",
                    "Thank you for sharing this light - it matters. What's supporting this feeling for you?"
                ]
                
                celebratory = [
                    "I love that you're in this space. It's so important to honour these moments.\n\nLet yourself soak in this feeling. Where do you feel that goodness in your body?",
                    
                    "Yes! Let's take a breath together and really take this in.\n\nBreathe into that softness. Let it expand a little. What allowed this feeling to come forward?",
                    
                    "I'm smiling with you. This kind of ease deserves to be named and enjoyed.\n\nStay with it for a moment. What's this shift like for you?"
                ]
                
                responses = reflective + celebratory
            
            elif positive_state == 'gratitude':
                responses = [
                    "That's beautiful to hear. What part of your day feels especially full of gratitude right now?",
                    
                    "Your heart sounds full. That's a gift to feel.\n\nLet that gratitude settle into your body. Breathe with it. What are you most grateful for in this moment?",
                    
                    "I love that you're in this space. Gratitude like this can anchor us.\n\nWhat do you want to savour about this feeling?"
                ]
            
            elif positive_state == 'energy_momentum':
                responses = [
                    "I love hearing that. You sound like yourself again.\n\nWhat's supporting this feeling for you? What shifted?",
                    
                    "That momentum is real. Your energy feels lighter.\n\nThank you for sharing this light - it matters. What do you notice is different now?",
                    
                    "Yes! Let's take a breath together and really take this in.\n\nWhat part of you feels the proudest right now?",
                    
                    "That's wonderful! You did it.\n\nLet that sense of accomplishment settle in. What does it feel like to have completed this?",
                    
                    "I can hear the satisfaction in your words. You followed through.\n\nTake a moment to acknowledge yourself. What made the difference?",
                    
                    "That's a real achievement. You set out to do something and you did it.\n\nStay with that feeling of completion. What are you most proud of?"
                ]
            
            elif positive_state == 'relief':
                responses = [
                    "I can feel that exhale in your words. Relief is so real.\n\nWhat part of your moment feels especially relieved right now?",
                    
                    "That's beautiful - like something finally unclenched. Stay with that feeling.\n\nWhat's supporting this sense of relief for you?",
                    
                    "I'm really glad you're feeling this way. Let yourself breathe into that lightness.\n\nWhat do you want to savour about it?"
                ]
            
            elif positive_state == 'peace':
                responses = [
                    "That's beautiful to hear. What part of your day feels especially peaceful right now?",
                    
                    "I love that you're in this space of calm. It's so important to honour these moments.\n\nWhat's supporting this feeling for you?",
                    
                    "Thank you for sharing this light. This kind of settled feeling deserves to be named and enjoyed.\n\nWhere do you feel that peace in your body?"
                ]
            
            elif positive_state == 'self_care':
                responses = [
                    "Yes. That's exactly what you need. Taking time for yourself isn't selfish - it's essential.\n\nWhat does rest look like for you today?",
                    
                    "I love that you're honoring your needs. That's real wisdom.\n\nYou deserve this time. What are you most looking forward to?",
                    
                    "That boundary you're setting? That takes strength. I'm proud of you.\n\nWhat will help you truly unwind and recharge?",
                    
                    "Beautiful choice. Rest is productive. Your body and mind need this.\n\nHow can you make this time really nourishing for yourself?",
                    
                    "Yes. Stepping back to take care of yourself is an act of self-respect.\n\nWhat does relaxation mean to you right now?"
                ]
            
            else:  # general_positive
                responses = [
                    "That's beautiful to hear. What part of your day or moment feels especially good right now?",
                    
                    "I'm really glad you're feeling this way. What do you want to savour about it?",
                    
                    "I love that you're in this space. It's so important to honour these moments.\n\nWhat's supporting this feeling for you?"
                ]
            
            response = random.choice([r for r in responses if r not in str(recent_ai_messages)])
            if not response:
                response = random.choice(responses)
            
            # Add gentle check-in
            check_ins = [
                "\n\nWould you like to talk about this feeling more?",
                "\n\nDo you want to keep exploring this, or is this a good place to rest?",
                "\n\nI'm here - would you like to stay with this for a bit?"
            ]
            
            if not is_dysregulated:  # Only add check-in for grounded positive states
                response += random.choice(check_ins)
            
            return {
                'response': response,
                'pattern': 'positive_state',
                'emotion': emotion,
                'needs_tool': False
            }
        
        # Check for greetings/pleasantries
        is_greeting = any(phrase in message_lower for phrase in [
            'how are you', 'how r u', 'how are u', 'hows it going', "how's it going",
            'whats up', "what's up", 'how do you do', 'how you doing', 'howdy',
            'hey there', 'hi there', 'hello there',
            # Check-in greetings
            'are you ok', 'are you okay', 'you ok', 'you okay', 'u ok', 'u okay',
            'are you alright', 'you alright', 'are you good', 'you good',
            'are you doing ok', 'are you doing okay', 'doing ok', 'doing okay',
            'everything ok', 'everything okay', 'all good with you'
        ])
        
        # Check if it's just a simple hi/hello without other content
        is_simple_hello = message_lower.strip() in ['hi', 'hello', 'hey', 'hiya', 'heya', 'yo']
        
        if is_greeting or is_simple_hello:
            greeting_responses = [
                "I'm doing well, thank you for asking. But I'm here for you-how are you doing today?",
                "I appreciate you asking! I'm here and present. More importantly, how are you feeling?",
                "I'm good, thanks. But this space is for you-what's on your mind today?",
                "I'm well, thank you. What I really want to know is: how are you? What brings you here today?",
                "Thank you for the kindness! I'm here and ready to listen. How are you really doing?",
                "I'm doing fine, but I'm more interested in you. What's going on in your world today?"
            ]
            
            response = random.choice([r for r in greeting_responses if r not in str(recent_ai_messages)])
            if not response:
                response = random.choice(greeting_responses)
            
            return {
                'response': response,
                'pattern': None,
                'emotion': None,
                'needs_tool': False
            }
        
        # Check for farewell (when not in positive state)
        if self.detect_farewell_intention(message_lower):
            farewell_responses = [
                "Take care of yourself. I'll be right here whenever you need me.",
                "Rest well. I'm here anytime you want to talk.",
                "See you soon. You know where to find me.",
                "Go gently. I'll be here waiting when you're ready.",
                "Take good care. Come back whenever you need.",
                "I'll be here. Rest, recharge, and return when you're ready."
            ]
            return {
                'response': random.choice(farewell_responses),
                'pattern': 'farewell',
                'emotion': self.detect_emotion(message_lower),
                'needs_tool': False
            }
        
        # PRIORITY: Immediate support detection - comes first
        immediate_support = any(phrase in message_lower for phrase in [
            'need support', 'need help now', 'need help right now', 'need someone', 
            'help me now', 'cant do this alone', "can't do this alone", 'need you', 
            'please help', 'help me please', 'struggling right now',
            'really struggling', 'need to talk', 'talk to someone'
        ])
        
        if immediate_support:
            support_responses = [
                "I'm here with you. I can hear that you need support right now.\n\nBefore we figure out how I can help, tell me-what's going on? What's happening that made you reach out?",
                
                "I'm listening, and I'm here. You reached out for support, and that takes courage.\n\nCan you tell me what's happening right now? What's weighing on you?",
                
                "I'm right here with you. You don't have to carry this alone.\n\nWhat's going on? Help me understand what you're experiencing right now.",
                
                "I hear you-you need support. I'm here, and I'm not going anywhere.\n\nTalk to me. What's happening that feels so heavy right now?"
            ]
            
            response = random.choice(support_responses)
            
            return {
                'response': response,
                'pattern': None,
                'emotion': self.detect_emotion(message_lower),
                'needs_tool': False
            }
        
        # Check for reassurance loops (repeated distress signals)
        reassurance_phrases = [
            'dont know what to do', "don't know what to do", 'i cant cope', "i can't cope",
            'im scared', "i'm scared", 'dont know how', "don't know how", 'feel so lost'
        ]
        
        if any(phrase in message_lower for phrase in reassurance_phrases) and history:
            # Check how many times they've said similar things
            recent_user_msgs = [msg[1].lower() for msg in history[:6] if msg[0] == 'user']
            reassurance_count = sum(1 for msg in recent_user_msgs 
                                   if any(p in msg for p in reassurance_phrases))
            
            if reassurance_count >= 2:
                # Gentle escalation to professional support
                loop_response = (
                    "I'm right here with you. Let's take this one breath at a time.\n\n"
                    "I notice you're feeling really stuck and scared. That makes so much sense given what you're experiencing. "
                    "Sometimes when we keep circling back to the same feeling, it's our heart telling us we need more support than one person can give.\n\n"
                    "Would it feel okay to talk to someone who can offer deeper, ongoing care? A therapist or counselor who can walk alongside you through this? "
                    "Reaching out for that kind of support is a powerful act of strength-it shows you're ready for change.\n\n"
                    "I'll stay with you here. What feels most accessible to you right now?"
                )
                
                return {
                    'response': loop_response,
                    'pattern': 'reassurance_loop',
                    'emotion': self.detect_emotion(message_lower),
                    'needs_tool': False
                }
        
        # Check if user is agreeing to try a tool (short affirmative responses)
        tool_agreement = any(phrase in message_lower for phrase in [
            'yh', 'yeah', 'yes', 'ok', 'okay', 'sure', 'alright', 'lets try', "let's try",
            'ill try', "i'll try", 'sounds good', 'that works'
        ])
        
        # If it's a very short message (1-5 words) with agreement words, they're likely responding to a tool offer
        word_count = len(message_lower.split())
        if tool_agreement and word_count <= 5:
            agreement_responses = [
                "Beautiful. Take your time with this. There's no rush, no right way to do it.\n\nWhen you're ready, notice what comes up. I'm here when you want to share.",
                
                "Good. I'm right here with you.\n\nGive yourself permission to really be with this exercise. No pressure. Just explore.\n\nHow does it feel?",
                
                "I'm glad you're trying this. Stay with it as long as you need.\n\nWhen you're ready, let me know what you noticed-even if it's just one small thing.",
                
                "Yes. Take a moment with this.\n\nThere's no deadline. Just be with whatever comes up. I'll be here when you're ready to talk about it.",
                
                "Perfect. Breathe with it. No need to force anything.\n\nWhen you're done, tell me: what shifted? What did you notice?"
            ]
            
            response = random.choice(agreement_responses)
            
            return {
                'response': response,
                'pattern': None,
                'emotion': self.detect_emotion(message_lower),
                'needs_tool': False
            }
        
        # Check if user is saying they don't have time or are too busy
        no_time = any(phrase in message_lower for phrase in [
            'dont have time', "don't have time", 'no time', 'too busy', 'cant do this now',
            "can't do this", 'dont have the time', 'rushed', 'in a hurry'
        ])
        
        if no_time:
            time_responses = [
                "I hear you - time feels scarce right now. That's exactly why we need something that takes 60 seconds or less. Can I guide you through one quick breath? Just 4 counts in, 4 out. That's all. Will you try with me?",
                "I get it. You're already overwhelmed, and I'm asking you to add more. But what if I told you this takes 30 seconds? One minute breathing exercise that might give you MORE energy and time. Can I walk you through it?",
                "Time pressure is real. But here's the thing: when we're this rushed, our nervous system needs grounding MORE, not less. Just 60 seconds. Let me guide you step-by-step through a quick reset. Ready?",
                "I understand. You're already stretched thin. This is exactly when your body needs a pause most. What if I guide you through just ONE breath cycle right now? 10 seconds. That's it."
            ]
            response = random.choice([r for r in time_responses if r not in str(recent_ai_messages)])
            
            return {
                'response': response,
                'pattern': None,
                'emotion': self.detect_emotion(message_lower),
                'needs_tool': False
            }
        
        # Check if user is asking for suggestions/advice/help
        asking_for_help = any(word in message_lower for word in [
            'suggest', 'advice', 'help me', 'what should i do', 'what can i', 
            'how do i', 'how can i', 'recommend', 'need help', 'dont know what', 'dont know how'
        ])
        
        # Check if user wants to be guided through something
        wants_guidance = any(phrase in message_lower for phrase in [
            'guide me', 'walk me through', 'show me how', 'help me do', 'yes', 'okay', 'ready',
            'ill try', "i'll try", 'lets do it', "let's do"
        ])
        
        if wants_guidance and any('breath' in msg for msg in recent_ai_messages[:2]):
            # User agreed to breathing exercise - guide them through it
            guided_breath = (
                "Perfect. Let's do this together right now.\n\n"
                "**Box Breathing - Follow Along:**\n\n"
                "1️⃣ Breathe IN slowly through your nose: 1...2...3...4\n"
                "2️⃣ HOLD your breath: 1...2...3...4\n"
                "3️⃣ Breathe OUT slowly through your mouth: 1...2...3...4\n"
                "4️⃣ HOLD empty: 1...2...3...4\n\n"
                "Now repeat that 3 more times on your own. I'll wait.\n\n"
                "...\n\n"
                "How do you feel now?"
            )
            return {
                'response': guided_breath,
                'pattern': None,
                'emotion': None,
                'needs_tool': False
            }
        
        if wants_guidance and any('grounding' in msg.lower() or '5-4-3-2-1' in msg for msg in recent_ai_messages[:2]):
            # User agreed to grounding exercise
            guided_grounding = (
                "Great. We're going to ground you right now.\n\n"
                "**5-4-3-2-1 Grounding - Do This With Me:**\n\n"
                "First, take a deep breath.\n\n"
                "Now:\n"
                "👁️ Name **5 things you can SEE** around you\n"
                "(Look around slowly... a wall, a light, your phone, maybe a plant, the floor...)\n\n"
                "✋ Name **4 things you can TOUCH**\n"
                "(Your chair, your clothes, the ground, your hair...)\n\n"
                "👂 Name **3 things you can HEAR**\n"
                "(Traffic? Breathing? A hum? Silence?)\n\n"
                "👃 Name **2 things you can SMELL**\n"
                "(Air? Fabric? Soap? Just notice...)\n\n"
                "👅 Name **1 thing you can TASTE**\n"
                "(Your mouth, your last drink, toothpaste...)\n\n"
                "Take a breath. You're here. You're present. How do you feel?"
            )
            return {
                'response': guided_grounding,
                'pattern': None,
                'emotion': None,
                'needs_tool': False
            }
        
        # Check for specific emotional themes
        feeling_trapped = any(word in message_lower for word in [
            'trapped', 'stuck', 'cant escape', 'no way out', 'cornered', 'imprisoned'
        ])
        
        feeling_lost = any(word in message_lower for word in [
            'lost', 'confused', 'dont know', "don't know", 'unclear', 'uncertain', 'directionless'
        ])
        
        feeling_hopeless = any(word in message_lower for word in [
            'hopeless', 'pointless', 'no point', 'give up', 'cant go on', 'no future'
        ])
        
        feeling_exhausted = any(word in message_lower for word in [
            'exhausted', 'tired', 'drained', 'worn out', 'cant anymore', 'too much'
        ])
        
        # Check if user is asking about tools
        asking_for_tools = any(word in message_lower for word in [
            'tool', 'technique', 'exercise', 'practice', 'coping', 'calm down'
        ])
        
        emotion = self.detect_emotion(message_lower)
        
        # Respond to specific themes first
        if feeling_trapped:
            trapped_responses = [
                "Feeling trapped is so overwhelming. That sense of having no way out can be paralyzing. Let's explore this together - what's one small thing that might give you even a tiny bit of breathing room?",
                "I hear that trapped feeling. Sometimes when we feel cornered, we stop seeing the exits that are there. Can you tell me more about what's keeping you stuck? What would freedom look like?",
                "That trapped sensation is real and heavy. Your nervous system is in fight-or-flight. Before we look for solutions, can you tell me: where do you feel this 'trapped' sensation in your body?",
                "Being trapped is one of the hardest feelings. But here's what I know: you've gotten through trapped feelings before, even if it doesn't feel like it right now. What's one small thing that feels even slightly within your control?"
            ]
            response = random.choice([r for r in trapped_responses if r not in str(recent_ai_messages)])
            
            return {
                'response': response,
                'pattern': None,
                'emotion': emotion,
                'needs_tool': True
            }
        
        if feeling_lost:
            lost_responses = [
                "Not knowing can feel really destabilizing. It's okay to not have all the answers right now. What do you know for certain in this moment, even if it's just 'I'm here' or 'I'm feeling lost'?",
                "That confusion and uncertainty is uncomfortable. But sometimes being lost is actually where transformation begins. What are you trying to figure out? Let's untangle it together.",
                "I can hear how disorienting this feels. When we don't know what to do, it often means we're in transition. What's the decision or situation that's got you feeling this way?",
                "Not knowing is human. You don't have to have it all figured out. What if we started with just the very next step, not the whole path?"
            ]
            response = random.choice([r for r in lost_responses if r not in str(recent_ai_messages)])
            
            return {
                'response': response,
                'pattern': None,
                'emotion': emotion,
                'needs_tool': False
            }
        
        if feeling_hopeless:
            hopeless_responses = [
                "I hear the hopelessness in your words, and I want you to know: you don't have to carry this alone. When everything feels pointless, it's often because you're carrying too much. What's the heaviest thing you're holding right now?",
                "Hopelessness is a really dark place. I'm here with you in it. You don't have to convince me things will get better - you just need to survive this moment. What would help you do that?",
                "That despair is real. But feelings aren't facts, even when they feel overwhelming. You're still here, which means part of you hasn't given up. What's that part holding onto?",
                "I'm worried about you. These feelings are really intense. Can you tell me - are you safe right now? And what's brought you to this edge?"
            ]
            response = random.choice([r for r in hopeless_responses if r not in str(recent_ai_messages)])
            
            return {
                'response': response,
                'pattern': None,
                'emotion': emotion,
                'needs_tool': True
            }
        
        if feeling_exhausted:
            exhausted_responses = [
                "That exhaustion is real. You've been pushing through, haven't you? What if you gave yourself permission to just... stop? Even for five minutes. What do you need most right now?",
                "I can feel how drained you are. Exhaustion often means we've been running on empty for too long. When did you last truly rest?",
                "Being worn out like this is your body's way of saying 'enough.' What would it look like to honor that? What's one thing you could let go of or postpone?",
                "That tiredness runs deep. Sometimes we need to rest before we can do anything else. What's preventing you from resting right now?"
            ]
            response = random.choice([r for r in exhausted_responses if r not in str(recent_ai_messages)])
            
            return {
                'response': response,
                'pattern': None,
                'emotion': emotion,
                'needs_tool': False
            }
        
        if asking_for_help or asking_for_tools:
            # Provide actual suggestions with offer to guide
            suggestions = [
                f"I'm glad you're asking. Here are some things that might help:\n\n"
                f"1. **Box Breathing** (60 seconds): Breathe in for 4, hold 4, out for 4, hold 4. Calms your nervous system fast.\n"
                f"2. **5-4-3-2-1 Grounding** (2 minutes): Brings you back to the present moment.\n"
                f"3. **Hand on heart** (30 seconds): Self-compassion through touch.\n\n"
                f"Want me to guide you through one of these right now? Just say which one.",
                
                f"Let's get you some relief. Here are quick options:\n\n"
                f"• **Quick breath reset** (30 seconds) - I can guide you through this\n"
                f"• **Grounding exercise** (2 minutes) - Step-by-step with me\n"
                f"• **Body scan** (3 minutes) - We'll do it together\n\n"
                f"Which one feels doable right now? Or say 'guide me' and I'll pick the best one for you.",
                
                f"Here's what I recommend:\n\n"
                f"1. **Breathing technique** - Takes 1 minute, very effective for anxiety\n"
                f"2. **Sensory grounding** - Takes 2 minutes, brings you to present\n"
                f"3. **Gentle movement** - Takes 30 seconds, releases tension\n\n"
                f"I can walk you through any of these step-by-step. Which one calls to you?",
                
                f"I have a few tools that might help:\n\n"
                f"• **Box breathing** - 4 rounds, I'll count with you\n"
                f"• **Grounding** - Name things you sense, I'll guide you\n"
                f"• **Self-compassion phrase** - I'll teach you a powerful one\n\n"
                f"Tell me which one, or just say 'breathe' and we'll start there."
            ]
            
            response = random.choice([s for s in suggestions if s not in str(recent_ai_messages)])
            
            # Add emotion-specific affirmation if emotion detected
            if emotion and emotion in self.affirmations:
                affirmation = random.choice(self.affirmations[emotion])
                response += f"\n\n✨ {affirmation}"
            
            return {
                'response': response,
                'pattern': None,
                'emotion': emotion,
                'needs_tool': False
            }
        
        # Check if expressing gratitude or positive sharing
        if any(word in message_lower for word in ['thank', 'grateful', 'appreciate', 'helped']):
            gratitude_responses = [
                "I'm so glad this is helpful. You're doing important work by showing up for yourself. How are you feeling right now?",
                "Your willingness to engage with this process is beautiful. That takes real courage. What's shifted for you?",
                "You're very welcome. Remember, healing isn't linear - be patient with yourself. What's one thing you're proud of today?"
            ]
            response = random.choice([r for r in gratitude_responses if r not in str(recent_ai_messages)])
            return {
                'response': response,
                'pattern': None,
                'emotion': emotion,
                'needs_tool': False
            }
        
        # Check if sharing progress or positive update
        if any(word in message_lower for word in ['better', 'helped', 'working', 'trying', 'practicing']):
            progress_responses = [
                "That's wonderful to hear. Progress isn't always linear, but you're showing up for yourself and that matters. What's been the most helpful part?",
                "I'm really proud of you for putting in this work. It's not easy to face these things. What do you notice changing?",
                "This is great. Keep building on what's working. What would support you in continuing this momentum?"
            ]
            response = random.choice([r for r in progress_responses if r not in str(recent_ai_messages)])
            return {
                'response': response,
                'pattern': None,
                'emotion': emotion,
                'needs_tool': False
            }
        
        # General empathetic responses for exploration - make them more varied
        # Check if user already mentioned a time period
        time_period = self.extract_time_period(message_lower)
        
        if time_period:
            # User already mentioned duration - acknowledge it and ask deeper questions
            time_aware_responses = [
                f"I hear you. You mentioned this has been happening for {time_period}. Has it been going on longer than that, or did something specific trigger it {time_period} ago?",
                f"That's a lot to carry for {time_period}. What's been making this period particularly difficult?",
                f"You said {time_period} - that's significant. What's changed or gotten harder during this time?",
                f"I'm hearing {time_period} of struggle. What's kept you going through it? And what made you reach out today?"
            ]
            
            available_responses = [r for r in time_aware_responses if r not in str(recent_ai_messages)]
            if not available_responses:
                available_responses = time_aware_responses
        else:
            # No time period mentioned - can ask about duration
            exploration_responses = [
                f"I hear you. Can you tell me more about that? What does it feel like for you?",
                f"That sounds really difficult. What's making this particularly hard right now?",
                f"I'm here with you. Help me understand - what's the most challenging part of this?",
                f"I'm listening. When you think about this, what comes up for you?",
                f"Tell me more. What's this experience like from your perspective?",
                f"I want to understand better. Can you walk me through what you're experiencing?",
                f"What stands out to you most about what you're feeling right now?",
                f"That's a lot to carry. How long has this been weighing on you?"
            ]
            
            # Filter out responses that were recently used
            available_responses = [r for r in exploration_responses if r not in str(recent_ai_messages)]
            if not available_responses:
                available_responses = exploration_responses  # Use all if all were recent
        
        return {
            'response': random.choice(available_responses),
            'pattern': None,
            'emotion': emotion,
            'needs_tool': False
        }

# Initialize AI
ai = HealingGuruAI()

@app.route('/')
def index():
    if 'user_id' not in session:
        session['user_id'] = secrets.token_hex(8)
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    user_id = session.get('user_id')
    
    # Get conversation history BEFORE saving new message
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    c.execute('SELECT role, content FROM messages WHERE user_id = ? ORDER BY timestamp DESC LIMIT 10',
              (user_id,))
    history = c.fetchall()
    
    # Save user message
    c.execute('INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)',
              (user_id, 'user', user_message))
    
    # Generate AI response with history
    ai_analysis = ai.analyze_message(user_message, history)
    
    # Save AI response
    c.execute('INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)',
              (user_id, 'assistant', ai_analysis['response']))
    
    # Save detected pattern
    if ai_analysis['pattern']:
        c.execute('INSERT INTO insights (user_id, pattern_type, description) VALUES (?, ?, ?)',
                  (user_id, ai_analysis['pattern'], user_message[:200]))
    
    conn.commit()
    conn.close()
    
    # Build response with tools if needed
    response_data = {
        'message': ai_analysis['response'],
        'pattern': ai_analysis['pattern'],
        'emotion': ai_analysis['emotion']
    }
    
    # Include intelligently recommended tools if available
    if ai_analysis.get('needs_tool') and ai_analysis.get('recommended_tools'):
        response_data['urgent_tools'] = ai_analysis['recommended_tools']
    elif ai_analysis.get('needs_tool'):
        # Fallback to first 3 tools if no specific recommendations
        response_data['urgent_tools'] = ai.coping_tools[:3]
    
    return jsonify(response_data)

@app.route('/api/get_tool', methods=['POST'])
def get_tool():
    """Get a specific coping tool"""
    data = request.json
    emotion = data.get('emotion', 'anxiety')
    
    # Filter tools by emotion
    relevant_tools = [tool for tool in ai.coping_tools if emotion in tool['when']]
    
    if not relevant_tools:
        relevant_tools = ai.coping_tools[:2]
    
    return jsonify({'tools': relevant_tools})

@app.route('/api/affirmation', methods=['POST'])
def get_affirmation():
    """Get a random affirmation"""
    data = request.json
    emotion = data.get('emotion', 'anxiety')
    
    if emotion in ai.affirmations:
        import random
        affirmation = random.choice(ai.affirmations[emotion])
        return jsonify({'affirmation': affirmation})
    
    return jsonify({'affirmation': 'You are doing the best you can, and that is enough.'})

@app.route('/api/insights', methods=['GET'])
def get_insights():
    """Get user's pattern insights"""
    user_id = session.get('user_id')
    
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    c.execute('''SELECT pattern_type, COUNT(*) as count, MAX(detected_at) as last_seen
                 FROM insights WHERE user_id = ?
                 GROUP BY pattern_type ORDER BY count DESC''',
              (user_id,))
    
    insights = []
    for row in c.fetchall():
        insights.append({
            'pattern': row[0],
            'count': row[1],
            'last_seen': row[2]
        })
    
    conn.close()
    return jsonify({'insights': insights})

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    user_id = session.get('user_id')
    
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    c.execute('SELECT role, content, timestamp FROM messages WHERE user_id = ? ORDER BY timestamp',
              (user_id,))
    
    messages = []
    for row in c.fetchall():
        messages.append({
            'role': row[0],
            'content': row[1],
            'timestamp': row[2]
        })
    
    conn.close()
    return jsonify({'messages': messages})

if __name__ == '__main__':
    import os
    # Get port from environment variable (Railway) or use 5002 for local
    port = int(os.environ.get('PORT', 5002))
    # Allow external connections
    app.run(debug=False, host='0.0.0.0', port=port)
