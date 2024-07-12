# QR_CodeD

QR_CodeD is a web application developed in Flask that allows users to upload files and protect them with a password. After the upload, a QR code is generated, which can be shared with others. When the QR code is scanned, the user is directed to a page where they must enter the correct password to download the file.

## Summary

1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Technologies Used](#technologies-used)
4. [Features](#features)
5. [Setup and Execution](#setup-and-execution)
6. [Source Code](#source-code)
7. [Final Considerations](#final-considerations)

## Introduction

QR_CodeD is a practical solution for securely sharing files through password-protected QR codes. The application was developed with a focus on simplicity and security, using best practices in web development.

## Project Structure

The project structure is organized as follows:

```
qr_coded_project/
│
├── static/
│   └── style.css
│
├── templates/
│   ├── index.html
│   └── password.html
│
├── uploads/
│   (uploaded files will be stored here)
│
└── app.py
```

- **static/**: Contains the CSS style file.
- **templates/**: Contains the project's HTML templates.
- **uploads/**: Directory where uploaded files are stored.
- **app.py**: Main script of the Flask application.

## Technologies Used

- **Flask**: Web framework used to build the application.
- **Werkzeug**: Utility used for secure file upload operations.
- **QRCode**: Library used to generate QR codes.
- **HTML/CSS**: Used to build the user interface.

## Features

1. **File Upload**:
    - Users can upload files through the web interface.
    - Allowed file types: png, jpg, jpeg, gif, pdf, mp4, mp3.
    
2. **Password Protection**:
    - After the upload, the user must provide a password that will be used to protect the file.
    
3. **QR Code Generation**:
    - A QR code is generated containing the URL that redirects to the page where the password must be entered.
    - The QR code is provided to the user to be shared.
    
4. **Password Validation and Download**:
    - Upon accessing the QR code URL, the user must enter the correct password to download the file.

## Setup and Execution

### Prerequisites

- Python 3.x
- Pip (Python package manager)

### Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/your-username/qr_coded_project.git
    cd qr_coded_project
    ```

2. **Create a virtual environment**:

    ```bash
    python -m venv venv
    source venv/bin/activate   # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**:

    ```bash
    pip install Flask qrcode[pil]
    ```

### Execution

1. **Run the application**:

    ```bash
    python app.py
    ```

2. **Access in the browser**:

    Open your browser and go to `http://localhost:5000`

## Source Code

### `app.py`

```python
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash, send_file
import qrcode
import os
import io
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # secret key for using flash messages

# Upload configurations
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'mp4', 'mp3'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check if the file is allowed
def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Dictionary to store file information and passwords
files_info = {}

# Notebook IP address
NOTEBOOK_IP = '192.168.1.11'

@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    if 'file' not in request.files:
      flash('No file uploaded')
      return redirect(request.url)
     
    file = request.files['file']
    if file.filename == '':
      flash('No file selected')
      return redirect(request.url)
     
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
       
      password = request.form['password']
      file_id = filename
      files_info[file_id] = {'filename': filename, 'password': password}

      url = f'http://{NOTEBOOK_IP}:5000/password/{file_id}'
      qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
      )
      qr.add_data(url)
      qr.make(fit=True)
      img = qr.make_image(fill_color="black", back_color="white")

      img_io = io.BytesIO()
      img.save(img_io, 'PNG')
      img_io.seek(0)

      return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='qrcode.png')

  return render_template('index.html')

@app.route('/password/<file_id>', methods=['GET', 'POST'])
def password(file_id):
  if request.method == 'POST':
    password = request.form['password']
    if password == files_info[file_id]['password']:
      filename = files_info[file_id]['filename']
      return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    else:
      flash('Incorrect password. Please try again.')

  return render_template('password.html', file_id=file_id)

if __name__ == '__main__':
  if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
  app.run(debug=True, host='0.0.0.0')
```

### `index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>QR_CodeD</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <header>
    QR_CodeD
  </header>
  <div class="container">
    <h1>Generate QR Code with Password Protection</h1>
    <form action="/" method="post" enctype="multipart/form-data">
     <label for="file">Select a file:</label>
     <input type="file" id="file" name="file" required>
     <label for="password">Create a password:</label>
     <div class="password-wrapper">
      <input type="password" id="password" name="password" required>
      <span class="toggle-password" onclick="togglePassword('password')">&#128065;</span>
     </div>
     <input type="submit" value="Generate QR Code">
    </form>
    {% with messages = get_flashed_messages() %}
     {% if messages %}
     <div class="flash-messages">
      {% for message in messages %}
      <p>{{ message }}</p>
      {% endfor %}
     </div>
     {% endif %}
    {% endwith %}
  </div>
  <footer>
    © 2024 Augusto Barbosa. All rights reserved.
  </footer>
  <script>
    function togglePassword(inputId) {
     const input = document.getElementById(inputId);
     const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
     input.setAttribute('type', type);
    }
  </script>
</body>
</html>
```

### `password.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>QR_CodeD Password</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <header>
    QR_CodeD Password
  </header>
  <div class="container">
    <h1>Enter Password to Download</h1>
    <form action="" method="post">
     <label for="password">Password:</label>
     <div class="password-wrapper">
      <input type="password" id="password" name="password" required>
      <span class="toggle-password" onclick="togglePassword('password')">&#128065;</span>
     </div>


     <input type="submit" value="Submit">
    </form>
    {% with messages = get_flashed_messages() %}
     {% if messages %}
     <div class="flash-messages">
      {% for message in messages %}
      <p>{{ message }}</p>
      {% endfor %}
     </div>
     {% endif %}
    {% endwith %}
  </div>
  <footer>
    © 2024 Augusto Barbosa. All rights reserved.
  </footer>
  <script>
    function togglePassword(inputId) {
     const input = document.getElementById(inputId);
     const type = input.getAttribute('type') === 'password' ? 'text' :

 'password';
     input.setAttribute('type', type);
    }
  </script>
</body>
</html>
```

### `style.css`

```css
body {
  font-family: Arial, sans-serif;
  background-color: #f4f4f4;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

header {
  background-color: #333;
  color: #fff;
  padding: 10px 0;
  text-align: center;
  font-size: 24px;
}

.container {
  width: 100%;
  max-width: 600px;
  margin: 50px auto;
  padding: 20px;
  background-color: #fff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  flex: 1;
}

form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

label {
  font-size: 18px;
}

input[type="file"],
input[type="password"],
input[type="submit"] {
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

input[type="submit"] {
  background-color: #007BFF;
  color: #fff;
  border: none;
  cursor: pointer;
}

input[type="submit"]:hover {
  background-color: #0056b3;
}

.flash-messages {
  color: red;
  font-weight: bold;
  margin-bottom: 10px;
  text-align: center;
}

footer {
  background-color: #333;
  color: #fff;
  text-align: center;
  padding: 10px 0;
  font-size: 12px;
}

.password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-wrapper input[type="password"] {
  flex: 1;
}

.password-wrapper .toggle-password {
  position: absolute;
  right: 10px;
  cursor: pointer;
  font-size: 18px;
  color: #333;
}
```

## Final Considerations

This project is a practical solution for securely sharing files through password-protected QR codes. Feel free to report any issues on the project repository.

© 2024 Augusto Barbosa. All rights reserved.
