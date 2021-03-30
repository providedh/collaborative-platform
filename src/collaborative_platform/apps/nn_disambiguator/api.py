import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse, HttpResponseNotFound

from apps.nn_disambiguator.helpers import queue_task, abort_pending, serialize_unification_proposals
from apps.nn_disambiguator.models import CeleryTask, UnificationProposal
from apps.views_decorators import objects_exists, user_has_access


@login_required
@objects_exists
@user_has_access('RW')
def calculations(request: HttpRequest, project_id: int):
    if request.method == "POST":
        data = json.loads(request.body)
        if data.get("action") == "start":
            return queue_task(project_id, "P")
        elif data.get("action") == "abort":
            return abort_pending(project_id, "P")
        else:
            return HttpResponseBadRequest("No action parameter!")

    elif request.method == "GET":
        try:
            hist = CeleryTask.objects.filter(project_id=project_id, type="P").order_by("created").all()
            hist = [{
                "id": task.id,
                "status": task.get_status_display(),
                "type": task.get_type_display(),
                "task_id": task.task_id,
                "created": task.created
            } for task in hist]
        except CeleryTask.DoesNotExist:
            hist = []
        return JsonResponse(hist, safe=False)
    else:
        return HttpResponseBadRequest()


@login_required
@objects_exists
@user_has_access('RW')
def proposals(request: HttpRequest, project_id: int):
    if request.method == "GET":
        try:
            ups = UnificationProposal.objects.filter(entity__file__project=project_id, decided=False).order_by(
                "-confidence").values_list("id", flat=True)
        except UnificationProposal.DoesNotExist:
            ups = []

        return JsonResponse(list(ups), safe=False)

    if request.method == "PUT":
        args = json.loads(request.body)
        try:
            up = UnificationProposal.objects.get(id=args["id"])
        except UnificationProposal.DoesNotExist:
            return HttpResponseNotFound("No proposal with this ID.")

        if up.decided:
            return JsonResponse({"message": "Proposal has been already decided on."}, status=304)

        if args["decision"]:
            up.accept(request.user, args["certainty"], args["categories"])
            return JsonResponse({"message": "Unified successfully"})
        else:
            up.reject(request.user)
            return JsonResponse({"message": "Rejected successfully"})

    else:
        return HttpResponseBadRequest()


@login_required
@objects_exists
@user_has_access('RW')
def file_proposals(request: HttpRequest, project_id: int, file_id: int):
    if request.method == "GET":
        try:
            ups = UnificationProposal.objects.filter(entity__file__project_id=project_id,
                                                     decided=False,
                                                     entity__file_id=file_id).order_by("-confidence"
                                                                                       ).values_list("id", flat=True)
        except UnificationProposal.DoesNotExist:
            return JsonResponse({"message": "There are no proposals to show."})

        return JsonResponse(list(ups), safe=False)


@login_required
@objects_exists
@user_has_access('RW')
def proposals_details(request: HttpRequest, project_id: int):
    if request.method == "GET":
        ids = request.GET.getlist("ids")
        if ids is not None:
            ids = list(ids)
            try:
                ups = UnificationProposal.objects.filter(id__in=ids).all()
            except UnificationProposal.DoesNotExist:
                return HttpResponseNotFound()

            result = serialize_unification_proposals(project_id, ups, request.user)
            return JsonResponse(result, safe=False)
        else:
            return HttpResponseBadRequest()

    else:
        return HttpResponseBadRequest()
