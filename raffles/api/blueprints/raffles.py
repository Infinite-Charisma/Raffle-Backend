from flask import jsonify, request, abort
from shared.api.dependencies import get_dependency, DependencyBlueprint
from shared.api.authentication import with_signed_user, get_signed_user
from ..services.raffles_service import RafflesService
from raffles.shared.near import ReadOnlyRafflesContractFactory
from raffles.shared.raffles_cache import RafflesCache


raffles_blueprint = DependencyBlueprint("raffles", __name__)\
    .register_dependencies(
        lambda deps: deps
    .add_direct(RafflesService)
    .add_direct(ReadOnlyRafflesContractFactory)
    .add_direct_singleton(RafflesCache)
)


@raffles_blueprint.route("/featured", methods=["GET"], strict_slashes=False)
@with_signed_user(require_user=False)
def get_featured():
    svc = get_dependency(RafflesService)
    return jsonify(svc.get_featured())


@raffles_blueprint.route("/total_sold", methods=["GET"], strict_slashes=False)
@with_signed_user(require_user=False)
def get_tickets_sold():
    svc = get_dependency(RafflesService)
    return jsonify(svc.get_tickets_sold())
