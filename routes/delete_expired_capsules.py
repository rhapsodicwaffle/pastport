from models import Capsule, db
from datetime import date

def delete_expired_capsules():
    today = date.today().isoformat()
    expired_capsules = Capsule.query.filter(
        Capsule.expiry_date != None,
        Capsule.expiry_date <= today
    ).all()

    deleted_count = len(expired_capsules)

    for capsule in expired_capsules:
        db.session.delete(capsule)

    db.session.commit()
    print(f" {deleted_count} expired capsules deleted.")
