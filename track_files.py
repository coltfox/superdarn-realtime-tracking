"""
Tracks real-time SuperDARN radar data.

Data is stored in a CSV file containing:
    Beam number
    Number of echoes
    Number of ionospheric echoes
    Number of ground scatter echoes

Each CSV file is updated for a 24 hour period.
"""
import socketio
import datetime as dt
import os
import csv
from dotenv import load_dotenv

OUTPUT_DIR = ".\output"
CSV_HEADERS = ['Timestamp', 'Beam_Number', 'Num_Echoes',
               'Num_Ionosph_Echoes', 'Num_Gnd_sctr_Echoes']

RADARS = ['sas', 'rkn', 'pgr', 'cly', 'inv', 'bks', 'fhe', 'fhw', 'kap', 'gbr', 'cve', 'cvw', 'mcm', 'kod', 'hok', 'hkw', 'wal']


def start_listening(socket_addr: str):
    """
    Start listening for JSON packets on `socket_addr`

    :Args:
        socket_addr (str): Address that pushes JSON packets of radar data using Socket IO
    """

    print(f"Listening on ${socket_addr}\n")
    with socketio.SimpleClient() as sio:
        sio.connect(socket_addr, transports=['websocket'])

        while True:
            try:
                event = sio.receive()
                dmap_dict = event[1:][0]
                print(f"Received data from radar ${dmap_dict['site_name']}")
                write_csv(dmap_dict)
            except KeyboardInterrupt:
                print("Stopping...")


def write_csv(json_packet: dict):
    """
    Write data to a CSV file from a JSON packet received from a socket

    :Args:
        json_packet (dict): The JSON packet received from the socket
    """
    now = dt.datetime.now()
    timestamp = now.strftime('%Y-%m-%d-%H:%M:%S.%f')
    site_name = json_packet['site_name']

    # Check if directory exists, create it if not
    subdir_name = now.strftime("%Y-%m-%d")
    subdir_path = os.path.join(OUTPUT_DIR, subdir_name)

    if not os.path.exists(subdir_path):
        print(f"No directory exists for today (${subdir_name}), creating one...")
        os.mkdir(subdir_path)

    # Check if csv already exists, create it if not
    csv_path = os.path.join(subdir_path, site_name + ".csv")

    if not os.path.exists(csv_path):
        print(f"No csv exists at '${csv_path}', creating one...")
        init_csv_file(csv_path)

    print(f"Updating '${csv_path}' with latest data...")

    num_echoes, num_ionosph_echoes, num_grd_sctr_echoes = get_num_echoes(json_packet)

    with open(csv_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([timestamp, json_packet["beam"], num_echoes, num_ionosph_echoes, num_grd_sctr_echoes])

def init_csv_file(path: str):
    with open(path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADERS)


def get_num_echoes(json_packet: dict):
    """
    Get number of echoes, number of ground scatter echoes,
    and number of ionospheric echoes in a json packet

    :Args:
        json_packet (dict): The JSON packet recieved from the socket
    
    :Returns:
        tuple[int, int, int]: A tuple containing:
            - num_echoes (int): Total number of echoes
            - num_ionosph_echoes (int): Number of ionospheric echoes
            - num_grd_sctr_echoes (int): Number of ground scatter echoes
    """
    # Total number of echoes is len(slist), which is number of velocity values in the json packet
    # Number of ground scatter echoes is the number of echoes where the ground scatter flag is 1
    # Number of ionospheric echoes is the number of echoes where the ground scatter flag is 0
    grd_sctr_flags = json_packet["g_scatter"]
    num_echoes = len(json_packet["velocity"])

    num_grd_sctr_echoes = grd_sctr_flags.count(1)
    num_ionosph_echoes = grd_sctr_flags.count(0)

    return num_echoes, num_ionosph_echoes, num_grd_sctr_echoes


if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    socket_addr = os.getenv('SOCKET_ADDR')

    if socket_addr is None:
        print(f"No 'SOCKET_ADDR' environment variable defined!")
        exit()

    start_listening(socket_addr)