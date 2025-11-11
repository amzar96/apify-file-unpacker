FROM apify/actor-python:3.13

USER myuser

RUN pip install uv

COPY --chown=myuser:myuser pyproject.toml ./
COPY --chown=myuser:myuser uv.lock* ./

RUN echo "Python version:" \
 && python --version \
 && echo "UV version:" \
 && uv --version \
 && echo "Installing dependencies with UV:" \
 && uv sync --frozen \
 && echo "All installed Python packages:" \
 && uv pip list

COPY --chown=myuser:myuser . ./


RUN python3 -m compileall -q src/

CMD ["uv", "run", "python3", "-m", "src"]
