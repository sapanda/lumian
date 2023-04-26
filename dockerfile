FROM python:3.9-alpine3.13
LABEL maintainer="getmetanext.com"

ENV PYTHONNUNBUFFERED 1

COPY ./scripts /scripts
ENV PATH="/scripts:/py/bin:$PATH"
CMD ["run.sh"]
