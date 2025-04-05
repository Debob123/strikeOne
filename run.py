# Entry point to start the Flask app  

from app import create_app
from app import create_tables_and_admin

app = create_app()
create_tables_and_admin(app)