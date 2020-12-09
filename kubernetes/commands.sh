kompose convert
mv *.yaml kubernetes
oc login https://console.paas-dev.psnc.pl --token=
oc apply -f redis-deployment.yaml
docker login -u ti010 http://registry.apps.paas-dev.psnc.pl
docker tag collaborative-platform_web registry.apps.paas-dev.psnc.pl/providedh-est/web:latest
docker push registry.apps.paas-dev.psnc.pl/providedh-est/web/providedh-est/web:latest