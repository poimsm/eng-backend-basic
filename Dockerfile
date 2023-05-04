FROM python:3.10.5-bullseye

RUN apt-get update
RUN apt-get install -y vim

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

# ENV NLTK_DATA /usr/local/share/nltk_data/corpora/wordnet
# RUN python -m nltk.downloader -d /usr/local/share/nltk_data all

ENV NLTK_DATA /usr/local/share/nltk_data/corpora/wordnet
RUN python -m nltk.downloader omw-1.4
RUN python -m nltk.downloader -d /usr/local/share/nltk_data wordnet
RUN python -m textblob.download_corpora

COPY ./backend /app

WORKDIR /app

COPY ./entrypoint.sh /

EXPOSE 8000 8100

ENTRYPOINT ["sh", "/entrypoint.sh"]