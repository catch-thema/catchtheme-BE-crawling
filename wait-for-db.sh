#!/bin/sh
# wait-for-db.sh - MySQL 연결 대기 스크립트

set -e

host="$1"
shift
cmd="$@"

until python -c "import pymysql; pymysql.connect(host='$host', port=3306, user='$DB_USER', password='$DB_PASSWORD', database='$DB_NAME')" 2>/dev/null; do
  >&2 echo "MySQL is unavailable - sleeping"
  sleep 2
done

>&2 echo "MySQL is up - executing command"
exec $cmd
