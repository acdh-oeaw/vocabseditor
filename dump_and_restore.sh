rm dump.sql
pg_dump -d vocabseditor -h 127.0.0.1 -p 5433 -U vocabseditor -c -f dump.sql
psql --username=postgres --dbname=vocabseditor  --port=5432
\ir dump.sql
