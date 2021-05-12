FROM python:3 as unit-tests

RUN pip3 install mock

COPY . .
# Run UT
run python test_keep_it_simple.py

# Build the actual image
FROM python:3

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
CMD [ "python3", "keep_it_simple.py" ]
