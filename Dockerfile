FROM python:3.10-slim-bookworm as release
WORKDIR /opt/ctfd_remote_llm

COPY --chown=1001:1001 . /opt/ctfd_remote_llm/
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd \
    --no-log-init \
    --shell /bin/bash \
    -u 1001 \
    ctfd_remote_llm \
    && mkdir -p /var/log/ctfd_remote_llm \
    && chown -R 1001:1001 /var/log/ctfd_remote_llm /opt/ctfd_remote_llm/remote_llm


USER 1001
EXPOSE 8000
ENTRYPOINT ["uvicorn","remote_llm.app:app", "--reload", "--host", "0.0.0.0", "--log-config", "logging.yml"]