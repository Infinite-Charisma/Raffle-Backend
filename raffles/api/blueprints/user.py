from flask import jsonify, request, abort
from shared.api.dependencies import get_dependency, DependencyBlueprint
from shared.api.authentication import with_signed_user, get_signed_user, SignedUserSessionHandler
from shared.api.exceptions import UnauthorizedException as ApiUnauthorizedException, ForbiddenException as ApiForbiddenException
from raffles.shared.repositories import UserRepository
from raffles.shared.exceptions import UnauthorizedException, ForbiddenException
from ..services.user_service import UserService


user_blueprint = DependencyBlueprint("user", __name__)\
    .register_dependencies(
        lambda deps: deps
    .add_resolver(UserRepository.resolver())
    .add_direct(UserService)
)


@user_blueprint.route("/", methods=["DELETE"], strict_slashes=False)
@with_signed_user(require_user=False)
def delete_session():
    session_handler = SignedUserSessionHandler()
    session_handler.delete()
    return jsonify({}), 201


@user_blueprint.route("/favourites", methods=["GET"], strict_slashes=False)
@with_signed_user(require_user=True)
def get_favourites():
    user = get_signed_user()
    if user.message != "favourites":
        raise ApiUnauthorizedException("Invalid signed message")
    svc = get_dependency(UserService)
    return jsonify(svc.get_favourites(user))


@user_blueprint.route("/favourites/<string:raffle_id>", methods=["PUT"], strict_slashes=False)
@with_signed_user(require_user=True)
def add_favourite(raffle_id):
    user = get_signed_user()
    if user.message != raffle_id:
        raise ApiUnauthorizedException("Invalid signed message")
    svc = get_dependency(UserService)
    try:
        return jsonify(svc.add_favourite(user, raffle_id)), 201
    except UnauthorizedException as e:
        raise ApiUnauthorizedException(e.reason)
    except ForbiddenException as e:
        raise ApiForbiddenException(e.reason)


@user_blueprint.route("/favourites/<string:raffle_id>", methods=["DELETE"], strict_slashes=False)
@with_signed_user(require_user=True)
def remove_favourite(raffle_id):
    user = get_signed_user()
    if user.message != raffle_id:
        raise ApiUnauthorizedException("Invalid signed message")
    svc = get_dependency(UserService)
    try:
        return jsonify(svc.remove_favourite(user, raffle_id)), 204
    except UnauthorizedException as e:
        raise ApiUnauthorizedException(e.reason)
    except ForbiddenException as e:
        raise ApiForbiddenException(e.reason)
