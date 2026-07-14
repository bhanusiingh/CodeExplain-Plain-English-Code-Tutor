import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import requests
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

# Cache the Firebase initialization so it only runs once per app lifecycle
@st.cache_resource
def init_firebase():
    """Initialize Firebase Admin SDK and Firestore client."""
    if not firebase_admin._apps:
        try:
            # We expect a [firebase] block in secrets.toml
            if "firebase" not in st.secrets:
                logger.warning("Firebase credentials not found in st.secrets. Skipping init.")
                return None
                
            # Convert streamlit secrets AttrDict to a normal dict
            cert_dict = dict(st.secrets["firebase"])
            # Ensure private_key has correct newlines
            if "private_key" in cert_dict:
                cert_dict["private_key"] = cert_dict["private_key"].replace("\\n", "\n")
                
            cred = credentials.Certificate(cert_dict)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            logger.error(f"Error initializing Firebase: {e}")
            return None
    return firestore.client()

def get_firestore_db():
    return init_firebase()

# ── Auth REST API ────────────────────────────────────────────────────────────
# We use the REST API for client-side operations (login, signup, reset) 
# because Firebase Admin SDK only mints custom tokens and doesn't verify email/password.

def _get_api_key():
    try:
        return st.secrets["firebase_web"]["api_key"]
    except KeyError:
        return None

def sign_in_with_email_and_password(email: str, password: str) -> dict:
    """Sign in using Firebase REST API."""
    api_key = _get_api_key()
    if not api_key:
        return {"error": "Missing Firebase Web API key in secrets.toml"}
        
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        if "error" in data:
            return {"error": data["error"].get("message", "Authentication failed")}
        return {
            "uid": data["localId"],
            "email": data["email"],
            "idToken": data["idToken"],
            "refreshToken": data["refreshToken"]
        }
    except Exception as e:
        return {"error": str(e)}

def create_user_with_email_and_password(email: str, password: str, name: str) -> dict:
    """Sign up using Firebase REST API."""
    api_key = _get_api_key()
    if not api_key:
        return {"error": "Missing Firebase Web API key in secrets.toml"}
        
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        if "error" in data:
            return {"error": data["error"].get("message", "Registration failed")}
            
        # Optional: Set the display name via Admin SDK or REST update profile
        uid = data["localId"]
        
        return {
            "uid": uid,
            "email": data["email"],
            "idToken": data["idToken"],
            "refreshToken": data["refreshToken"],
            "name": name
        }
    except Exception as e:
        return {"error": str(e)}

def send_password_reset_email(email: str) -> dict:
    """Send a password reset email using Firebase REST API."""
    api_key = _get_api_key()
    if not api_key:
        return {"error": "Missing Firebase Web API key in secrets.toml"}
        
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
    payload = {
        "requestType": "PASSWORD_RESET",
        "email": email
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        if "error" in data:
            return {"error": data["error"].get("message", "Failed to send reset email")}
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

# ── Firestore CRUD ────────────────────────────────────────────────────────────

def save_user_history(uid: str, item: dict) -> bool:
    """Save a history item to the user's Firestore collection."""
    db = get_firestore_db()
    if not db:
        return False
        
    try:
        # Avoid saving full datetime objects directly if they cause serialization issues.
        # Firebase accepts standard Python datetime objects in Admin SDK.
        doc_ref = db.collection('users').document(uid).collection('history').document(item['id'])
        doc_ref.set(item)
        return True
    except Exception as e:
        logger.error(f"Error saving history to Firestore: {e}")
        return False

def get_user_history(uid: str) -> list[dict]:
    """Retrieve all history items for a user, newest first."""
    db = get_firestore_db()
    if not db:
        return []
        
    try:
        docs = db.collection('users').document(uid).collection('history')\
                 .order_by('timestamp', direction=firestore.Query.DESCENDING)\
                 .get()
                 
        history = []
        for doc in docs:
            item = doc.to_dict()
            # Convert Firestore DatetimeWithNanoseconds back to standard datetime if needed, 
            # though Streamlit usually handles it fine. Let's ensure it's standard datetime.
            if hasattr(item.get('timestamp'), 'timestamp'):
                 item['timestamp'] = datetime.fromtimestamp(item['timestamp'].timestamp())
            history.append(item)
        return history
    except Exception as e:
        logger.error(f"Error fetching history from Firestore: {e}")
        return []

def delete_user_history_item(uid: str, item_id: str) -> bool:
    """Delete a specific history item from Firestore."""
    db = get_firestore_db()
    if not db:
        return False
        
    try:
        db.collection('users').document(uid).collection('history').document(item_id).delete()
        return True
    except Exception as e:
        logger.error(f"Error deleting history from Firestore: {e}")
        return False

def clear_user_history(uid: str) -> bool:
    """Clear all history for a user."""
    db = get_firestore_db()
    if not db:
        return False
        
    try:
        docs = db.collection('users').document(uid).collection('history').stream()
        batch = db.batch()
        for doc in docs:
            batch.delete(doc.reference)
        batch.commit()
        return True
    except Exception as e:
        logger.error(f"Error clearing history in Firestore: {e}")
        return False
