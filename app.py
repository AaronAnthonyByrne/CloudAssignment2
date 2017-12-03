from flask import Flask, Response, render_template, request
import json
from subprocess import Popen, PIPE
import os
from tempfile import mkdtemp
from werkzeug import secure_filename

app = Flask(__name__)

@app.route("/")
def index():
    return """
Available API endpoints:
GET /containers                     List all containers
GET /containers?state=running      List running containers (only)
GET /containers/<id>                Inspect a specific container
GET /containers/<id>/logs           Dump specific container logs
GET /images                         List all images
POST /images                        Create a new image
POST /containers                    Create a new container
PATCH /containers/<id>              Change a container's state
PATCH /images/<id>                  Change a specific image's attributes
DELETE /containers/<id>             Delete a specific container
DELETE /containers                  Delete all containers (including running)
DELETE /images/<id>                 Delete a specific image
DELETE /images                      Delete all images
"""

@app.route('/containers', methods=['GET'])
def containers_index():
    """
    List all containers

    curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers | python -mjson.tool
    curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers?state=running | python -mjson.tool
    """
    if request.args.get('state') == 'running':
        output = docker('ps')
        resp = json.dumps(docker_ps_to_array(output))

    else:
        output = docker('ps', '-a')
        resp = json.dumps(docker_ps_to_array(output))

    return Response(response=resp, mimetype="application/json")

@app.route('/images', methods=['GET'])
def images_index():
    """
    List all images
    Complete the code below generating a valid response.
    """

    output = docker('images')
    resp = json.dumps(docker_images_to_array(output))

    return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>', methods=['GET'])
def containers_show(id):
    """
    Inspect specific container
    """
    resp = docker('inspect', id)
   # output = docker('inspect',id)
   # resp = json.dumps(docker_logs_to_object(id,output))
   # removed the above code becasue I couldn't get it to work but tried to call it directly and it worked, even tried a .decode()
    return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>/logs', methods=['GET'])
def containers_log(id):
    """
    Dump specific container logs
    """
    # added a decode() in order to show the logs as it was the only way I could get it to show
    output = docker('logs', id).decode()
    resp = json.dumps(docker_logs_to_object(id,output))
    return Response(response=resp, mimetype="application/json")


@app.route('/images/<id>', methods=['DELETE'])
def images_remove(id):
    """
    Delete a specific image
   #This curl here to is used to call the deleted method tp  get the code to work
    curl -s -X DELETE -H 'Content-Type: application/json' http://35.195.120.220:8080/images/<id> | python -mjson.tool
   #-X:specify HTTP request method, this instance its Delete. -H:specify request headers, this instance we used Content-type:application/json
    """
    docker ('rmi','-f', id) #had to sepcify -f to force remove an image
    resp = '{"The image that was just deleted was id": "%s"}\n' %id
    return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>', methods=['DELETE'])
def containers_remove(id):
    """
    Delete a specific container - must be already stopped/killed
   #this curl is used to call the delete method to delete a container
   curl -s -X DELETE -H 'Content-Type: application/json' http://35.195.120.220:8080/containers/<id> | python -mjson.tool
   #-X:specify HTTP request method, this instance its Delete. -H:specify request headers, this instance we used Content-type:application/json
    """
    docker ('rm',id)
    resp = '{"The following container was just deleted": "%s"}\n' %id
    return Response(response=resp, mimetype="application/json")

@app.route('/containers', methods=['DELETE'])
def containers_remove_all():
    """
    Force remove all containers - dangrous!
    #this curl is used to call the delete method to forcefully delete all containers
    curl -s -X DELETE -H 'Content-Type: application/json' http://35.195.120.220:8080/containers/ | python -mjson.tool
    #-X:specify HTTP request method, this instance its Delete. -H:specify request headers, this instance we used Content-type:application/json
    """
    # docker container rm $(docker container ls -a -q)
    # docker('container','rm',docker('container','ls', '-a','-q'))

    # trying to loop to get it working
    output = docker('ps','-a')
    loop = docker_ps_to_array(output)
    for i in loop:
        docker('stop', i['id'])
        docker('rm', i['id'])
        resp = '{"deleting conainer": "%s"}\n' %i['id']

    return Response(response=resp, mimetype="application/json")

@app.route('/images', methods=['DELETE'])
def images_remove_all():
    """
    Force remove all images - dangrous!
    #this curl is used to call the delete method to delete all images
    curl -s -X DELETE -H 'Content-Type: application/json' http://35.195.120.220:8080/images | python -mjson.tool
    #-X:specify HTTP request method, this instance its Delete. -H:specify request headers, this instance we used Content-type:application/json
    """
    #docker image rm $(docker image ls -a -q)
    # docker('image','rm','$docker','image','ls','-a','-q')

    #using the code from GET images and loop from delete all containers
    output = docker('images')
    loop = docker_images_to_array(output)
    for i in loop:
        docker('rmi','-f', i['id'])

    resp = '{"all images deleted"}\n'
    return Response(response=resp, mimetype="application/json")


@app.route('/containers', methods=['POST'])
def containers_create():
    """
    Create container (from existing image using id or name)
    curl -X POST -H 'Content-Type: application/json' http://localhost:8080/containers -d '{"image": "my-app"}'
    curl -X POST -H 'Content-Type: application/json' http://localhost:8080/containers -d '{"image": "b14752a6590e"}'
    curl -X POST -H 'Content-Type: application/json' http://localhost:8080/containers -d '{"image": "b14752a6590e","publish":"8081:22"}'
    """
    body = request.get_json(force=True)
    image = body['image']
    args = ('run', '-d')
    id = docker(*(args + (image,)))[0:12]
    return Response(response='{"id": "%s"}' % id, mimetype="application/json")


@app.route('/images', methods=['POST'])
def images_create():
    """
    Create image (from uploaded Dockerfile)
    curl -H 'Accept: application/json' -F file=@Dockerfile http://localhost:8080/images
    """
    # research for this part lead me to https://gist.github.com/dAnjou/2874714 so some code is similar
    files = request.files['file']
    newpath = mkdtemp() #this is as it is part of imports. it generates temp  directory
    filename = secure_filename(files.filename) #sercure_filename is used to make sure that the filename is secure. in built flask function
    file_dir = os.path.join(newpath,filename)
    file_path = os.path.join(newpath,'.')
    files.save(file_dir)

    resp = docker('build','-t', filename.lower(),'-f',file_dir,file_path)
    return Response(response=resp, mimetype="application/json")




@app.route('/containers/<id>', methods=['PATCH'])
def containers_update(id):
    """
    Update container attributes (support: state=running|stopped)
    curl -X PATCH -H 'Content-Type: application/json' http://localhost:8080/containers/b6cd8ea512c8 -d '{"state": "running"}'
    curl -X PATCH -H 'Content-Type: application/json' http://localhost:8080/containers/b6cd8ea512c8 -d '{"state": "stopped"}'
    """
    body = request.get_json(force=True)
    try:
        state = body['state']
        if state == 'running':
            docker('restart', id)
    except:
        pass

    resp = '{"id": "%s"}' % id
    return Response(response=resp, mimetype="application/json")

@app.route('/images/<id>', methods=['PATCH'])
def images_update(id):
    """
    Update image attributes (support: name[:tag])  tag name should be lowercase only
    curl -s -X PATCH -H 'Content-Type: application/json' http://localhost:8080/images/7f2619ed1768 -d '{"tag": "test:1.0"}'
    """
    body = request.get_json(force=True)
    resp = docker('tag',id,body['tag'])
    return Response(response=resp, mimetype="application/json")

@app.route('/services', methods=['GET'])
def services_show():
    """
    Here the service are displayed
    """
    output=docker('service','ls')
    resp = json.dumps(docker_services_to_array(output))
    return Response(response=resp, mimetype="application/json")

@app.route('/nodes', methods=['GET'])
def nodes_show():
    """
    Here the nodes in the swarm are displayed
    """
    output=docker('node','ls')
    resp = json.dumps(docker_nodes_to_array(output))
    return Response(response=resp, mimetype="application/json")

def docker(*args):
    cmd = ['docker']
    for sub in args:
        cmd.append(sub)
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stderr.startswith(b'Error'):
        print ('Error: {0} -> {1}'.format(' '.join(cmd), stderr))
    return stderr + stdout

# 
# Docker output parsing helpers
#

#
# Parses the output of a Docker PS command to a python List
# 
def docker_ps_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[0].decode()
        each['image'] = c[1].decode()
        each['name'] = c[-1].decode()
        each['ports'] = c[-2].decode()
        all.append(each)
    return all

#
# Parses the output of a Docker logs command to a python Dictionary
# (Key Value Pair object)
def docker_logs_to_object(id, output):
    logs = {}
    logs['id'] = id
    all = [' ']
    for line in output.splitlines():
        all.append(line)
    logs['logs'] = all
    return logs

#
# Parses the output of a Docker image command to a python List
# 
def docker_images_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[2].decode()
        each['tag'] = c[1].decode()
        each['name'] = c[0].decode()
        all.append(each)
    return all

#Parses the output of a docker service command to a python list - missing from code inserted based on the code above
def docker_services_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[0].decode()
        each['image'] = c[4].decode()
        each['name'] = c[1].decode()
        each['mode'] = c[2].decode()
        each['replicas'] = c[3].decode()
        all.append(each)
    return all

#Parses the output of a docker node command to a python list - missing from code inserted based on the code above
def docker_nodes_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[0].decode()
        each['hostname'] = c[1].decode()
        each['status'] = c[2].decode()
        each['AVAILABILITY'] = c[3].decode()
        each['manager_status'] = c[4].decode()
        all.append(each)
    return all

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8080, debug=True)
