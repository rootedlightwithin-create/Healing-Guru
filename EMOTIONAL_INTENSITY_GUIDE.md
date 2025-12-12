# Emotional Intensity Scale - Implementation Guide

## Overview
The Healing Guru app now includes an **internal 0-10 emotional intensity scale** that operates silently in the background. This scale is **never shown to users** - it's a quiet compass that guides the AI's intervention level and tone.

## How It Works

### Internal Scoring System (0-10)

**Critical (9-10)** - Immediate crisis intervention
- Phrases: "want to die", "kill myself", "end it all", "can't do this anymore"
- Response: Crisis resources (988 hotline, Crisis Text Line)
- Tone: Immediate, compassionate, clear resources

**Severe Distress (7-8)** - Strong professional support encouragement  
- Phrases: "can't cope", "falling apart", "unraveling", "no way out"
- Response: Encourages reaching out to doctor, therapist, crisis counselor
- Adds crisis line information at bottom

**High Distress (6-7)** - Enhanced emotional support
- Phrases: "can't function", "spiraling", "drowning", "losing it"
- Response: Regular therapeutic response + crisis hotline reminder
- Offers grounding tools proactively

**Moderate-High (5-6)** - Active coping support
- Phrases: "overwhelmed", "too much", "can't think", "trapped"
- Response: Guided exercises, specific interventions
- More directive support

**Moderate (4-5)** - Standard supportive response
- Phrases: "anxious", "stressed", "worried", "exhausted"
- Response: Empathetic exploration with tools offered

**Low-Moderate (0-3)** - Conversational support
- No distress indicators detected
- Response: Reflective, exploratory, building awareness

### Additional Analysis Factors

**Tone Analysis:**
- Fragmented messages (+1 to score)
- Repetitive hopeless phrases (+2 to score)
- ALL CAPS or excessive punctuation (+1 to score)

**Pattern Tracking:**
- Compares recent messages to earlier in conversation
- Detects escalating negativity over time
- Adjusts score upward if deterioration detected

## User Experience

### What Users See:
- **Compassionate, tailored responses** that match their emotional state
- **Appropriate level of intervention** without being told they're in "crisis"
- **Gentle offers of support** that feel natural, not alarming
- **Professional resources** presented warmly when needed

### What Users DON'T See:
- The 0-10 number itself
- Clinical language or diagnostic terms
- Sudden shifts that feel robotic
- Anxiety-inducing labels

## Key Features Implemented

### 1. Crisis Detection (Score 7-10)
When emotional intensity reaches crisis levels:
```
"I'm hearing a lot of pain in your words... and you don't have to 
carry this alone.

Sometimes pain like this needs more than I can offer as an AI. 
Would you consider reaching out?

📞 **Crisis Support (24/7):**
- Call/text 988 (Suicide & Crisis Lifeline)
- Text HOME to 741741 (Crisis Text Line)
- Visit findahelpline.com for global resources

I'm here while you think about it. What's one small thing that 
might help right now?"
```

### 2. Immediate Support Recognition
Fixed: **"I need support right now"** now triggers:
```
"I'm here with you right now. You reached out, and that takes 
real courage.

**What do you need most in this moment?**
• Someone to talk through this with
• A grounding exercise to help you feel more centered
• Resources for immediate crisis support

Tell me what would help."
```

Detected phrases:
- "need support"
- "need help right now"
- "can't do this alone"
- "please help"
- "struggling right now"

### 3. Adaptive Response Style
The AI now automatically adjusts its approach based on intensity:

- **High intensity:** More directive, offers concrete tools immediately
- **Moderate intensity:** Balanced exploration with support
- **Low intensity:** Reflective questions, building awareness

### 4. No Diagnosis, Just Support
Critical design principle:
- ❌ "You seem to be in crisis"
- ❌ "Your score is 8/10"
- ❌ "You're experiencing severe distress"

- ✅ "I'm hearing a lot of pain in your words"
- ✅ "This sounds really heavy"
- ✅ "You don't have to carry this alone"

## Testing the System

### Test Case 1: Crisis Language
**User:** "I want to die"
**Expected:** Immediate crisis response with 988 hotline

### Test Case 2: Immediate Support Request
**User:** "I need support right now"
**Expected:** Present options (talk/exercise/resources) immediately

### Test Case 3: Severe Distress
**User:** "I'm falling apart and can't cope anymore"
**Expected:** Compassionate response + professional support encouragement

### Test Case 4: Time Pressure
**User:** "I don't have time for this"
**Expected:** Validates time scarcity, offers 60-second exercises

### Test Case 5: Guided Exercise Flow
**User:** "I'm overwhelmed"
**AI:** [Offers breathing exercise]
**User:** "okay" or "yes"
**Expected:** Step-by-step guided breathing instructions

## Privacy & Ethics

- **No data storage** of intensity scores (currently)
- **No external sharing** of crisis flags
- **User-controlled** - can decline all suggestions
- **Transparent** - AI explains reasoning when asked
- **Compassionate** - never shaming or diagnostic

## Future Enhancements

1. **Intensity tracking over time** - Detect patterns of escalation
2. **Regional crisis resources** - Tailor to user location
3. **Follow-up after high-intensity moments** - Check in later
4. **Integration with journal** - Track emotional patterns
5. **Professional referral suggestions** - Gentle recommendations

## Technical Implementation

**File:** `/Users/shennahodge/healing_guru_app/app_chat.py`

**Key Methods:**
- `assess_emotional_intensity(message, conversation_history)` - Returns 0-10 score
- `get_crisis_response(intensity_level)` - Generates intervention for 7-10
- `analyze_message()` - Calls intensity check first, routes response
- `generate_empathetic_response()` - Includes immediate support detection

**Database:**
- Currently stores: messages, insights, patterns
- Future: Add intensity_score column to messages table for trend analysis

## Tone Guidelines

**Always:**
- Warm, human, present
- "I'm here" language
- Validate emotions without labeling severity
- Offer options, not directives

**Never:**
- Clinical terminology
- Diagnostic language
- Alarm or panic
- Force solutions

**Example Transitions:**
- Score 4→6: Add tools proactively
- Score 6→8: Mention professional support gently
- Score 8→10: Lead with crisis resources warmly

---

**Remember:** This scale exists to ensure the most vulnerable users get the most appropriate support, wrapped in the warmest possible delivery. It's a safety net that feels like a soft hand at their back.
