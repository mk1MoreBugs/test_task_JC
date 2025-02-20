# test_task_JC

## Run project
0. Install docker and docker compose

1. Create file `db_password.txt` with password from postgresql db in root dir

2. Run:
```
docker compose up
```
####
__**link to view docs:**__ http://localhost:8080/docs

####
## Run tests
1. Run project in docker-compose
2. cd to `backend` dir
```commandline
cd ./backend
```
3. Create a virtual environment
```commandline
python -m venv .venv
```
4. Activate a virtual environment
```commandline
source .venv/bin/activate
```
5. Install dependencies
```commandline
pip install -r requirements.txt
```
6. Run bash script. *This script creates a test database, runs the tests using pytest, and deletes the test database.*
```commandline
app/tests/run_tests.sh
```
