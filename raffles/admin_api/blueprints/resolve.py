from flask import jsonify, request, abort
from shared.api.dependencies import get_dependency, DependencyBlueprint
from shared.api.authentication import with_signed_user, get_signed_user
from ..services.raffle_resolution_service import RaffleResolutionService
from raffles.shared.near import RafflesContractFactory
from shared.near import NearAccountResolver
from raffles.shared.client import AdminApiClient, SelfAdminClientUrlResolver


resolve_blueprint = DependencyBlueprint("resolve", __name__)\
    .register_dependencies(
        lambda deps: deps
    .add_direct(RafflesContractFactory)
    .add_direct(RaffleResolutionService)
    .add_direct(AdminApiClient)
    .add_direct(SelfAdminClientUrlResolver)
)


@resolve_blueprint.route("/refresh", methods=["POST"], strict_slashes=False)
def refresh():
    svc = get_dependency(RaffleResolutionService)
    return jsonify(svc.refresh())


@resolve_blueprint.route("/<int:raffle_id>", methods=["POST"], strict_slashes=False)
def resolve(raffle_id):
    svc = get_dependency(RaffleResolutionService)
    return jsonify(svc.resolve_raffle(raffle_id))
