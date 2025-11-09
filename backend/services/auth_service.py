from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from config import settings
from repositories.mysql_repository import MySQLUserRepository
from models import User


class AuthService:
    """Service for handling authentication and authorization"""
    
    def __init__(self, user_repository: MySQLUserRepository):
        self.user_repository = user_repository
    
    def create_access_token(self, user_id: str) -> str:
        """Create a JWT access token for a user"""
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        to_encode = {
            "sub": user_id,
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[str]:
        """
        Verify a JWT token and return the user_id if valid
        
        Returns:
            user_id if token is valid, None otherwise
        """
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return user_id
        except JWTError:
            return None
    
    def get_or_create_user(self, google_id: str, email: str, name: str, picture: str) -> User:
        """
        Get existing user by Google ID or create a new one
        
        Args:
            google_id: User's Google ID
            email: User's email
            name: User's display name
            picture: URL to user's avatar
            
        Returns:
            User object
        """
        user = self.user_repository.get_user_by_google_id(google_id)
        if user:
            # Update user info if changed
            self.user_repository.update_user(
                user.id,
                email=email,
                display_name=name,
                avatar_url=picture
            )
            return user
        
        # Create new user
        return self.user_repository.create_user(
            google_id=google_id,
            email=email,
            display_name=name,
            avatar_url=picture
        )