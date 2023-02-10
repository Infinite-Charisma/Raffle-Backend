import os
from flask import Flask
from flask_cors import CORS
from shared.api.dependencies import Dependencies, get_dependency
from shared.logging import configure_logger, LoggerConfig
from .blueprints import resolve_blueprint
from .services.shared_dependencies import register_shared_config
from shared.api.authentication import register_signed_user_dependencies
from shared.api.exceptions import ApiException, handle_api_exception, handle_exception

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)
deps = Dependencies(app)\
    .register_with(register_shared_config)\
    .register_with(register_signed_user_dependencies)\

deps.register_blueprint(resolve_blueprint, url_prefix="/resolve")

app.register_error_handler(ApiException, handle_api_exception)
app.register_error_handler(Exception, handle_exception)


@app.before_first_request
def configure_logging():
    config = get_dependency(LoggerConfig)
    configure_logger(config)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
