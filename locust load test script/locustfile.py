# from locust import User, task, between, events
# import socketio
# import random
# import string
# import time

# class ChatUser(User):
#     wait_time = between(1, 2)

#     def on_start(self):
#         self.username = "user_" + ''.join(random.choices(string.ascii_lowercase, k=6))
#         self.sio = socketio.Client(logger=True, engineio_logger=True)
#         self.connected = False

#         @self.sio.on('connect')
#         def on_connect():
#             self.connected = True
#             self.sio.emit("new user", self.username, callback=self.handle_login)

#         @self.sio.on('new message')
#         def on_message(data):
#             pass  # You can handle or ignore this

#         try:
#             self.sio.connect("http://34.71.189.84:80", transports=['websocket'], wait=True)
#         except Exception as e:
#             events.request_failure.fire(
#                 request_type="socket.io",
#                 name="connect",
#                 response_time=0,
#                 exception=e,
#             )

#     def handle_login(self, success):
#         if not success:
#             self.username += "_1"
#             self.sio.emit("new user", self.username, callback=self.handle_login)

#     @task
#     def send_message(self):
#         if not self.connected:
#             return

#         msg = "Hello " + ''.join(random.choices(string.ascii_letters, k=10))
#         start_time = time.time()

#         try:
#             def ack_callback():
#                 elapsed = int((time.time() - start_time) * 1000)
#                 events.request_success.fire(
#                     request_type="socket.io",
#                     name="send_message",
#                     response_time=elapsed,
#                     response_length=len(msg),
#                 )

#             self.sio.emit("send message", msg, callback=ack_callback)

#         except Exception as e:
#             events.request_failure.fire(
#                 request_type="socket.io",
#                 name="send_message",
#                 response_time=0,
#                 exception=e,
#             )






# from locust import User, task, between, events
# import socketio
# import time
# import random
# import string

# class WebSocketClient:
#     def __init__(self, base_url):
#         self.base_url = base_url
#         self.sio = socketio.Client()
#         self.username = self._generate_username()

#     def _generate_username(self):
#         return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

#     def connect(self):
#         try:
#             self.sio.connect(self.base_url, transports=["polling"])
#         except Exception as e:
#             raise RuntimeError(f"Socket.IO connection failed: {e}")

#     def register_user(self):
#         def ack(response):
#             if not response:
#                 raise RuntimeError("Username already exists or Redis failed.")
        
#         start_time = time.time()
#         try:
#             self.sio.emit("new user", self.username, ack=ack)
#             elapsed = int((time.time() - start_time) * 1000)
#             events.request_success.fire(request_type="socketio", name="new user", response_time=elapsed, response_length=0)
#         except Exception as e:
#             elapsed = int((time.time() - start_time) * 1000)
#             events.request_failure.fire(request_type="socketio", name="new user", response_time=elapsed, exception=e)

#     def send_message(self):
#         start_time = time.time()
#         try:
#             self.sio.emit("send message", f"Hello from {self.username}")
#             elapsed = int((time.time() - start_time) * 1000)
#             events.request_success.fire(request_type="socketio", name="send message", response_time=elapsed, response_length=0)
#         except Exception as e:
#             elapsed = int((time.time() - start_time) * 1000)
#             events.request_failure.fire(request_type="socketio", name="send message", response_time=elapsed, exception=e)

#     def disconnect(self):
#         try:
#             self.sio.disconnect()
#         except:
#             pass

# class WebChatUser(User):
#     wait_time = between(1, 3)

#     def on_start(self):
#         self.client = WebSocketClient("http://35.225.80.220:80")
#         self.client.connect()
#         self.client.register_user()

#     @task
#     def send_message(self):
#         self.client.send_message()

#     def on_stop(self):
#         self.client.disconnect()





# from locust import User, task, between, events
# import socketio
# import random
# import string
# import time

# class ChatUser(User):
#     wait_time = between(1, 2)

#     def on_start(self):
#         self.username = "user_" + ''.join(random.choices(string.ascii_lowercase, k=6))
#         self.sio = socketio.Client()
#         self.connected = False

#         # Setup event handlers BEFORE connect
#         @self.sio.event
#         def connect():
#             self.connected = True
#             self.sio.emit("new user", self.username, callback=self.handle_login)

#         @self.sio.event
#         def disconnect():
#             self.connected = False

#         try:
#             self.sio.connect("http://34.71.189.84:80", transports=["websocket"])
#         except Exception as e:
#             events.request_failure.fire(
#                 request_type="socket.io",
#                 name="connect",
#                 response_time=0,
#                 exception=e,
#             )

#     def handle_login(self, success):
#         if not success:
#             self.username += "_1"
#             self.sio.emit("new user", self.username, callback=self.handle_login)

#     @task
#     def send_message(self):
#         if not self.connected:
#             return

#         msg = "Hello " + ''.join(random.choices(string.ascii_letters, k=10))
#         start_time = time.time()

#         try:
#             def ack_callback(*args):
#                 elapsed = int((time.time() - start_time) * 1000)
#                 events.request_success.fire(
#                     request_type="socket.io",
#                     name="send_message",
#                     response_time=elapsed,
#                     response_length=len(msg),
#                 )

#             self.sio.emit("send message", msg, callback=ack_callback)

#         except Exception as e:
#             events.request_failure.fire(
#                 request_type="socket.io",
#                 name="send_message",
#                 response_time=0,
#                 exception=e,
#             )





# from locust import User, task, between, events
# import socketio
# import random
# import string
# import time

# def random_username():
#     return "user_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

# class WebChatUser(User):
#     wait_time = between(1, 3)  # Simulate realistic delays between actions

#     def on_start(self):
#         self.username = random_username()
#         self.sio = socketio.Client(reconnection=False, logger=False, engineio_logger=False)

#         start = time.time()
#         try:
#             self.sio.connect("http://35.225.80.220:80")
#         except Exception as e:
#             print("Connection failed:", e)
#             total = time.time() - start
#             events.request.fire(
#                 request_type="socket.io",
#                 name="connect",
#                 response_time=total * 1000,
#                 response_length=0,
#                 exception=e,
#             )
#             return

#         total = time.time() - start
#         events.request.fire(
#             request_type="socket.io",
#             name="connect",
#             response_time=total * 1000,
#             response_length=0,
#         )

#         # Register new user
#         def register_callback(success):
#             if not success:
#                 print(f"Username {self.username} already taken.")

#         start = time.time()
#         self.sio.emit("new user", self.username, callback=register_callback)
#         total = time.time() - start
#         events.request.fire(
#             request_type="socket.io",
#             name="new user",
#             response_time=total * 1000,
#             response_length=0,
#         )

#     @task
#     def send_message(self):
#         message = "Hello from Locust!"
#         payload = {"msg": message}

#         start = time.time()
#         try:
#             self.sio.emit("send message", message)
#             total = time.time() - start
#             events.request.fire(
#                 request_type="socket.io",
#                 name="send message",
#                 response_time=total * 1000,
#                 response_length=len(message),
#             )
#         except Exception as e:
#             total = time.time() - start
#             events.request.fire(
#                 request_type="socket.io",
#                 name="send message",
#                 response_time=total * 1000,
#                 response_length=0,
#                 exception=e,
#             )

#     def on_stop(self):
#         try:
#             self.sio.disconnect()
#         except Exception:
#             pass



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
