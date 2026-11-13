from itertools import count
from threading import Lock

from connexion.exceptions import Forbidden, ProblemException

from openapi_server.models.deletion_result import DeletionResult
from openapi_server.models.work_order import WorkOrder


_orders: dict[int, WorkOrder] = {}
_order_ids = count(1)
_lock = Lock()
_collection_path = "/work-orders"


def _ok(data, *, link_to_collection=False):
    headers = {"Content-Type": "application/json", "Cache-Control": "no-store"}
    if link_to_collection:
        headers["Link"] = f'<{_collection_path}>; rel="collection"'
    return data, 200, headers


def _require_write_access(token_info):
    if token_info["role"] != "editor":
        raise Forbidden(detail="У сотрудника нет права записи.")


def _get_existing_order(order_id):
    try:
        return _orders[order_id]
    except KeyError:
        raise ProblemException(
            status=404,
            title="Not Found",
            detail=f"Заказ-наряд с ID {order_id} не найден.",
        ) from None


def _work_order_from_body(order_id, body):
    return WorkOrder(
        id=order_id,
        vehicle_plate=body["vehiclePlate"],
        work_description=body["workDescription"],
        status=body["status"],
        href=f"{_collection_path}/{order_id}",
    )


def list_work_orders(status=None):
    with _lock:
        orders = [
            order
            for order in _orders.values()
            if status is None or order.status == status
        ]
    return _ok(orders)


def get_work_order(order_id):
    with _lock:
        return _ok(_get_existing_order(order_id), link_to_collection=True)


def create_work_order(body, token_info):
    _require_write_access(token_info)
    with _lock:
        order_id = next(_order_ids)
        order = _work_order_from_body(order_id, body)
        _orders[order_id] = order
    return _ok(order, link_to_collection=True)


def replace_work_order(order_id, body, token_info):
    _require_write_access(token_info)
    with _lock:
        _get_existing_order(order_id)
        order = _work_order_from_body(order_id, body)
        _orders[order_id] = order
    return _ok(order, link_to_collection=True)


def delete_work_order(order_id, token_info):
    _require_write_access(token_info)
    with _lock:
        _get_existing_order(order_id)
        del _orders[order_id]
    return _ok(DeletionResult(id=order_id, deleted=True), link_to_collection=True)
