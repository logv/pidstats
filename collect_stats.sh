# 15 second interval collection
INTERVAL=15

# FLAGS FOR PIDSTAT
# -u collects cpu stats
# -r collects mem stats
FLAGS="-u -r"

DB_DIR="./db"
SYBIL_FLAGS="-table perf@pidstats -dir ${DB_DIR}"

LAST_DIGEST=$(date +%s)

iter=0
while [[ 1 ]]; do 
  pidstat ${FLAGS} -h ${INTERVAL} 1 | python parse_stats.py ${INTERVAL} | sybil ingest ${SYBIL_FLAGS} 2>/dev/null
  ex=$?
  if [ $ex -ne 0 ]; then
    break
  fi


  now=$(date +%s)
  mod_iter=$(($now - $LAST_DIGEST))
  if [ $mod_iter -gt 60 ]; then
    echo "DIGEST ITER $iter, SINCE LAST DIGEST", $mod_iter
    sybil digest ${SYBIL_FLAGS} 2>/dev/null &
    LAST_DIGEST=$now
  fi

  iter=$((iter+1))
done
