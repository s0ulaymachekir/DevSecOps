from flask import Flask, request, render_template, redirect, jsonify, session, url_for  # Import necessary modules
import mysql.connector

# Create an instance of the Flask application
app = Flask(__name__)
app.secret_key = 'key'  # Replace 'your_secret_key' with a secure random key

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '55889528'
app.config['MYSQL_DB'] = 'users'

def get_mysql_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

#partie client
@app.route('/', methods=['GET', 'POST'])
def home1():
    return render_template('1.html')


@app.route('/client', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search_term']
        mysql = get_mysql_connection()
        cursor = mysql.cursor()
        # Requête SQL pour récupérer les projets correspondants
        query = "SELECT * FROM project WHERE ref LIKE %s"
        cursor.execute(query, ('%' + search_term + '%',))
        projects = cursor.fetchall()
        cursor.close()
        session['selected_project'] = None  # Reset selected project
        return render_template('clients.html', projects=projects, search_term=search_term)

    return render_template('clients.html', projects=[])


@app.route('/project/<ref>')
def project_details(ref):
    session['selected_project_ref'] = ref
    return redirect(url_for('details_page'))


@app.route('/lod')
def details_page():
    ref = session.get('selected_project_ref')

    # Establish a database connection
    mysql = get_mysql_connection()
    cursor = mysql.cursor()

    try:
        # Execute the query to retrieve data
        cursor.execute('SELECT * FROM project WHERE ref = %s', (ref,))
        data = cursor.fetchone()

        # Render the HTML template with the retrieved data
        return render_template('lod.html', data=data)

    except Exception as e:
        # Handle any exceptions that might occur during data retrieval
        error_message = f"Error retrieving data: {e}"
        return render_template('lod.html', error_message=error_message)
    finally:
        # Close the cursor and connection
        cursor.close()


#ajouter une discipline
@app.route('/ajouterdl', methods=['POST', 'GET'])
def ajouterdl():
    if request.method == 'POST':
        code = request.form['Code']
        description = request.form['Description']
        task = request.form['Task']
        document = request.form['Document']

        # Connect to the database
        mysql = get_mysql_connection()
        c = mysql.cursor()

        # Verify if the discipline with the given code exists in the discipline table
        verify_req = "SELECT * FROM discipline WHERE code = %s"
        c.execute(verify_req, (code,))
        existing_discipline = c.fetchone()

        if existing_discipline:
            # Discipline exists, insert it into the "lod" table
            insert_req = "INSERT INTO lod (code, description, tache, document) VALUES (%s, %s, %s, %s)"
            data = (code, description, task, document)
            c.execute(insert_req, data)

            # Commit the connection
            mysql.commit()
            return redirect('/lod')  # Redirect to the "/lod" page after adding the entry
        else:
            # Discipline doesn't exist, display an error message or take appropriate action
            error_message = "Discipline does not exist in the discipline table."
            return render_template('lod.html', error_message=error_message)

    return render_template('lod.html')  # Return the 'ajouterd.html' template for the registration form


# home1 page
@app.route('/home1')
def home():
    return render_template('home.html')


# register page
@app.route('/register', methods=['GET', 'POST'])  # Define a route for registration
def register():
    if request.method == 'POST':  # Check if the form is submitted
        fname = request.form['First Name']  # Get the value of the 'First Name' field from the submitted form
        lname = request.form['Last Name']  # Get the value of the 'Last Name' field from the submitted form
        email = request.form['Email']  # Get the value of the 'Email' field from the submitted form
        pname = request.form['Project Name']  # Get the value of the 'First Name' field from the submitted form
        role = request.form['Category']  # Get the value of the 'First Name' field from the submitted form
        password = request.form['Password']  # Get the value of the 'Password' field from the submitted form

        # Connect to the database
        mysql = get_mysql_connection()
        c = mysql.cursor()

        # Insert the data into the database
        req = "INSERT INTO users (fname, lname, email, pname, role, password) VALUES ('{f}','{l}','{e}','{p}','{r}','{pa}')".format(f=fname, l=lname, e=email, p=pname, r=role, pa=password)
        c.execute(req)

        # Commit the connection
        mysql.commit()
        

        return render_template('login.html')

    return render_template('register.html')  # Return the 'index.html' template for the registration form


# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['Email']
        password = request.form['password']
        # Connect to the database
        mysql = get_mysql_connection()
        cur = mysql.cursor()

        # Prepare the query with placeholders for username or email
        query = "SELECT * FROM users WHERE email = %s"

        # Execute the query with the provided values
        cur.execute(query, (email,))
        user = cur.fetchone()

        if user and user[5] == password:
            # User authenticated, store the email in session
            session['email'] = email
            # User authenticated, redirect to the profile page for example
            return redirect('/home2')
        else:
            # Invalid credentials, display an error message
            error = 'Invalid credentials. Please try again.'
            return render_template('login.html', error=error)

    return render_template('login.html')


#admin page
@app.route('/admin')
def admin():
    try:
        # Get the email from the session
        email = session.get('email')

        if not email:
            # Redirect to login if email is not in session
            return redirect('/login')

        # Connexion à la base de données
        mysql = get_mysql_connection()
        cursor = mysql.cursor()

        # Exécution de la requête pour récupérer les données
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        data = cursor.fetchall()

        # Fermeture de la connexion à la base de données
        cursor.close()
        

        # Rendu du modèle HTML avec les données récupérées
        return render_template('admin.html', user=data[0])

    except mysql.connector.Error as e:
        # Log the error or print it for debugging
        print("MySQL Error:", str(e))
        # Return an error message or redirect to an error page
        return "An error occurred with the database."


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # Rediriger vers la page d'accueil ou une autre page après la déconnexion
    # Clear the 'email' session variable to log out the user
    session.pop('email', None)
    return redirect('/')


@app.route('/home2', methods=['GET', 'POST'])
def home2():
    return render_template('home2.html')


#Gestion des membres:
@app.route('/Gmembres', methods=['GET', 'POST'])
def member():
    # Connexion à la base de données
    mysql = get_mysql_connection()
    cursor = mysql.cursor()

    # Exécution de la requête pour récupérer les données
    cursor.execute('SELECT * FROM users')
    data = cursor.fetchall()

    # Fermeture de la connexion à la base de données
    cursor.close()
  
    # Rendu du modèle HTML avec les données récupérées
    return render_template('Gmembres.html', users=data)


@app.route('/ajouterm', methods=['POST', 'GET'])
def ajouterm():
    if request.method == 'POST':  # Check if the form is submitted
        fname = request.form['First Name']  # Get the value of the 'First Name' field from the submitted form
        lname = request.form['Last Name']  # Get the value of the 'Last Name' field from the submitted form
        email = request.form['Email']  # Get the value of the 'Email' field from the submitted form
        pname = request.form['Project Name']  # Get the value of the 'First Name' field from the submitted form
        role = request.form['Category']  # Get the value of the 'First Name' field from the submitted form
        password = request.form['Password']  # Get the value of the 'Password' field from the submitted form
        # Connect to the database
        mysql = get_mysql_connection()
        c = mysql.cursor()

        # Insert the data into the database
        req2 = "INSERT INTO users (fname, lname, email, pname, role, password) VALUES (%s, %s, %s, %s, %s, %s)"
        data = (fname, lname, email, pname, role, password)
        c.execute(req2, data)

        # Redirect to the "/Gmembres" page after adding the entry
        return redirect('/Gmembres')

    return render_template('ajouterm.html')  # Return the 'ajouterm.html' template for the registration form


@app.route('/supprimerm/<fname>/<lname>', methods=['GET', 'POST'])
def supprimerm(fname, lname):
    try:
        # Connexion à la base de données
        mysql = get_mysql_connection()
        cursor = mysql.cursor()

        # Requête pour sélectionner l'email correspondant à fname et lname
        cursor.execute('SELECT email FROM users WHERE fname=%s AND lname=%s', (fname, lname))
        emailbd = cursor.fetchone()

        # Vérification si l'email existe et correspond à l'utilisateur connecté
        if emailbd and session.get('email') == emailbd[0]:
            return "you can't delete this user"

        # Exécution de la requête pour supprimer la ligne
        cursor.execute('DELETE FROM users WHERE fname=%s and lname=%s', (fname, lname,))
        

        # Fermeture de la connexion à la base de données
        cursor.close()
       

        return redirect('/Gmembres')

    except Exception as e:
        return jsonify({"error": str(e)}), 404


@app.route('/modifierm/<fname>/<lname>', methods=['GET', 'POST'])
def modifierm(fname, lname):
    if request.method == 'POST':
        try:
            # Get form data from the submitted form
            nfname = request.form['First_Name']
            nlname = request.form['Last_Name']
            nemail = request.form['Email']
            npname = request.form['Project_Name']
            nrole = request.form['Category']
            npassword = request.form['Password']

            # Connect to the database
            mysql = get_mysql_connection()
            with mysql:
                cursor = mysql.cursor()

                # Execute the query to update the user data in the database
                req = "UPDATE users SET fname=%s, lname=%s, email=%s, pname=%s, role=%s, password=%s WHERE fname=%s AND lname=%s"
                data = (nfname, nlname, nemail, npname, nrole, npassword, fname, lname)
                cursor.execute(req, data)

                
        except Exception as e:
            # Log the error for debugging purposes
            print("An error occurred during user update:", str(e))
            # You can also log the error to a file or a logging service

            # Raise an exception or return an error message to handle the error gracefully
            raise Exception("Failed to update the user. Please try again later.")

        # Redirect to the "/Gmembres" page after updating the entry
        return redirect('/Gmembres')

    # Render the 'modifierm.html' template with user data for modification
    return render_template('modifierm.html', user=(fname, lname,))


#Gestion des disciplines:
@app.route('/Gdiscipline', methods=['GET', 'POST'])
def afficher_tableau():
    # Connexion à la base de données
    mysql = get_mysql_connection()
    cursor = mysql.cursor()

    # Exécution de la requête pour récupérer les données
    cursor.execute('select * from discipline')
    data = cursor.fetchall()

    # Fermeture de la connexion à la base de données
    cursor.close()
   

    # Rendu du modèle HTML avec les données récupérées
    return render_template('discipline.html', disciplines=data)


# Route pour ajouter une nouvelle entrée dans la base de données
@app.route('/ajouterd', methods=['POST', 'GET'])
def ajouterd():
    if request.method == 'POST':  # Check if the form is submitted
        code = request.form['Code']  # Get the value of the 'Code' field from the submitted form
        description = request.form['Description']  # Get the value of the 'Description' field from the submitted form

        # Connect to the database
        mysql = get_mysql_connection()
        c = mysql.cursor()

        # Insert the data into the database
        req2 = "INSERT INTO discipline (code, description) VALUES (%s, %s)"
        data = (code, description)
        c.execute(req2, data)

        
        # Redirect to the "/Gdiscipline" page after adding the entry
        return redirect('/Gdiscipline')

    return render_template('ajouterd.html')  # Return the 'ajouterd.html' template for the registration form


    # Route pour supprimer une entrée de la base de données
@app.route('/supprimerd/<code>', methods=['GET', 'POST'])
def supprimerd(code):
        try:
            # Connexion à la base de données
            mysql = get_mysql_connection()
            cursor = mysql.cursor()

            # Exécution de la requête pour supprimer la ligne
            cursor.execute('DELETE FROM discipline WHERE code=%s', (code,))
            mysql.commit()

            # Fermeture de la connexion à la base de données
            cursor.close()
            

            return redirect('/Gdiscipline')

        except Exception as e:
            return jsonify({"error": str(e)}), 404


@app.route('/modifierd/<code>', methods=['GET', 'POST'])
def modifierd(code):

    if request.method == 'POST':  # Check if the form is submitted
        new_code = request.form['Code']
        new_description = request.form['Description']


        # Connect to the database
        mysql = get_mysql_connection()
        cursor = mysql.cursor()

        # Execute the query to update the user data in the database
        req = "UPDATE discipline SET code=%(new_code)s, description=%(new_description)s WHERE code=%(old_code)s"
        data = {
            'new_code': new_code,
            'new_description': new_description,
            'old_code': code
        }
        cursor.execute(req, data)

        # Commit and close the connection
        mysql.commit()
        cursor.close()

        # Redirect to the "/Gmembre" page after updating the entry
        return redirect('/Gdiscipline')

    return render_template('modifierd.html', row=(code,))  # Return the 'modifierd.html' template with user data for modification

#Gestion des roles:
@app.route('/Grole', methods=['GET', 'POST'])
def role():
    # Connexion à la base de données
    mysql = get_mysql_connection()
    cursor = mysql.cursor()

    # Exécution de la requête pour récupérer les données
    cursor.execute('select * from roles')
    data = cursor.fetchall()

    # Fermeture de la connexion à la base de données
    cursor.close()

    # Rendu du modèle HTML avec les données récupérées
    return render_template('role.html', roles=data)

# Route pour ajouter une nouvelle entrée dans la base de données
@app.route('/ajouterr', methods=['POST', 'GET'])
def ajouterr():
    if request.method == 'POST':
        role = request.form['Category']
        description = request.form['Description']

        try:
            mysql = get_mysql_connection()
            c = mysql.cursor()

            req2 = "INSERT INTO roles (role, description) VALUES (%s, %s)"
            data = (role, description)
            c.execute(req2, data)

            
            return redirect('/Grole')

        except mysql.connector.Error as e:
            error_message = f"Error: {e}"
            return render_template('role.html', error_message=error_message)

    return render_template('ajouterr.html')



    # Route pour supprimer une entrée de la base de données
@app.route('/supprimerr/<role>', methods=['GET', 'POST'])
def supprimerr(role):
        try:
            # Connexion à la base de données
            mysql = get_mysql_connection()
            cursor = mysql.cursor()

            # Exécution de la requête pour supprimer la ligne
            cursor.execute('DELETE FROM roles WHERE role=%s', (role,))
            mysql.commit()

            # Fermeture de la connexion à la base de données
            cursor.close()

            return redirect('/Grole')

        except Exception as e:
            return jsonify({"error": str(e)}), 404


@app.route('/modifierr/<role>', methods=['GET', 'POST'])
def modifierr(role):

    if request.method == 'POST':  # Check if the form is submitted
        new_role = request.form['Category']
        new_description = request.form['Description']


        # Connect to the database
        mysql = get_mysql_connection()
        cursor = mysql.cursor()

        # Execute the query to update the user data in the database
        req = "UPDATE roles SET role=%(new_role)s, description=%(new_description)s WHERE role=%(old_role)s"
        data = {
            'new_role': new_role,
            'new_description': new_description,
            'old_role': role
        }
        cursor.execute(req, data)

        # Commit and close the connection
        
        cursor.close()
      
        # Redirect to the "/Gmembre" page after updating the entry
        return redirect('/Grole')

    return render_template('modifierr.html', row=(role,))  # Return the 'modifierr.html' template with user data for modification


#Gestion des projets:
@app.route('/Gprojects', methods=['GET', 'POST'])
def projet():
    # Connexion à la base de données
    mysql = get_mysql_connection()
    cursor = mysql.cursor()

    # Exécution de la requête pour récupérer les données
    cursor.execute('select * from project')
    data = cursor.fetchall()

    # Fermeture de la connexion à la base de données
    cursor.close()
    

    # Rendu du modèle HTML avec les données récupérées
    return render_template('project.html', project=data)


# Route pour ajouter une nouvelle entrée dans la base de données
@app.route('/ajouterp', methods=['POST', 'GET'])
def ajouterp():
    if request.method == 'POST':  # Check if the form is submitted
        ref = request.form['Reference']  # Get the value of the 'reference' field from the submitted form
        ref_com = request.form['Reference_Commercial']  # Get the value of the 'Description' field from the submitted form
        titre = request.form['Titre']
        date_deb = request.form['Date_deb']
        date_fin = request.form['Date_fin']
        coordinateur = request.form['Coordinateur']

        # Connect to the database
        mysql = get_mysql_connection()
        c = mysql.cursor()

        # Insert the data into the database
        req2 = "INSERT INTO project (ref, ref_com, titre, date_deb, date_fin, coordinateur) VALUES (%s, %s, %s, %s, %s, %s)"
        data = (ref, ref_com, titre, date_deb, date_fin, coordinateur)
        c.execute(req2, data)

        
        # Redirect to the "/Gprojects" page after adding the entry
        return redirect('/Gprojects')

    return render_template('ajouterp.html')  # Return the 'ajouterp.html' template for the registration form


    # Route pour supprimer une entrée de la base de données
@app.route('/supprimerp/<ref>', methods=['GET', 'POST'])
def supprimerp(ref):
      # Connexion à la base de données
       mysql = get_mysql_connection()
       cursor = mysql.cursor()

       # Exécution de la requête pour supprimer la ligne
       cursor.execute('DELETE FROM project WHERE ref=%s', (ref,))
       mysql.commit()

       # Fermeture de la connexion à la base de données
       cursor.close()
      
       return redirect('/Gprojects')


@app.route('/modifierp/<ref>', methods=['GET', 'POST'])
def modifierp(ref):

    if request.method == 'POST':  # Check if the form is submitted
        new_ref = request.form['Reference']
        new_ref_com = request.form['Reference_Commercial']
        new_titre = request.form['Titre']
        new_date_deb = request.form['Date_deb']
        new_date_fin = request.form['Date_fin']
        new_coordinateur = request.form['Coordinateur']


        # Connect to the database
        mysql = get_mysql_connection()
        cursor = mysql.cursor()

        # Execute the query to update the user data in the database
        req = "UPDATE project SET ref=%(new_ref)s, ref_com=%(new_ref_com)s, titre=%(new_titre)s, date_deb=%(new_date_deb)s, date_fin=%(new_date_fin)s, coordinateur=%(new_coordinateur)s WHERE ref=%(old_ref)s"
        data = {
            'new_ref': new_ref,
            'new_ref_com': new_ref_com,
            'new_titre': new_titre,
            'new_date_deb': new_date_deb,
            'new_date_fin': new_date_fin,
            'new_coordinateur': new_coordinateur,
            'old_ref': ref
        }
        cursor.execute(req, data)

        # Commit and close the connection
        mysql.commit()
        cursor.close()
        

        # Redirect to the "/Gmembre" page after updating the entry
        return redirect('/Gprojects')

    return render_template('modifierp.html', row=(ref,))  # Return the 'modifierp.html' template with user data for modification


# start the app
if __name__ == '__main__':
    app.run(debug=True, port=5000)

