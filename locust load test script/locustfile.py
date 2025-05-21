from locust import User, task, between, events
import socketio
import random
import string
import time
import threading

def random_username():
    return "user_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

class WebChatUser(User):
    wait_time = between(1, 3)

    def on_start(self):
        self.username = random_username()
        self.sio = socketio.Client(reconnection=False, logger=False, engineio_logger=False)
        self.connected = False
        self.registered = threading.Event()

        start = time.time()
        try:
            self.sio.connect("http://34.172.33.101")  # No port needed since LoadBalancer exposes 80
            self.connected = True
        except Exception as e:
            total = (time.time() - start) * 1000
            print(f"Connection failed: {e}")
            events.request.fire(
                request_type="socket.io",
                name="connect",
                response_time=total,
                response_length=0,
                exception=e,
            )
            return

        total = (time.time() - start) * 1000
        events.request.fire(
            request_type="socket.io",
            name="connect",
            response_time=total,
            response_length=0,
        )

        def register_callback(success):
            if not success:
                print(f"Username {self.username} already taken.")
            self.registered.set()

        # Emit new user and wait for callback
        start = time.time()
        self.sio.emit("new user", self.username, callback=register_callback)
        # Wait for callback or timeout after 5s
        if not self.registered.wait(timeout=5):
            print("Registration callback timed out")
            events.request.fire(
                request_type="socket.io",
                name="new user",
                response_time=5000,
                response_length=0,
                exception=Exception("Registration callback timed out"),
            )
        else:
            total = (time.time() - start) * 1000
            events.request.fire(
                request_type="socket.io",
                name="new user",
                response_time=total,
                response_length=0,
            )

    @task
    def send_message(self):
        if not self.connected:
            return  # Skip if not connected

        message = "Hello from Locust!"

        start = time.time()
        try:
            self.sio.emit("send message", message)
            total = (time.time() - start) * 1000
            events.request.fire(
                request_type="socket.io",
                name="send message",
                response_time=total,
                response_length=len(message),
            )
        except Exception as e:
            total = (time.time() - start) * 1000
            print(f"send message failed: {e}")
            events.request.fire(
                request_type="socket.io",
                name="send message",
                response_time=total,
                response_length=0,
                exception=e,
            )

    def on_stop(self):
        try:
            start = time.time()
            self.sio.disconnect()
            total = (time.time() - start) * 1000
            events.request.fire(
                request_type="socket.io",
                name="disconnect",
                response_time=total,
                response_length=0,
            )
        except Exception as e:
            print(f"Disconnect failed: {e}")
