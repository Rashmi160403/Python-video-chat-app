import cv2
import socket
import pickle
import struct

# Sender function
def sender():
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sender_socket.bind(("0.0.0.0", 1234))
    sender_socket.listen(5)
    

    print("Waiting for a connection...")
    sender_conn, sender_addr = sender_socket.accept()
    print("Connected to", sender_addr)

    capture = cv2.VideoCapture(0)

    while True:
        ret, frame = capture.read()
        data = pickle.dumps(frame)
        sender_conn.sendall(struct.pack("Q", len(data)) + data)

        cv2.imshow("Sender", frame)
        if cv2.waitKey(1) == 13:
            cv2.destroyAllWindows()
            break

    sender_conn.close()

# Receiver function
def receiver():
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver_socket.connect(("127.0.0.1", 1234))

    data = b""
    payload_size = struct.calcsize("Q")

    while True:
        while len(data) < payload_size:
            packet = receiver_socket.recv(4 * 1024)
            if not packet:
                break
            data += packet

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0]

        while len(data) < msg_size:
            data += receiver_socket.recv(4 * 1024)

        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data)

        cv2.imshow("Receiver", frame)
        if cv2.waitKey(1) == 13:
            cv2.destroyAllWindows()
            break

    receiver_socket.close()

if __name__ == "__main__":
    import threading

    sender_thread = threading.Thread(target=sender)
    receiver_thread = threading.Thread(target=receiver)

    sender_thread.start()
    receiver_thread.start()
