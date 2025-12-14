from flask import Flask, render_template, request, jsonify, session, redirect
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
    
    # Healing paths table
    c.execute('''CREATE TABLE IF NOT EXISTS paths
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  slug TEXT UNIQUE NOT NULL,
                  description TEXT,
                  summary TEXT,
                  icon TEXT,
                  duration TEXT,
                  is_active BOOLEAN DEFAULT 1,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Path modules table
    c.execute('''CREATE TABLE IF NOT EXISTS modules
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  path_id INTEGER,
                  step_number INTEGER,
                  title TEXT NOT NULL,
                  purpose TEXT,
                  guru_message TEXT,
                  tools TEXT,
                  reflection_prompt TEXT,
                  action_invitation TEXT,
                  is_free BOOLEAN DEFAULT 0,
                  estimated_minutes INTEGER,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (path_id) REFERENCES paths(id))''')
    
    # User path progress table
    c.execute('''CREATE TABLE IF NOT EXISTS user_progress
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT,
                  path_id INTEGER,
                  module_id INTEGER,
                  started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  completed_at DATETIME,
                  reflection_response TEXT,
                  FOREIGN KEY (path_id) REFERENCES paths(id),
                  FOREIGN KEY (module_id) REFERENCES modules(id))''')
    
    # User subscriptions table (Gumroad integration)
    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT UNIQUE,
                  gumroad_license_key TEXT,
                  subscription_status TEXT,
                  started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  expires_at DATETIME)''')
    
    # Community posts table
    c.execute('''CREATE TABLE IF NOT EXISTS community_posts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT,
                  display_name TEXT,
                  path_slug TEXT,
                  category TEXT,
                  title TEXT NOT NULL,
                  content TEXT NOT NULL,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Community comments table
    c.execute('''CREATE TABLE IF NOT EXISTS community_comments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  post_id INTEGER,
                  user_id TEXT,
                  display_name TEXT,
                  content TEXT NOT NULL,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (post_id) REFERENCES community_posts(id))''')
    
    # User consent table (GDPR compliance)
    c.execute('''CREATE TABLE IF NOT EXISTS user_consent
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT UNIQUE,
                  cookies_accepted BOOLEAN DEFAULT 0,
                  data_processing_accepted BOOLEAN DEFAULT 0,
                  consent_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                  ip_address TEXT,
                  last_updated DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

def seed_freeze_path():
    """Seed the 'From Freeze to Gentle Action' healing path using the 4 R Framework"""
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    
    # Check if path already exists
    c.execute("SELECT id FROM paths WHERE slug = 'freeze-to-action'")
    if c.fetchone():
        conn.close()
        return  # Already seeded
    
    # Insert path
    c.execute("""INSERT INTO paths (title, slug, description, summary, icon, duration, is_active)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              ('From Freeze to Gentle Action',
               'freeze-to-action',
               "Move from shutdown and paralysis to gentle, grounded action using the 4 R Framework: Root, Release, Reflect, Rise. Each session includes check-in questions, grounding exercises, and embodied practices.",
               'Transform freeze response into empowered action',
               '🌊',
               '7 sessions',
               1))
    
    path_id = c.lastrowid
    
    # Insert modules following 4 R Framework phases
    modules = [
        {
            'step': 1,
            'title': 'Phase 1: Clearing - Root (Identifying the Block)',
            'purpose': 'Ground in safety and identify what belief or energy block is surfacing',
            'guru_message': """**Check-In Questions:**
• How has your week been?
• What's been showing up for you?
• What's one word that describes your energy today?

**Grounding Exercise (2-3 minutes):**
Close your eyes. Place one hand on your heart, one on your belly. Inhale for 4, hold for 2, exhale for 6. Repeat twice. Visualize roots growing down into the earth. Affirm: "I am safe. I am here. I am open to what I need today."

---

**🌿 ROOT - Being grounded, safe, and developing self-trust**

There's nothing wrong with you. Freeze is a wise response when things once felt too much. Your body learned this to keep you safe.

Today, we're not trying to fix anything. We're just going to notice and identify what's coming up for you.""",
            'tools': 'Body Scan,Grounding',
            'reflection': """**Root Reflection Questions:**
• What has been bothering me most at the moment?
• What belief do I have that no longer serves me about my freeze response?
• Where do I feel this belief in my body?
• What part of me needs reassurance or grounding right now?

**Affirmation:** "I am safe to feel what I'm feeling. I am safe to notice my freeze response without judgment."

Write down what stands out most strongly. Do a gentle body scan to notice where this belief connects in your body.""",
            'action': 'Just notice freeze today. No fixing. No pressure. Just awareness. Write down when you notice it and where you feel it in your body.',
            'is_free': True,
            'minutes': 20
        },
        {
            'step': 2,
            'title': 'Phase 1: Clearing - Release (Letting Go)',
            'purpose': 'Release stuck patterns and shame around freeze response',
            'guru_message': """**Check-In Questions:**
• How has your week been?
• What's been showing up for you since last session?
• What's one word that describes your energy today?

**Grounding Exercise (2-3 minutes):**
Eyes closed, one hand heart, one hand belly. Inhale 4, hold 2, exhale 6 (repeat twice). Visualize roots growing down into the earth. Affirm: "I am safe. I am here. I am open to what I need today."

---

**🌊 RELEASE - Relief from stuck patterns and energy drains**

Your body learned freeze to protect you. It isn't failure - it's your nervous system doing what it thought it needed to do.

Today, we practice releasing the shame and old patterns that keep you stuck in freeze.""",
            'tools': 'Butterfly Hug,Box Breathing',
            'reflection': """**Release Reflection Questions:**
• What feels heavy right now about my freeze response?
• What am I still carrying that no longer belongs to me?
• What emotion have I been avoiding or suppressing?
• If my body could speak clearly, what would it say it's done with?
• What am I afraid will happen if I release this freeze pattern?

**Release Visualization:**
Visualize cords attached to the body parts where you felt sensations earlier. These cords represent the limiting belief about freeze. Imagine cutting these cords and watching them fade away. Affirm: "I release all that does not serve me. I release the shame around my freeze response."

Write what you're ready to release.

---

**Understanding Your Energetic Blueprint**

Your freeze response isn't random - it's connected to your soul-state pattern. These patterns shape how you respond to stress and where you seek safety.

**The 6 Core Soul-States:**

• **WOUNDED:** Carrying unhealed pain that colors your responses
• **ROOTED:** Grounded and stable, connected to your physical safety  
• **ELEVATED:** Spiritually aware, seeking higher meaning and understanding
• **HEALED:** Integrated your experiences, at peace with your journey
• **NURTURER:** Care deeply for others, deeply heart-centered
• **AVOIDANT:** Protect your peace through distance or boundaries

These don't exist alone - they combine to create YOUR unique energetic signature.

---

**Self-Identification Questions:**

**When you freeze, which feels most true?**
□ I feel stuck in old pain that I can't seem to move past (Wounded)
□ I feel disconnected from my body, floating or numb (Elevated)  
□ I feel unsafe, unstable, or like the ground is shifting (Rooted)
□ I retreat into my mind to escape feelings (Avoidant)
□ I disappear into taking care of others (Nurturer)

**How do you relate to others when stressed?**
□ I over-give and lose myself in caregiving (Nurturer)
□ I retreat and need space, possibly shutting down (Avoidant)
□ I stay present physically but can't access my emotions (Rooted)
□ I float away into spiritual or intellectual realms (Elevated)
□ I feel my unhealed wounds get louder (Wounded)

---

**Common Freeze Patterns**

Here are the most common combinations - see which resonates with your soul:

**🌸 WOUNDED-NURTURER**
*"You give until there's nothing left, then freeze"*

**Energetic Pattern:** Strong heart chakra but depleted sacral and root. You give from an empty well.

**Essence:** You care deeply for others, but your capacity to nurture comes from unhealed wounds. You learned that love equals sacrifice. Your freeze happens when you've poured everything out and your nervous system shuts down to prevent total collapse.

**Recognize yourself?** You say yes automatically, feel guilty resting, and believe your worth is tied to being needed.

---

**🌑 ROOTED-WOUNDED**  
*"Strong on the outside, shaken within"*

**Energetic Pattern:** Strong root chakra with disruptions in heart and sacral. You hold it together through sheer will.

**Essence:** You appear grounded, capable, dependable - the one everyone leans on. But underneath is unhealed pain you've never had space to express. Your freeze happens when you can no longer hold the weight alone and your body forces you to stop.

**Recognize yourself?** You're the "strong one," you dismiss your own needs, and vulnerability feels dangerous.

---

**🌊 AVOIDANT-ELEVATED**
*"Retreat into your head when emotions feel too big"*

**Energetic Pattern:** Strong third eye and crown, but blocked heart and sacral. You escape up and out.

**Essence:** You're spiritually aware, intuitive, deeply thoughtful. But when emotions get intense, you disconnect from your body and retreat into ideas, analysis, or spiritual concepts. Your freeze is leaving your body to avoid feeling.

**Recognize yourself?** You intellectualize feelings, prefer solitude when stressed, and feel safer in your mind than your body.

---

**🌿 WOUNDED-ELEVATED**
*"Spiritual awareness meets unhealed pain"*

**Energetic Pattern:** Active crown and third eye, wounded heart chakra. Wisdom without embodiment.

**Essence:** You have spiritual insight and seek higher meaning, but carry deep emotional wounds. You may use spiritual practices to bypass pain. Your freeze happens when your body's unhealed trauma conflicts with your elevated consciousness.

**Recognize yourself?** You're drawn to healing work but struggle to heal yourself, you know what you "should" do but can't embody it.

---

**🪨 ROOTED-AVOIDANT**
*"Grounded in survival, distant in emotion"*

**Energetic Pattern:** Strong root, blocked heart. Practical but emotionally protected.

**Essence:** You're stable, responsible, and handle practical matters well. But emotional intimacy feels threatening. Your freeze looks like withdrawal - you stay functional but emotionally unreachable.

**Recognize yourself?** You're reliable and independent, but struggle to open up or ask for help.

---

**Which Pattern Resonates Most With You?**

Write it down. Don't overthink it - your body knows.

In the premium modules, you'll receive:

✦ **Your specific chakra and energetic signature**
✦ **The childhood origin of YOUR pattern** (not generic - YOUR story)
✦ **Personalized tools designed for YOUR nervous system**
✦ **Shadow work for YOUR specific blocks**
✦ **A healing path that honors YOUR unique wiring**
✦ **Light-side activation practices**
✦ **Pattern interrupts that actually work for you**

This isn't generic healing advice. This is your energetic blueprint - and in the premium path, you'll learn exactly how to work with it.""",
            'action': 'One small act of care today: warm drink, lying down for 5 minutes, stepping outside, or wrapping yourself in a blanket. Practice the release visualization whenever shame about freeze shows up.',
            'is_free': True,
            'minutes': 25
        },
        {
            'step': 3,
            'title': 'Phase 1: Clearing - Reflect (Gaining Clarity)',
            'purpose': 'Gain clarity about what you truly want underneath the freeze',
            'guru_message': """**Check-In Questions:**
• How has your week been?
• What's been showing up for you?
• What's one word that describes your energy today?

**Grounding Exercise:**
Close eyes. Hand on heart, hand on belly. Inhale 4, hold 2, exhale 6 (twice). Roots to earth. "I am safe. I am here. I am open."

---

**🔮 REFLECT - Clarity about what you truly want**

Action only works when safety comes first. When your nervous system doesn't feel safe, pushing forward creates more freeze.

Let's reflect on what you truly need and desire.""",
            'tools': 'Orienting,Grounding',
            'reflection': """**Reflect Questions:**
• What do I truly want underneath this freeze response?
• How does freeze distort or block my true desire for movement and agency?
• What new perspective feels more aligned with my authentic self?
• What helps me feel even 5% safer right now?
• How can I offer safety to myself first?

---

**Deep Personalized Guidance for Your Soul-State Pattern**

**🌸 WOUNDED-NURTURER**

**Energetic Pattern:** Strong heart chakra with leaking, imbalanced energy. Depleted sacral (pleasure, boundaries) and root (safety, worthiness). You give endlessly but without boundaries - your energy drains rapidly.

**Childhood Origin:** You were the emotional anchor for caregivers or family - praised for being "mature," "responsible," "so helpful." Your emotional labor was invisible. You learned: *"If I am lovable, I must prove it by being useful."*

**What Safety Looks Like for You:**
• Permission to rest without proving your worth
• Saying no without guilt spiraling afterward  
• Receiving care without feeling like a burden
• Being loved for who you are, not what you do

**Your Micro-Anchor Safety Practice:**
Place hand on heart. Say out loud: *"I am loved even when I am resting."*

Notice: Do you believe it? What tightens in your body? Where does doubt live? Stay with the sensation for 30 seconds. You don't have to believe it yet - just practice saying it.

**Shadow Work Question:** When you over-give, pause and ask: *"Am I loving them, or avoiding feeling unloved?"*

**Your New Truth:** "I am worthy of rest. My needs matter as much as anyone else's. Love doesn't require my depletion."

---

**🌑 ROOTED-WOUNDED**

**Energetic Pattern:** Strong root chakra (survival, stability) but with disruptions in heart and sacral. You suppress emotional expression, rely on structure over surrender, disconnect from vulnerability to stay functional.

**Childhood Origin:** You had to grow up fast. Maybe you were the protector, the rock, the one who couldn't afford to fall apart. Emotional needs were unseen or deemed "weak." You learned: *"If I don't stay strong, everything falls apart."*

**What Safety Looks Like for You:**
• Letting someone see what's underneath your armor
• Sharing the weight instead of carrying it alone
• Being vulnerable without everything collapsing
• Rest that doesn't feel like giving up

**Your Micro-Anchor Safety Practice:**
Place both hands on belly. Breathe slowly. Say: *"I am safe to soften. Strength includes tenderness."*

Notice: Where does resistance live? Does your jaw clench? Shoulders tighten? That's the old armor. Breathe into it.

**Shadow Work Question:** *"What am I afraid will happen if I let others see I'm not okay?"*

**Your New Truth:** "I don't have to hold it all together alone. Vulnerability is not weakness - it's connection. I can be both strong AND soft."

---

**🌊 AVOIDANT-ELEVATED**

**Energetic Pattern:** Strong third eye and crown (intuition, spiritual awareness) but blocked heart and sacral. You can feel overly logical, dissociated, or floating. Your energy escapes upward instead of staying grounded in your body.

**Childhood Origin:** Emotional vulnerability wasn't safe or modeled. You may have felt misunderstood, overwhelmed, or criticized. You learned to detach from feelings and retreat into thoughts, knowledge, or spiritual concepts. You learned: *"It's safer to think or transcend than to feel or reveal."*

**What Safety Looks Like for You:**
• Emotional space without pressure to "open up" immediately
• Connection that doesn't feel overwhelming or consuming  
• Staying in your body when emotions arise
• Being seen without being analyzed or fixed

**Your Micro-Anchor Safety Practice:**
Place both hands on your lower belly. Feet flat on ground. Say: *"I am safe in my body. My emotions won't overwhelm me if I stay present."*

Notice: Do you feel the urge to float away? To analyze instead of feel? Gently bring awareness back to your belly, your feet, your breath.

**Shadow Work Question:** *"What am I protecting myself from by staying in my head?"*

**Your New Truth:** "I can stay present in my body even when emotions arise. Feelings are information, not threats. I am safe to feel."

---

**🌿 WOUNDED-ELEVATED**

**Energetic Pattern:** Highly active third eye and crown (spiritual gifts, intuition) but weak root chakra. You're psychically open and spiritually aware, but ungrounded. Your body holds unhealed trauma while your consciousness seeks to transcend it.

**Childhood Origin:** You were likely "too sensitive," "too dreamy," misunderstood. Your environment didn't nurture your gifts. You may have turned to spiritual practices to escape pain. You learned: *"It's safer to leave than to feel."*

**What Safety Looks Like for You:**
• Being in your body without overwhelming pain
• Spiritual connection that's grounded in earth, not just ether
• Healing emotional wounds instead of transcending them
• Feeling "at home" here, not always longing for elsewhere

**Your Micro-Anchor Safety Practice:**
Sit or stand. Feel your sit bones or feet. Say: *"My body is sacred too. Being human is part of my divinity."*

Notice: Does being in your body feel heavy? Painful? That's the unhealed wounding calling you back down. Breathe. You're safe to be here.

**Shadow Work Question:** *"What pain am I spiritually bypassing by staying elevated?"*

**Your New Truth:** "I can be spiritually connected AND fully embodied. My healing includes my body, not just my spirit. I belong here."

---

**🪨 ROOTED-AVOIDANT**

**Energetic Pattern:** Strong root chakra (grounded, stable) but blocked heart and sacral. You're practical, functional, and self-sufficient - but emotionally distant. Your energy is solid but rigid.

**Childhood Origin:** You grew up in unpredictable or emotionally unsafe environments. You learned to handle things alone. Emotional expression might have been seen as weakness. You learned: *"If I stay strong and silent, I stay safe."*

**What Safety Looks Like for You:**
• Emotional expression without losing control
• Connection that doesn't threaten your stability  
• Vulnerability in small, manageable doses
• Being supported without losing independence

**Your Micro-Anchor Safety Practice:**
Place one hand on heart, one on belly. Breathe. Say: *"I can soften without falling apart. Connection is safe."*

Notice: Does your body want to pull away? Shut down? That's the protective pattern. Stay present for 30 seconds.

**Shadow Work Question:** *"What would become available to me if I let others in?"*

**Your New Truth:** "Strength can include softness. I am safe to open my heart in small ways. Connection won't destroy my stability."

---

**Loving Space Visualization:**

Close your eyes. Visualize a space where you feel completely safe - maybe in nature, a cozy room, or held by loving presence. See your pattern's NEW truth filling this space with light. Let it expand through your whole body.

Write: What does safety feel like in your body when you imagine your new truth?

**Your Personal Affirmation:**
Choose the affirmation from your pattern above, or create your own based on what your soul needs to hear."""  ,
            'action': 'Choose one micro-safety anchor for today: a cozy corner, a specific song, a grounding object you can touch. Use it whenever you notice freeze starting.',
            'is_free': False,
            'minutes': 25
        },
        {
            'step': 4,
            'title': 'Phase 1-2: Clearing to Embodying - Rise (Taking Action)',
            'purpose': 'Build confidence to take one small action from your new truth',
            'guru_message': """**Check-In:**
• How has your week been?
• What's been showing up for you?
• One word for your energy today?

**Grounding:**
Eyes closed. Hands on heart and belly. Inhale 4, hold 2, exhale 6 (twice). Roots down. "I am safe. I am here. I am open."

---

**🔥 RISE - Confidence to take action**

We don't leap out of freeze. We thaw, slowly.

Today is about the smallest possible movement - not because you should, but because you can. This is where we transition from clearing old energy to embodying your new truth.""",
            'tools': 'Movement,Breath',
            'reflection': """**Rise Questions:**
• What is one small action I can take right now to embody this new truth about safety and movement?
• How can I reinforce this new pattern when freeze shows up again?
• What felt possible today that didn't yesterday?

---

**Deep Embodiment Practice for Your Soul-State**

**🌸 WOUNDED-NURTURER**

**Light Side Activation:** Your capacity to love is profound. Now we channel it toward yourself.

**Shadow Pattern:** You equate self-care with selfishness. Your nervous system believes: rest = abandonment of others.

**Personalized Micro-Action:**
• Do ONE thing today that feels indulgent, not productive (lie down for 10 minutes, light a candle just for you, drink tea slowly)
• Notice the guilt that arises - don't push it away
• Place hand on heart: *"I can rest and still be loving."*
• Let the guilt exist WITHOUT acting on it - just breathe through it

**Chakra Activation Work:**
Ground your heart energy into your root:
- Stand barefoot (or visualize roots from feet)
- Place hands on heart, feel the warmth
- Visualize green light (heart) flowing DOWN into red (root) at base of spine
- Say: *"My love includes me too. I am rooted in self-worth."*

**Integration:** Journal - *"What would it feel like to receive without earning it?"*

---

**🌑 ROOTED-WOUNDED**

**Light Side Activation:** You are incredibly strong. Now we integrate softness with that strength.

**Shadow Pattern:** Vulnerability feels like weakness. Your nervous system believes: opening up = everything falls apart.

**Personalized Micro-Action:**
• Text or tell ONE safe person: *"I've been struggling with ___. I just wanted to share."*
• You don't need them to fix it - just witness it
• Notice the discomfort of being seen as "not okay"
• Place hands on belly: *"I am safe to let my armor down."*
• Stay present with the vulnerability for 60 seconds

**Chakra Activation Work:**
Open your heart while staying rooted:
- Sit with feet flat on ground
- Place one hand on root (low belly), one on heart
- Breathe into heart space (expand on inhale)
- Say: *"I can be strong AND tender. Both are true."*

**Integration:** Journal - *"What becomes possible when I don't have to be strong all the time?"*

---

**🌊 AVOIDANT-ELEVATED**

**Light Side Activation:** Your awareness is a gift. Now we anchor it in your body.

**Shadow Pattern:** You escape into your head when emotions arise. Your nervous system believes: feeling = losing control.

**Personalized Micro-Action:**
• Place both hands on lower belly
• Say out loud ONE emotion you've been avoiding: *"I feel angry"* or *"I feel sad"* or *"I feel scared"*
• Don't analyze WHY - just name it and FEEL it
• Stay present in your body for 30-60 seconds
• Notice the urge to float away - gently come back to your belly, your feet
• Say: *"My body is safe to hold emotions."*

**Chakra Activation Work:**
Bring crown energy down into root:
- Sit with spine straight
- Visualize white/violet light at crown
- Breathe it down through your body into feet
- Feel the light grounding into earth
- Say: *"I am safe to be fully here, fully present, fully embodied."*

**Integration:** Journal - *"What emotion have I been avoiding, and what might it be trying to tell me?"*

---

**🌿 WOUNDED-ELEVATED**

**Light Side Activation:** You have spiritual wisdom. Now we integrate it with body healing.

**Shadow Pattern:** You use spiritual practice to bypass emotional pain. Your nervous system believes: transcending = healing (but the body still hurts).

**Personalized Micro-Action:**
• Sit or lie down - feel your full weight supported
• Place hands on the part of your body that holds the most pain or tension
• Say: *"I'm here with you. You're safe to be felt."*
• Breathe into that space for 2 minutes
• Don't try to fix or transcend - just witness
• Say: *"My body's pain is sacred. I don't have to rise above it to heal it."*

**Chakra Activation Work:**
Anchor elevated consciousness into root:
- Stand barefoot outside (or visualize)
- Feel spiritual connection above you
- Now feel earth beneath you
- Breathe: draw both energies into your heart
- Say: *"I belong here. Earth is my home too."*

**Integration:** Journal - *"What would change if I brought my spiritual awareness INTO my body's wounds instead of above them?"*

---

**🪨 ROOTED-AVOIDANT**

**Light Side Activation:** You are stable and grounded. Now we soften the edges.

**Shadow Pattern:** You protect through emotional distance. Your nervous system believes: opening = instability.

**Personalized Micro-Action:**
• Choose one safe person
• Share one small vulnerable thing (could be: *"I'm tired"* or *"I've been lonely"*)
• Don't minimize it or laugh it off
• Let it land - let them see you
• Notice the discomfort - breathe through it
• Say internally: *"Connection doesn't threaten my foundation."*

**Chakra Activation Work:**
Open heart while maintaining root stability:
- Stand with knees slightly bent (grounded)
- Place one hand on heart
- Breathe into heart space - let it expand
- Say: *"I can stay grounded AND open. Both are possible."*

**Integration:** Journal - *"What might I gain by letting one person see the real me?"*

---

**Embodiment Integration:**

1. Write down your new belief from Module 3
2. Complete your pattern's micro-action TODAY
3. Notice what arises - resistance, fear, relief, surprise
4. Journal about it

**Habit Stacking for Your Pattern:**

Link your affirmation to something you already do daily:
• Brushing teeth: Say your affirmation in the mirror
• Making coffee/tea: Say it while water boils
• Getting into bed: Say it with hand on heart

Consistency matters more than perfection. Even once a day rewires your nervous system over time."""  ,
            'action': 'One gentle, non-urgent movement: 30-second stretch, send one text, wash one dish, step outside for 60 seconds. Choose what feels possible today.',
            'is_free': False,
            'minutes': 20
        },
        {
            'step': 5,
            'title': 'Phase 2: Embodying - Tracking & Releasing Old Patterns',
            'purpose': 'Identify when old freeze patterns surface and redirect with compassion',
            'guru_message': """**Check-In:**
• How has your week been?
• What's been showing up for you since last time?
• One word describing your energy today?

**Grounding:**
Hand on heart, hand on belly. Inhale 4, hold 2, exhale 6 (twice). Roots to earth core. "I am safe. I am here. I am open."

---

**Phase 2: EMBODYING - Living the New Energy**

**🌊 RELEASE - Identifying and Tracking Old Patterns**

Resistance isn't failure - it's information. When you notice yourself pulling back or shutting down, pause.

Old patterns will still show up. That's normal. The power is that you now notice, interrupt, and return to your truth faster each time.""",
            'tools': 'Inner Dialogue,Grounding',
            'reflection': """**Pattern Recognition Questions:**
• When did freeze show up this week? What triggered it?
• What emotions signaled I was moving out of alignment? (guilt, overwhelm, numbness)
• What old habits or distractions stole my energy?
• Where did tension show up in my body when freeze appeared?
• What felt hard today, and why might that make sense?

---

**Deep Pattern Recognition: Your Soul-State's Signature Triggers**

**🌸 WOUNDED-NURTURER**

**Signature Freeze Triggers:**
1. After over-giving (saying yes automatically, taking on others' emotions)
2. When someone doesn't reciprocate your care
3. Saying yes when you meant no
4. Feeling unappreciated or taken for granted
5. Exhaustion from constant emotional labor

**Energetic Signature When Freeze Hits:**
• Heart space feels hollow or aching
• Sudden exhaustion or collapse
• Resentment simmering underneath care
• Throat closes (can't express needs)
• Sacral depleted (no pleasure, no boundaries)

**Your Early Warning System:**
Notice BEFORE total depletion:
- Do you check your own capacity before saying yes?
- Do you feel resentment building while you're helping?
- Are you giving from fullness or fear of rejection?

**Your PAUSE Method (Pattern Interrupt):**
- **P**ause: Before automatic yes, take 3 breaths
- **A**sk: *"Is this from love or fear of being unloved?"*
- **U**nder: Feel the discomfort in your body, don't act yet
- **S**ay: *"Let me check my capacity and get back to you"*
- **E**valuate: After 10 minutes, decide from groundedness

---

**🌑 ROOTED-WOUNDED**

**Signature Freeze Triggers:**
1. Pressure to "keep being strong" when you're breaking inside
2. Someone asks "How are you, really?" (threatens the armor)
3. Being alone with your thoughts after holding it together all day
4. Witnessing others' vulnerability (reminds you of your hidden pain)
5. Any situation requiring emotional expression

**Energetic Signature When Freeze Hits:**
• Jaw clenches, shoulders lock
• Emotional numbness or shutdown
• Chest tightens (heart protected)
• Mind goes blank or dissociates
• Body feels rigid, frozen in place

**Your Early Warning System:**
Notice when:
- Your body feels like stone
- You minimize your struggles with "I'm fine"
- Tears threaten but you swallow them back
- You're exhausted from holding the mask in place

**Your ARMOR-DOWN Method (Pattern Interrupt):**
- **A**cknowledge: *"I'm shutting down to protect myself"*
- **R**emember: *"I don't have to be strong right now"*
- **M**ove: Gentle movement (shoulder rolls, neck stretches)
- **O**pen: One hand on heart, breathe into the armor
- **R**eveal: Say ONE true thing out loud, even if just to yourself

---

**🌊 AVOIDANT-ELEVATED**

**Signature Freeze Triggers:**
1. Conflict or confrontation
2. Someone expressing big emotions near you
3. Pressure to "go deep" emotionally
4. Intimacy that requires staying present in your body
5. Any situation where you can't intellectualize your way out

**Energetic Signature When Freeze Hits:**
• Floating sensation, feeling ungrounded
• Disconnection from body (numb, can't feel)
• Mind races or goes completely blank
• Urge to escape, leave, or retreat
• Crown/third eye active, but root nonexistent

**Your Early Warning System:**
Notice when:
- You start analyzing instead of feeling
- You feel the urge to be alone immediately
- Your body feels far away or foreign
- You're "in your head" narrating instead of experiencing

**Your GROUND Method (Pattern Interrupt):**
- **G**et physical: Touch something textured, feet on floor
- **R**eturn to breath: 5-4-3-2-1 sensory grounding
- **O**bserve: *"I'm leaving my body to avoid feeling"*
- **U**nder: Place hands on lower belly, breathe there
- **N**ame: Say the emotion out loud: *"I'm feeling ___"*
- **D**ecide: *"I can stay present for 60 more seconds"*

---

**🌿 WOUNDED-ELEVATED**

**Signature Freeze Triggers:**
1. Body pain or physical discomfort you can't spiritualize away
2. Being asked to stay grounded when you want to transcend
3. Earthly responsibilities that feel too heavy
4. Relationships requiring embodied presence
5. Any reminder that healing requires being IN your body

**Energetic Signature When Freeze Hits:**
• Dissociation or out-of-body feeling
• Spiritual bypassing ("everything is love and light")
• Physical pain intensifies
• Longing to "go home" (escape earth)
• Crown hyperactive, root collapsed

**Your Early Warning System:**
Notice when:
- You're using spiritual language to avoid real feelings
- Your body hurts but you're ignoring it
- You feel like you don't belong on earth
- You're escaping into meditation instead of feeling

**Your ANCHOR Method (Pattern Interrupt):**
- **A**cknowledge: *"I'm trying to transcend instead of heal"*
- **N**otice: Where in body is pain/tension right now?
- **C**ome down: Visualize energy moving from crown to root
- **H**old: Place hands on painful/tense area
- **O**pen: *"My body is part of my healing, not the enemy"*
- **R**oot: Feel feet, sit bones, earth beneath you

---

**🪨 ROOTED-AVOIDANT**

**Signature Freeze Triggers:**
1. Someone getting "too close" emotionally
2. Being asked to express feelings
3. Situations requiring emotional vulnerability
4. When stability feels threatened by intimacy
5. Any request to "open up" or "share more"

**Energetic Signature When Freeze Hits:**
• Emotional numbness or flatness
• Walls up, defenses activated
• Body present but heart unavailable
• Practical mode (task focus to avoid feeling)
• Urge to withdraw or isolate

**Your Early Warning System:**
Notice when:
- You say "I'm fine" but feel nothing
- You become busy to avoid conversation
- Someone's vulnerability makes you uncomfortable
- You feel the urge to leave or shut down

**Your SOFTEN Method (Pattern Interrupt):**
- **S**top: Pause the automatic withdrawal
- **O**bserve: *"I'm protecting myself through distance"*
- **F**eel: One hand on heart - what's there?
- **T**ry: Stay present for 30 seconds longer than comfortable
- **E**xpress: Say ONE feeling word (even "uncomfortable")
- **N**otice: Connection didn't destroy your stability

---

**Pattern Tracker Exercise**

For each freeze moment this week, track:

| **Situation** | **Trigger** (use your signature above) | **Body Sensation** | **My Reaction** | **Outcome** | **New Choice Next Time** |
|---------------|---------------------------------------|-------------------|-----------------|-------------|-------------------------|
| Example: Friend asked for help | Automatic yes (Wounded-Nurturer) | Throat closed, chest tight | Said yes, felt resentful | Exhausted, resentful | Use PAUSE method |

**Daily Pattern Interrupt Practice:**

When you catch freeze starting:
1. Name it: *"I'm noticing my [your pattern] freeze starting"*
2. Use YOUR method (PAUSE, ARMOR-DOWN, GROUND, ANCHOR, or SOFTEN)
3. Choose differently - even 1% different counts
4. Journal: What happened? How did it feel?

Write: What's your most common trigger this week? What new choice will you practice?"""  ,
            'action': '''Rewrite one harsh inner message with kindness. Example: "I'm so lazy" becomes "I'm protecting myself from something that feels overwhelming." Keep your pattern tracker this week.''',
            'is_free': False,
            'minutes': 30
        },
        {
            'step': 6,
            'title': 'Phase 2-3: Embodying to Aligning - Rising Into Choice',
            'purpose': 'Practice embodying new identity and aligning daily actions with it',
            'guru_message': """**Check-In:**
• How has your week been?
• What's been showing up for you?
• One word for your energy today?

**Grounding:**
Eyes closed. Heart and belly. Inhale 4, hold 2, exhale 6 (twice). Roots to earth. "I am safe. I am here. I am open."

---

**🔥 RISE - Living as the New Version**

You get to choose differently, even in small ways. Freeze often comes from feeling like there's no choice. Today, we practice noticing where choice still lives.

This is where you consciously step into the new version of yourself - the one who has agency, who moves at their own pace, who honors their nervous system while also taking aligned action.""",
            'tools': 'Visualization,Grounding',
            'reflection': """**Embodiment Questions:**
• What is one choice I made this week that reflects my new energy?
• What daily practice or ritual helps me root into this version of me?
• Where do I still feel pulled back into freeze?
• How do I redirect myself gently when that happens?
• What choice feels aligned right now - even if it's tiny?
• If I trusted this version of me fully, what would I do differently?

---

**Living as Your New Self: Deep Identity Work**

**🌸 WOUNDED-NURTURER → HEALED-NURTURER**

**OLD IDENTITY (Freeze State):**
✗ Love = constant availability and depletion
✗ Worth = measured by usefulness to others
✗ Rest = selfishness or laziness
✗ No = rejection or abandonment
✗ Receiving = being a burden

**NEW IDENTITY (Aligned State):**
✓ Love = presence from fullness, not obligation
✓ Worth = inherent, not earned through service
✓ Rest = sacred responsibility to myself
✓ No = honoring my truth and capacity
✓ Receiving = allowing love to flow both ways

**How the New You Lives:**
• Says no without guilt or over-explaining
• Checks capacity BEFORE offering help: *"Do I actually have space for this?"*
• Takes breaks without apologizing
• Asks for support when needed
• Receives care without immediately reciprocating

**When Old Pattern Whispers:** *"You're being selfish"*
**You Respond:** *"I'm being sustainable. I give from overflow now, not depletion."*

**Embodiment Practice:**
Stand with hand on heart. Say: *"I am the Healed-Nurturer. I give from overflow, not obligation. My presence is the gift, not my exhaustion."*

Repeat daily looking in mirror. Let it sink into your nervous system.

---

**🌑 ROOTED-WOUNDED → ROOTED-HEALED**

**OLD IDENTITY (Freeze State):**
✗ Strength = never showing weakness or need
✗ Safety = holding everything together alone
✗ Vulnerability = danger or collapse
✗ Emotions = distractions from survival
✗ Support = weakness or failure

**NEW IDENTITY (Aligned State):**
✓ Strength = includes softness and flexibility
✓ Safety = being supported by others too
✓ Vulnerability = connection and authenticity
✓ Emotions = valuable information and wisdom
✓ Support = wisdom in interdependence

**How the New You Lives:**
• Lets armor down with safe people
• Shares one vulnerable thing per week ("I'm struggling" / "I need help")
• Says "I'm not okay" when that's true
• Allows others to see underneath the strong exterior
• Rests without calling it "giving up"

**When Old Pattern Whispers:** *"Be strong, hold it together"*
**You Respond:** *"Strength includes softness. I can be both capable AND human. Both are true."*

**Embodiment Practice:**
Sit with one hand on heart, one on belly. Say: *"I am the Rooted-Healed. I am strong enough to be soft. I share the weight with safe others."*

---

**🌊 AVOIDANT-ELEVATED → GROUNDED-ELEVATED**

**OLD IDENTITY (Freeze State):**
✗ Safety = staying in my head, avoiding feelings
✗ Emotions = overwhelming or dangerous
✗ Body = something to escape from
✗ Intimacy = losing myself or being consumed
✗ Presence = vulnerability I can't handle

**NEW IDENTITY (Aligned State):**
✓ Safety = staying present in my body AND emotions
✓ Emotions = information that flows through me
✓ Body = sacred home for my consciousness
✓ Intimacy = connection while staying grounded
✓ Presence = strength and awareness

**How the New You Lives:**
• Stays present during emotional moments (yours and others')
• Notices urge to disconnect, breathes through it
• Says "I need a moment" instead of disappearing entirely
• Names emotions out loud instead of analyzing them away
• Chooses grounding before floating away

**When Old Pattern Whispers:** *"Retreat, this is too much"*
**You Respond:** *"I can handle feeling this. My body is safe to hold emotions. I stay present."*

**Embodiment Practice:**
Stand barefoot. Hands on lower belly. Say: *"I am Grounded-Elevated. My awareness lives IN my body. I am safe to feel everything."*

---

**🌿 WOUNDED-ELEVATED → HEALED-ELEVATED**

**OLD IDENTITY (Freeze State):**
✗ Healing = transcending the body and pain
✗ Earth = temporary, not my true home
✗ Emotions = to be spiritualized or bypassed
✗ Body = burden or obstacle to enlightenment
✗ Presence = heavy and painful

**NEW IDENTITY (Aligned State):**
✓ Healing = integrating body, heart, AND spirit
✓ Earth = sacred home, part of my divinity
✓ Emotions = gateways to deeper healing
✓ Body = temple that holds my consciousness
✓ Presence = gift of embodied awareness

**How the New You Lives:**
• Brings spiritual awareness INTO body wounds, not above them
• Stays grounded while maintaining spiritual connection
• Honors physical pain as sacred information
• Practices embodiment as spiritual practice
• Belongs here on earth, not always longing elsewhere

**When Old Pattern Whispers:** *"Rise above it, transcend the pain"*
**You Respond:** *"I heal BY being here, not by leaving. My body is part of my divinity."*

**Embodiment Practice:**
Sit in meditation. Feel crown and root simultaneously. Say: *"I am Healed-Elevated. Heaven and earth meet in my body. I belong here."*

---

**🪨 ROOTED-AVOIDANT → ROOTED-OPEN**

**OLD IDENTITY (Freeze State):**
✗ Safety = emotional distance and walls
✗ Connection = threat to stability
✗ Vulnerability = loss of control
✗ Opening up = instability or danger
✗ Independence = only way to stay secure

**NEW IDENTITY (Aligned State):**
✓ Safety = grounded stability WITH open heart
✓ Connection = enhances life without threatening foundation
✓ Vulnerability = strength in small doses
✓ Opening up = deepening roots while expanding branches
✓ Interdependence = security through authentic connection

**How the New You Lives:**
• Opens heart in small, safe ways
• Shares feelings without losing grounding
• Lets one person in at a time
• Stays present in conversation instead of shutting down
• Asks for support without feeling weak

**When Old Pattern Whispers:** *"Close off, protect yourself"*
**You Respond:** *"I can stay grounded AND open. Connection doesn't threaten my stability."*

**Embodiment Practice:**
Stand rooted. Hand on heart. Say: *"I am Rooted-Open. I have deep roots AND an open heart. Both are possible."*

---

**Identity Anchoring Exercise:**

Write 5-7 statements as your NEW self:
"As the [new identity], I..."

Examples:
- "As the Healed-Nurturer, I give from fullness, not fear."
- "As Rooted-Healed, I share my struggles with safe people."
- "As Grounded-Elevated, I stay present in my body when emotions arise."

Make them specific to YOUR pattern and YOUR life.

---

**Future-Self Visualization:**

Close your eyes. See yourself living ONE full day as this new identity:

• How do you wake up? (with what energy?)
• How do you move through your day? (with what presence?)
• How do you respond when freeze starts? (with what tools?)
• How do you interact with others? (with what boundaries?)
• How do you end your day? (with what peace?)

Notice:
- How you walk
- How you speak  
- How you breathe
- The expression on your face
- The lightness or groundedness in your body

**Choose ONE anchor word** that captures this version of you:
(Examples: Gentle. Grounded. Open. Present. Whole. Free. Rooted.)

Write it down. Use it as your cue this week: when you notice freeze, say your word and embody that energy for 30 seconds."""  ,
            'action': 'One conscious yes or no today. Say yes to something nourishing. Say no to something draining. Notice how it feels to exercise choice, even in small ways.',
            'is_free': False,
            'minutes': 25
        },
        {
            'step': 7,
            'title': 'Phase 4: Expanding - Integration & Living Your Bigger Vision',
            'purpose': 'Integrate all learnings and expand into your fuller expression',
            'guru_message': """**Check-In:**
• How has your week been?
• What's been showing up for you?
• One word that describes your energy today?

**Grounding:**
Hand on heart, hand on belly. Inhale 4, hold 2, exhale 6 (twice). Roots deep into earth. "I am safe. I am here. I am open."

---

**Phase 4: EXPANDING - Living the Larger Vision**

**🔮 REFLECT & 🔥 RISE - Integration**

You've walked through this with such care. Notice what's changed - even subtly.

Freeze may still show up sometimes. But now you have a way to work with it. Now you expand into the fuller version of yourself - the one who can hold both rest and action, both pause and movement.""",
            'tools': 'Gentle Review,Reflection',
            'reflection': """**Integration Reflection:**
• What feels more available in me now than when I started?
• What do I want to remember about this journey?
• What parts of my vision for myself feel most alive right now?
• Where have I already surprised myself by embodying more than I thought possible?
• How has my relationship with freeze transformed?
• What is my next edge to rise into?

**Your Soul-State Transformation - Deep Celebration:**

**🌸 WOUNDED-NURTURER → HEALED-NURTURER**

**Where You Started (Freeze State):**
- Froze when depleted from over-giving
- Said yes automatically, felt resentful later
- Believed worth = usefulness to others
- Couldn't receive without guilt
- Rest felt like selfishness

**What You've Healed:**
- Recognized your pattern without shame
- Said no and survived the discomfort
- Received care without immediately reciprocating
- Rested without earning it first
- Gave from choice, not fear

**Your New Energetic Signature (Healed-Nurturer):**
✦ Heart chakra: Open but boundaried, giving from overflow
✦ Root chakra: Secure in worthiness independent of service
✦ Throat chakra: Speaks needs and limits with love
✦ Sacral chakra: Pleasure and self-care prioritized

**Light Side Fully Activated:**
You nurture others beautifully - AND you nurture yourself. Your love is sustainable now. You give from fullness.

**Integration Mantra:** *"I am the Healed-Nurturer. My worth is inherent. I give from overflow, receive with grace, and rest as sacred practice."*

**Your Next Edge:** Deepen self-prioritization. Practice joy for yourself, not just others. Keep checking: Am I giving from fullness or fear?

---

**🌑 ROOTED-WOUNDED → ROOTED-HEALED**

**Where You Started (Freeze State):**
- Froze when armor got too heavy to hold
- Appeared strong, hid pain underneath
- Dismissed vulnerability as weakness
- Carried everything alone
- Emotions stayed locked away

**What You've Healed:**
- Let safe people see underneath the strength
- Shared struggles without everything falling apart
- Said "I'm not okay" and were still loved
- Discovered softness doesn't equal collapse
- Let others carry some of the weight

**Your New Energetic Signature (Rooted-Healed):**
✦ Root chakra: Deeply stable, grounded in self
✦ Heart chakra: Open, able to give and receive
✦ Sacral chakra: Emotions flow, not suppressed
✦ Throat chakra: Speaks truth, including pain

**Light Side Fully Activated:**
You are strong AND tender. Capable AND human. Your stability includes flexibility now.

**Integration Mantra:** *"I am Rooted-Healed. I am strong enough to be soft. My vulnerability is my connection. I share the weight."*

**Your Next Edge:** Deepen emotional intimacy with safe people. Practice being held, not just holding. Trust that softness strengthens you.

---

**🌊 AVOIDANT-ELEVATED → GROUNDED-ELEVATED**

**Where You Started (Freeze State):**
- Froze by leaving your body, floating away
- Retreated into head when emotions arose
- Analyzed feelings instead of feeling them
- Spiritually aware but physically disconnected
- Intimacy felt threatening

**What You've Healed:**
- Stayed present in body when emotions showed up
- Named feelings out loud without analyzing
- Noticed urge to escape, chose to stay
- Grounded spiritual awareness into physical form
- Connected with others while staying embodied

**Your New Energetic Signature (Grounded-Elevated):**
✦ Root chakra: Grounded, present, anchored in body
✦ Crown/Third Eye: Spiritually aware, intuitive
✦ Heart chakra: Open without feeling overwhelmed
✦ Whole system: Heaven and earth integrated

**Light Side Fully Activated:**
You're spiritually aware AND fully embodied. Your wisdom lives in your body now. You feel everything without losing yourself.

**Integration Mantra:** *"I am Grounded-Elevated. My consciousness lives in my body. I feel deeply and stay present. I am safe here."*

**Your Next Edge:** Deepen emotional intimacy in small doses. Practice staying present longer in vulnerable moments. Trust your body to hold it all.

---

**🌿 WOUNDED-ELEVATED → HEALED-ELEVATED**

**Where You Started (Freeze State):**
- Froze by spiritually bypassing body pain
- Used transcendence to escape healing
- Felt like earth wasn't your true home
- Body held wounds you wouldn't touch
- Spiritual but not embodied

**What You've Healed:**
- Brought spiritual awareness INTO body wounds
- Honored physical pain as sacred information
- Grounded elevated consciousness in earthly form
- Practiced embodiment as spiritual work
- Chose to belong here, on earth

**Your New Energetic Signature (Healed-Elevated):**
✦ Root chakra: Grounded in earth, belonging here
✦ Crown chakra: Spiritually connected, wise
✦ Heart chakra: Integrated spirit and matter
✦ Whole system: Divine embodiment, heaven on earth

**Light Side Fully Activated:**
You bridge heaven and earth in your body. Your spiritual wisdom includes your humanity. You are holy AND whole.

**Integration Mantra:** *"I am Healed-Elevated. My body is my temple. Heaven and earth meet in me. I belong here."*

**Your Next Edge:** Continue deepening embodiment practices. Let earth be home. Trust that healing happens HERE, not elsewhere.

---

**🪨 ROOTED-AVOIDANT → ROOTED-OPEN**

**Where You Started (Freeze State):**
- Froze by shutting down emotionally
- Protected through distance and walls
- Stable but emotionally unavailable
- Independence felt safer than connection
- Vulnerability threatened your foundation

**What You've Healed:**
- Opened heart in small, safe ways
- Shared feelings without losing stability
- Let one person see the real you
- Stayed present in emotional conversations
- Discovered connection enhances security

**Your New Energetic Signature (Rooted-Open):**
✦ Root chakra: Deeply stable, unshakeable foundation
✦ Heart chakra: Open, warm, connected
✦ Throat chakra: Expresses emotions honestly
✦ Whole system: Grounded stability with open heart

**Light Side Fully Activated:**
You are stable AND open. Grounded AND connected. Your strength includes tenderness now.

**Integration Mantra:** *"I am Rooted-Open. I have deep roots and an open heart. Connection strengthens my foundation."*

**Your Next Edge:** Continue opening in safe relationships. Practice receiving support. Trust that intimacy doesn't threaten your stability.

---

**Wins List:**
Write every shift, big or small, that happened through this journey. Include moments when you caught your pattern early, made a different choice, or surprised yourself.

**Legacy Prompt:**
If freeze shows up again, what will you want to remember? Write a compassionate note to your future self. Include:
• What you now know about your pattern
• The tools that work for YOUR nervous system
• Permission to be exactly where you are
• Reminder that freeze is information, not failure

**Expansion Questions:**
• What practices keep me stable as I step into a bigger life beyond freeze?
• What values do I refuse to compromise on as I expand?
• If my expanded self were mentoring me, what advice would they give?

Write your integration insights and your note to your future self.""",
            'action': '''Write your compassionate note to future self for next time freeze shows up. Create one daily ritual that keeps you rooted in your new truth. Celebrate how far you've come - you've done beautiful work.''',
            'is_free': False,
            'minutes': 30
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

def seed_inner_bully_path():
    """Seed the 'Healing The Inner Bully' path using the 4 R Framework"""
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    
    # Check if path already exists
    c.execute("SELECT id FROM paths WHERE slug = 'inner-bully'")
    if c.fetchone():
        conn.close()
        return  # Already seeded
    
    # Insert path
    c.execute("""INSERT INTO paths (title, slug, description, summary, icon, duration, is_active)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              ('Healing The Inner Bully',
               'inner-bully',
               "Transform your inner critic from bully to compassionate guide. Learn to observe, understand, and gently reshape the harsh voice within using the 4 R Framework: Root, Release, Reflect, Rise.",
               'Transform self-criticism into self-compassion',
               '🌼',
               '7 sessions',
               1))
    
    path_id = c.lastrowid
    
    # Insert Module 1
    modules = [
        {
            'step': 1,
            'title': 'Meeting the Inner Bully',
            'purpose': 'Gently observing your inner voice without judgment',
            'guru_message': """**Check-In Questions:**
• How has your week been?
• What's been showing up for you?
• What's one word that describes your energy today?

**Grounding Exercise (2-3 minutes):**
Close your eyes. Place one hand on your heart, one on your belly. Inhale for 4, hold for 2, exhale for 6. Repeat twice. Visualize roots growing down into the earth. Affirm: "I am safe. I am here. I am open to what I need today."

---

**🌼 WELCOME**

Welcome to Module 1.

This week, we begin by slowing down and gently meeting a part of ourselves that often goes unnoticed: our inner voice.

Some call it the inner critic, others the ego, the overachiever, the perfectionist... But in this space, we'll meet it as the **Inner Bully** — not with shame, but with curiosity and compassion.

Before we try to heal or shift anything, we first learn to observe. No fixing. No fighting. No judgment. Just noticing. Just listening.

---

**🌊 Why Do We Have an Inner Voice?**

Your inner voice is that quiet (or sometimes loud) stream of thoughts running through your mind all day.

It developed to:
• Keep you safe
• Make sense of the world
• Help you navigate relationships, work, goals

It was shaped by:
• Childhood experiences
• Parents, teachers, caregivers
• Cultural messages and social norms
• Emotional moments of fear, rejection, or pressure

Sometimes this voice is helpful. But sometimes, it turns harsh — and that's when it becomes an inner bully.

---

**🌘 Why Does It Get So Loud or So Mean?**

The inner bully isn't evil — it's scared.

It shows up when we:
• Feel vulnerable or exposed
• Are about to grow, stretch, or shine
• Get triggered by old memories or self-doubt
• Are tired, overwhelmed, or disconnected from our truth

Its job is to protect you — but the way it does that isn't loving. It learned to use fear, shame, control, and criticism... because that's what it saw or experienced.

---

**🔍 This Week's Practice: Observation Without Judgment**

Your only job this week is to notice.""",
            'tools': 'Body Scan,Inner Dialogue',
            'reflection': """**✧ Step 1: Hear the Voice**

Start listening for:
• **Criticism:** "Why did you say that?" "You're not good enough."
• **Fear:** "You'll mess it up." "Don't even try."
• **Control:** "You should be better by now." "No one else thinks that way."

💡 Every time you catch it, pause and say: "That's the inner bully. I'm just observing."

---

**✧ Step 2: Notice the Pattern**

Ask yourself:
• When does this voice show up?
• What triggers it — stress, tiredness, rejection?
• How does it make me feel in my body?

---

**✧ Step 3: Name the Voice**

Give it a name, tone, or image.
• Is it a worried teacher? A strict parent? A scared child?
• Does it sound like someone you used to know?

This helps you separate from it. **You are not the bully. You are the one who hears it.**

---

**🧘🏽‍♀️ Gentle Journal Prompts**

You can write or speak these aloud each day:
• What did my inner voice say today?
• How did I feel when I heard it?
• What was I doing or thinking when it showed up?
• Does this voice remind me of someone or somewhere?
• What would I say to this part of me if I knew it was just scared?

---

**🌱 Integration: A Loving Reminder**

You are not broken. You are growing.

The inner bully is not your truth — it's an old voice trying to protect you in a way that no longer serves.

This week, you are learning to listen differently. Not to believe the bully, but to hear it, witness it, and gently reclaim your power.""",
            'action': 'Track your inner bully this week. Each day, write down: one thing it said, when it showed up, and how you felt. Remember: observation without judgment. You\'re building awareness, not fixing anything yet.',
            'is_free': True,
            'minutes': 20
        },
        {
            'step': 2,
            'title': 'The Roots of the Bully - Where Did This Voice Come From?',
            'purpose': 'Understand the origin of the inner bully with compassion',
            'guru_message': """**Check-In Questions:**
• How has your week been?
• What's been showing up for you since last session?
• What's one word that describes your energy today?

**Grounding Exercise (2-3 minutes):**
Close your eyes. One hand on heart, one on belly. Inhale 4, hold 2, exhale 6 (repeat twice). Visualize roots growing down into the earth. Affirm: "I am safe. I am here. I am open to what I need today."

---

**🌿 WELCOME BACK**

Before we can shift the inner bully, we need to understand it.

Not with blame. Not with shame. But with curiosity. With softness. With compassion.

**🫧 This is gentle work.**

As you explore this module, please be kind to your nervous system:
• Drink lots of water
• Get fresh air if you can
• Take breaks when you need to
• Rest if something feels heavy
• Let things come up in their own time

You're not behind. You're right on time.

---

**🪞 This Week: Looking at Where the Inner Bully Began**

The voice that says "you're not enough," or "you're too much" — it didn't start with you.

It was shaped by:
• What you were told
• What you weren't told
• What you felt but didn't have words for
• The moments you didn't feel seen, loved, or safe

It often comes from a time when your nervous system learned:
*"If I just get it right... maybe I'll be safe. Maybe I'll belong."*

---

**✨ Ask Yourself: Whose Voice Does This Sound Like?**

• A parent?
• A teacher?
• Someone who wanted the best for you... but didn't know how to say it kindly?
• A sibling? A coach? A boss?
• Society's voice telling you who you should be?

The voice might sound familiar. But it is not you.

It's a pattern. A memory. A form of protection that stayed too long.""",
            'tools': 'Grounding,Visualization',
            'reflection': """**🌀 The Voice Map Exercise**

Take out your journal and reflect:
• What's the first memory I have of self-criticism?
• What moment taught me to shrink, to hide, or to hustle for love?
• What did I learn about "success," "being good," or "being lovable"?
• What beliefs did I carry forward that weren't mine to hold?

You can write, draw, or even create a timeline. The goal is to see the thread — so you can choose what stays, and what ends here.

---

**💬 What We're Practicing This Week:**
🌱 Compassionate understanding
🕊️ Gentle truth-telling
🖋️ Tracking the story so it no longer runs the show

---

**✍🏽 Deeper Journal Prompts:**
• Whose voice is this really?
• What was this voice trying to protect me from?
• What did I believe about myself after hearing it?
• Is that belief true now?
• What would I say to the younger version of me who first believed it?

---

**🌟 This Week's Mantra:**
*"This voice was trying to protect me. I choose to listen with compassion, not fear."*

---

**💌 Optional Bonus Practice:**

Write a letter to your inner bully's origin. To the person or moment that shaped it.

You don't have to send it. Just let it out — truthfully, safely, freely.

And most importantly: This is a week for gentleness. Let softness be your strength. Let rest be your medicine. You are allowed to heal in ways that feel good.

---

**🌼 Identifying Your Inner Bully Archetype**

Your inner bully may sound like:

**💼 The Strict Teacher**
"You should've done better." Harsh, perfectionistic, driven by pressure.

**🧒🏽 The Scared Child**
"What if something goes wrong?" Fearful, worried, trying to keep you small to stay safe.

**🪞 The Perfectionist**
"It's not ready yet." Chasing impossible standards, scared of being seen.

**🛡️ The Protector**
"You'll only get hurt." Defensive, cautious, keeping walls up.

**😞 The Shamer**
"You're not good enough." Cruel, mocking, rooted in old pain or rejection.

You might hear one of these loud and clear. You might hear a mix — depending on the day, your energy, or where you're growing.

Which archetype(s) resonate with you? Write it down. In the premium modules, you'll receive personalized tools for working with YOUR specific inner bully pattern.""",
            'action': 'Complete "The Voice Map" exercise this week. Trace back one belief the inner bully holds about you to its origin. Write a short letter (that you won\'t send) to the person/moment where this voice began. Remember: gentleness first.',
            'is_free': True,
            'minutes': 25
        },
        {
            'step': 3,
            'title': 'Creating Safety - Regulating the Nervous System',
            'purpose': 'Create safety in the body before changing the voice',
            'guru_message': """**Check-In Questions:**
• How has your week been?
• What's been showing up for you?
• What's one word that describes your energy today?

**Grounding Exercise (2-3 minutes):**
Close your eyes. Hand on heart, hand on belly. Inhale 4, hold 2, exhale 6 (repeat twice). Roots to earth. "I am safe. I am here. I am open."

---

**🌱 ROOT - Creating Safety First**

Before we change the voice, we create safety in the body.

The inner bully gets louder when the nervous system is overwhelmed. Healing doesn't work when you're in fight/flight/freeze. We must settle first.

**You don't need to fix yourself — you need to feel safe.**

---

**Understanding Your Nervous System**

Your body has three main states:

**🟢 Ventral Vagal (Safe & Social)**
You feel calm, connected, able to think clearly. This is where healing happens.

**🟡 Sympathetic (Fight or Flight)**
Heart racing, restless, anxious, overthinking. The inner bully gets LOUD here.

**🔴 Dorsal Vagal (Freeze/Shutdown)**
Numb, disconnected, exhausted, "can't even." The bully becomes a heavy fog.

Self-criticism spikes during stress because your nervous system thinks you're in danger. The bully is trying to control an uncontrollable situation.

**The truth:** Safety comes first. Then the voice softens.""",
            'tools': 'Grounding,Box Breathing,Butterfly Hug',
            'reflection': """**Identifying Your Personal Signs of Overwhelm**

Ask yourself:
• When does my inner bully get loudest?
• What does overwhelm feel like in MY body? (racing heart, tight chest, foggy brain, etc.)
• What signs tell me I'm moving out of my safe zone?

**Creating Your "Safe Anchor" Practice**

Choose 3 grounding tools that work for YOU:

**Simple Grounding Tools:**
• **Feet on floor:** Feel the ground beneath you. Press down.
• **5-4-3-2-1:** Name 5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste.
• **Cold water:** Splash face, hold ice, drink slowly.
• **Butterfly Hug:** Cross arms, tap shoulders alternately.
• **Box Breathing:** Inhale 4, hold 4, exhale 4, hold 4.
• **Safe touch:** Hand on heart, hand on belly. Feel your own presence.

Write down:
• My top 3 grounding tools are...
• I know I need to ground when I notice...
• My safe anchor phrase is... (e.g., "I am here. I am safe. I can handle this.")

**Practice This Week:**
Use your grounding tools BEFORE responding to the inner bully. Notice what shifts when you settle your body first.""",
            'action': 'Practice grounding 3 times this week when you notice the inner bully getting loud. Don\'t try to change the voice yet — just notice how it shifts when your nervous system feels safer. Journal: "When I grounded first, I noticed..."',
            'is_free': False,
            'minutes': 20
        },
        {
            'step': 4,
            'title': 'Reparenting the Inner World - Meeting the Voice with Compassion',
            'purpose': 'Learn to respond to the inner bully differently',
            'guru_message': """**Check-In Questions:**
• How has your week been?
• What's been showing up for you?
• What's one word that describes your energy today?

**Grounding Exercise:**
Close eyes. Hand on heart, hand on belly. Inhale 4, hold 2, exhale 6 (twice). Roots to earth. "I am safe. I am here. I am open."

---

**🌸 RELEASE & REFLECT - Reparenting Your Inner World**

This is where transformation really begins — not by silencing the voice, but by meeting it with care.

**You become the safe adult your inner world always needed.**

---

**The Difference Between Reacting and Responding**

**Reacting to the bully:**
• Believing it ("You're right, I AM terrible")
• Fighting it ("Shut up! You're wrong!")
• Ignoring it (pushing it down, pretending it's not there)

**Responding to the bully:**
• Acknowledging it ("I hear you")
• Questioning it gently ("Is that really true?")
• Meeting it with compassion ("I know you're scared. We're okay.")

The goal isn't to make the voice disappear. It's to change your relationship with it.

---

**How to Speak to Yourself as You Would a Child You Love**

When the inner bully says:
❌ "You're so stupid. Why can't you get this right?"

Reparenting response:
✅ "Hey, that's really harsh. You're learning. It's okay to make mistakes. I've got you."

When the inner bully says:
❌ "You're going to fail. Don't even try."

Reparenting response:
✅ "I know you're scared. That makes sense. But we're going to try anyway, and I'll be here no matter what happens."

**Introducing Compassion Without Bypassing Truth**

Compassion doesn't mean pretending everything is fine. It means holding both truth AND kindness.

Example:
"Yes, I made a mistake today. That's true. AND I'm still learning. AND I'm doing my best. AND one mistake doesn't define me."

You can acknowledge reality while still being gentle.""",
            'tools': 'Inner Dialogue,Grounding',
            'reflection': """**Compassionate Inner Dialogue Practice**

This week, practice catching the bully and responding differently:

**Step 1:** Notice the harsh voice.
**Step 2:** Pause. Take 3 grounding breaths.
**Step 3:** Ask: "Would I say this to a child I love?"
**Step 4:** Rephrase with compassion.

**Reparenting Phrases to Practice:**

When you're struggling:
• "You're doing your best, and that's enough."
• "It's okay to find this hard. It IS hard."
• "I'm proud of you for trying."

When you make a mistake:
• "Mistakes are how we learn. You're safe with me."
• "One moment doesn't define you."
• "Let's try again, together."

When you're scared:
• "I know this feels scary. I'm here with you."
• "We can take this one step at a time."
• "You don't have to be brave alone."

**Holding Boundaries with Kindness:**

Sometimes the bully needs a gentle but firm boundary:

"I hear you, but I'm not going to let you speak to me that way anymore. I'm learning to be kinder to myself."

**Journal Prompts:**
• What did the inner bully say this week?
• How did I respond with compassion?
• What felt hard about being kind to myself?
• What would the younger version of me need to hear right now?""",
            'action': 'Practice reparenting dialogue 5 times this week. Each time the inner bully speaks, pause, ground, and respond as you would to a scared child. Write down: "The bully said ___, I responded with ___."',
            'is_free': False,
            'minutes': 25
        },
        {
            'step': 5,
            'title': 'Rewriting the Story - Beliefs, Truth & Choice',
            'purpose': 'Separate old beliefs from present truth',
            'guru_message': """**Check-In Questions:**
• How has your week been?
• What's been showing up for you?
• What's one word that describes your energy today?

**Grounding Exercise:**
Close eyes. Hand on heart, hand on belly. Inhale 4, hold 2, exhale 6 (twice). Roots to earth. "I am safe. I am here. I am open."

---

**🔥 RISE - Rewriting Your Story**

The inner bully feeds on outdated beliefs. This module gently dismantles them and replaces them with lived truth.

**You are allowed to update your story.**

---

**Identifying Core Limiting Beliefs**

The inner bully often repeats the same core beliefs:

Common ones include:
• "I'm not good enough"
• "I have to be perfect to be loved"
• "I can't trust myself"
• "If I rest, I'm lazy"
• "My needs don't matter"
• "I have to prove my worth"
• "I'm too much / not enough"

**Ask yourself:**
What belief does MY inner bully repeat most?

---

**Questioning What is Inherited vs. Chosen**

Many beliefs aren't yours — they were handed down.

**Belief Inquiry:**

1. What is the belief?
   Example: "I have to be perfect to be loved."

2. Where did this come from?
   Example: "My parent only praised me when I succeeded."

3. Is this belief actually TRUE?
   Example: "No. I've been loved even when I wasn't perfect."

4. What EVIDENCE contradicts this belief?
   Example: "My friend loves me even when I mess up. My partner supports me on hard days."

5. What would I rather believe?
   Example: "I am lovable as I am, including my imperfections."

6. What small action can I take to practice this new belief?
   Example: "I'll share something vulnerable with someone safe and notice that I'm still loved."

---

**Learning to Update Beliefs Without Force**

You can't force yourself to believe something new overnight. But you CAN:
• Notice when the old belief shows up
• Question it gently
• Look for evidence of the new belief
• Practice acting AS IF the new belief is true

Over time, the new belief becomes lived experience.""",
            'tools': 'Inner Dialogue,Reflection',
            'reflection': """**Truth vs. Training Exercise**

For each limiting belief, ask:

**Is this TRUTH or TRAINING?**

**Training:** Something I learned, was told, or absorbed from my environment.
**Truth:** What is actually real, now, in this present moment.

Example:
• **Training:** "I'm not smart enough."
• **Truth:** "I've learned new things throughout my life. I'm capable of growth."

**Choose Your New Internal Language**

Old language: "I'm so stupid."
New language: "I'm learning. It's okay not to know everything."

Old language: "I always mess up."
New language: "I've made mistakes, and I've also succeeded. I'm human."

Old language: "No one cares about me."
New language: "Some people care. I'm learning to let that in."

**Journal Prompts:**
• What is one core limiting belief my inner bully holds?
• Where did this belief come from? (person, moment, pattern)
• What EVIDENCE do I have that this belief isn't fully true?
• What would I rather believe instead?
• What is one small action I can take this week to practice the new belief?

**Choosing New Beliefs:**

Write your new belief as an affirmation:
• "I am enough, exactly as I am."
• "My worth is not tied to my productivity."
• "I am allowed to make mistakes and still be loved."

Say it daily. Even if you don't fully believe it yet. You're teaching your nervous system a new truth.""",
            'action': 'Complete the Belief Inquiry exercise for ONE limiting belief this week. Identify: the belief, its origin, evidence against it, and your new chosen belief. Practice the new belief through one small action. Notice what shifts.',
            'is_free': False,
            'minutes': 30
        },
        {
            'step': 6,
            'title': 'Integration - Living Without the Bully in Charge',
            'purpose': 'Recognize progress and what life looks like when the bully isn\'t running the show',
            'guru_message': """**Check-In Questions:**
• How has your week been?
• What's been showing up for you?
• What's one word that describes your energy today?

**Grounding Exercise:**
Close eyes. Hand on heart, hand on belly. Inhale 4, hold 2, exhale 6 (twice). Roots to earth. "I am safe. I am here. I am open."

---

**🌊 REFLECT - Integration & Living Free**

Healing isn't about perfection — it's about noticing when you've shifted.

**You don't need to be healed to live freely.**

---

**Recognizing Progress Without Minimizing It**

Progress doesn't always look like you expect:

**Progress might look like:**
• Catching the inner bully sooner than before
• Responding with compassion once this week (even if you forgot the other 6 times)
• Noticing when you're overwhelmed and choosing to ground
• Taking a break without guilt (even if the guilt came later)
• Asking for help
• Saying no
• Resting without justifying it
• Making a mistake and NOT spiraling

**You're not looking for perfection. You're looking for moments.**

Even one moment of responding differently is evidence of change.

---

**What Setbacks Really Mean**

The inner bully WILL come back. That doesn't mean you've failed.

**Setbacks are information:**
• "I was stressed and reverted to old patterns. That makes sense."
• "I need more support right now."
• "This belief is deeper than I thought. I need more time."

**Setbacks are NOT proof that:**
• Nothing is working
• You're broken
• You'll always be this way

They're proof that you're HUMAN. And that healing is not linear.

---

**How the Bully May Try to Return in Subtle Ways**

Even as the loud bully softens, watch for sneaky versions:

• "I should be further along by now" (perfectionism)
• "Other people heal faster" (comparison)
• "I'm doing this wrong" (self-doubt)
• "I'm being too self-focused" (guilt about self-care)

These are all just... the inner bully wearing a different mask.

Meet them the same way: with compassion.""",
            'tools': 'Grounding,Reflection',
            'reflection': """**Daily Check-Ins**

For the next week, answer these each day:

• On a scale of 1-10, how loud was the inner bully today?
• When it showed up, how did I respond?
• What helped me feel more grounded today?
• What is one kind thing I did for myself?

**Gentle Self-Trust Building**

Trust isn't built overnight. But you can build it in small moments.

**This week, practice trusting yourself by:**
• Making one small decision without seeking external validation
• Honoring a boundary you set
• Listening to your body (rest when tired, eat when hungry, move when restless)
• Believing yourself when you say something is hard

**Celebrating Micro-Shifts**

Write down EVERY small shift you notice:

Examples:
• "I caught myself mid-criticism and paused."
• "I asked for help without apologizing."
• "I rested without guilt (for 10 minutes at least)."
• "I responded to the bully with compassion once today."
• "I didn't spiral after a mistake."

These aren't "small wins." They're EVIDENCE that you're changing.

**Journal Prompts:**
• What progress have I made since Module 1, even if it feels small?
• What does life feel like when the inner bully isn't running the show?
• How do I want to keep supporting myself moving forward?
• What setbacks have I experienced, and what did they teach me?""",
            'action': 'Complete daily check-ins all week. At the end, write a letter to yourself celebrating every micro-shift you noticed. Read it out loud. Let yourself FEEL the progress, even if it feels small.',
            'is_free': False,
            'minutes': 25
        },
        {
            'step': 7,
            'title': 'Embodiment & Continuity - Walking Forward with Trust',
            'purpose': 'Carry this work into everyday life with ongoing support',
            'guru_message': """**Check-In Questions:**
• How has your week been?
• What's been showing up for you?
• What's one word that describes your energy today?

**Grounding Exercise:**
Close eyes. Hand on heart, hand on belly. Inhale 4, hold 2, exhale 6 (twice). Roots to earth. "I am safe. I am here. I am open."

---

**🌟 RISE - Walking Forward with Trust**

This module ensures the course doesn't end — it integrates.

**You are no longer at war with yourself.**

---

**Trusting Yourself Moving Forward**

You've learned so much:
• You can identify the inner bully
• You understand where it came from
• You know how to ground your nervous system
• You can respond with compassion
• You've questioned old beliefs and chosen new ones
• You recognize progress, even when it's small

Now the question is: **How do I keep this going?**

The answer: **You don't have to do it perfectly. You just have to remember to come back.**

---

**Creating Personal Rituals for Ongoing Support**

**Morning Ritual (5 minutes):**
• Hand on heart. "Good morning. What do you need today?"
• Set ONE intention: "Today, I will be kind to myself."
• Ground before you start the day.

**Midday Check-In (2 minutes):**
• Pause. Notice: Is the inner bully loud right now?
• If yes: Ground. Respond with compassion.
• If no: Celebrate. "I'm doing okay."

**Evening Reflection (5 minutes):**
• What went well today?
• When did the bully show up, and how did I respond?
• What is one kind thing I can do for myself before bed?

**Knowing When to Return to the Tools**

You'll know it's time to come back when:
• The inner bully gets loud again
• You notice you're in old patterns
• Life gets overwhelming
• You forget to be kind to yourself

**And that's okay.** This isn't about never struggling again. It's about having tools to come back to.""",
            'tools': 'Grounding,Reflection,Visualization',
            'reflection': """**Creating Your Personal Grounding Routine**

Design a simple routine you can do ANYTIME the inner bully gets loud:

Example:
1. Pause. Notice the voice.
2. Take 3 deep breaths.
3. Hand on heart: "I hear you. You're scared. We're okay."
4. Ground (feet, 5-4-3-2-1, cold water, etc.)
5. Choose: What do I need right now?

Write YOUR routine. Keep it simple. Keep it accessible.

---

**Designing a "Support Plan" for Hard Days**

On hard days, you might forget everything you've learned. So write it down NOW:

**When I'm struggling, I will:**
• Ground first (my top 3 tools: ___)
• Reach out to (person/support/community)
• Remind myself: "This is temporary. I've gotten through hard days before."
• Do ONE small kind thing for myself

**I will NOT:**
• Believe everything the inner bully says
• Isolate completely
• Push through without rest
• Shame myself for struggling

---

**Closing Ritual / Reflection**

Take a moment to reflect on this entire journey:

• What has changed since Module 1?
• What do I understand now that I didn't before?
• How do I feel about the inner bully now?
• What do I want to carry forward?

**Write a letter to your future self:**

"Dear Future Me,

If the inner bully gets loud again, here's what I want you to remember:

[Your wisdom here]

You are not alone. You have tools. You are allowed to struggle AND you are capable of gentleness.

With love,
[Your name]"

**Final Affirmation:**

"I am no longer at war with myself. I am learning to be the safe, compassionate presence I always needed. I trust myself to keep showing up, one gentle moment at a time."

You did it. You walked this path. And you can return to it anytime you need.

**You are not broken. You were never broken. You are healing.**""",
            'action': 'Complete your closing ritual. Write your letter to future self. Create your personal grounding routine and support plan. Save them somewhere you can find them on hard days. Celebrate how far you\'ve come. You did beautiful work.',
            'is_free': False,
            'minutes': 30
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

init_db()
seed_freeze_path()  # Seed the path on startup
seed_inner_bully_path()  # Seed inner bully path

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
                'keywords': ['dont want to upset', 'everyone else', 'their needs', 'cant say no', 'disappointing', 'letting them down', 'always helping', 'exhausted from', "don't get anything back", 'nothing back', 'one-sided', 'all the effort', 'trying to be nice', 'tired of trying', 'tired of being nice', 'always giving', 'never appreciated', 'taken for granted', 'unappreciated'],
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
                'keywords': ['ignoring it', 'putting it off', 'deal with it later', 'cant face', 'escape', 'distract myself', 'running from', 'avoiding', 'put off', 'hide from', 'procrastinating', 'dodging'],
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
        
        # Everyday life topic patterns - for sharing life, not just pain
        self.life_topics = {
            'work': {
                'keywords': ['work', 'job', 'office', 'colleagues', 'colleague', 'meeting', 'boss', 'career', 'workplace', 'coworker', 'manager', 'project', 'deadline'],
                'celebration_keywords': ['got praised', 'promotion', 'raise', 'accomplished', 'finished project', 'good feedback', 'recognition'],
                'stress_keywords': ['overwhelmed', 'overwhelming', 'stressed', 'stressful', 'annoyed', 'frustrated', 'anxious about', 'worried about', 'too much', 'too many', 'was mean', 'being mean', 'rude', 'difficult', 'hard day', 'bad day', 'exhausted', 'exhausting', 'tired', 'draining', 'awful', 'horrible', 'terrible', 'unbearable', "don't want to go", 'dread', 'hate going', "can't face"],
                'stressed_responses': [
                    "Work can pull so much from your energy. What part of today felt the heaviest?",
                    "Let's slow this down together—what's underneath the overwhelm?",
                    "What do you need most right now: clarity, grounding, or a moment to breathe?",
                    "Being in that environment sounds draining. Where do you feel it most in your body?"
                ],
                'celebration_responses': [
                    "That's beautiful! Let yourself enjoy this moment—it matters.",
                    "I'm proud of you. What part of this win feels most meaningful to you?",
                    "Celebrate this. You worked for it. How does it feel to be recognized?",
                    "That's wonderful. Let yourself really feel this accomplishment."
                ],
                'neutral_responses': [
                    "Tell me about work. What's happening there for you?",
                    "I'm listening. What's the situation at work?",
                    "Work is a big part of life. What's going on?"
                ]
            },
            'relationships': {
                'keywords': ['friend', 'friends', 'friendship', 'partner', 'boyfriend', 'girlfriend', 'parent', 'parents', 'mum', 'mom', 'dad', 'father', 'mother', 'sister', 'brother', 'family', 'relationship', 'relative'],
                'celebration_keywords': ['lovely day', 'lovely time', 'good conversation', 'connected', 'special moment', 'quality time'],
                'stress_keywords': ['upset me', 'hurt me', 'conflict', 'argument', 'fight', 'misunderstood', "don't feel understood", "don't listen", "won't listen", "doesn't listen", 'not listening', 'ignoring', 'tension', 'was mean', 'being mean', 'rude', 'ignored', 'dismissed', 'angry at', 'mad at', 'frustrating', 'difficult', 'falling out', 'issue with', "don't get anything back", "nothing back", "not reciprocated", 'one-sided', 'all the effort', 'trying to be nice', 'tired of trying', 'tired of being', 'exhausted from trying', 'always giving', 'never receive', 'unappreciated', 'taken for granted', 'no effort back'],
                'stressed_responses': [
                    "It sounds like your heart was tender in that moment. What felt most painful for you?",
                    "Being misunderstood is such a lonely feeling. Where did you feel it in your body?",
                    "Let's explore what you needed that you didn't receive.",
                    "That relational pain runs deep. What part of this is sitting with you most?"
                ],
                'celebration_responses': [
                    "I'm glad you had a nourishing moment. What made it feel good?",
                    "Cherish this connection—it's a reminder of what supports your spirit.",
                    "That sounds really special. What did you appreciate most about that time together?",
                    "Connection like that is precious. Let yourself savor it."
                ],
                'neutral_responses': [
                    "Tell me about this relationship. What's happening?",
                    "I'm here. What's going on with them?",
                    "Relationships can be complex. What's on your mind?"
                ]
            },
            'pets': {
                'keywords': ['dog', 'cat', 'pet', 'puppy', 'kitten', 'animal', 'vet', 'fur baby'],
                'celebration_keywords': ['cute', 'adorable', 'sweet', 'funny', 'made me smile', 'made me laugh'],
                'stress_keywords': ['unwell', 'sick', 'scared', 'worried', 'vet', 'ill', 'not eating', 'injured', 'hurt', 'pain', 'limping', 'vomiting', "won't eat", 'emergency', 'hospital', 'surgery'],
                'stressed_responses': [
                    "It makes sense to feel scared when a pet isn't well. You care deeply.",
                    "What symptoms are you noticing? I'm here with you as you navigate this.",
                    "The worry for them is real. Have you been able to speak with a vet?",
                    "Your bond with them is precious. This concern shows how much you love them."
                ],
                'celebration_responses': [
                    "That sounds adorable. These little moments soften the heart—thank you for sharing it.",
                    "Your bond with them is special. What did it bring up for you?",
                    "I love that you noticed that sweet moment. Pets bring such light.",
                    "That's lovely. Those small joys matter so much."
                ],
                'neutral_responses': [
                    "Tell me about your pet. What's happening?",
                    "I'm listening. What's going on with them?",
                    "Pets are family. What's on your heart?"
                ]
            },
            'home': {
                'keywords': ['home', 'house', 'flat', 'apartment', 'room', 'space', 'living space', 'bedroom', 'kitchen'],
                'celebration_keywords': ['tidied', 'cleaned', 'organized', 'peaceful', 'calm space', 'cozy', 'comfortable'],
                'stress_keywords': ['chaotic', 'messy', 'overwhelming', 'uncomfortable', "don't feel comfortable", 'cluttered', 'stressful', 'too much', 'falling apart', 'broken', 'issues with', 'problems with', 'noise', 'noisy', 'dirty', 'unsafe'],
                'stressed_responses': [
                    "A chaotic space can unsettle your whole system. What part feels most overwhelming?",
                    "Let's take this gently—one corner, one breath at a time.",
                    "Not feeling comfortable at home is really hard. What's making it feel unsafe or uncomfortable?",
                    "Your environment affects everything. What would help you feel more settled there?"
                ],
                'celebration_responses': [
                    "That's a lovely accomplishment. How does your body feel in the calmer space?",
                    "Creating peace in your space creates peace in your mind. Well done.",
                    "That's beautiful. What shifted for you when you created that order?",
                    "Your space matters. I'm glad you're feeling more at ease there."
                ],
                'neutral_responses': [
                    "Tell me about your home situation. What's happening?",
                    "I'm listening. What's going on at home?",
                    "Your living space is important. What's on your mind?"
                ]
            },
            'money': {
                'keywords': ['money', 'bills', 'bill', 'paid', 'debt', 'finance', 'financial', 'rent', 'mortgage', 'savings', 'salary', 'income', 'afford', 'expensive'],
                'celebration_keywords': ['paid off', 'paid it off', 'cleared', 'saved', 'bonus', 'raise', 'got paid'],
                'stress_keywords': ['tight', 'anxious about', 'worried about', "can't afford", 'struggling', 'stress', 'stressful', 'broke', 'running out', 'overdue', 'behind on', 'owe', 'debt', 'expensive', 'too expensive', 'too much'],
                'stressed_responses': [
                    "Financial strain touches deeply on safety. Your worry makes sense.",
                    "Let's explore what's causing the biggest pressure right now.",
                    "Money stress affects everything. What's the most immediate concern?",
                    "That financial weight is real. What would help you feel more stable?"
                ],
                'celebration_responses': [
                    "That's a big step—well done. How does this shift your sense of stability?",
                    "Celebrate this! Financial wins matter. What does this free up for you?",
                    "I'm proud of you for working toward this. How does it feel?",
                    "That's excellent. Let yourself feel the relief of that."
                ],
                'neutral_responses': [
                    "Tell me about the financial situation. What's happening?",
                    "I'm listening. What's going on with money?",
                    "Money concerns are valid. What's on your mind?"
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
        try:
            recent_ai_messages = [msg[1] for msg in conversation_history if len(msg) >= 2 and msg[0] == 'assistant'][:3]
        except (IndexError, TypeError, AttributeError):
            recent_ai_messages = []
        
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
        
        # Check for everyday life topics (work, relationships, pets, home, money)
        # This runs BEFORE emotional states so we can respond to life sharing, not just pain
        for topic_name, topic_data in self.life_topics.items():
            # Check if topic keywords are present
            if any(keyword in message_lower for keyword in topic_data['keywords']):
                
                # EXCEPTION: If it's relationships and "friend" is used as a greeting, skip it
                if topic_name == 'relationships':
                    # Check if "friend" appears only in greeting context (start of message)
                    greeting_with_friend = any(phrase in message_lower for phrase in [
                        'hey friend', 'hi friend', 'hello friend', 'hey, friend', 'hi, friend'
                    ])
                    # If it's just a greeting with friend and they're not talking ABOUT a friend, skip
                    if greeting_with_friend and not any(word in message_lower for word in ['my friend', 'a friend', 'with friend', 'about friend', 'friend and', 'friend said', 'friend told', 'friend upset']):
                        continue  # Skip relationship detection for greetings
                
                # Determine if it's celebratory, stressful, or neutral
                is_celebration = any(keyword in message_lower for keyword in topic_data['celebration_keywords'])
                is_stressed = any(keyword in message_lower for keyword in topic_data['stress_keywords'])
                
                # Select appropriate response type
                if is_celebration:
                    available_responses = [r for r in topic_data['celebration_responses'] if r not in str(recent_ai_messages)]
                    if not available_responses:
                        available_responses = topic_data['celebration_responses']
                elif is_stressed:
                    available_responses = [r for r in topic_data['stressed_responses'] if r not in str(recent_ai_messages)]
                    if not available_responses:
                        available_responses = topic_data['stressed_responses']
                else:
                    available_responses = [r for r in topic_data['neutral_responses'] if r not in str(recent_ai_messages)]
                    if not available_responses:
                        available_responses = topic_data['neutral_responses']
                
                response = random.choice(available_responses)
                
                # Only offer tools if it's a stressed situation
                needs_tool = is_stressed and intensity_score >= 4
                
                return {
                    'response': response,
                    'pattern': f'life_topic_{topic_name}',
                    'emotion': self.detect_emotion(message_lower),
                    'needs_tool': needs_tool
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
            try:
                recent_user_msgs = [msg[1].lower() for msg in conversation_history[:5] if len(msg) >= 2 and msg[0] == 'user']
                hopeless_count = sum(1 for msg in recent_user_msgs if any(
                    word in msg for word in ['hopeless', 'pointless', 'give up', 'cant', "can't", 'no point']
                ))
                if hopeless_count >= 2:
                    score += 2
            except (IndexError, TypeError, AttributeError):
                pass
        
        # Escalating pattern (messages getting darker)
        if conversation_history and len(conversation_history) >= 4:
            try:
                recent_msgs = [msg[1].lower() for msg in conversation_history[:4] if len(msg) >= 2 and msg[0] == 'user']
                if len(recent_msgs) >= 2:
                    # Check if negative words increasing
                    neg_words = ['worse', 'cant', "can't", 'hopeless', 'stuck', 'nothing', 'never']
                    recent_neg = sum(1 for msg in recent_msgs[:2] for word in neg_words if word in msg)
                    older_neg = sum(1 for msg in recent_msgs[2:] for word in neg_words if word in msg)
                    if recent_neg > older_neg:
                        score += 1
            except (IndexError, TypeError, AttributeError):
                pass
        
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
        try:
            recent_ai_messages = [msg[1] for msg in history if len(msg) >= 2 and msg[0] == 'assistant'][:3]
        except (IndexError, TypeError, AttributeError):
            recent_ai_messages = []
        
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
        
        # Check if user is stating what they need (peace, calm, clarity, etc.)
        # This is an opportunity to offer immediate tools - BUT ask permission first
        needs_peace = any(word in message_lower for word in ['peace', 'peaceful', 'calm', 'quiet'])
        needs_grounding = any(phrase in message_lower for phrase in ['need grounding', 'want grounding', 'ground me', 'help me ground', 'grounding exercise'])
        needs_clarity = any(word in message_lower for word in ['clarity', 'clear', 'think straight', 'clear head'])
        needs_rest = any(word in message_lower for word in ['rest', 'sleep', 'relax', 'unwind'])
        needs_relief = any(word in message_lower for word in ['relief', 'break', 'escape', 'pause'])
        
        # Check if it's a short response (likely answering "what do you need?")
        word_count = len(message_lower.split())
        is_short_need_statement = word_count <= 5
        
        # Exception: "I'm here" is just affirming presence, not requesting grounding
        is_affirming_presence = message_lower.strip() in ["i'm here", "im here", "here", "i am here"]
        
        if is_short_need_statement and (needs_peace or needs_grounding or needs_clarity or needs_rest or needs_relief) and not is_affirming_presence:
            # Ask permission before offering the tool
            if needs_peace or needs_rest:
                tool_offer = (
                    "I can guide you through a **4-7-8 Breathing exercise** right now - it's proven for calm and takes about 90 seconds.\n\n"
                    "Would you like to try it?"
                )
            elif needs_grounding:
                tool_offer = (
                    "I can guide you through a **5-4-3-2-1 Grounding exercise** - it brings you back to the present moment in about 2 minutes.\n\n"
                    "Would you like to try it?"
                )
            elif needs_clarity:
                tool_offer = (
                    "I can guide you through **Box Breathing** - it clears mental fog and takes about 90 seconds.\n\n"
                    "Would you like to try it?"
                )
            else:  # needs_relief
                tool_offer = (
                    "I can guide you through a **Physiological Sigh** - it releases tension in about 30 seconds.\n\n"
                    "Would you like to try it?"
                )
            
            return {
                'response': tool_offer,
                'pattern': 'tool_offer_consent',
                'emotion': self.detect_emotion(message_lower),
                'needs_tool': False
            }
        
        # Check for open-ended sharing statements (neutral - could be good or bad news)
        neutral_sharing = any(phrase in message_lower for phrase in [
            'wanted to share', 'want to share', 'need to share', 'have to share',
            'wanted to tell you', 'want to tell you', 'need to tell you',
            'something to share', 'something happened', 'something i want to',
            'i have news', 'got news'
        ])
        
        if neutral_sharing:
            sharing_responses = [
                "I'm listening. What would you like to share?",
                "I'm here. What's on your mind?",
                "I'm all ears. What happened?",
                "Tell me. What would you like to share?",
                "I'm right here with you. What's going on?",
                "Please, share. I'm listening."
            ]
            
            response = random.choice([r for r in sharing_responses if r not in str(recent_ai_messages)])
            if not response:
                response = random.choice(sharing_responses)
            
            return {
                'response': response,
                'pattern': 'open_sharing',
                'emotion': None,
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
            'guide me', 'walk me through', 'show me how', 'help me do', 'yes', 'yeah', 'yh', 'okay', 'ok', 'sure', 'ready',
            'ill try', "i'll try", 'lets do it', "let's do", 'would like to', 'want to try'
        ])
        
        # Check if user agreed to a specific tool offer by looking at recent messages
        if wants_guidance and recent_ai_messages:
            last_ai_message = recent_ai_messages[0] if recent_ai_messages else ""
            
            # Check which tool was offered
            if '4-7-8 Breathing' in last_ai_message or 'calm and sleep' in last_ai_message:
                guided_breath_478 = (
                    "Perfect. Let's do this together right now.\n\n"
                    "**4-7-8 Breathing - Follow Along:**\n\n"
                    "1️⃣ Breathe IN through your nose: 1...2...3...4\n"
                    "2️⃣ HOLD: 1...2...3...4...5...6...7\n"
                    "3️⃣ Breathe OUT through your mouth: 1...2...3...4...5...6...7...8\n\n"
                    "Now repeat that 3 more times on your own. I'll wait.\n\n"
                    "...\n\n"
                    "How does that feel?"
                )
                return {
                    'response': guided_breath_478,
                    'pattern': 'guided_exercise',
                    'emotion': None,
                    'needs_tool': False
                }
            
            elif '5-4-3-2-1' in last_ai_message or 'Grounding' in last_ai_message:
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
                    "Take a breath. You're here. You're present. What did you notice?"
                )
                return {
                    'response': guided_grounding,
                    'pattern': 'guided_exercise',
                    'emotion': None,
                    'needs_tool': False
                }
            
            elif 'Box Breathing' in last_ai_message or 'clears mental fog' in last_ai_message:
                guided_box = (
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
                    'response': guided_box,
                    'pattern': 'guided_exercise',
                    'emotion': None,
                    'needs_tool': False
                }
            
            elif 'Physiological Sigh' in last_ai_message or 'releases tension' in last_ai_message:
                guided_sigh = (
                    "Perfect. Let's do this right now.\n\n"
                    "**Physiological Sigh - Do With Me:**\n\n"
                    "1️⃣ Two quick inhales through your nose: IN-IN\n"
                    "2️⃣ One long exhale through your mouth: AHHHHHH\n\n"
                    "Again:\n"
                    "IN-IN... AHHHHHH\n\n"
                    "One more:\n"
                    "IN-IN... AHHHHHH\n\n"
                    "How does that feel?"
                )
                return {
                    'response': guided_sigh,
                    'pattern': 'guided_exercise',
                    'emotion': None,
                    'needs_tool': False
                }
        
        # Legacy breath detection for backward compatibility
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
        
        # Check if expressing gratitude or reporting that a tool helped
        tool_worked = any(phrase in message_lower for phrase in [
            'that helped', 'it helped', 'helped', 'that worked', 'it worked', 'worked',
            'feel better', 'feeling better', 'feels better', 'bit better', 'little better',
            'breathing helped', 'grounding helped', 'exercise helped', 'tool helped',
            'did the breathing', 'tried the breathing', 'tried breathing', 'did breathing',
            'took your advice', 'followed your', 'did what you', 'tried what you'
        ])
        
        if tool_worked:
            tool_success_responses = [
                "That's wonderful - you showed up for yourself and it made a difference. That takes courage.\n\nDo you want to keep building on this feeling, or is this a good place to rest for now?",
                "I'm so proud of you for trying that. Notice how you just shifted your own state - that's your power, not mine.\n\nHow do you want to continue from here? Keep exploring, or take this win and rest?",
                "Beautiful. You just proved to yourself that you have the tools to shift how you feel. That's huge.\n\nWhat do you need now? More support, or space to sit with this relief?",
                "That's really good to hear. You did that - you chose to try something and it helped. That matters.\n\nShall we continue, or is this a good stopping point for today?"
            ]
            response = random.choice([r for r in tool_success_responses if r not in str(recent_ai_messages)])
            return {
                'response': response,
                'pattern': 'tool_success',
                'emotion': 'relief',
                'needs_tool': False
            }
        
        # Check if expressing general gratitude
        if any(word in message_lower for word in ['thank', 'grateful', 'appreciate']):
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
        # Check if user already mentioned a time period in THIS message OR recent conversation
        time_period = self.extract_time_period(message_lower)
        
        # Also check recent user messages for time periods (last 3 messages)
        if not time_period and history:
            try:
                recent_user_messages = [msg[1].lower() for msg in history if len(msg) >= 2 and msg[0] == 'user'][:3]
                for prev_msg in recent_user_messages:
                    time_period = self.extract_time_period(prev_msg)
                    if time_period:
                        break  # Found a time period in recent history
            except (IndexError, TypeError, AttributeError):
                # If history format is unexpected, just skip this check
                pass
        
        if time_period:
            # User already mentioned duration - DON'T ask "how long", ask deeper questions
            time_aware_responses = [
                f"I hear you. What's been making this particularly difficult?",
                f"That sounds really painful. What part of this weighs on you most?",
                f"I'm listening. What would help you feel more supported through this?",
                f"That's a lot to carry. What keeps you going despite this challenge?"
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

# Helper function to check subscription status
def has_premium_access(user_id):
    """Check if user has active premium subscription that hasn't expired"""
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    c.execute("""SELECT subscription_status, expires_at FROM subscriptions 
                 WHERE user_id = ?""", (user_id,))
    result = c.fetchone()
    conn.close()
    
    if not result:
        return False
    
    status, expires_at = result
    
    # Check if status is active or cancelled (but not expired yet)
    if status not in ['active', 'cancelled']:
        return False
    
    # If there's an expiration date, check if it's still valid
    if expires_at:
        from datetime import datetime
        try:
            expiry_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            if datetime.now() > expiry_date:
                # Subscription expired - update status
                conn = sqlite3.connect('healing_guru_chat.db')
                c = conn.cursor()
                c.execute("""UPDATE subscriptions SET subscription_status = 'expired' 
                           WHERE user_id = ?""", (user_id,))
                conn.commit()
                conn.close()
                return False
        except:
            pass  # If date parsing fails, allow access (benefit of doubt)
    
    return True

@app.route('/')
def index():
    if 'user_id' not in session:
        session['user_id'] = secrets.token_hex(8)
    
    # Get all active paths
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    c.execute("SELECT id, title, slug, summary, icon, duration FROM paths WHERE is_active = 1")
    paths = c.fetchall()
    conn.close()
    
    return render_template('home.html', paths=paths)

@app.route('/chat')
def chat_page():
    """Direct chat interface"""
    if 'user_id' not in session:
        session['user_id'] = secrets.token_hex(8)
    return render_template('chat.html')

@app.route('/path/<slug>')
def path_detail(slug):
    """Show path overview and modules"""
    print(f"DEBUG: Accessing path with slug: {slug}")  # Debug line
    user_id = session.get('user_id')
    if not user_id:
        session['user_id'] = secrets.token_hex(8)
        user_id = session['user_id']
    
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    
    # Get path info
    c.execute("SELECT id, title, description, icon, duration FROM paths WHERE slug = ?", (slug,))
    path = c.fetchone()
    
    print(f"DEBUG: Path found: {path}")  # Debug line
    
    if not path:
        conn.close()
        print(f"DEBUG: No path found for slug: {slug}")  # Debug line
        return "Path not found", 404
    
    path_id = path[0]
    
    # Get modules
    c.execute("""SELECT id, step_number, title, purpose, is_free, estimated_minutes 
                 FROM modules WHERE path_id = ? ORDER BY step_number""", (path_id,))
    modules = c.fetchall()
    
    # Get user progress
    c.execute("""SELECT module_id, completed_at FROM user_progress 
                 WHERE user_id = ? AND path_id = ?""", (user_id, path_id))
    progress = {row[0]: row[1] for row in c.fetchall()}
    
    conn.close()
    
    has_premium = has_premium_access(user_id)
    
    return render_template('path_detail.html', 
                          slug=slug,
                          path=path, 
                          modules=modules, 
                          progress=progress,
                          has_premium=has_premium)

@app.route('/path/<slug>/module/<int:step>')
def module_view(slug, step):
    """View a specific module"""
    user_id = session.get('user_id')
    if not user_id:
        session['user_id'] = secrets.token_hex(8)
        user_id = session['user_id']
    
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    
    # Get path and module
    c.execute("SELECT id FROM paths WHERE slug = ?", (slug,))
    path_result = c.fetchone()
    
    if not path_result:
        conn.close()
        return "Path not found", 404
    
    path_id = path_result[0]
    
    c.execute("""SELECT id, step_number, title, purpose, guru_message, tools, 
                        reflection_prompt, action_invitation, is_free, estimated_minutes
                 FROM modules WHERE path_id = ? AND step_number = ?""", (path_id, step))
    module = c.fetchone()
    
    if not module:
        conn.close()
        return "Module not found", 404
    
    module_id = module[0]
    is_free = module[8]
    
    # Check access
    has_premium = has_premium_access(user_id)
    if not is_free and not has_premium:
        conn.close()
        return render_template('paywall.html', slug=slug, step=step)
    
    # Check if already completed
    c.execute("""SELECT reflection_response, completed_at FROM user_progress 
                 WHERE user_id = ? AND module_id = ?""", (user_id, module_id))
    progress = c.fetchone()
    
    # Mark as started if not already
    if not progress:
        c.execute("""INSERT INTO user_progress (user_id, path_id, module_id)
                     VALUES (?, ?, ?)""", (user_id, path_id, module_id))
        conn.commit()
    
    conn.close()
    
    return render_template('module.html', 
                          slug=slug, 
                          module=module, 
                          progress=progress,
                          path_id=path_id)

@app.route('/path/<slug>/module/<int:step>/complete', methods=['POST'])
def complete_module(slug, step):
    """Mark module as complete with reflection"""
    user_id = session.get('user_id')
    data = request.json
    reflection = data.get('reflection', '')
    
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    
    # Get module
    c.execute("""SELECT m.id FROM modules m
                 JOIN paths p ON m.path_id = p.id
                 WHERE p.slug = ? AND m.step_number = ?""", (slug, step))
    module = c.fetchone()
    
    if module:
        module_id = module[0]
        c.execute("""UPDATE user_progress 
                     SET completed_at = CURRENT_TIMESTAMP, reflection_response = ?
                     WHERE user_id = ? AND module_id = ?""",
                  (reflection, user_id, module_id))
        conn.commit()
    
    conn.close()
    
    return jsonify({'success': True, 'next_step': step + 1})

@app.route('/verify-license', methods=['POST'])
def verify_license():
    """Verify Gumroad license key and activate subscription"""
    data = request.json
    license_key = data.get('license_key')
    user_id = session.get('user_id')
    
    if not user_id or not license_key:
        return jsonify({'success': False, 'error': 'Missing information'})
    
    # TODO: Add actual Gumroad API verification here
    # For now, we'll accept any license key (temporary for testing)
    # In production, call: https://api.gumroad.com/v2/licenses/verify
    
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    
    # Delete existing subscription if any
    c.execute("DELETE FROM subscriptions WHERE user_id = ?", (user_id,))
    # Save new subscription
    c.execute("""INSERT INTO subscriptions 
                 (user_id, gumroad_license_key, subscription_status, started_at)
                 VALUES (?, ?, 'active', CURRENT_TIMESTAMP)""",
              (user_id, license_key))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/activate-premium-test')
def activate_premium_test():
    """TEST ONLY: Activate premium for current user"""
    user_id = session.get('user_id')
    if not user_id:
        session['user_id'] = secrets.token_hex(8)
        user_id = session['user_id']
    
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    # Delete existing subscription if any
    c.execute("DELETE FROM subscriptions WHERE user_id = ?", (user_id,))
    # Insert new subscription
    c.execute("""INSERT INTO subscriptions 
                 (user_id, gumroad_license_key, subscription_status, started_at)
                 VALUES (?, 'TEST_KEY', 'active', CURRENT_TIMESTAMP)""", (user_id,))
    conn.commit()
    conn.close()
    
    return redirect('/')

@app.route('/progress')
def view_progress():
    """View user's healing journey progress"""
    user_id = session.get('user_id')
    if not user_id:
        session['user_id'] = secrets.token_hex(8)
        user_id = session['user_id']
    
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    
    # Get overall stats
    c.execute("""SELECT COUNT(*) FROM user_progress 
                 WHERE user_id = ? AND completed_at IS NOT NULL""", (user_id,))
    total_completed = c.fetchone()[0]
    
    c.execute("""SELECT COUNT(DISTINCT path_id) FROM user_progress 
                 WHERE user_id = ?""", (user_id,))
    paths_started = c.fetchone()[0]
    
    c.execute("""SELECT COUNT(*) FROM user_progress 
                 WHERE user_id = ? AND reflection_response IS NOT NULL""", (user_id,))
    total_reflections = c.fetchone()[0]
    
    stats = {
        'total_completed': total_completed,
        'paths_started': paths_started,
        'total_reflections': total_reflections
    }
    
    # Get journey details
    c.execute("""SELECT DISTINCT p.id, p.title, p.icon FROM paths p
                 JOIN user_progress up ON p.id = up.path_id
                 WHERE up.user_id = ?""", (user_id,))
    paths = c.fetchall()
    
    journeys = []
    for path in paths:
        path_id, path_title, path_icon = path
        
        # Get total modules
        c.execute("SELECT COUNT(*) FROM modules WHERE path_id = ?", (path_id,))
        total_modules = c.fetchone()[0]
        
        # Get completed modules
        c.execute("""SELECT COUNT(*) FROM user_progress 
                     WHERE user_id = ? AND path_id = ? AND completed_at IS NOT NULL""",
                  (user_id, path_id))
        completed = c.fetchone()[0]
        
        # Get recent reflections
        c.execute("""SELECT m.step_number, m.title, up.reflection_response, 
                            DATE(up.completed_at) as date
                     FROM user_progress up
                     JOIN modules m ON up.module_id = m.id
                     WHERE up.user_id = ? AND up.path_id = ? 
                     AND up.reflection_response IS NOT NULL
                     ORDER BY up.completed_at DESC LIMIT 3""",
                  (user_id, path_id))
        reflections = []
        for row in c.fetchall():
            reflections.append({
                'step': row[0],
                'title': row[1],
                'text': row[2],
                'date': row[3]
            })
        
        journeys.append({
            'title': path_title,
            'icon': path_icon,
            'total': total_modules,
            'completed': completed,
            'reflections': reflections
        })
    
    conn.close()
    
    return render_template('progress.html', stats=stats, journeys=journeys)

@app.route('/debug-db')
def debug_db():
    """Debug route to check database contents"""
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM paths")
    paths = c.fetchall()
    
    c.execute("SELECT COUNT(*) FROM modules")
    module_count = c.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'paths': paths,
        'module_count': module_count,
        'message': f'Found {len(paths)} paths and {module_count} modules'
    })

@app.route('/googleccc479b763b17be8.html')
def google_verification():
    """Serve Google site verification file"""
    from flask import Response
    return Response('google-site-verification: googleccc479b763b17be8.html', mimetype='text/plain')

@app.route('/community')
def community():
    """Community discussion board"""
    user_id = session.get('user_id')
    if not user_id:
        session['user_id'] = secrets.token_hex(8)
        user_id = session['user_id']
    
    # Get filter parameters
    path_filter = request.args.get('path', 'all')
    category_filter = request.args.get('category', 'all')
    
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    
    # Get all paths for filter dropdown
    c.execute("SELECT slug, title, icon FROM paths WHERE is_active = 1")
    paths = c.fetchall()
    
    # Build query based on filters
    query = """SELECT cp.id, cp.display_name, cp.path_slug, cp.category, cp.title, 
                      cp.content, cp.created_at,
                      (SELECT COUNT(*) FROM community_comments WHERE post_id = cp.id) as comment_count,
                      p.title as path_title, p.icon as path_icon
               FROM community_posts cp
               LEFT JOIN paths p ON cp.path_slug = p.slug
               WHERE 1=1"""
    params = []
    
    if path_filter != 'all':
        query += " AND cp.path_slug = ?"
        params.append(path_filter)
    
    if category_filter != 'all':
        query += " AND cp.category = ?"
        params.append(category_filter)
    
    query += " ORDER BY cp.created_at DESC LIMIT 50"
    
    c.execute(query, params)
    posts = c.fetchall()
    
    conn.close()
    
    return render_template('community.html', 
                          posts=posts, 
                          paths=paths,
                          current_path=path_filter,
                          current_category=category_filter)

@app.route('/community/post/<int:post_id>')
def view_post(post_id):
    """View a single post with comments"""
    user_id = session.get('user_id')
    if not user_id:
        session['user_id'] = secrets.token_hex(8)
        user_id = session['user_id']
    
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    
    # Get post
    c.execute("""SELECT cp.id, cp.display_name, cp.path_slug, cp.category, cp.title, 
                        cp.content, cp.created_at,
                        p.title as path_title, p.icon as path_icon
                 FROM community_posts cp
                 LEFT JOIN paths p ON cp.path_slug = p.slug
                 WHERE cp.id = ?""", (post_id,))
    post = c.fetchone()
    
    if not post:
        conn.close()
        return "Post not found", 404
    
    # Get comments
    c.execute("""SELECT id, display_name, content, created_at
                 FROM community_comments 
                 WHERE post_id = ? 
                 ORDER BY created_at ASC""", (post_id,))
    comments = c.fetchall()
    
    conn.close()
    
    return render_template('community_post.html', post=post, comments=comments)

@app.route('/community/new', methods=['GET', 'POST'])
def new_post():
    """Create a new community post"""
    user_id = session.get('user_id')
    if not user_id:
        session['user_id'] = secrets.token_hex(8)
        user_id = session['user_id']
    
    if request.method == 'POST':
        display_name = request.form.get('display_name', 'Anonymous')
        path_slug = request.form.get('path_slug', 'general')
        category = request.form.get('category')
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not all([category, title, content]):
            return "Missing required fields", 400
        
        conn = sqlite3.connect('healing_guru_chat.db')
        c = conn.cursor()
        
        c.execute("""INSERT INTO community_posts 
                     (user_id, display_name, path_slug, category, title, content)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (user_id, display_name, path_slug, category, title, content))
        
        post_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return redirect(f'/community/post/{post_id}')
    
    # GET: Show form
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    c.execute("SELECT slug, title, icon FROM paths WHERE is_active = 1")
    paths = c.fetchall()
    conn.close()
    
    return render_template('new_post.html', paths=paths)

@app.route('/community/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    """Add a comment to a post"""
    user_id = session.get('user_id')
    if not user_id:
        session['user_id'] = secrets.token_hex(8)
        user_id = session['user_id']
    
    display_name = request.form.get('display_name', 'Anonymous')
    content = request.form.get('content')
    
    if not content:
        return "Comment content required", 400
    
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    
    c.execute("""INSERT INTO community_comments 
                 (post_id, user_id, display_name, content)
                 VALUES (?, ?, ?, ?)""",
              (post_id, user_id, display_name, content))
    
    conn.commit()
    conn.close()
    
    return redirect(f'/community/post/{post_id}')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'No session found'}), 400
        
        # Quick response - skip heavy processing for now
        conn = sqlite3.connect('healing_guru_chat.db', timeout=5)
        c = conn.cursor()
        
        # Save user message quickly
        c.execute('INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)',
                  (user_id, 'user', user_message))
        
        # Simple fast response
        response_text = "I hear you. Tell me more about that."
        
        # Save AI response
        c.execute('INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)',
                  (user_id, 'assistant', response_text))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': response_text,
            'pattern': None,
            'emotion': None
        })
    
    except Exception as e:
        print(f"ERROR in /api/chat: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Application error', 'details': str(e)}), 500

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

# ===== GDPR COMPLIANCE ROUTES =====

@app.route('/privacy')
def privacy_policy():
    """Privacy Policy page (GDPR Article 13 compliance)"""
    return render_template('privacy.html')

@app.route('/terms')
def terms_of_service():
    """Terms of Service page"""
    return render_template('terms.html')

@app.route('/account')
def account_dashboard():
    """User data dashboard with GDPR rights management"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/')
    
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    
    # Get user data statistics
    c.execute('SELECT COUNT(*) FROM messages WHERE user_id = ?', (user_id,))
    message_count = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM journal WHERE user_id = ?', (user_id,))
    journal_count = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM community_posts WHERE user_id = ?', (user_id,))
    post_count = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM user_progress WHERE user_id = ? AND completed_at IS NOT NULL', (user_id,))
    completed_modules = c.fetchone()[0]
    
    # Get account info
    c.execute('SELECT MIN(timestamp) FROM messages WHERE user_id = ?', (user_id,))
    first_activity = c.fetchone()[0]
    member_since = first_activity[:10] if first_activity else 'Recent'
    
    # Get subscription status
    c.execute('SELECT subscription_status FROM subscriptions WHERE user_id = ?', (user_id,))
    sub_result = c.fetchone()
    subscription_status = sub_result[0] if sub_result else 'Free Tier'
    
    # Get consent info
    c.execute('SELECT cookies_accepted, data_processing_accepted, consent_date FROM user_consent WHERE user_id = ?', (user_id,))
    consent_result = c.fetchone()
    
    if consent_result:
        consent = {
            'cookies_accepted': consent_result[0],
            'data_processing_accepted': consent_result[1]
        }
        consent_date = consent_result[2][:10] if consent_result[2] else 'Not recorded'
    else:
        consent = {
            'cookies_accepted': False,
            'data_processing_accepted': False
        }
        consent_date = 'Not given'
    
    conn.close()
    
    stats = {
        'messages': message_count,
        'journal_entries': journal_count,
        'community_posts': post_count,
        'modules_completed': completed_modules
    }
    
    return render_template('account.html',
                         user_id=user_id,
                         stats=stats,
                         member_since=member_since,
                         subscription_status=subscription_status,
                         consent=consent,
                         consent_date=consent_date)

@app.route('/consent', methods=['POST'])
def record_consent():
    """Record user consent for GDPR compliance"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'No session'}), 400
    
    data = request.json
    cookies = data.get('cookies', False)
    analytics = data.get('analytics', False)
    processing = data.get('processing', False)
    
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    
    # Get IP address (for consent verification)
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # Insert or update consent
    c.execute('''INSERT INTO user_consent (user_id, cookies_accepted, data_processing_accepted, ip_address, last_updated)
                 VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                 ON CONFLICT(user_id) DO UPDATE SET
                 cookies_accepted = ?,
                 data_processing_accepted = ?,
                 last_updated = CURRENT_TIMESTAMP''',
              (user_id, analytics, processing, ip_address, analytics, processing))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/account/consent', methods=['POST'])
def update_consent():
    """Update specific consent preferences from account dashboard"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'No session'}), 400
    
    data = request.json
    consent_type = data.get('type')  # 'cookies' or 'processing'
    value = data.get('value', False)
    
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    
    if consent_type == 'cookies':
        c.execute('''UPDATE user_consent SET cookies_accepted = ?, last_updated = CURRENT_TIMESTAMP WHERE user_id = ?''',
                  (value, user_id))
    elif consent_type == 'processing':
        c.execute('''UPDATE user_consent SET data_processing_accepted = ?, last_updated = CURRENT_TIMESTAMP WHERE user_id = ?''',
                  (value, user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/account/export')
def export_data():
    """Export all user data as JSON (GDPR Article 20 - Right to Data Portability)"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/')
    
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    
    # Collect all user data
    export_data = {
        'export_date': datetime.now().isoformat(),
        'user_id': user_id,
        'data': {}
    }
    
    # Messages
    c.execute('SELECT role, content, timestamp FROM messages WHERE user_id = ? ORDER BY timestamp', (user_id,))
    export_data['data']['messages'] = [{'role': r[0], 'content': r[1], 'timestamp': r[2]} for r in c.fetchall()]
    
    # Journal entries
    c.execute('SELECT emotion, intensity, content, timestamp FROM journal WHERE user_id = ? ORDER BY timestamp', (user_id,))
    export_data['data']['journal'] = [{'emotion': r[0], 'intensity': r[1], 'content': r[2], 'timestamp': r[3]} for r in c.fetchall()]
    
    # Insights
    c.execute('SELECT pattern_type, description, detected_at FROM insights WHERE user_id = ? ORDER BY detected_at', (user_id,))
    export_data['data']['insights'] = [{'pattern': r[0], 'description': r[1], 'detected_at': r[2]} for r in c.fetchall()]
    
    # Module progress
    c.execute('''SELECT p.title, m.title, up.started_at, up.completed_at, up.reflection_response 
                 FROM user_progress up 
                 JOIN modules m ON up.module_id = m.id 
                 JOIN paths p ON up.path_id = p.id 
                 WHERE up.user_id = ? 
                 ORDER BY up.started_at''', (user_id,))
    export_data['data']['progress'] = [{'path': r[0], 'module': r[1], 'started': r[2], 'completed': r[3], 'reflection': r[4]} for r in c.fetchall()]
    
    # Community posts
    c.execute('SELECT title, content, category, path_slug, created_at FROM community_posts WHERE user_id = ? ORDER BY created_at', (user_id,))
    export_data['data']['community_posts'] = [{'title': r[0], 'content': r[1], 'category': r[2], 'path': r[3], 'created_at': r[4]} for r in c.fetchall()]
    
    # Community comments
    c.execute('SELECT content, post_id, created_at FROM community_comments WHERE user_id = ? ORDER BY created_at', (user_id,))
    export_data['data']['community_comments'] = [{'content': r[0], 'post_id': r[1], 'created_at': r[2]} for r in c.fetchall()]
    
    # Subscription info (excluding sensitive payment details)
    c.execute('SELECT subscription_status, started_at FROM subscriptions WHERE user_id = ?', (user_id,))
    sub = c.fetchone()
    if sub:
        export_data['data']['subscription'] = {'status': sub[0], 'started': sub[1]}
    
    # Consent records
    c.execute('SELECT cookies_accepted, data_processing_accepted, consent_date FROM user_consent WHERE user_id = ?', (user_id,))
    consent = c.fetchone()
    if consent:
        export_data['data']['consent'] = {'cookies': consent[0], 'processing': consent[1], 'date': consent[2]}
    
    conn.close()
    
    # Return as downloadable JSON file
    from flask import Response
    import json
    
    response = Response(
        json.dumps(export_data, indent=2),
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment;filename=valiant_growth_data_{user_id[:8]}.json'}
    )
    return response

@app.route('/account/delete', methods=['POST'])
def delete_account():
    """Delete account and all user data (GDPR Article 17 - Right to Erasure)"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/')
    
    # Verify deletion confirmation
    confirm = request.form.get('confirm', '')
    if confirm != 'DELETE':
        return redirect('/account')
    
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    
    # Delete all user data (CASCADE or manual deletion)
    c.execute('DELETE FROM messages WHERE user_id = ?', (user_id,))
    c.execute('DELETE FROM journal WHERE user_id = ?', (user_id,))
    c.execute('DELETE FROM insights WHERE user_id = ?', (user_id,))
    c.execute('DELETE FROM user_progress WHERE user_id = ?', (user_id,))
    c.execute('DELETE FROM community_posts WHERE user_id = ?', (user_id,))
    c.execute('DELETE FROM community_comments WHERE user_id = ?', (user_id,))
    c.execute('DELETE FROM subscriptions WHERE user_id = ?', (user_id,))
    c.execute('DELETE FROM user_consent WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()
    
    # Clear session
    session.clear()
    
    # Redirect to goodbye page or home with message
    return redirect('/?deleted=true')

# ===== GUMROAD WEBHOOK FOR SUBSCRIPTION MANAGEMENT =====

@app.route('/webhook/gumroad', methods=['POST'])
def gumroad_webhook():
    """
    Handle Gumroad subscription events (sale, cancellation, refund)
    
    Gumroad sends webhooks for these events:
    - sale: New subscription created
    - cancellation: User cancelled subscription
    - refund: Subscription refunded
    - subscription_updated: Subscription renewed
    
    Configure in Gumroad: Settings → Advanced → Webhooks
    Webhook URL: https://your-domain.up.railway.app/webhook/gumroad
    """
    try:
        # Get webhook data from Gumroad
        data = request.form.to_dict()
        
        # Extract relevant fields
        event_type = data.get('sale_id') and 'sale'  # Gumroad doesn't send explicit event type
        email = data.get('email')
        license_key = data.get('license_key')
        recurrence = data.get('recurrence')  # 'monthly', 'cancelled', etc.
        refunded = data.get('refunded') == 'true'
        
        # Determine subscription status
        if refunded:
            subscription_status = 'refunded'
        elif recurrence == 'cancelled':
            subscription_status = 'cancelled'
        elif recurrence == 'monthly':
            subscription_status = 'active'
        else:
            subscription_status = 'active'  # Default for new sales
        
        # Calculate expiration date (30 days from now for active subscriptions)
        from datetime import datetime, timedelta
        if subscription_status == 'active':
            expires_at = (datetime.now() + timedelta(days=30)).isoformat()
        elif subscription_status == 'cancelled':
            # If cancelled, set expiration to end of current billing period (30 days from start)
            # Allow continued access until period ends
            expires_at = (datetime.now() + timedelta(days=30)).isoformat()
        else:
            expires_at = datetime.now().isoformat()  # Expired immediately for refunds
        
        conn = sqlite3.connect('healing_guru_chat.db')
        c = conn.cursor()
        
        # Try to find existing subscription by license key or email
        c.execute("""SELECT user_id FROM subscriptions WHERE gumroad_license_key = ?""", (license_key,))
        existing = c.fetchone()
        
        if existing:
            # Update existing subscription
            user_id = existing[0]
            c.execute("""UPDATE subscriptions 
                       SET subscription_status = ?,
                           expires_at = ?
                       WHERE user_id = ?""",
                     (subscription_status, expires_at, user_id))
            
            # Log the update
            print(f"[WEBHOOK] Updated subscription for user {user_id}: {subscription_status}, expires: {expires_at}")
        else:
            # New subscription - create placeholder
            # Note: User will need to verify license key on first login to link to their session
            # We can't create a user_id here because we don't have their session
            print(f"[WEBHOOK] New subscription received: {license_key}, status: {subscription_status}")
            # Store in a separate table for pending verification
            c.execute("""CREATE TABLE IF NOT EXISTS pending_subscriptions
                       (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        license_key TEXT UNIQUE,
                        email TEXT,
                        subscription_status TEXT,
                        expires_at DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
            
            c.execute("""INSERT OR REPLACE INTO pending_subscriptions 
                       (license_key, email, subscription_status, expires_at)
                       VALUES (?, ?, ?, ?)""",
                     (license_key, email, subscription_status, expires_at))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Webhook processed'}), 200
        
    except Exception as e:
        print(f"[WEBHOOK ERROR] {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/verify-license', methods=['POST'])
def verify_license():
    """
    Allow user to verify their Gumroad license key and activate premium access
    This links the Gumroad purchase to their session user_id
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'No session'}), 400
    
    data = request.json
    license_key = data.get('license_key', '').strip()
    
    if not license_key:
        return jsonify({'error': 'License key required'}), 400
    
    conn = sqlite3.connect('healing_guru_chat.db')
    c = conn.cursor()
    
    # Check if license key exists in pending subscriptions
    c.execute("""SELECT email, subscription_status, expires_at 
                 FROM pending_subscriptions 
                 WHERE license_key = ?""", (license_key,))
    pending = c.fetchone()
    
    if pending:
        email, status, expires_at = pending
        
        # Move to active subscriptions table
        c.execute("""INSERT OR REPLACE INTO subscriptions 
                   (user_id, gumroad_license_key, subscription_status, expires_at, started_at)
                   VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                 (user_id, license_key, status, expires_at))
        
        # Remove from pending
        c.execute("""DELETE FROM pending_subscriptions WHERE license_key = ?""", (license_key,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Premium access activated!',
            'status': status,
            'expires': expires_at
        })
    else:
        # Check if already verified
        c.execute("""SELECT subscription_status FROM subscriptions 
                   WHERE gumroad_license_key = ?""", (license_key,))
        existing = c.fetchone()
        conn.close()
        
        if existing:
            return jsonify({
                'success': True,
                'message': 'License already verified',
                'status': existing[0]
            })
        else:
            return jsonify({
                'error': 'Invalid license key or not found. Please check your Gumroad purchase confirmation email.'
            }), 404

if __name__ == '__main__':
    import os
    # Get port from environment variable (Railway) or use 5002 for local
    port = int(os.environ.get('PORT', 5002))
    # Allow external connections
    app.run(debug=False, host='0.0.0.0', port=port)
