kompose convert
mv *.yaml kubernetes
oc login https://console.paas-dev.psnc.pl --token=
oc apply -f redis-deployment.yaml
docker login -u ti010 http://registry.apps.paas-dev.psnc.pl
docker tag collaborative-platform_web registry.apps.paas-dev.psnc.pl/testing-providedh/web:latest
docker push registry.apps.paas-dev.psnc.pl/testing-providedh/web/testing-providedh/web:latest
oc new-app --docker-image="registry.apps.paas-dev.psnc.pl/testing-providedh/web:latest" https://github.com/providedh/collaborative-platform <źle
oc new-app registry.apps.paas-dev.psnc.pl/testing-providedh/web:latest~https://github.com/providedh/collaborative-platform.git --strategy=docker

hub.docker.com
docker tag collaborative-platform_web ti010/collaborative_platform:latest                                                                                               [1]
docker push ti010/collaborative_platform:latest

oc new-app "ti010/collaborative_platform:latest~https://github.com/providedh/collaborative-platform#PaaStests" --strategy=docker

oc new-app "https://github.com/providedh/collaborative-platform#PaaStests"
oc apply -f web-storage-persistentvolumeclaim.yaml

oc expose deployments/nginx
oc expose service/nginx

oc get -o yaml --export all > project.yaml

for object in $(oc api-resources --namespaced=true -o name)
do
  oc get -o yaml $object > $object.yaml
done