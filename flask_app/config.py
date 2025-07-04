"""Configuration settings for Beautiful Flicker Flask app."""

import os


class Config:
    """Base configuration."""
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # File upload settings
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_UPLOAD_SIZE', 52428800))  # 50MB default
    ALLOWED_EXTENSIONS = {'csv', 'txt'}
    UPLOAD_FOLDER = 'uploads'
    
    # CORS settings
    CORS_ORIGINS = ['*']  # In production, specify allowed origins
    
    # Session settings
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Application settings
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = FLASK_ENV == 'development'
    
    # Chart export settings
    EXPORT_DPI = 300  # Default DPI for exports
    EXPORT_MAX_WIDTH = 4000  # Maximum width in pixels
    EXPORT_MAX_HEIGHT = 3000  # Maximum height in pixels


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Use environment variables for sensitive data
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}