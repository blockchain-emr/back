# CareBlocks

CareBlocks is a demonstration on the applications of Blockchain technology in healthcare.





### List of contents:

- [Installation for developers](https://github.com/blockchain-emr/back#installation-for-developers)
   1. [Prerequisites](https://github.com/blockchain-emr/back#prerequisites)
   2. [Running the infrastructure](https://github.com/blockchain-emr/back#running-the-infrastructure-)

- [Development process](https://github.com/blockchain-emr/back#development-process)
   1. [Running the Code](https://github.com/blockchain-emr/back#1---running-the-code)
   2. [Adding new code/functionality](https://github.com/blockchain-emr/back#2--adding-new-codefunctionality)
      - [Adding Code](https://github.com/blockchain-emr/back#adding-code)
      - [Adding libraries/imports](https://github.com/blockchain-emr/back#adding-librariesimports)
      - [Adding API Endpoints](https://github.com/blockchain-emr/back#adding-api-endpoints)

- [Documentation](https://github.com/blockchain-emr/back#documentation)
  1. [API (Swagger)](https://github.com/blockchain-emr/back#api-swagger-)
  2. [Functions' docs](https://github.com/blockchain-emr/back#functions-docs-)

********

## Installation for developers
### Prerequisites:
First of all you need to have these requirements installed :

- [docker](https://docs.docker.com/install/)
- [docker-compose](https://docs.docker.com/compose/install/)
- [python == 3.6.x (python3.7 is not the same)](https://realpython.com/installing-python/)
- pip
- [virtualenv](https://virtualenv.pypa.io/en/latest/installation/)
- [nodejs](https://nodejs.org/en/download/)
- truffle, just run `sudo npm install -g truffle@5.0.2`

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
- 1 IPFS node.


To kill the containers guess what :grin: :
```bash
cd Infra/
docker-compose down
```

## Development process

### 1 - Running the Code:

You can run the code using either:

1. [**Running on your machine directly.**](https://github.com/blockchain-emr/back/blob/master/README.md#to-run-on-your-machine-directly-)

2. [**Running in a docker container.**](https://github.com/blockchain-emr/back/blob/master/README.md#L62)


#### To run on your machine directly :

1. Make sure the virtualenv is created, if so activate it.
```bash
cd src/
#creating virtual env
virtualenv -p $(which python3) venv
#activating the virtual env
source venv/bin/activate
```

2. Make sure to install the requirements.
```bash
cd src/
pip install -r requirements.txt
```
**NOTE: IF you Encounter Python.h not found error, make sure to install python development tools like so:**
* Fedora/Redhat
   ```bash
      dnf install python3-devel
   ```
* Ubuntu/Debian
   ```bash
      apt-get install python3-dev
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

**Before you do anything, please make sure you have the latest code by pulling the master branch.**

#### Adding Code:
The project code can be found at ```src/app``` and organized as the following :

- ```api```  : contains code for api endpoints.

- ```common```  : contains configurations, constants, templates, whatever is shared and has no functionality.

- ```utils```  : contains helper functions, utilities, etc.

- ```docs```  : contains any documents related to the code (not the whole project, only the code).


#### Adding libraries/imports:
**When installing/using additional libraries in the code please, please, please don't forget to append it to the ``src/requirements.txt``**
```bash
pip freeze > requirements.txt
```

#### Adding API Endpoints:
You can create a file with the category your creating endpoints to, for example ``account_details.py`` contains functions to do CRUD on user data like name, balance, etc.

Above the function your write, please use ``@swag_from("path")`` decorator to refer to the swagger yaml documentation.

When done writing your endpoints, if you created a new file don't forget to add and import line in ``app.py``  to make it work like :  
```python
#from api.<file-you-added> import *
from api.account_details import *
```


Happy Coding !! :grinning:

## Documentation

### API (Swagger) :

To access _API's docs (a fully functional swagger documentation)_, after running the api you can navigate to http://localhost:5000/apidocs with your browser.


Each endpoint in the api exist in ```src/app/api``` directory.

The documentation for each endpoint can be found at ```src/app/docs/swagger/<category>/<endpoint_name>.yml```.



### Functions' docs :

You can find inline docs in functions, it's basically consists of:

- A description.
- args : the parameters that function takes.
- returns: what function returns.

Both args and returns are in the following format :
```python
   variable_name <variable_data_type> : variable description.
```
