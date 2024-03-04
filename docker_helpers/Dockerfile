RUN apt-get update && apt-get install -y netcat-traditional jq

RUN useradd -m -u 1000 user
RUN chown -R user:user / || true
RUN chown -R user:user /src/
RUN chown -R user:user /root/
RUN chown -R user:user /var/
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONPATH=$HOME/app \
    PYTHONUNBUFFERED=1 \
    GRADIO_ALLOW_FLAGGING=never \
    GRADIO_NUM_PORTS=1 \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_THEME=huggingface \
    SYSTEM=spaces 

WORKDIR $HOME/app
COPY ./requirements.txt /code/requirements.txt

# create virtual env for Gradio app
RUN python -m venv $HOME/.venv && \
    . $HOME/.venv/bin/activate && \ 
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /code/requirements.txt 

COPY --chown=user . $HOME/app
RUN chmod +x $HOME/app/run.sh
CMD ["bash", "-c", "$HOME/app/run.sh"]
