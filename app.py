from flask import Flask, render_template, request, redirect, send_from_directory, url_for, flash
from flaskext.mysql import MySQL
from datetime import datetime
import os


app = Flask(__name__)
app.secret_key="KONO DIO DA"

mysql = MySQL()
app.config["MYSQL_DATABASE_HOST"]="localhost"
app.config["MYSQL_DATABASE_USER"]="root"
app.config["MYSQL_DATABASE_PASSWORD"]=""
app.config["MYSQL_DATABASE_DB"]="sistema"
mysql.init_app(app)

CARPETA = os.path.join("uploads")
app.config["CARPETA"]=CARPETA

@app.route('/uploads/<NombreFoto>')
def uploads(NombreFoto):
    return send_from_directory(app.config["CARPETA"], NombreFoto)

@app.route("/")
def index():
    sql= "SELECT * FROM `empleados`;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)

    empleados=cursor.fetchall()
    print(empleados)

    conn.commit()
    return render_template("empleados/index.html", empleados=empleados)

@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT foto FROM empleados WHERE id=%s", id)
    fila=cursor.fetchall()
    os.remove(os.path.join(app.config["CARPETA"], fila[0][0]))

    cursor.execute("DELETE FROM empleados WHERE id=%s", (id))
    conn.commit()
    return redirect("/")

@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleados WHERE id=%s",(id) )
    empleados=cursor.fetchall()
    conn.commit()
    print(empleados)

    return render_template("empleados/edit.html", empleados=empleados)

@app.route('/update', methods=['POST'])
def update():
    nombre = request.form["txtnombre"]
    correo = request.form["txtcorreo"]
    foto = request.files["txtfoto"]
    id=request.form["txtID"]
    sql= "UPDATE `empleados` SET nombre= %s, correo= %s WHERE id=%s;"
   
    datos=(nombre,correo,id)
   
    conn= mysql.connect()
    cursor= conn.cursor()

    now = datetime.now()
    tiempo= now.strftime("%Y%H%M%S")
    
    if foto.filename!="":
        NuevaFoto = tiempo+foto.filename
        foto.save("uploads/"+NuevaFoto)
        cursor.execute("SELECT foto FROM empleados WHERE id=%s", id)
        fila=cursor.fetchall()
        os.remove(os.path.join(app.config["CARPETA"], fila[0][0]))
        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s", (NuevaFoto, id))
        conn.commit()

    cursor.execute(sql,datos)
    conn.commit()

    return redirect("/")



@app.route('/create')
def create():
    return render_template("empleados/create.html")

@app.route('/store', methods=['POST'])
def storage():
    nombre = request.form["txtnombre"]
    correo = request.form["txtcorreo"]
    foto = request.files["txtfoto"]

    if nombre=="" or correo=="" or foto=="":
        flash("Debes llenar los campos")
        return redirect(url_for("create"))


    now = datetime.now()
    tiempo= now.strftime("%Y%H%M%S")
    if foto.filename!="":
        NuevaFoto = tiempo+foto.filename
        foto.save("uploads/"+NuevaFoto)

    sql= "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s,%s);"
   
    datos=(nombre,correo,NuevaFoto)
   
    conn= mysql.connect()
    cursor= conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()
    return redirect("/")



if __name__ == "__main__":
    app.run(debug=True)