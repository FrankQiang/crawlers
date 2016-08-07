### 首先

    install python, python3 and pip

### 配置环境

    pip install virtualenv

    git clone

    # flash 目录下

    virtualenv -p python3 env

    source env/bin/activate

    pip install -r requirements.txt

### 参数配置

    # flash/flash 目录下

    cp constant.py.sample constant.py

    修改 LOCAL_HOST  为 本地或服务器 HOST

    cp settings.py.sample  settings.py

    修改 mongoengine 用户名和密码

    cp uwsgi.ini.sample  uwsgi.ini

    chdir           = /local_code_path
    daemonize       = /local_code_path/logs/uwsgi.log
    home            = /local_code_path/env


### nginx 配置

    upstream django {
      server unix:///tmp/flash.sock;
    }

    server {
          listen *:80;
          server_name local.flash;
          location / {
              uwsgi_pass  django;
              include     uwsgi_params;
          }
    }

### 服务启动

    切换到root 用户
    ./flash.sh start

### 其它

    ps aux | grep uwsgi  #查看uwsgi 进程
