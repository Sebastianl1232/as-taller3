FROM postgres:15-alpine

# Copiar scripts de inicialización
COPY init.sql /docker-entrypoint-initdb.d/01-init.sql
COPY shema.sql /docker-entrypoint-initdb.d/02-schema.sql

# Exponer el puerto
EXPOSE 5432