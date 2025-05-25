import random
from typing import Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import os # Needed for potential model persistence
import uuid
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import torch
from sentence_transformers import SentenceTransformer, util
import numpy as np
import json
import re

# Define conversation states
STATE_INITIAL = 'initial'
STATE_ID_PROVIDED = 'id_provided'
STATE_ASKING_NAME = 'asking_name'
STATE_ASKING_COURSE = 'asking_course'
STATE_VERIFIED_SUCCESS = 'verified_success'
STATE_VERIFIED_FAIL = 'verified_fail'
STATE_OTHER = 'other'
STATE_ID_FOUND = 'id_found'

class CertificateChatbot:
    def __init__(self, certificates_db: Dict[str, Dict[str, Any]]):
        # Initialize the transformer models
        self.intent_classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        
        # Initialize sentence transformer for semantic similarity
        self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Store certificates database reference
        self.certificates_db = certificates_db
        
        # Define intents
        self.intents = {
            'greeting': ['hello', 'hi', 'hey', 'greetings'],
            'farewell': ['goodbye', 'bye', 'see you', 'farewell'],
            'thanks': ['thank you', 'thanks', 'appreciate it'],
            'ask_name': ['who is this for', 'recipient name', 'who received this'],
            'ask_course': ['what course', 'which course', 'course name'],
            'ask_date': ['when was it issued', 'issue date', 'date of issue'],
            'ask_id': ['what is the id', 'certificate id', 'verification code'],
            'ask_all': ['tell me everything', 'show all details', 'all information']
        }
        
        # Define conversation states
        self.STATE_INITIAL = 'initial'
        self.STATE_ID_FOUND = 'id_found'
        self.STATE_VERIFIED_SUCCESS = 'verified_success'
        self.STATE_VERIFIED_FAIL = 'verified_fail'
        self.STATE_OTHER = 'other'
        
        # Store conversation states
        self.conversation_states = {}

    def is_certificate_id(self, text: str) -> bool:
        """Check if the input text is a certificate ID in UUID format."""
        # UUID format: 8-4-4-4-12 hexadecimal digits
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, text.strip().lower()))
    
    def get_intent(self, text: str) -> str:
        """Classify the intent of the user's message using transformers."""
        # Prepare the text for classification
        candidate_labels = list(self.intents.keys())
        
        # Get classification results
        result = self.intent_classifier(
            text,
            candidate_labels=candidate_labels,
            hypothesis_template="This text is about {}."
        )
        
        # Return the highest confidence intent
        return result['labels'][0]
    
    def get_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        # Encode the texts
        embedding1 = self.sentence_transformer.encode(text1, convert_to_tensor=True)
        embedding2 = self.sentence_transformer.encode(text2, convert_to_tensor=True)
        
        # Calculate cosine similarity
        similarity = util.pytorch_cos_sim(embedding1, embedding2)
        return similarity.item()
    
    def get_certificate_summary(self, certificate_data: Dict[str, Any]) -> str:
        """Generate a summary of all certificate details."""
        return (
            f"Here are all the details for certificate {certificate_data['certificate_id']}:\n"
            f"• Recipient: {certificate_data['recipient_name']}\n"
            f"• Course: {certificate_data['course_name']}\n"
            f"• Issue Date: {certificate_data['issue_date']}\n"
            f"• Certificate ID: {certificate_data['certificate_id']}"
        )

    def get_bot_response(self, conversation_id: str, user_input: str, certificate_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get bot response based on user input and conversation state."""
        # Get or initialize conversation state
        if conversation_id not in self.conversation_states:
            self.conversation_states[conversation_id] = {
                "state": self.STATE_INITIAL,
                "certificate_data": None
            }
        
        state = self.conversation_states[conversation_id]
        
        # If certificate data is provided (from QR scan), update state
        if certificate_data:
            state["certificate_data"] = certificate_data
            state["state"] = self.STATE_ID_FOUND
            return {
                "response": f"I found a certificate for {certificate_data['recipient_name']}. What would you like to know about it?",
                "conversation_id": conversation_id
            }
        
        # Get intent from user input
        intent = self.get_intent(user_input)
        
        # Handle different states
        if state["state"] == self.STATE_INITIAL:
            # Check if input is a certificate ID
            if self.is_certificate_id(user_input):
                # Check if certificate exists in database
                if user_input in self.certificates_db:
                    state["certificate_data"] = self.certificates_db[user_input]
                    state["state"] = self.STATE_ID_FOUND
                    return {
                        "response": f"I found a certificate for {state['certificate_data']['recipient_name']}. What would you like to know about it?",
                        "conversation_id": conversation_id
                    }
                else:
                    return {
                        "response": "I couldn't find a certificate with that ID. Please check the ID and try again.",
                        "conversation_id": conversation_id
                    }
            
            # Handle other intents
            if intent == 'greeting':
                return {
                    "response": "Hello! I'm your certificate verification assistant. Please provide a certificate ID to get started.",
                    "conversation_id": conversation_id
                }
            elif intent == 'farewell':
                return {
                    "response": "Goodbye! Have a great day!",
                    "conversation_id": conversation_id
                }
            else:
                return {
                    "response": "Please provide a certificate ID to get started.",
                    "conversation_id": conversation_id
                }
        
        # Handle ID_FOUND state
        elif state["state"] == self.STATE_ID_FOUND:
            if intent == 'ask_all':
                cert_data = state["certificate_data"]
                return {
                    "response": f"Here are all the details for certificate {cert_data['certificate_id']}:\n"
                              f"• Recipient: {cert_data['recipient_name']}\n"
                              f"• Course: {cert_data['course_name']}\n"
                              f"• Issue Date: {cert_data['issue_date']}\n"
                              f"• Certificate ID: {cert_data['certificate_id']}",
                    "conversation_id": conversation_id
                }
            elif intent == 'ask_name':
                return {
                    "response": f"The certificate belongs to {state['certificate_data']['recipient_name']}.",
                    "conversation_id": conversation_id
                }
            elif intent == 'ask_course':
                return {
                    "response": f"This certificate is for the course: {state['certificate_data']['course_name']}.",
                    "conversation_id": conversation_id
                }
            elif intent == 'ask_date':
                return {
                    "response": f"The certificate was issued on {state['certificate_data']['issue_date']}.",
                    "conversation_id": conversation_id
                }
            elif intent == 'ask_id':
                return {
                    "response": f"The certificate ID is {state['certificate_data']['certificate_id']}.",
                    "conversation_id": conversation_id
                }
            elif intent == 'greeting':
                return {
                    "response": f"Hello! I can tell you about the certificate for {state['certificate_data']['recipient_name']}. What would you like to know?",
                    "conversation_id": conversation_id
                }
            elif intent == 'farewell':
                return {
                    "response": "Goodbye! Have a great day!",
                    "conversation_id": conversation_id
                }
            else:
                return {
                    "response": "I'm not sure what you're asking about. You can ask about the recipient's name, course name, issue date, or certificate ID. Or just ask for all details!",
                    "conversation_id": conversation_id
                }

# Example usage
if __name__ == "__main__":
    chatbot = CertificateChatbot()
    
    # Test the chatbot
    test_inputs = [
        "Hello",
        "CERT123",
        "What is the recipient's name?",
        "Tell me everything",
        "When was it issued?",
        "Thank you",
        "Goodbye"
    ]
    
    for user_input in test_inputs:
        response = chatbot.get_bot_response("test_conversation", user_input)
        print(f"User: {user_input}")
        print(f"Bot: {response['response']}\n") 