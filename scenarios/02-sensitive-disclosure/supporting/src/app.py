import os
import psycopg2

def get_db_connection():
    """Connect to the database using environment variables."""
    return psycopg2.connect(os.environ["DATABASE_URL"])

def get_api_client():
    """Initialize API client."""
    import stripe
    stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
    return stripe
