from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import os
import datetime
import xml.etree.ElementTree as ET
from flask import Response

app = Flask(__name__)

# Global variable to track camera state
camera_enabled = False


def parse_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    coordinates = []
    for obj in root.findall(".//object"):
        xmin = int(obj.find("bndbox/xmin").text)
        ymin = int(obj.find("bndbox/ymin").text)
        xmax = int(obj.find("bndbox/xmax").text)
        ymax = int(obj.find("bndbox/ymax").text)
        coordinates.append((xmin, ymin, xmax, ymax))
    return coordinates

def calculate_accuracy(detected_coords, ground_truth_coords):
    intersection_area = 0
    total_ground_truth_area = sum([(coord[2] - coord[0]) * (coord[3] - coord[1]) for coord in ground_truth_coords])

    for detected_coord in detected_coords:
        for ground_truth_coord in ground_truth_coords:
            x1 = max(detected_coord[0], ground_truth_coord[0])
            y1 = max(detected_coord[1], ground_truth_coord[1])
            x2 = min(detected_coord[2], ground_truth_coord[2])
            y2 = min(detected_coord[3], ground_truth_coord[3])
            intersection_area += max(0, x2 - x1 + 1) * max(0, y2 - y1 + 1)

    total_detected_area = sum([(coord[2] - coord[0]) * (coord[3] - coord[1]) for coord in detected_coords])

    if total_detected_area > 0:
        accuracy_percentage = min((intersection_area / total_ground_truth_area) * 100, 100)
    else:
        accuracy_percentage = 0

    return accuracy_percentage


def detect_stains(frame, stain_coords):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected_coords = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        for coord in stain_coords:
            xmin, ymin, xmax, ymax = coord
            if x >= xmin and y >= ymin and x + w <= xmax and y + h <= ymax:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                accuracy = calculate_accuracy([(x, y, x + w, y + h)], [coord])
                accuracy_text = f"Stain, {accuracy:.2f}%"
                cv2.putText(frame, accuracy_text, (x, y - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                detected_coords.append((x, y, x + w, y + h))
                break

    accuracy = calculate_accuracy(detected_coords, stain_coords)
    if accuracy >= 70:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        print("Hole detected")
        print("Uncommit this line to save the screenshot")
        # screenshot_name = os.path.join("F:\FYP check\defects\defects-img\stain_ss", f"defect_screenshot_{timestamp}.png")
        # cv2.imwrite(screenshot_name, frame)

    return frame

def detect_holes(frame, hole_coords):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(blurred, 70, 200)
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    min_area = 500
    defects = []

    for contour in contours:
        if cv2.contourArea(contour) > min_area:
            x, y, w, h = cv2.boundingRect(contour)
            defects.append((x, y, x + w, y + h))

    for defect in defects:
        x, y, x_max, y_max = defect
        cv2.rectangle(frame, (x, y), (x_max, y_max), (0, 0, 255), 2)
        accuracy = calculate_accuracy([(x, y, x_max, y_max)], hole_coords)
        accuracy_text = f"Hole, {accuracy:.2f}%"
        cv2.putText(frame, accuracy_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        if 70 <= accuracy <= 100:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            print("Hole detected")
            print("Uncommit this line to save the screenshot")
            # screenshot_name = os.path.join("F:\FYP check\defects\defects-img\hole_ss", f"defect_screenshot_{timestamp}.png")
            # cv2.imwrite(screenshot_name, frame)

    return frame

def generate_frames():
    xml_directory_stain = r"E:\PROJECTS\Automated_Garments_Inspection\required\train"
    all_stain_coords = []

    for xml_file in os.listdir(xml_directory_stain):
        if xml_file.endswith(".xml"):
            all_stain_coords.extend(parse_xml(os.path.join(xml_directory_stain, xml_file)))

    xml_directory_hole = r"E:\PROJECTS\Automated_Garments_Inspection\required\test"
    all_hole_coords = []

    for xml_file in os.listdir(xml_directory_hole):
        if xml_file.endswith(".xml"):
            all_hole_coords.extend(parse_xml(os.path.join(xml_directory_hole, xml_file)))

    cap = cv2.VideoCapture(0)
    
    print("Camera started")
    print("HEEELOZ",camera_enabled)
    while True:  # Check if camera is enabled
        print("here")
        ret, frame = cap.read()
        if not ret:
            break

        frame_combined = frame.copy() # Make a copy of the frame

        frame_combined = detect_stains(frame_combined, all_stain_coords)
        frame_combined = detect_holes(frame_combined, all_hole_coords)

        # Convert frame to JPEG format
        ret, jpeg = cv2.imencode('.jpg', frame_combined)
        frame_bytes = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()
    cv2.destroyAllWindows()
    print("Camera stopped")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_camera')
def start_camera():
    global camera_enabled, cap
    if not camera_enabled:
        cap = cv2.VideoCapture(0)  # Reinitialize VideoCapture object
        camera_enabled = True
        print("Camera started")
    return 'Camera started.'

@app.route('/stop_camera')
def stop_camera():
    global camera_enabled, cap
    if camera_enabled:
        cap.release()  # Release the VideoCapture object
        camera_enabled = False
        print("Camera stopped")
    return 'Camera stopped.'

if __name__ == '__main__':
    app.run(debug=True)
