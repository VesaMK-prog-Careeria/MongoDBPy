from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# Yhteys MongoDB:hen
client = MongoClient('localhost', 27017)

# Valitaan tietokanta jasenrek_db jos ei ole olemassa, niin se luodaan
db = client.jasenrek_db

# Luodaan kokoelma, johon jäsenrekisterin tiedot tallennetaan
members = db.members

# Aloitussivu (index.html) renderöinti
@app.route('/')
def index():
    return render_template('index.html')

# POST-reitti tietojen tallentamiseksi tietokantaan
@app.route('/add_member', methods=['POST'])
def add_member():
    # Oletetaan, että tiedot tulevat JSON-muodossa POST-pyynnöstä
    data = request.json
    
    # Luo asiakirja (document) tietokantaan tallennettavaksi
    member = {
        "Etunimi": data.get('Etunimi'),
        "Sukunimi": data.get('Sukunimi'),
        "Osoite": data.get('Osoite'),
        "Postinumero": data.get('Postinumero'),
        "Puhelin": data.get('Puhelin'),
        "Sähköposti": data.get('Sähköposti'),
        "JäsenyydenAlkuPvm": data.get('JäsenyydenAlkuPvm')
    }
    
    # Tallenna asiakirja MongoDB-kokoelmaan
    result = members.insert_one(member)
    
    # Palautetaan vastaus, jossa vahvistetaan tallennus ja annetaan tallennettu ID
    return jsonify({"message": "Jäsen tallennettu", "id": str(result.inserted_id)}), 201

# GET-reitti kaikkien jäsenten hakemiseen
@app.route('/get_members', methods=['GET'])
def get_members():
    all_members = list(members.find())
    for member in all_members:
        member['_id'] = str(member['_id'])  # Muunna ObjectId merkkijonoksi
    return jsonify(all_members)

# GET-reitti yksittäisen jäsenen hakemiseen
@app.route('/get_member/<id>', methods=['GET'])
def get_member(id):
    member = members.find_one({"_id": ObjectId(id)})
    if member:
        member['_id'] = str(member['_id'])  # Muunna ObjectId merkkijonoksi
        return jsonify(member)
    else:
        return jsonify({"message": "Jäsentä ei löytynyt"}), 404

# DELETE-reitti jäsenen poistamiseksi
@app.route('/delete_member/<id>', methods=['DELETE'])
def delete_member(id):
    result = members.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return jsonify({"message": "Jäsen poistettu"}), 200
    else:
        return jsonify({"message": "Jäsentä ei löytynyt"}), 404
    
# PUT-reitti jäsenen tietojen päivittämiseksi
@app.route('/update_member/<id>', methods=['PUT'])
def update_member(id):
    data = request.json
    updated_member = {
        "Etunimi": data.get('Etunimi'),
        "Sukunimi": data.get('Sukunimi'),
        "Osoite": data.get('Osoite'),
        "Postinumero": data.get('Postinumero'),
        "Puhelin": data.get('Puhelin'),
        "Sähköposti": data.get('Sähköposti'),
        "JäsenyydenAlkuPvm": data.get('JäsenyydenAlkuPvm')
    }
    result = members.update_one({"_id": ObjectId(id)}, {"$set": updated_member})
    if result.modified_count == 1:
        return jsonify({"message": "Jäsenen tiedot päivitetty"}), 200
    else:
        return jsonify({"message": "Jäsentä ei löytynyt"}), 404
    
if __name__ == '__main__':
    app.run(debug=True)