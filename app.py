from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash, send_file
import qrcode
import os
import io
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # chave secreta para uso do flash messages

# Configurações de upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'mp4', 'mp3'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Função para verificar se o arquivo é permitido
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Dicionário para armazenar informações dos arquivos e senhas
files_info = {}

# Endereço IP do notebook
NOTEBOOK_IP = '192.168.1.11'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo enviado')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('Nenhum arquivo selecionado')
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
            flash('Senha incorreta. Tente novamente.')

    return render_template('password.html', file_id=file_id)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, host='0.0.0.0')
