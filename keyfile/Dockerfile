FROM mongo:8.0.9
COPY /auth/mongodb-keyfile /keyfile/auth/mongodb-keyfile
RUN chmod 600 /keyfile/auth/mongodb-keyfile
RUN chown 999:999 /keyfile/auth/mongodb-keyfile