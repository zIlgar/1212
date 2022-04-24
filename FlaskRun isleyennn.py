import cv2
import imutils
from flask import Flask, Response, render_template, request
from jyserver import Flask as js

stream_on = [1]

class BaseDetector():

    def FlaskFormat(self, frame):
        _, frame = cv2.imencode('.jpeg', frame)
        frame = frame.tobytes()

        return b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'

class ColorDetector(BaseDetector):
    def Detect(self, frame, lower_color, upper_color, draw = 1):
        centers = []
        areas = []

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask_color = cv2.inRange(hsv, lower_color, upper_color)

        cv2.imshow("Mask", mask_color)

        contours_color = cv2.findContours(mask_color, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_color = imutils.grab_contours(contours_color)

        for contour in contours_color:
            area = cv2.contourArea(contour)
            if(area >  500):
                areas.append(area)
                cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
                M = cv2.moments(contour)
                center_x = int(M["m10"] / M["m00"])
                center_y = int(M["m01"] / M["m00"])

                centers.append((center_x, center_y))

                if(draw):
                    cv2.circle(frame, (center_x, center_y), 7, (255, 255, 255), -1)

        return frame, centers, areas # sekil, obyektlerin ortasi, obyektlerin sahesi

def Stream():
    while(1):
        if(stream_on[0]):
            _, Frame = Webcam.read()
            Frame, Centers, Areas = Detecor.Detect(Frame, lower_color, upper_color)

            yield Detecor.FlaskFormat(Frame)

app = Flask(__name__)
Webcam = cv2.VideoCapture(0)
WIDTH, HEIGHT = Webcam.get(3), Webcam.get(4)

lower_color = (140, 61, 90)
upper_color = (179, 255, 255)

angle = [0]

Detecor = ColorDetector()

@js.use(app)
class App():
    def start_stream(self):
        global Webcam

        Webcam = cv2.VideoCapture(0)
        stream_on[0] = 1

    def stop_stream(self):
        stream_on[0] = 0
        Webcam.release()
    
    def shutdown_server(self):
        func = request.environ.get('werkzeug.server.shutdown')
        func()

@app.route("/")
@app.route("/home")
def Home():
    return App.render(render_template("Home.html"))

@app.route("/frame_generated")
def ResponseFrame():
    return Response(Stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

if(__name__ == "__main__"):
    app.run("192.168.2.213")