import os
import net as neuronet
import base64
import json
import threading
import lxml.etree as ET
from flask import Flask
from flask import request, Response, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO

app = Flask(__name__)

SECRET_KEY = 'secret'
app.config['SECRET_KEY'] = SECRET_KEY
bootstrap = Bootstrap(app)


@app.route("/")
def hello():
    return render_template('home.html')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)


# наша новая функция сайта
@app.route("/data_to")
def data_to():
    return render_template('simple.html')


app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdWjfUUAAAAAL7mLdm45iopHgunpXdOyP0gi1yt'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdWjfUUAAAAAGSRVo9OqQLCSX72vKPxVCvrXEw-'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}


# app.config['UPLOAD_FOLDER'] = './data'
# app.config['ALLOWED_EXTENSIONS'] = {'jpg','png','jpeg'}

# создаем форму для загрузки файла
class NetForm(FlaskForm):
    # валидатор проверяет введение данных после submit
    # и указывает пользователю ввести данные
    openid = StringField('openid', validators=[DataRequired()])
    # здесь валидатор укажет ввести правильные файлы
    upload = FileField('Load image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    recaptcha = RecaptchaField()
    # кнопка submit
    submit = SubmitField('send')


@app.route("/net", methods=['GET', 'POST'])
def net():
    # создаем объект формы
    form = NetForm()
    # обнуляем переменные передаваемые в форму
    filename = None
    neurodic = {}
    # проверяем нажатие сабмит и валидацию введенных данных
    if form.validate_on_submit():
        # файлы с изображениями читаются из каталога static
        filename = os.path.join('./static', secure_filename(form.upload.data.filename))
        fcount, fimage = neuronet.read_image_files(10, './static')
        # передаем все изображения в каталоге на классификацию
        # можете изменить немного код и передать только загруженный файл
        decode = neuronet.getresult(fimage)
        # записываем в словарь данные классификации
        for elem in decode:
            neurodic[elem[0][1]] = elem[0][2]
        # сохраняем загруженный файл
        form.upload.data.save(filename)
    # передаем форму в шаблон, так же передаем имя файла и результат работы нейронной
    # сети если был нажат сабмит, либо передадим falsy значения
    return render_template('net.html', form=form, image_name=filename, neurodic=neurodic)


@app.route("/apinet", methods=['GET', 'POST'])
def apinet():
    neurodic = {}
    if request.mimetype == 'application/json':
        data = request.get_json()
        filebytes = data['imagebin'].encode('utf-8')
        cfile = base64.b64decode(filebytes)
        img = Image.open(BytesIO(cfile))
        decode = neuronet.getresult([img])
        for elem in decode:
            neurodic[elem[0][1]] = str(elem[0][2])
            print(elem)
    ret = json.dumps(neurodic)
    resp = Response(response=ret,
                    status=200,
                    mimetype="application/json")
    return resp


@app.route("/apixml", methods=['GET', 'POST'])
def apixml():
    # парсим xml файл в dom
    dom = ET.parse("./static/xml/file.xml")
    # парсим шаблон в dom
    xslt = ET.parse("./static/xml/file.xslt")
    # получаем трансформер
    transform = ET.XSLT(xslt)
    # преобразуем xml с помощью трансформера xslt
    newhtml = transform(dom)
    # преобразуем из памяти dom в строку, возможно, понадобится указать кодировку
    strfile = ET.tostring(newhtml)
    return strfile