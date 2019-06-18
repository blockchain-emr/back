# CareBlocks

CareBlocks is a demonstration on the applications of Blockchain technology in healthcare.


## Installation for developers

### Prerequisites:
First of all you need to have these requirements installed :

- [docker](https://docs.docker.com/install/)
- [docker-compose](https://docs.docker.com/compose/install/)
- [python == 3.6.x (python3.7 is not the same)](https://realpython.com/installing-python/)
- pip
- [virtualenv](https://virtualenv.pypa.io/en/latest/installation/)

****
### Running the infrastructure :

First you have to start the private chain to start working with.

```bash
cd Infra/
docker-compose up -d
```
**NOTICE: make sure the docker service is up and running before runnig this.**

This should get the following up and running :
- 1 Bootstrap node.
- 1 geth (ethereum node) running with rpc port 8545 exposed.
- 1 ethereum monitoring interface can be accessed via http://localhost:3000/ .


To kill the containers guess what :grin: : 
```bash
cd Infra/
docker-compose down
```

## Development process

### 1 - Running the Code:

You can run the code using either:

1. [**Running on your machine directly.**](https://github.com/blockchain-emr/back/blob/master/README.md#L38)

2. [**Running in a docker container.**](https://github.com/blockchain-emr/back/blob/master/README.md#L62)


#### To run on your machine directly :

1. Make sure the virtualenv is created, if so activate it.
```bash
cd src/
#creating virtual env
virtualenv venv
#activating the virtual env
bash venv/bin/activate
```

2. Make sure to install the requirements.
```bash
cd src/
pip install -r requirements.txt
```

3. run the code with --debug option (recommended).
```bash
cd src/app
python app.py --debug
```
Make sure you don't have any other programs using port 5000.

#### To run using docker :

Forget about it right now, I'm fixing some issues with this approach.


_______________

### 2- Adding new code/functionality:
The project code can be found at ```src/app``` and organized as the following :

- ```api```  : contains code for api endpoints.

- ```common```  : contains configurations, constants, templates, whatever is shared and has no functionality.

- ```utils```  : contains helper functions, utilities, etc.

- ```docs```  : contains any documents related to the code (not the whole project, only the code).


Happy Coding !! :grinning:

## Documentation

**API (Swagger) :**

To access _API's docs (a fully functional swagger documentation)_, after running the api you can navigate to http://localhost:5000/apidocs with your browser.


Each endpoint in the api exist in ```src/app/api``` directory.

The documentation for each endpoint can be found at ```src/app/docs/swagger/<category>/<endpoint_name>.yml```.



**Functions :**

You can find inline docs in functions, it's basically consists of:

- A description.
- args : the parameters that function takes.
- returns: what function returns.

Both args and returns are in the following format :
```python
   variable_name <variable_data_type> : variable description.
```
