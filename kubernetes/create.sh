# oc login https://console.paas.psnc.pl --token=

oc project providedh

oc create -f db-data-persistentvolumeclaim.yaml
oc create -f app-persistentvolumeclaim.yaml
oc create -f media-persistentvolumeclaim.yaml
oc create -f es-persistentvolumeclaim.yaml
oc create -f redis-persistentvolumeclaim.yaml

oc create -f postgres-imagestream.yaml
oc create -f collaborative-platform-imagestream.yaml
oc create -f celery-imagestream.yaml
oc create -f nginx-imagestream.yaml

oc create -f postgres-buildconfig.yaml
oc create -f collaborative-platform-buildconfig.yaml
oc create -f celery-buildconfig.yaml
oc create -f nginx-buildconfig.yaml

oc create -f redis-deployment.yaml
oc create -f postgres-deployment.yaml
oc create -f elasticsearch-deployment.yaml
oc create -f collaborative-platform-deployment.yaml
oc create -f celery-deployment.yaml
oc create -f nginx-deployment.yaml

oc create -f redis-service.yaml
oc create -f postgres-service.yaml
oc create -f elasticsearch-service.yaml
oc create -f collaborative-platform-service.yaml
oc create -f celery-service.yaml
oc create -f nginx-service.yaml
