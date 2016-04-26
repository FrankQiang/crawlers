start(){
    supervisorctl -c /etc/supervisord.conf restart flash
}

case "$1" in
  start) start ;;
  *)  
    echo "Usage:"
    echo "./flash.sh start"
    exit 1
    ;;  
esac

exit 0

