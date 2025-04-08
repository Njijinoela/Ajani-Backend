from config import create_app
from dotenv import load_dotenv
import os

load_dotenv()

app = create_app()

app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'docx', 'jpg', 'jpeg', 'png'}

from routes import article_bp
app.register_blueprint(article_bp)

if __name__ == '__main__':
    app.run(debug=True)
