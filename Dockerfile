FROM python:3.12-alpine
WORKDIR /home/LiftJourney
ARG DOCKER_USER=app

# Dependencies
RUN apk add npm
COPY package.json .
RUN npm install .
RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip install --requirement /tmp/requirements.txt
COPY --chmod=744 gunicorn.conf.py .

# Source code
RUN addgroup -S $DOCKER_USER && adduser -S $DOCKER_USER -G $DOCKER_USER
COPY --chmod=777 backend ./backend
RUN npm run build-css
RUN chown -R $DOCKER_USER:$DOCKER_USER .
USER $DOCKER_USER

CMD ["gunicorn", "-c", "gunicorn.conf.py"]