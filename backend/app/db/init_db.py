from uuid import uuid4

from sqlalchemy import inspect, text
from sqlmodel import Session, SQLModel, select

from app.db.session import engine
from app.models.category import Category


def _seed_categories() -> None:
    """Seed default categories if the table is empty."""
    with Session(engine) as session:
        existing = session.exec(select(Category)).first()
        if existing is not None:
            return
        defaults = [
            ("social_media_scam", "Social Media Scam (Facebook, Telegram, Instagram, WhatsApp)"),
            ("marketplace_fraud", "Online Marketplace Fraud (Daraz, Alibaba, OLX, eBay)"),
            ("phishing", "Phishing / Account Takeover"),
            ("fake_job", "Fake Job / Employment Scam"),
            ("investment_scam", "Investment / Crypto Scam"),
            ("software_service_complaint", "Software & App Service Complaint"),
            ("billing_dispute", "Billing & Subscription Dispute"),
            ("poor_service", "Poor Service / Breach of Contract"),
            ("rental_property_scam", "Rental & Property Scam"),
            ("identity_theft", "Identity Theft / Impersonation"),
            ("delivery_courier_scam", "Delivery / Courier Scam"),
            ("other", "Other / General Complaint"),
        ]
        for value, label in defaults:
            session.add(Category(id=str(uuid4()), value=value, label=label))
        session.commit()


def _migrate_schema() -> None:
    """Add missing columns to existing tables (non-destructive migration)."""
    inspector = inspect(engine)
    if not inspector.has_table("user"):
        return
    existing_columns = {col["name"] for col in inspector.get_columns("user")}

    with engine.begin() as conn:
        if "name" not in existing_columns:
            conn.execute(text('ALTER TABLE "user" ADD COLUMN name VARCHAR NOT NULL DEFAULT \'\''))
        if "occupation" not in existing_columns:
            conn.execute(text('ALTER TABLE "user" ADD COLUMN occupation VARCHAR'))
        if "profile_image_url" not in existing_columns:
            conn.execute(text('ALTER TABLE "user" ADD COLUMN profile_image_url VARCHAR'))
        if "reset_token" not in existing_columns:
            conn.execute(text('ALTER TABLE "user" ADD COLUMN reset_token VARCHAR'))
        if "reset_token_expires" not in existing_columns:
            conn.execute(text('ALTER TABLE "user" ADD COLUMN reset_token_expires TIMESTAMP'))
        if "is_admin" not in existing_columns:
            conn.execute(text('ALTER TABLE "user" ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE'))
        if "is_banned" not in existing_columns:
            conn.execute(text('ALTER TABLE "user" ADD COLUMN is_banned BOOLEAN NOT NULL DEFAULT FALSE'))


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    _migrate_schema()
    _seed_categories()
