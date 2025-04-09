from flask import Flask, render_template, request, Response, redirect, url_for, flash
import os
import cv2

app = Flask(__name__)
app.secret_key = 'supersecretkey'  
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize camera
camera = cv2.VideoCapture(0)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/helmet-detect', methods=['GET', 'POST'])
def helmet_detect():
    if request.method == 'POST':
        if 'video' in request.files:
            video = request.files['video']
            if video.filename != '':
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
                video.save(filepath)
                flash('Video uploaded successfully!', 'success')
                return redirect(url_for('helmet_detect', video_url=filepath))
    video_url = request.args.get('video_url')
    return render_template('helmet_detect.html', video_url=video_url)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Draw an even larger blue square at the top center
            height, width, _ = frame.shape
            box_size = 300  # Increased size by half
            start_x = (width // 2) - (box_size // 2)
            start_y = 50  # Adjusted position for better visibility

            end_x = start_x + box_size
            end_y = start_y + box_size  # Making it square

            # Draw the larger blue square
            cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (255, 0, 0), 3)

            # Add text "No Helmet"
            cv2.putText(frame, "No Helmet", (start_x + 40, start_y + 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 4)

            # Convert the frame to JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Yield frame as multipart HTTP response
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
