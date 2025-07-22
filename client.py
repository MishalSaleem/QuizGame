#!/usr/bin/env python3
"""
Multi-User Flashcard Quiz Client
Connects to quiz server, participates in quizzes, and displays results.
"""

import socket
import json
import threading
import time
import sys
import os

class QuizClient:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.username = ""
        self.quiz_active = False
        
    def connect_to_server(self):
        """Connect to the quiz server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"🔗 Connected to quiz server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            return False
    
    def start_client(self):
        """Start the quiz client"""
        if not self.connect_to_server():
            return
        
        # Start listening thread
        listen_thread = threading.Thread(target=self.listen_to_server, daemon=True)
        listen_thread.start()
        
        # Registration process
        self.register_user()
        
        # Keep the client running
        try:
            while self.connected:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Disconnecting...")
        finally:
            self.disconnect()
    
    def register_user(self):
        """Register user with the server"""
        while True:
            username = input("👤 Enter your username: ").strip()
            if username:
                self.username = username
                message = {
                    'type': 'register',
                    'username': username
                }
                self.send_message(message)
                break
            else:
                print("❌ Username cannot be empty!")
    
    def listen_to_server(self):
        """Listen for messages from the server"""
        buffer = ""
        while self.connected:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            message = json.loads(line.strip())
                            self.handle_server_message(message)
                        except json.JSONDecodeError:
                            print("❌ Received invalid JSON from server")
                            
            except Exception as e:
                if self.connected:
                    print(f"❌ Error receiving data: {e}")
                break
        
        self.connected = False
    
    def handle_server_message(self, message):
        """Handle different types of messages from server"""
        msg_type = message.get('type')
        
        if msg_type == 'topics':
            self.handle_topics(message)
        elif msg_type == 'topic_confirmed':
            self.handle_topic_confirmed(message)
        elif msg_type == 'question':
            self.handle_question(message)
        elif msg_type == 'result':
            self.handle_result(message)
        elif msg_type == 'leaderboard':
            self.handle_leaderboard(message)
        elif msg_type == 'quiz_complete':
            self.handle_quiz_complete(message)
        elif msg_type == 'error':
            self.handle_error(message)
        else:
            print(f"❓ Unknown message type: {msg_type}")
    
    def handle_topics(self, message):
        """Handle topic selection"""
        topics = message.get('topics', [])
        print(f"\n{message.get('message', '')}")
        print("\n📚 Available topics:")
        
        for i, topic in enumerate(topics, 1):
            print(f"  {i}. {topic}")
        
        while True:
            try:
                choice = input(f"\n🎯 Select topic (1-{len(topics)}): ").strip()
                topic_index = int(choice) - 1
                
                if 0 <= topic_index < len(topics):
                    selected_topic = topics[topic_index]
                    message = {
                        'type': 'topic',
                        'topic': selected_topic
                    }
                    self.send_message(message)
                    break
                else:
                    print(f"❌ Please enter a number between 1 and {len(topics)}")
                    
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                print("\n👋 Disconnecting...")
                self.disconnect()
                return
    
    def handle_topic_confirmed(self, message):
        """Handle topic confirmation"""
        topic = message.get('topic')
        print(f"\n✅ {message.get('message', '')}")
        print(f"📖 Topic: {topic}")
        print("⏳ Get ready for your first question...\n")
        self.quiz_active = True
    
    def handle_question(self, message):
        """Handle incoming questions"""
        question = message.get('question')
        choices = message.get('choices', [])
        question_num = message.get('question_number', 0)
        total_questions = message.get('total_questions', 0)
        
        self.clear_screen()
        print("=" * 60)
        print(f"❓ QUESTION {question_num}/{total_questions}")
        print("=" * 60)
        print(f"\n{question}\n")
        
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")
        
        while True:
            try:
                answer_choice = input(f"\n🎯 Your answer (1-{len(choices)}): ").strip()
                choice_index = int(answer_choice) - 1
                
                if 0 <= choice_index < len(choices):
                    selected_answer = choices[choice_index]
                    answer_message = {
                        'type': 'answer',
                        'answer': selected_answer
                    }
                    self.send_message(answer_message)
                    break
                else:
                    print(f"❌ Please enter a number between 1 and {len(choices)}")
                    
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                print("\n👋 Disconnecting...")
                self.disconnect()
                return
    
    def handle_result(self, message):
        """Handle answer results"""
        is_correct = message.get('correct', False)
        correct_answer = message.get('correct_answer', '')
        user_answer = message.get('your_answer', '')
        score = message.get('score', 0)
        questions_answered = message.get('questions_answered', 0)
        
        print("\n" + "=" * 60)
        if is_correct:
            print("✅ CORRECT! Well done!")
        else:
            print("❌ INCORRECT!")
            print(f"   Your answer: {user_answer}")
            print(f"   Correct answer: {correct_answer}")
        
        print(f"📊 Your current score: {score}/{questions_answered}")
        print("=" * 60)
    
    def handle_leaderboard(self, message):
        """Handle leaderboard updates"""
        leaderboard = message.get('leaderboard', [])
        
        if leaderboard:
            print("\n🏆 CURRENT LEADERBOARD")
            print("-" * 50)
            print(f"{'Rank':<6}{'Player':<15}{'Score':<8}{'Topic':<12}{'Progress'}")
            print("-" * 50)
            
            for i, player in enumerate(leaderboard, 1):
                username = player['username']
                score = player['score']
                answered = player['answered']
                topic = player['topic']
                
                # Highlight current user
                marker = "👤" if username == self.username else "  "
                print(f"{marker}{i:<4}{username:<15}{score:<8}{topic:<12}{answered} questions")
            
            print("-" * 50)
    
    def handle_quiz_complete(self, message):
        """Handle quiz completion"""
        final_score = message.get('final_score', 0)
        total_questions = message.get('total_questions', 0)
        percentage = message.get('percentage', 0)
        
        self.clear_screen()
        print("\n" + "🎉" * 20)
        print("🏁 QUIZ COMPLETED!")
        print("🎉" * 20)
        print(f"\n📊 Your Final Results:")
        print(f"   Score: {final_score}/{total_questions}")
        print(f"   Percentage: {percentage}%")
        
        # Performance message
        if percentage >= 90:
            print("🌟 Excellent work! Outstanding performance!")
        elif percentage >= 80:
            print("🎯 Great job! You did very well!")
        elif percentage >= 70:
            print("👍 Good work! Nice effort!")
        elif percentage >= 60:
            print("📈 Not bad! Keep practicing!")
        else:
            print("💪 Keep studying and try again!")
        
        print("\n⏳ Waiting for final leaderboard...")
        self.quiz_active = False
    
    def handle_error(self, message):
        """Handle error messages"""
        error_msg = message.get('message', 'Unknown error')
        print(f"❌ Error: {error_msg}")
    
    def send_message(self, message):
        """Send JSON message to server"""
        try:
            data = json.dumps(message) + '\n'
            self.socket.send(data.encode('utf-8'))
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            self.connected = False
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("👋 Disconnected from server")

def main():
    """Main function to start the client"""
    print("🎓 Multi-User Flashcard Quiz Client")
    print("=" * 40)
    
    # Get server details
    host = input("🌐 Server host (default: localhost): ").strip()
    if not host:
        host = 'localhost'
    
    port_input = input("🔌 Server port (default: 12345): ").strip()
    try:
        port = int(port_input) if port_input else 12345
    except ValueError:
        port = 12345
        print("❌ Invalid port, using default: 12345")
    
    # Create and start client
    client = QuizClient(host, port)
    
    try:
        client.start_client()
    except KeyboardInterrupt:
        print("\n🛑 Client shutting down...")
    except Exception as e:
        print(f"❌ Client error: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
