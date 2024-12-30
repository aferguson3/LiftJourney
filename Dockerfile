FROM python:3.12-alpine
WORKDIR /home/LiftJourney
ARG DOCKER_USER=app
# Dependencies
COPY --chmod=744 requirements.txt .
RUN pip install -r requirements.txt
COPY --chmod=744 gunicorn.conf.py .

# Source code
RUN addgroup -S $DOCKER_USER && adduser -S $DOCKER_USER -G $DOCKER_USER
COPY --chmod=777 backend ./backend
RUN chown -R $DOCKER_USER:$DOCKER_USER .
EXPOSE 3000
USER $DOCKER_USER

CMD ["gunicorn", "-c", "gunicorn.conf.py"]