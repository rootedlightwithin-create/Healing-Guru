def seed_freeze_path():
    """Seed the 'From Freeze to Gentle Action' healing path"""
    import sqlite3
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    
    # Check if path already exists
    c.execute("SELECT id FROM paths WHERE slug = 'freeze-to-action'")
    if c.fetchone():
        conn.close()
        return  # Already seeded
    
    # Insert path
    c.execute("""INSERT INTO paths (title, slug, description, summary, icon, duration)
                 VALUES (?, ?, ?, ?, ?, ?)""",
              ('From Freeze to Gentle Action',
               'freeze-to-action',
               "There's nothing wrong with you. Freeze is a wise response when things once felt too much. This gentle 7-step journey helps you befriend your nervous system and rediscover the possibility of movement - without urgency, without pressure.",
               'Move from shutdown and paralysis to gentle, grounded action',
               '🌊',
               '7 days'))
    
    path_id = c.lastrowid
    
    # Insert modules
    modules = [
        {
            'step': 1,
            'title': 'Naming the Freeze',
            'purpose': 'Safety and recognition',
            'guru_message': "There's nothing wrong with you. Freeze is a wise response when things once felt too much. Your body learned this to keep you safe.\n\nToday, we're not trying to fix anything. We're just going to notice.",
            'tools': 'Body Scan,Gentle Grounding (feet, breath, weight)',
            'reflection': 'When I freeze, I notice it shows up as...',
            'action': 'Just notice freeze today. No fixing. No pressure. Just awareness.',
            'is_free': True,
            'minutes': 10
        },
        {
            'step': 2,
            'title': 'Befriending the Nervous System',
            'purpose': 'Reduce shame, build trust',
            'guru_message': "Your body learned this to protect you. Freeze isn't failure - it's your nervous system doing what it thought it needed to do.\n\nToday, we practice gratitude for the part of you that kept you safe, even if it doesn't serve you the same way now.",
            'tools': 'Butterfly Hug,Box Breathing',
            'reflection': 'What does my body need when it shuts down?',
            'action': 'One small act of care today: warm drink, lying down for 5 minutes, stepping outside, or wrapping yourself in a blanket.',
            'is_free': True,
            'minutes': 12
        },
        {
            'step': 3,
            'title': 'Safety Before Action',
            'purpose': 'Rewire urgency',
            'guru_message': "Action only works when safety comes first. When your nervous system doesn't feel safe, pushing forward creates more freeze.\n\nLet's find what signals safety to your body.",
            'tools': 'Orienting Exercise (naming safe objects),Grounding',
            'reflection': 'What helps me feel even 5% safer right now?',
            'action': 'Choose one micro-safety anchor for today: a cozy corner, a specific song, a grounding object you can touch.',
            'is_free': False,
            'minutes': 15
        },
        {
            'step': 4,
            'title': 'Tiny Movement',
            'purpose': 'Restore agency',
            'guru_message': "We don't leap out of freeze. We thaw, slowly.\n\nToday is about the smallest possible movement - not because you should, but because you can.",
            'tools': '30-second movement (stretch, shake, sway),Breath',
            'reflection': "What felt possible today that didn't yesterday?",
            'action': 'One gentle, non-urgent task: send one text, wash one dish, step outside for 60 seconds.',
            'is_free': False,
            'minutes': 12
        },
        {
            'step': 5,
            'title': 'Working with Resistance',
            'purpose': 'Compassionate accountability',
            'guru_message': "Resistance isn't failure - it's information.\n\nWhen you notice yourself pulling back or shutting down, pause. Ask: \"What does this part of me need right now?\"",
            'tools': 'Inner Dialogue,Grounding before reflection',
            'reflection': 'What felt hard today, and why might that make sense?',
            'action': "Rewrite one harsh inner message with kindness. Example: \"I'm so lazy\" becomes \"I'm protecting myself from something that feels overwhelming.\"",
            'is_free': False,
            'minutes': 15
        },
        {
            'step': 6,
            'title': 'Reclaiming Choice',
            'purpose': 'Empowerment',
            'guru_message': "You get to choose differently, even in small ways.\n\nFreeze often comes from feeling like there's no choice. Today, we practice noticing where choice still lives.",
            'tools': 'Visualization (responding differently next time),Grounding',
            'reflection': "What choice feels aligned right now - even if it's tiny?",
            'action': 'One conscious yes or no today. Say yes to something nourishing. Say no to something draining.',
            'is_free': False,
            'minutes': 14
        },
        {
            'step': 7,
            'title': 'Integration & Reflection',
            'purpose': 'Meaning-making',
            'guru_message': "You've walked through this with such care. Notice what's changed - even subtly.\n\nFreeze may still show up sometimes. But now you have a way to work with it.",
            'tools': 'Gentle Review,Reflection',
            'reflection': 'What feels more available in me now? What do I want to remember?',
            'action': 'Write a note to your future self for the next time freeze shows up. What would you want to hear?',
            'is_free': False,
            'minutes': 18
        }
    ]
    
    for module in modules:
        c.execute("""INSERT INTO modules 
                     (path_id, step_number, title, purpose, guru_message, tools, 
                      reflection_prompt, action_invitation, is_free, estimated_minutes)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (path_id, module['step'], module['title'], module['purpose'],
                   module['guru_message'], module['tools'], module['reflection'],
                   module['action'], module['is_free'], module['minutes']))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    seed_freeze_path()
    print("Path seeded successfully!")
