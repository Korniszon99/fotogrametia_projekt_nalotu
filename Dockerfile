FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd --create-home app && mkdir /data && chown app:app /data
COPY --chown=app:app . .
USER app
EXPOSE 8000
ENTRYPOINT ["sh", "docker-entrypoint.sh"]
CMD ["gunicorn", "fotogrametia_projekt_nalotu.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "1", "--timeout", "60"]
