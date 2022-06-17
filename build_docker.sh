#!/bin/bash
#optional as cli argument
dockerRepo=${1:-docker.io}/prometheus/website-monitoring-probe-generator
build=website-monitoring-probe-generator
builderImage=registry.access.redhat.com/ubi8/python-38:1-96.1654148946
RELEASE=`cat version`

s2i build . ${builderImage} ${build}:latest

docker tag ${build}:latest ${dockerRepo}:${RELEASE}
docker tag ${build}:latest ${dockerRepo}:latest
docker push ${dockerRepo}:${RELEASE}
docker push ${dockerRepo}:latest

docker rmi ${dockerRepo}:latest
docker rmi ${dockerRepo}:${RELEASE}
docker rmi ${build}:latest
