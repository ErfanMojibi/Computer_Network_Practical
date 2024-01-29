SERVER_SRC = server.py
CLIENT_SRC = client.py

SERVER_IP ?= 0.0.0.0
SERVER_PORT ?= 9999
CLIENT_ID ?= 12345

server: $(SERVER_SRC)
	python3 $(SERVER_SRC) $(SERVER_IP) $(SERVER_PORT)

client: $(CLIENT_SRC)
	python3 $(CLIENT_SRC) $(SERVER_IP) $(SERVER_PORT) $(CLIENT_ID)

clean:
	rm -rf *.pyc