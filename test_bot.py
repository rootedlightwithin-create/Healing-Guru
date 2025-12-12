#!/usr/bin/env python3
"""
Healing Guru Test Bot
Automatically tests the app with various scenarios and reports issues
"""

import requests
import json
import time
from datetime import datetime

# Test against Railway deployment
APP_URL = "https://valiant-growth-production-3977.up.railway.app"
# Or test locally:
# APP_URL = "http://localhost:5002"

class TestBot:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.errors = []
        
    def send_message(self, message):
        """Send a message to the chat API"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json={"message": message},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'response': data.get('message', ''),  # API returns 'message' not 'response'
                    'pattern': data.get('pattern'),
                    'emotion': data.get('emotion')
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_scenario(self, category, test_message, expected_patterns=None, should_not_contain=None):
        """Test a specific scenario"""
        print(f"\n🧪 Testing: {category}")
        print(f"   Message: '{test_message}'")
        
        result = self.send_message(test_message)
        
        if not result['success']:
            error = f"❌ FAIL: {category} - {result['error']}"
            print(error)
            self.errors.append(error)
            self.test_results.append({
                'category': category,
                'message': test_message,
                'status': 'FAIL',
                'error': result['error']
            })
            return False
        
        response_text = result['response']
        detected_pattern = result.get('pattern')
        
        # Check if response is appropriate
        issues = []
        
        if not response_text or len(response_text) < 10:
            issues.append("Response too short or empty")
        
        if expected_patterns and detected_pattern not in expected_patterns:
            issues.append(f"Expected pattern {expected_patterns}, got {detected_pattern}")
        
        if should_not_contain:
            for phrase in should_not_contain:
                if phrase.lower() in response_text.lower():
                    issues.append(f"Response should not contain '{phrase}'")
        
        if issues:
            error = f"❌ FAIL: {category}\n   Issues: {', '.join(issues)}\n   Response: {response_text[:100]}..."
            print(error)
            self.errors.append(error)
            self.test_results.append({
                'category': category,
                'message': test_message,
                'status': 'FAIL',
                'issues': issues,
                'pattern': detected_pattern,
                'response': response_text[:200]
            })
            return False
        else:
            print(f"   ✅ PASS - Pattern: {detected_pattern}")
            print(f"   Response: {response_text[:100]}...")
            self.test_results.append({
                'category': category,
                'message': test_message,
                'status': 'PASS',
                'pattern': detected_pattern,
                'response': response_text[:200]
            })
            return True
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("\n" + "="*70)
        print("🤖 HEALING GURU TEST BOT - Starting Tests")
        print("="*70)
        
        # Test 1: Greetings
        print("\n📋 CATEGORY: Greetings")
        self.test_scenario("Simple greeting", "Hi")
        self.test_scenario("Friendly greeting", "Hey friend, how are you?")
        
        # Test 2: Neutral sharing
        print("\n📋 CATEGORY: Neutral Sharing")
        self.test_scenario("Want to share", "I wanted to share something with you", 
                          should_not_contain=["difficult", "challenging", "struggle"])
        self.test_scenario("Have news", "I have some news")
        
        # Test 3: False positive detection
        print("\n📋 CATEGORY: Negation Detection (No False Positives)")
        self.test_scenario("Not doing good", "I'm not doing too good",
                          should_not_contain=["love that you're", "celebrate", "wonderful"])
        self.test_scenario("Not feeling great", "I'm not feeling great today")
        
        # Test 4: Work - Stressed
        print("\n📋 CATEGORY: Work Stress")
        self.test_scenario("Boss was mean", "My boss was mean and I had too much to do",
                          expected_patterns=['life_topic_work'])
        self.test_scenario("Overwhelmed at work", "Feeling overwhelmed by my workload",
                          expected_patterns=['life_topic_work'])
        self.test_scenario("Don't want to go", "I don't want to go back to work tomorrow")
        self.test_scenario("Feeling undervalued", "I've put in so much effort but no one seems to notice at work")
        self.test_scenario("Conflict with colleague", "I had a tense exchange with a colleague and keep replaying it")
        self.test_scenario("Afraid of losing job", "I'm sensing instability at the company and feel nervous")
        
        # Test 5: Work - Celebration
        print("\n📋 CATEGORY: Work Celebration")
        self.test_scenario("Got praised", "I got praised at work today!",
                          expected_patterns=['life_topic_work'])
        self.test_scenario("Finished project", "I finally finished that big project")
        self.test_scenario("Excited about promotion", "I got promoted! I want to celebrate this moment")
        
        # Test 6: Relationships - Stressed
        print("\n📋 CATEGORY: Relationship Stress")
        self.test_scenario("Friend upset me", "My friend upset me today",
                          expected_patterns=['life_topic_relationships'])
        self.test_scenario("Feel misunderstood", "I don't feel understood at home")
        self.test_scenario("Feeling left out", "My friends met up without me and it triggered abandonment feelings")
        self.test_scenario("Healing from fallout", "A close friend said something hurtful and I'm unsure how to rebuild trust")
        self.test_scenario("Growing apart", "I'm noticing misalignment and grieving the drifting of a friendship")
        
        # Test 7: Relationships - Celebration
        print("\n📋 CATEGORY: Relationship Celebration")
        self.test_scenario("Lovely day with mum", "I had a lovely day with my mum",
                          expected_patterns=['life_topic_relationships'])
        self.test_scenario("Unexpected kindness", "A friend supported me in a moment I didn't ask for")
        self.test_scenario("Making new friend", "I'm making a new friend and feel excited but unsure")
        
        # Test 8: Family scenarios
        print("\n📋 CATEGORY: Family Dynamics")
        self.test_scenario("Tension with parent", "I had a disagreement with my dad that brought up old childhood patterns")
        self.test_scenario("Setting boundaries", "I'm learning to say no to my family but feel guilty")
        self.test_scenario("Family milestone", "My sister just had a baby and I want to share this joy")
        self.test_scenario("Caring for elderly parent", "I'm caring for my elderly parent and feel exhausted and guilty")
        self.test_scenario("Feeling unseen in family", "I'm doing everything right but still feel misunderstood by my family")
        
        # Test 9: Romantic relationships
        print("\n📋 CATEGORY: Romantic Relationships")
        self.test_scenario("After argument", "I love my partner but feel hurt after our argument")
        self.test_scenario("New relationship", "I'm in a new relationship and have butterflies mixed with fear")
        self.test_scenario("Breakup processing", "The relationship ended and I feel empty and confused")
        self.test_scenario("Feeling neglected", "My partner isn't showing affection and it's affecting my self-worth")
        self.test_scenario("Celebrating love", "We had a beautiful deep conversation and I want to honor it")
        
        # Test 10: Pets
        print("\n📋 CATEGORY: Pets")
        self.test_scenario("Dog did something cute", "My dog did something so cute today")
        self.test_scenario("Cat is sick", "My cat is unwell and I'm scared")
        self.test_scenario("Pet sick", "My pet is really sick and I feel helpless")
        self.test_scenario("Pet funny", "My pet did something hilarious")
        self.test_scenario("Grieving pet", "I'm grieving my pet who passed away")
        self.test_scenario("Training challenges", "I'm feeling frustrated with training my dog")
        self.test_scenario("Bonding with new pet", "I'm bonding with my new rescue and it's so sweet")
        
        # Test 11: Home
        print("\n📋 CATEGORY: Home")
        self.test_scenario("Tidied space", "I finally tidied my space")
        self.test_scenario("Home feels chaotic", "My home feels really chaotic")
        self.test_scenario("Overwhelmed with chores", "Laundry, dishes, clutter - everything feels like a mountain")
        self.test_scenario("Moving homes", "I'm moving and feel stressed, excited, and nostalgic")
        self.test_scenario("Conflict with neighbor", "I had a conflict with my neighbor over noise")
        self.test_scenario("Unsafe at home", "I don't feel safe in my home environment")
        self.test_scenario("Loving home", "I feel so grateful for my home space")
        
        # Test 12: Money
        print("\n📋 CATEGORY: Money")
        self.test_scenario("Money is tight", "Money is really tight right now")
        self.test_scenario("Paid something off", "I just paid off my credit card!")
        self.test_scenario("Unexpected bill", "An unexpected bill arrived and I feel panicked")
        self.test_scenario("Worried about rent", "I'm worried about making rent this month")
        self.test_scenario("Big financial decision", "I'm considering a big financial decision and feel confused")
        self.test_scenario("Unexpected money", "I received unexpected money and feel grateful")
        
        # Test 13: Emotional & health
        print("\n📋 CATEGORY: Health & Emotional Well-being")
        self.test_scenario("Anxious no reason", "I'm feeling anxious but don't know why")
        self.test_scenario("Chronic fatigue", "I'm tired of feeling tired all the time")
        self.test_scenario("Therapy breakthrough", "I had a successful therapy session with breakthroughs")
        self.test_scenario("Self-worth struggle", "I'm struggling with feeling not enough")
        self.test_scenario("Personal growth", "I noticed I handled something better than I used to")
        
        # Test 14: Emotional states
        print("\n📋 CATEGORY: Emotional States")
        self.test_scenario("Feeling anxious", "I'm feeling really anxious")
        self.test_scenario("Feel hopeless", "I feel completely hopeless")
        self.test_scenario("Can't cope", "I can't cope anymore")
        
        # Test 15: Bullying/harm
        print("\n📋 CATEGORY: Bullying & Conflict")
        self.test_scenario("Being bullied", "Someone is bullying me at school")
        self.test_scenario("I hurt someone", "I hurt someone and I feel guilty")
        self.test_scenario("I snapped", "I lost control and snapped at them")
        
        # Test 16: School & academic
        print("\n📋 CATEGORY: School & Academic Life")
        self.test_scenario("Homework overwhelm", "I'm overwhelmed by homework and feel pressure piling up")
        self.test_scenario("Exam stress", "I'm stressed about exams and afraid of failing")
        self.test_scenario("Can't focus", "I'm struggling to focus in class")
        self.test_scenario("Good grade excited", "I got a good grade and want to share this win")
        self.test_scenario("Teacher conflict", "I had a misunderstanding with my teacher")
        self.test_scenario("Falling behind", "I'm falling behind in school and feel ashamed to ask for help")
        self.test_scenario("New school", "I'm starting a new school and feel nervous and hopeful")
        
        # Test 17: School social
        print("\n📋 CATEGORY: School Social Life")
        self.test_scenario("Excluded group chat", "I saw my friends talking in a group chat without me")
        self.test_scenario("Rumors spread", "Rumors are being spread about me and I feel hurt")
        self.test_scenario("Best friend drifting", "My best friend is drifting away and I can't explain why")
        self.test_scenario("Social anxiety school", "I have social anxiety and overthink everything at school")
        self.test_scenario("Invited nervous", "I got invited to something but I'm nervous about going")
        
        # Test 18: Teen family
        print("\n📋 CATEGORY: Teen Family Dynamics")
        self.test_scenario("Arguing with parents", "I'm arguing with my parents and feel unheard")
        self.test_scenario("Sibling conflict", "My sibling keeps crossing my boundaries")
        self.test_scenario("Pressure to succeed", "My parents are pushing too hard and I'm burnt out")
        self.test_scenario("Parents divorce", "My parents are divorcing and I'm trying to make sense of it")
        self.test_scenario("Invisible at home", "I feel invisible at home, my emotions are dismissed")
        
        # Test 19: Teen romantic
        print("\n📋 CATEGORY: Teen Romantic Life")
        self.test_scenario("First heartbreak", "I had my first heartbreak and it hurts so much")
        self.test_scenario("Crush anxiety", "I'm overthinking every interaction with my crush")
        self.test_scenario("Got ghosted", "They just ghosted me without explanation")
        self.test_scenario("Pressure not ready", "I feel pressured to do things I'm not ready for")
        
        # Test 20: Identity & self-worth
        print("\n📋 CATEGORY: Identity & Self-Worth")
        self.test_scenario("Body insecurity", "I feel insecure about my body")
        self.test_scenario("Not good enough", "I don't feel good enough")
        self.test_scenario("Questioning identity", "I'm trying to understand who I am")
        self.test_scenario("Feeling different", "I feel different and don't fit in any boxes")
        self.test_scenario("Lost disconnected", "Nothing feels exciting, everything feels heavy")
        
        # Test 21: Digital life
        print("\n📋 CATEGORY: Digital Life")
        self.test_scenario("Online bullying", "Someone left harsh comments online and it really stings")
        self.test_scenario("Embarrassing post", "I posted something embarrassing and can't stop thinking about it")
        self.test_scenario("Phone addiction", "I know I scroll too much but can't stop")
        self.test_scenario("Group chat drama", "There's drama in our group chat with screenshots and misunderstandings")
        
        # Test 22: Creative & performance
        print("\n📋 CATEGORY: Creative & Performance")
        self.test_scenario("Performance anxiety", "I have performance anxiety before my sports event")
        self.test_scenario("Not chosen team", "I didn't get chosen for the team and feel rejected")
        self.test_scenario("Proud of creation", "I made something I'm proud of but shy to share")
        self.test_scenario("Comparing to others", "I keep comparing myself to more talented peers")
        
        # Test 23: Cultural scenarios
        print("\n📋 CATEGORY: Cultural & Identity")
        self.test_scenario("Family reputation pressure", "I feel pressure to achieve for my family's reputation")
        self.test_scenario("First in family higher ed", "I'm the first in my family going to university")
        self.test_scenario("Career expectations", "My family wants me to be a doctor but I want something else")
        self.test_scenario("Adult responsibilities early", "I have to translate and help my parents with everything")
        self.test_scenario("Cultural duty conflict", "I want independence but feel guilty about cultural duty")
        self.test_scenario("Emotions not expressed", "In my culture we don't talk about emotions openly")
        self.test_scenario("Language barriers", "I struggle to express complex feelings in English")
        self.test_scenario("Caught between cultures", "I feel caught between cultures, not enough for either side")
        self.test_scenario("Accent judgment", "People mock my accent and it hurts")
        self.test_scenario("Mixed heritage", "I'm mixed heritage and trying to belong to multiple places")
        self.test_scenario("Religious expectations", "I'm navigating religious rules and guilt around my choices")
        self.test_scenario("Parents sacrificed", "My parents migrated and sacrificed so much for me")
        self.test_scenario("Cultural festival joy", "I'm excited about our cultural festival and want to share traditions")
        self.test_scenario("Heritage pride", "I'm proud of my heritage and want to share my culture")
        
        # Test 24: Discrimination
        print("\n📋 CATEGORY: Discrimination & Safety")
        self.test_scenario("Experiencing racism", "I experienced racism today and feel deeply hurt")
        self.test_scenario("Microaggressions", "I keep experiencing microaggressions and feel unsafe")
        self.test_scenario("Invasive questions", "People keep asking where I'm really from")
        self.test_scenario("Online hate ethnicity", "I received online hate because of my ethnicity")
        
        # Test 25: Spiritual
        print("\n📋 CATEGORY: Spiritual & Ritual")
        self.test_scenario("Spiritual disconnection", "I feel disconnected from my spiritual traditions")
        self.test_scenario("Spiritual practices shamed", "People judge my spiritual practices")
        self.test_scenario("Spiritual milestone", "I'm going through a spiritual coming-of-age ceremony")
        
        # Test 26: Time period awareness
        print("\n📋 CATEGORY: Time Period Detection")
        self.test_scenario("Had a bad week", "I've had a bad week",
                          should_not_contain=["How long has this been"])
        self.test_scenario("Struggling for months", "I've been struggling for 3 months")
        
        # Test 27: Crisis situations
        print("\n📋 CATEGORY: Crisis Detection")
        self.test_scenario("Self-harm mention", "I want to hurt myself")
        self.test_scenario("Suicidal ideation", "I don't want to be here anymore")
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*70)
        print("📊 TEST REPORT")
        print("="*70)
        
        total_tests = len(self.test_results)
        passed = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed = len([t for t in self.test_results if t['status'] == 'FAIL'])
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total_tests)*100:.1f}%")
        
        if self.errors:
            print("\n" + "="*70)
            print("❌ FAILED TESTS:")
            print("="*70)
            for error in self.errors:
                print(f"\n{error}")
        
        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"test_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'total_tests': total_tests,
                'passed': passed,
                'failed': failed,
                'success_rate': f"{(passed/total_tests)*100:.1f}%",
                'results': self.test_results,
                'errors': self.errors
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        print("\n" + "="*70)

if __name__ == "__main__":
    print("\n🤖 Healing Guru Test Bot")
    print("Testing app at:", APP_URL)
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    bot = TestBot(APP_URL)
    bot.run_all_tests()
