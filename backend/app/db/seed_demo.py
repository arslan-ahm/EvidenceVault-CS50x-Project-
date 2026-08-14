"""Seed the database with realistic demo data for manual/QA testing.

Idempotent: safe to re-run — existing users/organizations are looked up by
their unique key (email / slug) and reused rather than duplicated. Cases,
comments, upvotes, timeline events and evidence are only created the first
time (guarded by a marker case title prefix) so re-running doesn't pile up
duplicates.

Usage (from backend/, with the venv active and DATABASE_URL pointing at the
target database — local .env already points at the real Supabase project):

    python -m app.db.seed_demo

Prints the admin + demo user credentials at the end; the caller is
responsible for writing those into TEMP_CREDENTIALS.md.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlmodel import Session, select

from app.core.security import hash_password
from app.db.init_db import init_db
from app.db.session import engine
from app.models.case import Case
from app.models.comment import Comment
from app.models.organization import Organization
from app.models.timeline import TimelineEvent
from app.models.upvote import CaseUpvote
from app.models.evidence import Evidence
from app.models.user import User

random.seed(20260814)

ADMIN_EMAIL = "admin@evidencevault.app"
ADMIN_PASSWORD = "AdminDemo#2026!"
DEMO_PASSWORD = "DemoUser#2026!"

CATEGORIES = [
    "social_media_scam",
    "marketplace_fraud",
    "phishing",
    "fake_job",
    "investment_scam",
    "software_service_complaint",
    "billing_dispute",
    "poor_service",
    "rental_property_scam",
    "identity_theft",
    "delivery_courier_scam",
    "other",
]
SEVERITIES = ["low", "medium", "high", "critical"]
STATUSES = ["open", "in_progress", "resolved", "closed"]

DEMO_USERS = [
    ("Ayesha Khan", "ayesha.khan@example.com", "Software Engineer", False, False),
    ("Bilal Ahmed", "bilal.ahmed@example.com", "Freelancer", False, False),
    ("Sara Malik", "sara.malik@example.com", "Student", False, False),
    ("Usman Tariq", "usman.tariq@example.com", "Shop Owner", False, False),
    ("Fatima Noor", "fatima.noor@example.com", "Accountant", False, False),
    ("Hamza Sheikh", "hamza.sheikh@example.com", "", False, False),
    ("Zainab Iqbal", "zainab.iqbal@example.com", "Marketing Manager", False, False),
    ("Ali Raza", "ali.raza@example.com", "Consultant", False, False),
    ("Nimra Farooq", "nimra.farooq@example.com", "Teacher", False, False),
    ("Omar Siddiqui", "omar.siddiqui@example.com", "Delivery Rider", False, True),  # banned, for testing moderation
    ("Hina Yousaf", "hina.yousaf@example.com", "Designer", True, False),  # second admin, for testing admin management
]

ORGANIZATIONS = [
    ("QuickCart Marketplace", "E-commerce", "https://quickcart.example.com"),
    ("PayFast Wallet", "Fintech", "https://payfast.example.com"),
    ("SwiftShip Couriers", "Logistics", "https://swiftship.example.com"),
    ("CloudNest Hosting", "SaaS", "https://cloudnest.example.com"),
    ("UrbanNest Rentals", "Real Estate", "https://urbannest.example.com"),
    ("BrightWorks Jobs", "Recruitment", "https://brightworks.example.com"),
    ("CoinRise Investments", "Crypto", "https://coinrise.example.com"),
    ("StreamPlus Media", "Entertainment", "https://streamplus.example.com"),
    ("MegaMart Online", "Retail", "https://megamart.example.com"),
    ("SecureBank Digital", "Banking", "https://securebank.example.com"),
    ("TalkNet Social", "Social Media", "https://talknet.example.com"),
    ("FreshEats Delivery", "Food Delivery", None),
]

CASE_TEMPLATES = {
    "social_media_scam": [
        ("Fake giveaway page impersonating {org}", "A page pretending to be {org} ran a 'like & share' giveaway, then DMed winners asking for a small 'processing fee' via bank transfer. No prize was ever sent."),
        ("Cloned {org} account requesting money from my contacts", "My account was cloned and used to message my friends on {org} asking for emergency cash transfers."),
    ],
    "marketplace_fraud": [
        ("Paid for item on {org}, seller never shipped it", "Ordered a phone through {org}, paid in full via the in-app wallet. Seller stopped responding after payment and the order still shows 'preparing to ship' after 3 weeks."),
        ("Received counterfeit product from {org} seller", "The item that arrived from {org} was a cheap knockoff, not the branded product shown in the listing. Seller refused a refund."),
    ],
    "phishing": [
        ("Phishing email impersonating {org} login page", "Received an email that looked exactly like {org}'s official login page. Entered credentials before noticing the URL was misspelled — account was accessed within the hour."),
        ("SMS phishing link claiming to be {org} account verification", "Got a text claiming my {org} account was locked and needed 'verification' via a link. The link led to a fake login page."),
    ],
    "fake_job": [
        ("Fake remote job offer from '{org}' asking for a deposit", "Was offered a remote data-entry role at {org}, then asked to pay a 'training kit' deposit before starting. No job existed."),
        ("Recruiter impersonating {org} HR requested personal documents", "Someone claiming to be {org} HR asked for my CNIC and bank details 'for onboarding' before any interview took place."),
    ],
    "investment_scam": [
        ("{org} investment scheme promised guaranteed 40% monthly returns", "Invested through {org} after seeing testimonials online. Returns stopped after the first month and withdrawals have been blocked since."),
        ("Crypto trading bot from {org} drained my wallet", "Signed up for an automated trading bot advertised by {org}. It requested wallet access and transferred out the full balance."),
    ],
    "software_service_complaint": [
        ("{org} charged for premium features that never activated", "Upgraded to the paid tier on {org} but premium features never unlocked. Support has not responded in 2 weeks."),
        ("{org} app deleted my data after an update", "After the latest {org} app update, all my saved projects disappeared with no recovery option offered."),
    ],
    "billing_dispute": [
        ("{org} kept billing after I cancelled my subscription", "Cancelled my {org} subscription in the app, but was charged again the following month. Support says the cancellation 'didn't go through'."),
        ("Double-charged by {org} for a single order", "{org} charged my card twice for the same order. One charge was never reversed despite multiple support tickets."),
    ],
    "poor_service": [
        ("{org} failed to deliver the service outlined in our contract", "Signed a service agreement with {org} for monthly maintenance. Three months in, no technician has ever shown up."),
        ("{org} support has ignored my complaint for over a month", "Filed a formal complaint with {org} about a defective installation. No response despite repeated follow-ups."),
    ],
    "rental_property_scam": [
        ("Paid deposit to '{org}' for a listing that didn't exist", "Sent an advance deposit to secure an apartment listed by {org}. On arrival, the property didn't exist and the agent was unreachable."),
        ("{org} agent disappeared after receiving advance rent", "Paid two months advance rent through an agent claiming to represent {org}. Agent and listing vanished immediately after."),
    ],
    "identity_theft": [
        ("Someone opened a {org} account using my identity", "Discovered a {org} account was opened in my name without consent, used to take out a small loan."),
        ("My documents were used to register a fraudulent {org} listing", "A seller used photos of my ID to verify a {org} storefront that has since scammed several buyers."),
    ],
    "delivery_courier_scam": [
        ("{org} courier demanded extra 'customs fee' on delivery", "A courier claiming to be from {org} demanded an unexpected cash 'customs fee' before releasing my package."),
        ("Package marked delivered by {org} but never arrived", "{org} tracking shows 'delivered' but nothing was received and no proof of delivery photo exists."),
    ],
    "other": [
        ("General complaint against {org} over unresolved service issue", "Ongoing dispute with {org} that doesn't fit a specific category — details in the description."),
        ("{org} misrepresented terms during sign-up", "{org} advertised one set of terms during sign-up and applied a different, less favorable set afterward."),
    ],
}

COMMENT_TEMPLATES = [
    "Same thing happened to me with this exact organization last month.",
    "Did you manage to get a refund? I'm going through the same issue.",
    "I've reported this to the consumer protection helpline as well.",
    "Thanks for posting this — saved me from falling for the same thing.",
    "Following this, dealing with something almost identical right now.",
    "I have screenshots of a similar message if that helps your case.",
    "Any update on this? Curious how it got resolved.",
    "This matches a pattern I've seen reported elsewhere too.",
]

TIMELINE_TEMPLATES = [
    "Initial contact made with the organization's support team.",
    "Received an automated acknowledgement, no further response since.",
    "Escalated the complaint to a supervisor via email.",
    "Organization requested additional documentation.",
    "No response received after the promised follow-up window.",
    "Filed a formal complaint with the relevant consumer authority.",
]

# Real, publicly hosted images/documents used as evidence attachments so the
# demo data renders actual previews instead of broken links.
EVIDENCE_IMAGE_SEEDS = ["receipt", "chat", "screenshot", "invoice", "listing", "email"]
SAMPLE_PDF_URL = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"


def _avatar_url(seed: str) -> str:
    return f"https://api.dicebear.com/7.x/avataaars/svg?seed={seed.replace(' ', '-')}"


def _org_logo_url(name: str) -> str:
    return f"https://api.dicebear.com/7.x/initials/svg?seed={name.replace(' ', '-')}&backgroundType=gradientLinear"


def _evidence_image_url(seed: str) -> str:
    return f"https://picsum.photos/seed/{seed}/900/600"


def _get_or_create_user(session: Session, *, email: str, name: str, occupation: str | None,
                         password: str, is_admin: bool, is_banned: bool) -> User:
    existing = session.exec(select(User).where(User.email == email)).first()
    if existing:
        return existing
    user = User(
        id=str(uuid4()),
        email=email,
        hashed_password=hash_password(password),
        name=name,
        occupation=occupation or None,
        profile_image_url=_avatar_url(name),
        is_admin=is_admin,
        is_banned=is_banned,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _get_or_create_org(session: Session, *, name: str, industry: str, website: str | None) -> Organization:
    existing = session.exec(select(Organization).where(Organization.name == name)).first()
    if existing:
        return existing
    slug = "-".join(name.strip().lower().split())
    org = Organization(
        id=str(uuid4()),
        name=name,
        slug=slug,
        description=f"{name} is a {industry.lower()} company that appears in multiple community-reported complaints.",
        website=website,
        industry=industry,
        logo_url=_org_logo_url(name),
    )
    session.add(org)
    session.commit()
    session.refresh(org)
    return org


def seed_demo_data() -> dict:
    init_db()

    with Session(engine) as session:
        admin = _get_or_create_user(
            session,
            email=ADMIN_EMAIL,
            name="EvidenceVault Admin",
            occupation="Platform Administrator",
            password=ADMIN_PASSWORD,
            is_admin=True,
            is_banned=False,
        )

        demo_users = [admin]
        for name, email, occupation, is_admin, is_banned in DEMO_USERS:
            demo_users.append(
                _get_or_create_user(
                    session,
                    email=email,
                    name=name,
                    occupation=occupation,
                    password=DEMO_PASSWORD,
                    is_admin=is_admin,
                    is_banned=is_banned,
                )
            )

        orgs = [
            _get_or_create_org(session, name=name, industry=industry, website=website)
            for name, industry, website in ORGANIZATIONS
        ]

        # Cases are only seeded once — guard on a marker so re-running the
        # script doesn't create duplicates.
        marker = session.exec(select(Case).where(Case.title.like("[demo]%"))).first()
        if marker:
            return {
                "admin_email": ADMIN_EMAIL,
                "admin_password": ADMIN_PASSWORD,
                "demo_password": DEMO_PASSWORD,
                "demo_users": [(n, e) for n, e, *_ in DEMO_USERS],
                "skipped_cases": True,
            }

        now = datetime.now(timezone.utc)
        non_admin_users = [u for u in demo_users if not u.is_admin]
        case_count = 0

        for category in CATEGORIES:
            templates = CASE_TEMPLATES[category]
            # 4-5 cases per category so every category, status and severity
            # combination gets meaningful coverage across ~55 total cases.
            for i in range(5):
                title_tpl, desc_tpl = templates[i % len(templates)]
                org = random.choice(orgs) if random.random() > 0.15 else None
                owner = random.choice(non_admin_users)
                org_name = org.name if org else "the company"
                days_ago = random.randint(0, 89)
                created_at = now - timedelta(days=days_ago, hours=random.randint(0, 23))
                status = STATUSES[min(i, len(STATUSES) - 1)] if i < len(STATUSES) else random.choice(STATUSES)
                severity = random.choice(SEVERITIES)
                is_public = random.random() > 0.2

                case = Case(
                    id=str(uuid4()),
                    title=f"[demo] {title_tpl.format(org=org_name)}",
                    description=desc_tpl.format(org=org_name),
                    organization_id=org.id if org else None,
                    category=category,
                    severity=severity,
                    status=status,
                    is_public=is_public,
                    user_id=owner.id,
                    views_count=random.randint(0, 480),
                    upvotes_count=0,
                    created_at=created_at,
                )
                session.add(case)
                session.commit()
                session.refresh(case)
                case_count += 1

                # Evidence: most cases get 1-2 real image attachments, a few
                # also get a PDF document for file-type variety.
                for j in range(random.randint(1, 2)):
                    seed = f"{category}-{i}-{j}-{random.randint(1000, 9999)}"
                    session.add(Evidence(
                        id=str(uuid4()),
                        case_id=case.id,
                        user_id=owner.id,
                        file_path=f"demo/{seed}.jpg",
                        file_name=f"{random.choice(EVIDENCE_IMAGE_SEEDS)}-{j+1}.jpg",
                        file_type="image/jpeg",
                        extracted_text=None,
                        public_url=_evidence_image_url(seed),
                        metadata_json={"seeded": True, "source": "picsum.photos"},
                    ))
                if random.random() > 0.7:
                    session.add(Evidence(
                        id=str(uuid4()),
                        case_id=case.id,
                        user_id=owner.id,
                        file_path=f"demo/{case.id}.pdf",
                        file_name="supporting-document.pdf",
                        file_type="application/pdf",
                        extracted_text=None,
                        public_url=SAMPLE_PDF_URL,
                        metadata_json={"seeded": True, "source": "w3.org sample"},
                    ))

                # Timeline events for a portion of cases.
                if random.random() > 0.4:
                    for k in range(random.randint(1, 3)):
                        session.add(TimelineEvent(
                            id=str(uuid4()),
                            case_id=case.id,
                            event_text=random.choice(TIMELINE_TEMPLATES),
                            event_date=(created_at + timedelta(days=k * 2)).date(),
                            source_evidence_id=None,
                        ))

                # Comments from other users.
                commenters = [u for u in non_admin_users if u.id != owner.id and not u.is_banned]
                for _ in range(random.randint(0, 3)):
                    commenter = random.choice(commenters)
                    session.add(Comment(
                        id=str(uuid4()),
                        case_id=case.id,
                        user_id=commenter.id,
                        body=random.choice(COMMENT_TEMPLATES),
                        created_at=created_at + timedelta(hours=random.randint(1, 72)),
                    ))

                # Upvotes — real CaseUpvote rows kept consistent with the
                # case's cached upvotes_count.
                voters = random.sample(non_admin_users, k=min(len(non_admin_users), random.randint(0, 6)))
                for voter in voters:
                    if voter.id == owner.id:
                        continue
                    session.add(CaseUpvote(id=str(uuid4()), case_id=case.id, user_id=voter.id))
                case.upvotes_count = max(0, len(voters) - (1 if owner in voters else 0))
                session.add(case)

                session.commit()

        return {
            "admin_email": ADMIN_EMAIL,
            "admin_password": ADMIN_PASSWORD,
            "demo_password": DEMO_PASSWORD,
            "demo_users": [(n, e) for n, e, *_ in DEMO_USERS],
            "organizations_created": len(orgs),
            "cases_created": case_count,
            "skipped_cases": False,
        }


if __name__ == "__main__":
    result = seed_demo_data()
    print("Seed complete:")
    for key, value in result.items():
        print(f"  {key}: {value}")
