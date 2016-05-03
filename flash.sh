start(){
    uwsgi --ini ./flash/uwsgi.ini
}

stop(){
    uwsgi --stop /tmp/flash.pid
}

reload(){
    uwsgi --reload /tmp/flash.pid
}

case "$1" in
  start) start ;;
  stop) stop ;;
  reload) reload ;;
  restart)
    stop
    start
    ;;
  *)  
    echo "Usage:"
    echo "./flash.sh start"
    echo "./flash.sh stop"
    echo "./flash.sh reload"
    exit 1
    ;;  
esac

exit 0

