from app.database import SessionLocal
from app.models import Preference


def set_preference(owner_id: str, key: str, value: str):
    db = SessionLocal()

    try:
        owner_id = str(owner_id).strip()
        key = str(key).strip().lower()
        value = str(value).strip()

        if not owner_id:
            return {
                "success": False,
                "error": "Owner ID is required."
            }

        if not key:
            return {
                "success": False,
                "error": "Preference key is required."
            }

        if not value:
            return {
                "success": False,
                "error": "Preference value is required."
            }

        preference = (
            db.query(Preference)
            .filter(
                Preference.owner_id == owner_id,
                Preference.key == key,
            )
            .first()
        )

        if preference:
            preference.value = value
        else:
            preference = Preference(
                owner_id=owner_id,
                key=key,
                value=value,
            )
            db.add(preference)

        db.commit()

        return {
            "success": True,
            "owner_id": owner_id,
            "key": key,
            "value": value,
        }

    except Exception as exc:
        db.rollback()

        return {
            "success": False,
            "error": str(exc),
        }

    finally:
        db.close()


def get_preference(owner_id: str, key: str):
    db = SessionLocal()

    try:
        owner_id = str(owner_id).strip()
        key = str(key).strip().lower()

        preference = (
            db.query(Preference)
            .filter(
                Preference.owner_id == owner_id,
                Preference.key == key,
            )
            .first()
        )

        if not preference:
            return {
                "success": True,
                "found": False,
                "key": key,
            }

        return {
            "success": True,
            "found": True,
            "owner_id": owner_id,
            "key": preference.key,
            "value": preference.value,
        }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
        }

    finally:
        db.close()


def get_all_preferences(owner_id: str):
    db = SessionLocal()

    try:
        owner_id = str(owner_id).strip()

        preferences = (
            db.query(Preference)
            .filter(
                Preference.owner_id == owner_id
            )
            .all()
        )

        return {
            "success": True,
            "owner_id": owner_id,
            "preferences": [
                {
                    "key": preference.key,
                    "value": preference.value,
                }
                for preference in preferences
            ],
        }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
        }

    finally:
        db.close()