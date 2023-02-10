from flask import request, abort

from shared.api.dependencies import get_dependency, DependencyBlueprint
from shared.signature_verifier import Signer

signer_blueprint = DependencyBlueprint("signer", __name__)\
    .register_dependencies(
        lambda deps: deps
    .add_direct(Signer)
)


@signer_blueprint.route("/sign", methods=["POST"], strict_slashes=False)
def sign():
    data = request.json
    content = data["data"]
    private_key = data["private_key"]

    signer = get_dependency(Signer)

    return signer.sign(private_key, content)
