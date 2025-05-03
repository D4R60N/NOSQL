FROM mongo:8.0.9
COPY /auth/mongodb-keyfile /mongodb-build/auth/mongodb-keyfile
RUN chmod 600 /mongodb-build/auth/mongodb-keyfile
RUN chown 999:999 /mongodb-build/auth/mongodb-keyfile