#!/bin/bash
# script to run the commands for cloud computing assignment

#List all containers
    curl -s -X GET -H 'Accept: application/json' http://35.195.120.220:8080/containers 
#   curl -s -X GET -H 'Accept: application/json' http://35.195.120.220:8080/containers?state=running
#Inspect specific container
#	curl -s -X GET -H 'Accept: application/json'http://35.195.120.220:8080/containers/55e4ab534c2c
#Dump specific container logs
#	curl -s -X GET -H 'Accept: application/json'http://35.195.120.220:8080/containers/55e4ab534c2c/logs
#Create container (from existing image using id or name)
#    curl -X POST -H 'Content-Type: application/json' http://35.195.120.220:8080/containers -d '{"image": "my-app"}'
#    curl -X POST -H 'Content-Type: application/json' http://35.195.120.220:8080/containers -d '{"image": "b14752a6590e"}'
#    curl -X POST -H 'Content-Type: application/json' http://35.195.120.220:8080/containers -d '{"image": "b14752a6590e","publish":"8081:22"}'
#Update container attributes (support: state=running|stopped)
#    curl -X PATCH -H 'Content-Type: application/json' http://35.195.120.220:8080/containers/55e4ab534c2c -d '{"state": "running"}'
#    curl -X PATCH -H 'Content-Type: application/json' http://35.195.120.220:8080/containers/55e4ab534c2c -d '{"state": "stopped"}'	
#Delete a specific container - must be already stopped/killed
#   curl -s -X DELETE -H 'Content-Type: application/json' http://35.195.120.220:8080/containers/55e4ab534c2c
#Force remove all containers - dangrous!
#    curl -s -X DELETE -H 'Content-Type: application/json' http://35.195.120.220:8080/containers/
    
#Update Images
#    curl -s -X PATCH -H 'Content-Type: application/json' http://35.195.120.220:8080/images/55e4ab534c2c -d '{"tag": "test:1.0"}'
#List all images 
#	curl -s -X GET -H 'Accept: application/json'http://35.195.120.220:8080/images
#Delete a specific image
#	curl -s -X DELETE -H 'Content-Type: application/json' http://35.195.120.220:8080/images/55e4ab534c2c
#Create image (from uploaded Dockerfile)
#    curl -H 'Accept: application/json' -F "file=@./dockerfiles/Dockerfile" http://35.195.120.220:8080/images
#Force remove all images
#	curl -s -X DELETE -H 'Content-Type: application/json' http://35.195.120.220:8080/images
