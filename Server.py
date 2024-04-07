#@author: Joseph Oler
from flask import Flask, request, redirect, url_for, render_template
from flask import send_from_directory
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

def allowed_file(filename):
    return ('.' in filename) and (filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)       #(period means file type) and (reverse split once.lower[right half of split] is in allowed)

@app.route('/')                             # If first stop in server
def template():
    return render_template('template.html') # Generate template

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:         # If not file selected when upload button pressed
        return redirect(request.url)        # reload webpage
    file = request.files['file']            # read file
    if file.filename == '':                 # if file was nothing 
        return redirect(request.url)        # reload webpage
    if file and allowed_file(file.filename):                            # If file exists and is allowed
        filename = secure_filename(file.filename.rsplit('.', 1)[0])                       # Secure file name creation
        up_path = os.path.join(app.config['UPLOAD_FOLDER'], filename+'_original.png')   # Path to upload
        file.save(up_path)            # Saves the uploaded file to the location of the file path
        image = cv2.imread(up_path)   # AFTER upload to location, can then read from location  

        ksize = (21, 21)                                                        # Kernel takes average of values in surrounding pixels (10 L-R) & (10 U-D) respectively 
        blurred_image = cv2.blur(image, ksize)                                  # Apply blur
        blur_path = os.path.join(app.config['UPLOAD_FOLDER'], filename+'_blur.png') # Blur path
        cv2.imwrite(blur_path, blurred_image)                                   # Save blurred image 

        combined_image = np.hstack((image, blurred_image))                      # Appends blurred_image to end of image pixel array 
        combined_image = cv2.resize(combined_image, None, fx=1/3, fy=1/3)       # Resize to 1/3 original value
        combined_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename+'_combined.png')    # Path to combined image
        cv2.imwrite(combined_file_path, combined_image)                         # Writes the new image at the path location / names the new file 
        return render_template('template.html', filename=filename+'_combined.png')     # Reloads webpage, 
    else:
        return redirect(request.url)        # else reload webpage 
    
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':      # Begin
    app.run(debug=True)