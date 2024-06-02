import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://schedule:password@localhost/schedule'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    COOLSMS_API_KEY = os.environ.get('COOLSMS_API_KEY') or 'NCSQS4MSM5TZ5QS6'
    COOLSMS_API_SECRET = os.environ.get('COOLSMS_API_SECRET') or 'OUMCJKJ92BIGWOLVQUOFSSQRXO1HFAUH'
    COOLSMS_SENDER_NUMBER = os.environ.get('COOLSMS_SENDER_NUMBER') or '010-3475-1350'