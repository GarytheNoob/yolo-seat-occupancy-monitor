# YOLO Seat Occupancy Monitoring System

We are to develop a YOLO-based seat occupancy monitoring system.

The system will be running on a Raspberry Pi 5, with a webcam.

## Methodology

1. Detecting objects in the video / image using pre-trained YOLO model.

1. Requireing user to manually set the bounding boxes of seats. This only needs
   to be done once for eatch installation.

1. If a "Person" is detected in the bounding box of a seat, then the seat is
   occupied.

   TODO: We can detect if books / bags are on the table or the seat, and label
   the seat as "Reserved" instead of "Occupied".

1. The system deploys a web server to display the video feed with bounding boxes
   and occupancy status in a UI.
