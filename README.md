# CloudAssignment2
This is Cloud computing assignment 2. Implementation of a restful API in a google cloud service

External IP Address used http://35.195.120.220:8080

Link to Video: https://youtu.be/F6C0YR2Z4Bo
(Video was cut short due to it being free software)
This assignment demostrates the effectiveness of Docker.
Within the file you should be able to see the python code used to curl the commands.
I have also uploaded the bash file
#
To run any of the POST request yo can use the browser all that is required is the externel ip with a /.
For example listing all the images is http://35.195.120.220:8080/images

To do any other requests/methods (POST/DELETE/PATCH) you need to open a second instance of the vm. 
In this second instancd you need to call curl commands. I have listed all the curl commands below


#List all containers
    curl -s -X GET -H 'Accept: application/json' http://35.195.120.220:8080/containers 
    curl -s -X GET -H 'Accept: application/json' http://35.195.120.220:8080/containers?state=running
    
#Inspect specific container
	curl -s -X GET -H 'Accept: application/json'http://35.195.120.220:8080/containers/55e4ab534c2c
	
#Dump specific container logs
  curl -s -X GET -H 'Accept: application/json'http://35.195.120.220:8080/containers/55e4ab534c2c/logs
  
#Create container (from existing image using id or name)
    curl -X POST -H 'Content-Type: application/json' http://35.195.120.220:8080/containers -d '{"image": "my-app"}'
    
    curl -X POST -H 'Content-Type: application/json' http://35.195.120.220:8080/containers -d '{"image": "b14752a6590e"}'
    
    curl -X POST -H 'Content-Type: application/json' http://35.195.120.220:8080/containers -d '{"image": "b14752a6590e","publish":"8081:22"}'
    
#Update container attributes (support: state=running|stopped)

    curl -X PATCH -H 'Content-Type: application/json' http://35.195.120.220:8080/containers/55e4ab534c2c -d '{"state": "running"}'
    
    curl -X PATCH -H 'Content-Type: application/json' http://35.195.120.220:8080/containers/55e4ab534c2c -d '{"state": "stopped"}'	
    
#Delete a specific container - must be already stopped/killed

   curl -s -X DELETE -H 'Content-Type: application/json' http://35.195.120.220:8080/containers/55e4ab534c2c
   
#Force remove all containers - dangrous!

    curl -s -X DELETE -H 'Content-Type: application/json' http://35.195.120.220:8080/containers/
    
#Update Images

    curl -s -X PATCH -H 'Content-Type: application/json' http://35.195.120.220:8080/images/55e4ab534c2c -d '{"tag": "test:1.0"}'
    
#List all images 

	curl -s -X GET -H 'Accept: application/json'http://35.195.120.220:8080/images
#Delete a specific image
	curl -s -X DELETE -H 'Content-Type: application/json' http://35.195.120.220:8080/images/55e4ab534c2c
#Create image (from uploaded Dockerfile)
    curl -H 'Accept: application/json' -F "file=@./dockerfiles/Dockerfile" http://35.195.120.220:8080/images
#Force remove all images
	curl -s -X DELETE -H 'Content-Type: application/json' http://35.195.120.220:8080/images

