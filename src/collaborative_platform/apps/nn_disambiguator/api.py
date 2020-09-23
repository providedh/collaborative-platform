import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse, HttpResponseNotFound, HttpResponse

from apps.api_vis.request_handler import RequestHandler
from apps.nn_disambiguator.helpers import queue_task, abort_pending
from apps.nn_disambiguator.models import CeleryTask, UnificationProposal
from apps.projects.models import ProjectVersion
from apps.views_decorators import objects_exists, user_has_access


@login_required
@objects_exists
@user_has_access('RW')
def calculations(request: HttpRequest, project_id: int):
    if request.method == "POST":
        if request.POST["action"] == "start":
            return queue_task(project_id, "P")
        elif request.POST["action"] == "abort":
            return abort_pending(project_id, "P")
    elif request.method == "GET":
        try:
            hist = CeleryTask.objects.filter(project_id=project_id, type="P").all()
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
            ups = UnificationProposal.objects.filter(project_id=project_id, decided=False).all()
        except UnificationProposal.DoesNotExist:
            return JsonResponse({"message": "There are no proposals to show."})

        rh = RequestHandler(project_id, request.user)

        pv = ProjectVersion.objects.filter(project_id=project_id).latest("id")

        result = []
        for up in ups:
            res = {"id": up.id, "degree": up.confidence, "entity": rh.serialize_entities([up.entity], pv)[0]}
            if up.entity2 is not None:
                res["target_entity"] = rh.serialize_entities([up.entity2], pv)[0]
            elif up.clique is not None:
                clq = up.clique
                res["target_clique"] = {
                    "id": clq.id,
                    "name": clq.name,
                    "type": clq.type,
                    "entities": clq.unifications.values_list("entity_id", flat=True)
                }
            else:
                raise KeyError("Unification proposal has no target")
            result.append(res)

        return JsonResponse(result, safe=False)

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
            up.reject(request.user, args["certainty"])
            return JsonResponse({"message": "Rejected successfully"})
