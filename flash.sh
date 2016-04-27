start(){
    supervisorctl -c /etc/supervisord.conf start flash
}

stop(){
    supervisorctl -c /etc/supervisord.conf stop flash
}

case "$1" in
  start) start ;;
  stop) stop ;;
  restart)
    stop
    start
    ;;
  *)  
    echo "Usage:"
    echo "./flash.sh start"
    echo "./flash.sh stop"
    exit 1
    ;;  
esac

exit 0

