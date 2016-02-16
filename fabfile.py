import os
import sys
from distutils.version import LooseVersion as V
from fabric.api import env, run, cd, local, lcd, get, prefix, sudo

from version import VERSION


version = V(VERSION)


env.hosts = ['systori.com']


deploy_apps = {
    'dev': ['dev'],
    'production': ['production']
}


PROD_DUMP_FILE = 'systori.prod.dump'
PROD_MEDIA_PATH = '/srv/systori/production'
PROD_MEDIA_FILE = 'systori.media.tgz'


def deploy(env_name='dev'):
    env.user = 'ubrblik'

    for app in deploy_apps[env_name]:

        sudo('service uwsgi stop systori_' + app)

        with cd('/srv/systori/' + app + '/systori'):

            if env_name == 'dev':
                # load production db
                sudo('dropdb systori_dev', user='www-data')
                sudo('createdb systori_dev', user='www-data')
                sudo('pg_dump -f prod.sql systori_production', user='www-data')
                sudo('psql -f prod.sql systori_dev >/dev/null', user='www-data')
                sudo('rm prod.sql')

            run('git pull')

            with cd('systori/dart'):
                run('/usr/lib/dart/bin/pub get')
                run('/usr/lib/dart/bin/pub build')

            with prefix('source ../bin/activate'):
                run('pip install -q -U -r requirements/%s.pip' % env_name)
                sudo('./manage.py migrate --noinput', user='www-data')
                run('./manage.py collectstatic --noinput --verbosity 0')

        sudo('service uwsgi start systori_' + app)


def _reset_localdb():
    local('dropdb systori_local')
    local('createdb systori_local')


def fetch_productiondb():
    dbname = 'systori_production'
    # -Fc : custom postgresql compressed format
    sudo('pg_dump -Fc -x -f /tmp/%s %s' % (PROD_DUMP_FILE, dbname), user='www-data')
    get('/tmp/' + PROD_DUMP_FILE, PROD_DUMP_FILE)
    sudo('rm /tmp/' + PROD_DUMP_FILE)


def load_productiondb():
    _reset_localdb()
    local('pg_restore -d systori_local -O ' + PROD_DUMP_FILE)


def get_db():
    fetch_productiondb()
    load_productiondb()
    local('rm ' + PROD_DUMP_FILE)


def get_media():
    with cd(PROD_MEDIA_PATH):
        run('tar -cz media -f /tmp/' + PROD_MEDIA_FILE)
    get('/tmp/' + PROD_MEDIA_FILE, PROD_MEDIA_FILE)
    local('tar xfz ' + PROD_MEDIA_FILE)
    local('rm ' + PROD_MEDIA_FILE)
    run('rm /tmp/' + PROD_MEDIA_FILE)


def docker_from_productiondb(container_name='web'):
    settings = {
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db_1'
    }
    fetch_productiondb()
    local('docker-compose run {0} dropdb -h {HOST} -U {USER} {NAME}'.format(
        container_name, **settings))
    local('docker-compose run {0} createdb -h {HOST} -U {USER} {NAME}'.format(
        container_name, **settings))
    local('docker-compose run {0} pg_restore -d {NAME} -O {1} -h {HOST} -U {USER}'.format(
        container_name, PROD_DUMP_FILE, **settings))
    local('rm ' + PROD_DUMP_FILE)


def init_settings(env_name='local'):
    assert env_name in ['dev', 'production', 'local', 'travis']
    if os.path.exists('systori/settings/__init__.py'):
        print('Settings have already been initialized.')
    else:
        with open('systori/settings/__init__.py', 'w') as s:
            print('Initializing settings for {}'.format(env_name))
            s.write('from .{} import *\n'.format(env_name))


def make_messages():
    local('./manage.py makemessages -l de -e tex,html,py')


def get_dart():
    is_64bits = sys.maxsize > 2**32
    BIN_DIR = os.path.expanduser('~/bin')
    if not os.path.exists(BIN_DIR):
        os.mkdir(BIN_DIR)
    url = (
        'http://storage.googleapis.com/dart-archive/channels'
        '/stable/release/latest/sdk/dartsdk-linux-%s-release.zip'
    ) % ('x64' if is_64bits else 'ia32')
    with lcd(BIN_DIR):
        local("curl %s > dartsdk.zip" % url)
        local("unzip -qo dartsdk.zip")
    env_lines = """\
export DART_SDK="%s"
export PATH="$HOME/.pub-cache/bin:$DART_SDK/bin:$PATH"
""" % os.path.join(BIN_DIR, 'dart-sdk')
    bash_rc_file = os.path.expanduser('~/.bashrc')
    if not os.path.exists(bash_rc_file):
        print("Add to your environment:")
        print(env_lines)
    elif not 'DART_SDK' in open(bash_rc_file, 'r').read():
        with open(bash_rc_file, 'a') as file_handle:
            file_handle.write(env_lines)


def link_dart():
    with open('systori/dart/.packages', 'r') as packages:
        for package in packages:
            if package.startswith('#'):
                continue
            package_name, location = package.strip().split(':', 1)
            location = '/' + location.lstrip('file:///')
            try:
                os.symlink(location, os.path.join('systori/dart/web/packages', package_name))
            except OSError, exc:
                print exc


def make_dart():
    with lcd('systori/dart'):
        local('pub build --mode=debug')


def get_bitbucket_login():
    try:
        user, password = open('bitbucket.login').read().split(':')
        return user.strip(), password.strip()
    except:
        print
        'Bitbucket API requires your user credentials'
        user = raw_input('Username: ') or exit(1)
        password = raw_input('Password: ') or exit(1)
        saved = '{}:{}'.format(user, password)
        open('bitbucket.login', 'w').write(saved)
        return user, password


REPO = 'https://api.bitbucket.org/1.0/repositories/damoti/systori/'


def current_issues():
    import requests
    r = requests.get(REPO + 'issues?status=new', auth=get_bitbucket_login())
    print
    r.status_code
    print
    r.text


def mail():
    local('python -m smtpd -n -c DebuggingServer localhost:1025')


# Git Workflow
# See: http://nvie.com/posts/a-successful-git-branching-model/


def bump_version(ver):
    with file('version.py', 'w') as f:
        f.write('VERSION = \'%s\'' % ver)
    print('Bumped version number to %s' % ver)


def feature_start(name):
    "fab feature_start:name=my_new_feature"
    local('git checkout -b %s dev' % name)


def feature_finish(name):
    "fab feature_finish:name=my_new_feature"
    local('git checkout dev')
    local('git merge --no-ff %s' % name)
    local('git branch -d %s' % name)
    local('git push origin dev')


def release_start(ver):
    branch = 'release-%s' % ver
    local('git checkout -b %s dev' % branch)
    if VERSION != ver:
        bump_version(ver)
    with settings(warn_only=True):
        local('git commit -a -m "bumped version number to %s"' % ver)
    local('git push origin %s' % branch)


def release_finish():
    _merge_this()


def hotfix_start(bump='yes'):
    sub_number = version.version[1] + (bump == 'yes' and 1 or 0)
    new_ver = '%s.%s' % (version.version[0], sub_number)
    local('git checkout -b hotfix-%s master' % new_ver)
    if bump == 'bump':
        bump_version(new_ver)
        local('git commit version.py -m "bumped version number to %s"' % new_ver)


def hotfix_finish():
    _merge_this()


def _merge_this():
    '''
    Merge current branch into both master and dev branches, then delete it.
    Meant to be called from commands
    '''
    # Parsing branch version: (release|hotfix)-<major>.<minor>
    branch = local('git rev-parse --abbrev-ref HEAD', capture=True).rstrip()
    if branch in ('master', 'dev'):
        abort('''Your current branch is %s, which is one of the main branches. 
            Try checking out your hotfix/release branch.''' % branch)
    # Trying to figure out version from current branch name
    ver = branch.split('-')
    ver = len(ver) > 1 and ver[-1] or None
    # Merging into prod branch
    local('git checkout master')
    local('git merge --no-ff %s' % branch)
    if ver:
        # Updating prod branch tag
        local('git tag -a -f -m "{v}" {v}'.format(v=ver))
    local('git push')
    # Merging into dev
    local('git checkout dev')
    local('git merge --no-ff %s' % branch)
    # Killing this branch
    with settings(warn_only=True):
        local('git push origin :%s' % branch)
    local('git branch -d %s' % branch)
    local('git push')
