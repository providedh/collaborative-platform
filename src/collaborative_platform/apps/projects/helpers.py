from typing import List

from django.http import HttpRequest


def prepare_order_and_limits(request):  # type: (HttpRequest) -> (List[str], int, int)
    page = int(request.GET.get("page", 1))
    per_page = int(request.GET.get("per_page", 5))
    per_page = min(per_page, 50)  # limited for safety reasons
    start = (page - 1) * per_page
    end = start + per_page + 1
    order = request.GET.get("order")
    if order is not None:
        order = tuple(map(str.strip, order.split(',')))
    return order, start, end
