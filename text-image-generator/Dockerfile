FROM belval/trdg:latest

# Install all requirements
COPY requirements.txt /tmp/
RUN pip install --upgrade pip && pip install --no-cache-dir -r /tmp/requirements.txt

# Run as root to edit pip package
# RUN useradd --create-home appuser
# WORKDIR /home/appuser
# USER appuser

COPY . .

ENTRYPOINT [ "/bin/bash" ]
CMD [ "entrypoint.sh" ]
