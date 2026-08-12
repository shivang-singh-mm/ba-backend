from flask_jwt_extended import JWTManager
from flask_mail import Mail

# psycopg2 pool is managed via Core.database — not an extension object
jwt = JWTManager()
mail = Mail()
