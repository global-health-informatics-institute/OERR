import json
from flask import Flask
from apis.oerr_api import connect_to_oerr_test, oerr_bp
from apis.auth_api import connect_to_tokken, load_token_from_db, auth_bp
from apis.department_api import department_bp 
from apis.lab_test_types_api import connect_to_test_types , test_type_bp
from apis.lab_test_panels_api import connect_to_test_panels , test_panels_bp
from apis.wards_api import ward_bp
from apis.specimens_api import specimen_bp
from apis.extensions_api import config_file

app = Flask(__name__)

app.register_blueprint(auth_bp,)
app.register_blueprint(test_type_bp)
app.register_blueprint(test_panels_bp)
app.register_blueprint(ward_bp)
app.register_blueprint(specimen_bp)
app.register_blueprint(department_bp)
app.register_blueprint(oerr_bp)


settings = {}
with open(config_file) as json_file:
    settings = json.load(json_file)


if __name__ == "__main__":
    
    connect_to_tokken()
    connect_to_test_types()
    connect_to_test_panels()
    connect_to_oerr_test()
    TOKEN = load_token_from_db() 
    app_port = settings.get("app", {}).get("port", 8001)
    app.run(host="0.0.0.0", port=app_port, debug=True)
