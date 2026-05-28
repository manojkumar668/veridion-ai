
from flask_jwt_extended import create_access_token


# ================= GENERATE JWT TOKEN =================
def generate_token(email, role="user"):

    token = create_access_token(
        identity={
            "email": email,
            "role": role
        }
    )

    return token

