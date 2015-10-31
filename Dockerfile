FROM fedora

RUN dnf -y install python-flask
RUN dnf -y install python-requests
EXPOSE 5000

ADD . /opt/recipe-book
WORKDIR /opt/recipe-book


CMD python run.py -d
