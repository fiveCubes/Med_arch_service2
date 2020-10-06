from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import send_file
from os import environ
#from flask_cors import CORS
import requests
import json
import os
from flask import jsonify

app = Flask(__name__)
# cors = CORS(app, resources={r"/*": {"origins": "*"}})
#app.config['SQLALCHEMY_DATABASE_URI']='postgresql://vishnu@localhost:5432/medarch'
app.config['SQLALCHEMY_DATABASE_URI']=environ.get('DATABASE_URL')
db = SQLAlchemy(app)

#child model   
class Image_info(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    image_name = db.Column(db.String())
    vase_number = db.Column(db.Integer,db.ForeignKey('vase_info.vase_number'), nullable=False)

#parent model
class Vase_info(db.Model):
    vase_number = db.Column(db.Integer,primary_key=True)
    shape = db.Column(db.String())
    location= db.Column(db.String())
    dimension = db.Column(db.String())
    plate = db.Column(db.String())
    additional_info = db.Column(db.String())
    description = db.Column(db.String())
    image_info = db.relationship('Image_info',backref='vase_info',uselist=False,lazy=True)



db.create_all()

 # load fresh data
def load_database():
    response = requests.get('https://nameless-fjord-91687.herokuapp.com/')
    data = dict(json.loads(response.text))['Vase_details']
    for v in data:
        vase_info = Vase_info(vase_number = v['id'], shape=v['shape'],location = v['location'], dimension = v['dimension'], plate = v['plate'],
        additional_info=v['extras'], description = v['description'])
        db.session.add(vase_info)

    db.session.commit()

    file_list = os.listdir('./converted_images')
    for f_name in file_list:
        header = int(f_name.split('.')[0].split('-')[1][:2])
        if (header != 58):
            image_info =Image_info(image_name=f_name,vase_number=header)
        db.session.add(image_info)

    db.session.commit()

#load data for the first time when table is empty.
if(len(Vase_info.query.all())==0):
    load_database()



@app.route('/')
def index():
    mapped_list=[]
    data = Vase_info.query.all()
    for vase in data:
        mapped_data={"images":[]}
        vase_number = vase.vase_number
        mapped_data['id']= vase_number
        mapped_data['shape']=vase.shape
        mapped_data['location']= vase.location
        mapped_data['description']=vase.location
        mapped_data['plate']=vase.plate
        mapped_data['dimension']=vase.dimension
        mapped_data['additional_info']=vase.additional_info


        image_data = Image_info.query.filter_by(vase_number=vase_number)
        for img in image_data:
            mapped_data['images'].append(img.image_name)

        mapped_list.append(mapped_data)
    

    return jsonify({"vase_details": mapped_list})


    
@app.route('/<image_name>')
def getImage(image_name):
    img = f'converted_images/{image_name}'
    return send_file(img,mimetype='image/gif')