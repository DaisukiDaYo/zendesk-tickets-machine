from datetime import datetime

from fabric.api import (
    cd,
    env,
    local,
    put,
    run,
    sudo,
    task
)


PRODUCTION_IP = '54.154.235.243'
PROJECT_DIRECTORY = '/home/ubuntu/ztm/'
BACKUP_DIRECTORY = '/home/ubuntu/backup/'
COMPOSE_FILE = 'compose-production.yml'


@task
def production():
    env.run = sudo
    env.hosts = [
        'ubuntu@' + PRODUCTION_IP + ':22',
    ]


@task
def create_project_directory():
    run('mkdir -p ' + PROJECT_DIRECTORY)


@task
def update_compose_file():
    put('./' + COMPOSE_FILE, PROJECT_DIRECTORY)


@task
def backup():
    backup_time = datetime.now().strftime('%Y-%m-%d_%H%M')
    with cd(BACKUP_DIRECTORY):
        command = 'tar -cjvf ztm-' + backup_time + \
            '.tar.bz2 ' + PROJECT_DIRECTORY
        env.run(command)

    command = 's3cmd sync ' + BACKUP_DIRECTORY + ' ' \
        's3://zendesk-tickets-machine'
    run(command)


@task
def build():
    command = 'docker build -t ' \
        '133506877714.dkr.ecr.eu-west-1.amazonaws.com/ztm ' \
        '-f ./compose/django/Dockerfile .'
    local(command)


@task
def push():
    local('docker push 133506877714.dkr.ecr.eu-west-1.amazonaws.com/ztm')


@task
def compose_up():
    with cd(PROJECT_DIRECTORY):
        env.run('docker-compose -f ' + COMPOSE_FILE + ' pull')
        env.run('docker-compose -f ' + COMPOSE_FILE + ' up -d')


@task
def deploy():
    build()
    push()
    create_project_directory()
    update_compose_file()
    compose_up()
