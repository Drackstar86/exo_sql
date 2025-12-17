import csv
import json
import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'geofilm'
}


def clean_text(text):
    """ Nettoie et met en majuscules """

    if text:
        return " ".join(text.split()).upper()
    return None

def clean_address(text):
    """Nettoie et met en forme les adresses en mettant une majuscule à chaque mot et en supprimant les doubles espaces."""
    if text:
        return " ".join(text.split()).title()
    return None

def make_loc_signature(lat, lon):
    """ Crée les signatures de localisation pour le mapping """
    try:
        return f"{float(lat):.6f}|{float(lon):.6f}"
    except (ValueError, TypeError):
        return None

def get_json_str(lat, lon):
    """ Crée une signature unique entre la BDD et le CSV pour être assurer un bon traitement """

    d = {"latitude": float(lat), "longitude": float(lon)}
    return json.dumps(d, sort_keys=True, separators=(',', ':'))

def load_maps(cursor):
    """Va mapper les liaisons entre les entités"""
    
    cursor.execute("SELECT title, id_title FROM WorkTitle")
    map_title = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT type, id_filming_type FROM FilmingType")
    map_type = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT realisator, id_realisator FROM Realisator")
    map_real = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT productor, id_productor FROM Productor")
    map_prod = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT adress, postal_code, id_adress FROM Adress")
    map_addr = {(row[0], row[1]): row[2] for row in cursor.fetchall()}

    cursor.execute("SELECT geopoint_2d, id_location FROM Location")
    map_loc = {}
    for row in cursor.fetchall():
        try:
            val = row[0]
            d = val if isinstance(val, dict) else json.loads(val)
            sig = make_loc_signature(d['latitude'], d['longitude'])
            if sig: map_loc[sig] = row[1]
        except: pass

    return map_title, map_type, map_real, map_prod, map_addr, map_loc

def run_import(file_path):
    """Fonction principale d'import du CSV vers la BDD"""

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        print("\n--- PHASE 1 : Extraction des données uniques du CSV ---")
        
        # set() va forcer l'unicité des valeurs
        set_real = set()
        set_prod = set()
        set_title = set()
        set_type = set()
        set_loc = set()
        set_addr = set()

        # Lecture pour extraction attention à bien mettre utf-8-sig pour bien prendre en compte toute l'entête
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, delimiter=";")

            for row in reader:

                # Titres des films, types de tournage, réalisateurs et producteurs
                if row.get('Titre'): set_title.add(" ".join(row['Titre'].split()))
                if row.get('Type de tournage'): set_type.add(clean_text(row['Type de tournage']))
                if row.get('Réalisateur'): set_real.add(clean_text(row['Réalisateur']))
                if row.get('Producteur'): set_prod.add(clean_text(row['Producteur']))

                # Mise en forme du json des coordonnées
                pt = row.get('geo_point_2d')
                if pt and ',' in pt:
                    parts = pt.split(',')
                    try:
                        # On stocke le JSON string pour l'insertion
                        set_loc.add(get_json_str(parts[0], parts[1]))
                    except: pass
                
                # Mise en forme des adresses
                ad = clean_address(row.get('Localisation de la scène'))
                cp = clean_text(row.get('Code postal'))
                if ad or cp: set_addr.add((ad, cp))

        # On insère les données uniques extraites dans les lignes précédentes
        print("Insertion des données uniques dans la Base de Données...")
        cursor.executemany("INSERT IGNORE INTO Realisator (realisator) VALUES (%s)", [(x,) for x in set_real])
        cursor.executemany("INSERT IGNORE INTO Productor (productor) VALUES (%s)", [(x,) for x in set_prod])
        cursor.executemany("INSERT IGNORE INTO WorkTitle (title) VALUES (%s)", [(x,) for x in set_title])
        cursor.executemany("INSERT IGNORE INTO FilmingType (type) VALUES (%s)", [(x,) for x in set_type])
        cursor.executemany("INSERT IGNORE INTO Location (geopoint_2d) VALUES (%s)", [(x,) for x in set_loc])
        cursor.executemany("INSERT IGNORE INTO Adress (adress, postal_code) VALUES (%s, %s)", list(set_addr))
        conn.commit()
        print("-> Référentiels insérés avec succès.")

        print("\n--- PHASE 2 : Mapping ---")
        map_title, map_type, map_real, map_prod, map_addr, map_loc = load_maps(cursor)

        print("\n--- PHASE 3 : Préparation des Scènes ---")
        
        # On prépare les scènes à insérer en ajoutant un buffer pour tout envoyer d'un coup
        scenes_buffer = []
        links_real = []
        links_prod = []
        links_addr = []
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, delimiter=";")
            
            count = 0
            skipped = 0

            for row in reader:
                csv_id = row.get('Identifiant du lieu')
                if not csv_id: csv_id = list(row.values())[0]
                
                # Clés de recherche
                k_title = " ".join(row['Titre'].split())
                k_type = clean_text(row['Type de tournage'])
                
                k_loc_sig = None
                pt = row.get('geo_point_2d')
                if pt and ',' in pt:
                    parts = pt.split(',')
                    k_loc_sig = make_loc_signature(parts[0], parts[1])

                # Récupération IDs
                id_title = map_title.get(k_title)
                id_type = map_type.get(k_type)
                id_loc = map_loc.get(k_loc_sig)

                if not id_title or not id_type or not id_loc:
                    skipped += 1
                    continue

                # Ajout au buffer pour envoyer toutes les données d'un seul coup
                scenes_buffer.append((
                    csv_id, row['Date de début'], row['Date de fin'], row['Année du tournage'],
                    id_loc, id_type, id_title
                ))

                # Liaisons
                k_real = clean_text(row.get('Réalisateur'))
                if k_real and k_real in map_real:
                    links_real.append((csv_id, map_real[k_real]))

                k_prod = clean_text(row.get('Producteur'))
                if k_prod and k_prod in map_prod:
                    links_prod.append((csv_id, map_prod[k_prod]))
                
                k_ad = clean_address(row.get('Localisation de la scène'))
                k_cp = clean_text(row.get('Code postal'))
                if (k_ad or k_cp) and (k_ad, k_cp) in map_addr:
                    links_addr.append((csv_id, map_addr[(k_ad, k_cp)]))

                count += 1

        print(f"Analyse terminée. {len(scenes_buffer)} scènes prêtes. ({skipped} ignorées)")

        print("\n--- PHASE 4 : Insertion Finale ---")
        
        # On ajoute par batchs pour éviter d'en envoyer trop d'un coup
        batch_size = 2000
        
        sql_scene = "INSERT IGNORE INTO Scene (id_scene, startDate, endDate, yearFilming, id_location, id_filming_type, id_title) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        for i in range(0, len(scenes_buffer), batch_size):
            cursor.executemany(sql_scene, scenes_buffer[i:i+batch_size])
            conn.commit()
            print(f"Scènes batch {i} OK...")

        cursor.executemany("INSERT IGNORE INTO Scene_Realisator VALUES (%s, %s)", links_real)
        cursor.executemany("INSERT IGNORE INTO Scene_Productor VALUES (%s, %s)", links_prod)
        cursor.executemany("INSERT IGNORE INTO Adress_Scene VALUES (%s, %s)", links_addr)
        
        conn.commit()
        print("✅ SUCCÈS TOTAL ! Base de données remplie.")

    except mysql.connector.Error as err:
        print(f"ERREUR SQL : {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_import('datas.csv')