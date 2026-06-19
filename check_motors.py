"""Quick diagnostic: ping each motor on the follower arm individually."""
import scservo_sdk as scs

PORT = "/dev/tty.usbmodem5B610354731"
BAUDRATE = 1_000_000
MOTOR_IDS = [1, 2, 3, 4, 5, 6]

port_handler = scs.PortHandler(PORT)
packet_handler = scs.PacketHandler(0)  # protocol version 0

if not port_handler.openPort():
    print(f"Failed to open port {PORT}")
    exit(1)
if not port_handler.setBaudRate(BAUDRATE):
    print("Failed to set baud rate")
    exit(1)

print(f"Port open. Pinging motors on {PORT}...\n")

for motor_id in MOTOR_IDS:
    model, result, error = packet_handler.ping(port_handler, motor_id)
    if result == scs.COMM_SUCCESS:
        print(f"  Motor {motor_id}: OK (model={model})")
    else:
        status = packet_handler.getTxRxResult(result)
        print(f"  Motor {motor_id}: FAILED — {status}")

port_handler.closePort()
