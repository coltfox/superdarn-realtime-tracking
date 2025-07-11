## Superdarn Real-time Tracking

Tracks real-time data from SuperDARN radars in CSV format.

Currently tracks:
* Beam number
* Number of echoes
* Number ionospheric echoes
* Number of ground scatter echoes

Each file represents a 24-hour period.

The socket address should be stored as an environment variable called "SOCKET_ADDR" in a .env file in this directory.