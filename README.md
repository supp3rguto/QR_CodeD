# QR_CodeD

QR_CodeD é uma aplicação web desenvolvida em Flask que permite aos usuários fazer upload de arquivos e protegê-los com senha. Após o upload, um código QR é gerado, que pode ser compartilhado com outras pessoas. Quando o código QR é escaneado, o usuário é direcionado a uma página onde deve inserir a senha correta para fazer o download do arquivo.

## Sumário

1. [Introdução](#introdução)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Tecnologias Utilizadas](#tecnologias-utilizadas)
4. [Funcionalidades](#funcionalidades)
5. [Configuração e Execução](#configuração-e-execução)
6. [Código Fonte](#código-fonte)
7. [Considerações Finais](#considerações-finais)

## Introdução

QR_CodeD é uma solução prática para compartilhar arquivos de forma segura através de códigos QR protegidos por senha. A aplicação foi desenvolvida com foco na simplicidade e na segurança, utilizando as melhores práticas de desenvolvimento web.

## Estrutura do Projeto

A estrutura do projeto é organizada da seguinte forma:

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
│   (os arquivos enviados serão armazenados aqui)
│
└── app.py
```

- **static/**: Contém o arquivo de estilo CSS.
- **templates/**: Contém os templates HTML do projeto.
- **uploads/**: Diretório onde os arquivos enviados são armazenados.
- **app.py**: Script principal da aplicação Flask.

## Tecnologias Utilizadas

- **Flask**: Framework web utilizado para construir a aplicação.
- **Werkzeug**: Utilitário usado para operações seguras de upload de arquivos.
- **QRCode**: Biblioteca utilizada para gerar códigos QR.
- **HTML/CSS**: Utilizados para construir a interface do usuário.

## Funcionalidades

1. **Upload de Arquivos**:
    - Os usuários podem fazer upload de arquivos através da interface web.
    - Arquivos permitidos: png, jpg, jpeg, gif, pdf, mp4, mp3.
    
2. **Proteção por Senha**:
    - Após o upload, o usuário deve fornecer uma senha que será usada para proteger o arquivo.
    
3. **Geração de QR Code**:
    - Um código QR é gerado contendo a URL que redireciona para a página onde a senha deve ser inserida.
    - O código QR é fornecido para o usuário para que possa ser compartilhado.
    
4. **Validação de Senha e Download**:
    - Ao acessar a URL do QR code, o usuário deve inserir a senha correta para baixar o arquivo.

## Configuração e Execução

### Pré-requisitos

- Python 3.x
- Pip (gerenciador de pacotes do Python)

### Instalação

1. **Clone o repositório**:

    ```bash
    git clone https://github.com/seu-usuario/qr_coded_project.git
    cd qr_coded_project
    ```

2. **Crie um ambiente virtual**:

    ```bash
    python -m venv venv
    source venv/bin/activate   # No Windows use `venv\Scripts\activate`
    ```

3. **Instale as dependências**:

    ```bash
    pip install Flask qrcode[pil]
    ```

### Execução

1. **Execute o aplicativo**:

    ```bash
    python app.py
    ```

2. **Acesse no navegador**:

    Abra o navegador e vá para `http://localhost:5000`

## Código Fonte

### `app.py`

```python
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
     const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
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

## Considerações Finais

Este projeto é uma solução prática para compartilhar arquivos de forma segura através de códigos QR protegidos por senha. Sinta-se à vontade para relatar quaisquer problemas no repositório do projeto.

© 2024 Augusto Barbosa. All rights reserved.
```
