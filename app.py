from flask import Flask, render_template, request, jsonify, redirect, url_for
import cv2
import numpy as np
import os
import random
import datetime
import xml.etree.ElementTree as ET
from flask import Response

app = Flask(__name__)

#Change for the branch
global camera_enabled
camera_enabled = True

screenshot_hole_folder = "F:\FYP check\defects\defects-img\hole_ss"
screenshot_stain_folder = "F:\FYP check\defects\defects-img\stain_ss"

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
    # Convert the frame to the HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Define the lower and upper bounds for blue color in HSV
    lower_blue = np.array([0, 50, 50])
    upper_blue = np.array([30, 255, 255])

    # Create a mask for blue color
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    # Apply morphological operations to enhance stain detection
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask_blue, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Iterate through contours
    for contour in contours:
        # Calculate area of contour
        area = cv2.contourArea(contour)
        
        # Filter out small contours which are unlikely to be stains
        if area < 100:
            continue

        # Draw bounding box around the contour
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Calculate accuracy if needed
        accuracy = calculate_accuracy([(x, y, x + w, y + h)], stain_coords)
        accuracy_text = f"Stain, {accuracy:.2f}%"
        cv2.putText(frame, accuracy_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Save image if accuracy is within desired range
        if accuracy >= 70:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            screenshot_name = os.path.join(screenshot_stain_folder, f"defect_screenshot_{timestamp}.png")
            cv2.imwrite(screenshot_name, frame)

    return frame

# def detect_stains(frame, stain_coords):
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
#     contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     detected_coords = []

#     for contour in contours:
#         x, y, w, h = cv2.boundingRect(contour)
#         for coord in stain_coords:
#             xmin, ymin, xmax, ymax = coord
#             if x >= xmin and y >= ymin and x + w <= xmax and y + h <= ymax:
#                 cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
#                 accuracy = calculate_accuracy([(x, y, x + w, y + h)], [coord])
#                 accuracy_text = f"Stain, {accuracy:.2f}%"
#                 cv2.putText(frame, accuracy_text, (x, y - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0),2)
#                 detected_coords.append((x, y, x + w, y + h))
#                 break


    # accuracy = calculate_accuracy(detected_coords, stain_coords)
    # if accuracy >= 70:
    #     timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    #     print("Hole detected")
    #     print("Uncommit this line to save the screenshot")
    #     # screenshot_name = os.path.join(screenshot_stain_folder, f"defect_screenshot_{timestamp}.png")
    #     # cv2.imwrite(screenshot_name, frame)

    # return frame

# def detect_stains(frame):
#     # Convert the frame to grayscale
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
#     # Apply Gaussian blur to reduce noise
#     blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
#     # Use adaptive thresholding to create a binary image
#     binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    
#     # Find contours in the binary image
#     contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
#     # Initialize a list to store detected stain coordinates
#     detected_coords = []

#     # Iterate through the contours
#     for contour in contours:
#         # Calculate the area of each contour
#         area = cv2.contourArea(contour)
        
#         # Filter out small contours (noise)
#         if area > 100:
#             # Get the bounding box of the contour
#             x, y, w, h = cv2.boundingRect(contour)
            
#             # Draw a rectangle around the detected stain
#             cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
#             # Store the coordinates of the detected stain
#             detected_coords.append((x, y, x + w, y + h))

#     return frame



def detect_holes(frame, hole_coords):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(blurred, 70, 200)
    
    # Apply morphological operations (opening and closing)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    edges = cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel)
    
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    min_area = 300
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
            screenshot_name = os.path.join(screenshot_folder, f"defect_screenshot_{timestamp}.png")
            cv2.imwrite(screenshot_name, frame)

    return frame



def generate_frames():
    xml_directory_stain = r"F:\FYP check\defects\FYP\Automated_Garments_Inspection-\defects-img\stain_dataset"
    all_stain_coords = []

    for xml_file in os.listdir(xml_directory_stain):
        if xml_file.endswith(".xml"):
            all_stain_coords.extend(parse_xml(os.path.join(xml_directory_stain, xml_file)))

    xml_directory_hole = r"F:\FYP check\defects\FYP\Automated_Garments_Inspection-\defects-img\hole-dataset"
    all_hole_coords = []

    for xml_file in os.listdir(xml_directory_hole):
        if xml_file.endswith(".xml"):
            all_hole_coords.extend(parse_xml(os.path.join(xml_directory_hole, xml_file)))

    cap = cv2.VideoCapture(0) 
    global camera_enabled 
    while camera_enabled: 
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

    # If camera is stopped, yield an empty frame
    yield b'--frame\r\n\r\n'
    
    cap.release()
    cv2.destroyAllWindows()


# Dummy user data for demonstration (replace with actual user authentication)
users = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"}
}

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.form.get('username')
    password = request.form.get('password')

    if username in users and users[username]['password'] == password:
        role = users[username]['role']
        if role == 'admin':
            return redirect(url_for('admin'))  # Redirect to admin route
        elif role == 'user':
            return redirect(url_for('user'))  # Redirect to user route
    else:
        # Redirect back to login page if authentication fails
        return redirect(url_for('login'))

@app.route('/admin')
def admin():
    with open("count.txt", 'r+') as f:  
        readed_count = int(f.readline().strip())  
    return render_template('ADMIN.html',view_artical_count=readed_count)

@app.route('/user')
def user():
    
    lst_hole = os.listdir(screenshot_hole_folder)
    lst_stain = os.listdir(screenshot_stain_folder)

    random_hole_images = random.sample(lst_hole, min(len(lst_hole), 3)) if lst_hole else []
    random_hole_images_with_path = [os.path.join(screenshot_hole_folder, image) for image in random_hole_images]

    random_stain_images = random.sample(lst_stain, min(len(lst_stain), 3)) if lst_stain else []
    random_stain_images_with_path = [os.path.join(screenshot_stain_folder, image) for image in random_stain_images]

    print(random_hole_images_with_path)
    print(random_stain_images_with_path)
    return render_template('index.html'
                           ,holes = random_hole_images_with_path
                           ,stains = random_stain_images_with_path
                           )

# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/start_camera')
def start_camera(): 
    with open("count.txt", 'r+') as f:  
        readed_count = int(f.readline().strip())  
        f.seek(0) 
        f.write(str(readed_count + 1)) 

    global camera_enabled 
    camera_enabled = True
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_camera')
def stop_camera():
    global camera_enabled 
    camera_enabled = False
    print("Inside End")
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
