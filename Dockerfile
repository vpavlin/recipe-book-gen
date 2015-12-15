FROM fedora

RUN dnf -y install python-flask python-requests
RUN dnf -y install texlive-verse texlive-setspace texlive-etoolbox texlive-titlesec texlive-tocloft texlive-tcolorbox texlive-eso-pic
RUN dnf -y install texlive texlive-latex
RUN dnf -y install texlive-wrapfig texlive-hyphenat
RUN dnf -y install ImageMagick
EXPOSE 5000

ADD . /opt/recipe-book
WORKDIR /opt/recipe-book


CMD python run.py -d
