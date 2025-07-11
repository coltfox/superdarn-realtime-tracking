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
    print(f"Listening on ${socket_addr}\n")
    with socketio.SimpleClient() as sio:
        sio.connect(socket_addr, transports=['websocket'])

        while True:
            event = sio.receive()
            dmap_dict = event[1:][0]
            print(f"Received data from radar ${dmap_dict['site_name']}")
            write_csv(dmap_dict)

def write_csv(dmap_dict: dict):
    now = dt.datetime.now()
    timestamp = now.strftime('%Y-%m-%d-%H:%M:%S.%f')
    site_name = dmap_dict['site_name']

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
    with open(csv_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([timestamp, dmap_dict["beam"], len(dmap_dict["velocity"]), len(dmap_dict["velocity"]), len(dmap_dict["velocity"])])


def init_csv_file(path: str):
    with open(path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADERS)


def format_dmap_date(dmap_dict: dict):
    """
    Format date in dmap as a string

    :Args:
        dmap_dict (dict): The dmap dictionary

    :Returns:
        date (str): The date string
    """
    return dt.datetime(
        dmap_dict['time.yr'],
        dmap_dict['time.mo'],
        dmap_dict['time.dy'],
        dmap_dict['time.hr'],
        dmap_dict['time.mt'],
        dmap_dict['time.sc'],
        dmap_dict['time.us'],
        tzinfo=dt.timezone.utc,
    ).strftime('%Y-%m-%d %H:%M:%S.%f')

if __name__ == "__main__":
    load_dotenv()
    socket_addr = os.getenv('SOCKET_ADDR')

    if socket_addr is None:
        print(f"No 'SOCKET_ADDR' environment variable defined!")
        exit()

    try:
        start_listening(socket_addr)
    except KeyboardInterrupt:
        print("Stopping...")