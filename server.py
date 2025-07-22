#!/usr/bin/env python3
"""
Multi-User Flashcard Quiz Server
Handles multiple clients, manages quiz sessions, and broadcasts leaderboards.
"""

import socket
import threading
import json
import random
import time
import sys
from typing import Dict, List, Any

class QuizServer:
    def __init__(self, host='localhost', port=12345, questions_file='questions.json'):
        self.host = host
        self.port = port
        self.questions_file = questions_file
        
        # Server state
        self.clients = {}  # {conn: {'username': str, 'topic': str, 'score': int, 'answered': int}}
        self.questions_data = {}
        self.quiz_active = False
        self.max_questions = 5  # Number of questions per quiz
        self.current_round = 0
        self.lock = threading.Lock()
        
        # Load questions
        self.load_questions()
        
        # Socket setup
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    def load_questions(self):
        """Load quiz questions from JSON file"""
        try:
            with open(self.questions_file, 'r', encoding='utf-8') as f:
                self.questions_data = json.load(f)
            print(f"✅ Loaded questions for topics: {list(self.questions_data.keys())}")
        except FileNotFoundError:
            print(f"❌ Error: {self.questions_file} not found!")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"❌ Error: Invalid JSON in {self.questions_file}")
            sys.exit(1)
    
    def start_server(self):
        """Start the quiz server"""
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"🎓 Quiz Server started on {self.host}:{self.port}")
            print("📚 Available topics:", ", ".join(self.questions_data.keys()))
            print("⏳ Waiting for clients to connect...")
            
            while True:
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"🔗 New connection from {address}")
                    
                    # Start a new thread for each client
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except Exception as e:
                    print(f"❌ Error accepting connection: {e}")
                    
        except Exception as e:
            print(f"❌ Error starting server: {e}")
        finally:
            self.server_socket.close()
    
    def handle_client(self, client_socket, address):
        """Handle individual client connection"""
        try:
            # Initialize client data
            with self.lock:
                self.clients[client_socket] = {
                    'username': '',
                    'topic': '',
                    'score': 0,
                    'answered': 0,
                    'address': address
                }
            
            while True:
                try:
                    # Receive message from client
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data:
                        break
                    
                    message = json.loads(data)
                    self.process_message(client_socket, message)
                    
                except json.JSONDecodeError:
                    self.send_error(client_socket, "Invalid JSON format")
                except Exception as e:
                    print(f"❌ Error handling client {address}: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ Error with client {address}: {e}")
        finally:
            self.disconnect_client(client_socket)
    
    def process_message(self, client_socket, message):
        """Process different types of messages from clients"""
        msg_type = message.get('type')
        
        if msg_type == 'register':
            self.handle_registration(client_socket, message)
        elif msg_type == 'topic':
            self.handle_topic_selection(client_socket, message)
        elif msg_type == 'answer':
            self.handle_answer(client_socket, message)
        elif msg_type == 'ready':
            self.handle_ready(client_socket)
        elif msg_type == 'restart':
            self.handle_restart(client_socket)
        elif msg_type == 'disconnect':
            self.handle_manual_disconnect(client_socket, message)
        else:
            self.send_error(client_socket, f"Unknown message type: {msg_type}")
    
    def handle_registration(self, client_socket, message):
        """Handle client registration"""
        username = message.get('username', '').strip()
        
        if not username:
            self.send_error(client_socket, "Username cannot be empty")
            return
        
        # Check if username is already taken
        with self.lock:
            for client_data in self.clients.values():
                if client_data['username'] == username:
                    self.send_error(client_socket, "Username already taken")
                    return
            
            # Register the user
            self.clients[client_socket]['username'] = username
        
        # Send available topics
        response = {
            'type': 'topics',
            'topics': list(self.questions_data.keys()),
            'message': f"Welcome {username}! Please select a topic."
        }
        self.send_message(client_socket, response)
        print(f"👤 {username} registered from {self.clients[client_socket]['address']}")
    
    def handle_topic_selection(self, client_socket, message):
        """Handle topic selection"""
        topic = message.get('topic')
        
        if topic not in self.questions_data:
            self.send_error(client_socket, f"Invalid topic: {topic}")
            return
        
        with self.lock:
            self.clients[client_socket]['topic'] = topic
            username = self.clients[client_socket]['username']
        
        # Send confirmation and start quiz
        response = {
            'type': 'topic_confirmed',
            'topic': topic,
            'message': f"Topic '{topic}' selected! Get ready for {self.max_questions} questions."
        }
        self.send_message(client_socket, response)
        print(f"📖 {username} selected topic: {topic}")
        
        # Send first question
        self.send_question(client_socket)
    
    def handle_ready(self, client_socket):
        """Handle client ready signal"""
        self.send_question(client_socket)
    
    def send_question(self, client_socket):
        """Send a random question to the client"""
        with self.lock:
            client_data = self.clients[client_socket]
            
            if client_data['answered'] >= self.max_questions:
                self.send_quiz_complete(client_socket)
                return
            
            topic = client_data['topic']
            username = client_data['username']
        
        if topic not in self.questions_data:
            self.send_error(client_socket, "Topic not selected")
            return
        
        # Get random question
        questions = self.questions_data[topic]
        question_data = random.choice(questions)
        
        response = {
            'type': 'question',
            'question': question_data['q'],
            'choices': question_data['choices'],
            'question_number': client_data['answered'] + 1,
            'total_questions': self.max_questions
        }
        
        # Store correct answer for this client
        with self.lock:
            self.clients[client_socket]['current_answer'] = question_data['a']
        
        self.send_message(client_socket, response)
        print(f"❓ Sent question {client_data['answered'] + 1} to {username}")
    
    def handle_answer(self, client_socket, message):
        """Handle client answer"""
        user_answer = message.get('answer', '').strip()
        
        with self.lock:
            client_data = self.clients[client_socket]
            correct_answer = client_data.get('current_answer', '')
            username = client_data['username']
            
            # Check if answer is correct
            is_correct = user_answer.lower() == correct_answer.lower()
            
            if is_correct:
                client_data['score'] += 1
            
            client_data['answered'] += 1
            
            # Prepare response
            response = {
                'type': 'result',
                'correct': is_correct,
                'correct_answer': correct_answer,
                'your_answer': user_answer,
                'score': client_data['score'],
                'questions_answered': client_data['answered']
            }
        
        self.send_message(client_socket, response)
        
        status = "✅ Correct!" if is_correct else "❌ Wrong"
        print(f"{status} {username} answered: {user_answer} (correct: {correct_answer})")
        
        # Send leaderboard
        self.broadcast_leaderboard()
        
        # Check if quiz is complete
        if client_data['answered'] >= self.max_questions:
            self.send_quiz_complete(client_socket)
        else:
            # Send next question after a short delay
            threading.Timer(2.0, self.send_question, args=(client_socket,)).start()
    
    def send_quiz_complete(self, client_socket):
        """Send quiz completion message with enhanced feedback"""
        with self.lock:
            client_data = self.clients[client_socket]
            username = client_data['username']
            score = client_data['score']
            topic = client_data['topic']
        
        percentage = round((score / self.max_questions) * 100, 1)
        
        # Enhanced completion message
        response = {
            'type': 'quiz_complete',
            'final_score': score,
            'total_questions': self.max_questions,
            'percentage': percentage,
            'topic': topic,
            'message': f"Quiz completed! Your final score: {score}/{self.max_questions}",
            'can_restart': True
        }
        
        self.send_message(client_socket, response)
        print(f"🏁 {username} completed {topic} quiz with score: {score}/{self.max_questions} ({percentage}%)")
        
        # Send final leaderboard
        self.broadcast_leaderboard()
        
        # Offer restart option (handled by enhanced client)
    
    def broadcast_leaderboard(self):
        """Broadcast current leaderboard to all clients"""
        with self.lock:
            # Create leaderboard data
            leaderboard = []
            for client_data in self.clients.values():
                if client_data['username']:  # Only include registered users
                    leaderboard.append({
                        'username': client_data['username'],
                        'score': client_data['score'],
                        'answered': client_data['answered'],
                        'topic': client_data['topic']
                    })
            
            # Sort by score, then by questions answered
            leaderboard.sort(key=lambda x: (x['score'], x['answered']), reverse=True)
        
        # Prepare leaderboard message
        leaderboard_msg = {
            'type': 'leaderboard',
            'leaderboard': leaderboard
        }
        
        # Send to all clients
        for client_socket in list(self.clients.keys()):
            try:
                self.send_message(client_socket, leaderboard_msg)
            except:
                # Client might be disconnected
                pass
    
    def send_message(self, client_socket, message):
        """Send JSON message to client"""
        try:
            data = json.dumps(message) + '\n'
            client_socket.send(data.encode('utf-8'))
        except Exception as e:
            print(f"❌ Error sending message: {e}")
    
    def send_error(self, client_socket, error_message):
        """Send error message to client"""
        response = {
            'type': 'error',
            'message': error_message
        }
        self.send_message(client_socket, response)
    
    def disconnect_client(self, client_socket):
        """Handle client disconnection"""
        try:
            with self.lock:
                if client_socket in self.clients:
                    username = self.clients[client_socket].get('username', 'Unknown')
                    address = self.clients[client_socket].get('address', 'Unknown')
                    del self.clients[client_socket]
                    print(f"👋 {username} disconnected from {address}")
            
            client_socket.close()
            
            # Broadcast updated leaderboard
            self.broadcast_leaderboard()
            
        except Exception as e:
            print(f"❌ Error disconnecting client: {e}")
    
    def handle_restart(self, client_socket):
        """Handle client restart request"""
        with self.lock:
            if client_socket in self.clients:
                # Reset client state for new quiz
                self.clients[client_socket]['score'] = 0
                self.clients[client_socket]['answered'] = 0
                self.clients[client_socket]['topic'] = ''
                username = self.clients[client_socket]['username']
                
                print(f"🔄 {username} requested to restart quiz")
                
                # Send available topics again
                response = {
                    'type': 'topics',
                    'topics': list(self.questions_data.keys()),
                    'message': f"Welcome back {username}! Ready for another challenge?"
                }
                self.send_message(client_socket, response)
    
    def handle_manual_disconnect(self, client_socket, message):
        """Handle manual disconnect message from client"""
        username = message.get('username', 'Unknown')
        print(f"👋 {username} manually disconnected")
        self.disconnect_client(client_socket)

def main():
    """Main function to start the server"""
    print("🎓 Multi-User Flashcard Quiz Server")
    print("=" * 40)
    
    # Create and start server
    server = QuizServer()
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Server shutting down...")
    except Exception as e:
        print(f"❌ Server error: {e}")
    finally:
        try:
            server.server_socket.close()
        except:
            pass

if __name__ == "__main__":
    main()
