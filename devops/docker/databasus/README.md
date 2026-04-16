# How to Configure

Currently I have this link to the main db in devops/docker/postgres which stores all my main Bible Insight Data, I can connect to this using `host.docker.internal` and the rest of the details, and then hook it up to s3 storage from devops/docker/minio using `http://localhost:9900`.

