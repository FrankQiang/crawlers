start(){
    supervisorctl -c /etc/supervisord.conf restart flash
}

stop(){
    supervisorctl -c /etc/supervisord.conf stop flash
}

case "$1" in
  start) start ;;
  stop) stop ;;
  *)  
    echo "Usage:"
    echo "./flash.sh start"
    echo "./flash.sh stop"
    exit 1
    ;;  
esac

exit 0

