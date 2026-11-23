
from extensions import db
from datetime import datetime


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(160), default="")
    headline = db.Column(db.String(220), default="")
    email = db.Column(db.String(180), default="")
    phone = db.Column(db.String(60), default="")
    location = db.Column(db.String(160), default="Chile")
    professional_goals = db.Column(db.Text, default="")
    experience = db.Column(db.Text, default="")
    education = db.Column(db.Text, default="")
    skills = db.Column(db.Text, default="")
    certifications = db.Column(db.Text, default="")
    salary_min = db.Column(db.Integer, nullable=True)
    salary_currency = db.Column(db.String(12), default="CLP")
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(220), nullable=False)
    company = db.Column(db.String(180), default="")
    source = db.Column(db.String(80), default="Manual")
    url = db.Column(db.String(1000), default="")
    description = db.Column(db.Text, default="")
    analysis = db.Column(db.Text, default="")
    form_questions = db.Column(db.Text, default="")
    form_answers = db.Column(db.Text, default="")
    location = db.Column(db.String(180), default="")
    work_mode = db.Column(db.String(40), default="No especificado")

    # Seguimiento de ofertas manuales
    ya_revise = db.Column(db.Boolean, default=False, nullable=False)
    ya_postule = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class JobSearchResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    url = db.Column(db.String(1500), nullable=False)
    source = db.Column(db.String(100), default="")
    description = db.Column(db.Text, default="")
    result_type = db.Column(db.String(100), default="")
    is_general = db.Column(db.Boolean, default=True)

    # Seguimiento de resultados encontrados
    ya_revise = db.Column(db.Boolean, default=False, nullable=False)
    ya_postule = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    offer_id = db.Column(db.Integer, db.ForeignKey("offer.id"), nullable=True)
    company = db.Column(db.String(180), default="")
    title = db.Column(db.String(220), nullable=False)
    status = db.Column(db.String(40), default="Guardada")
    applied_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, default="")
    offer = db.relationship("Offer", backref="applications")


class InboxItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gmail_id = db.Column(db.String(120), unique=True, nullable=True)
    provider = db.Column(db.String(40), default="Manual")
    sender = db.Column(db.String(220), default="")
    subject = db.Column(db.String(300), nullable=False)
    body_preview = db.Column(db.Text, default="")
    category = db.Column(db.String(60), default="Sin clasificar")
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
