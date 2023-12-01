import pymysql

class DAOUsuario:
    def connect(self):
        return pymysql.connect(host="localhost",user="root",password="",db="db_poo" )
    
    def read(self, id):
        con = DAOUsuario.connect(self)
        cursor = con.cursor()

        try:
            if id == None:
                cursor.execute("SELECT * FROM usuario order by nombre asc")
            else:
                cursor.execute("SELECT * FROM usuario where id = %s order by nombre asc", (id,))
            return cursor.fetchall()
        except:
            return ()
        finally:
            con.close()

    def insert(self,data):
        con = DAOUsuario.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute("INSERT INTO usuario(nombre,apellido,email,password,telefono,rol,imagen,estado,direccion,dni,carrera,fecha,facebook_url,instagram_url,linkedin_url) VALUES(%s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)", (data['nombre'],data['apellido'],data['email'],data['password'],data['telefono'],data['rol'],data['imagen'],data['estado'], data['direccion'], data['dni'], data['carrera'], data['fecha'], data['facebook_url'], data['instagram_url'], data['linkedin_url']))
            con.commit()
            return True
        except:
            con.rollback()
            return False
        finally:
            con.close()

    def update(self, id, data):
        con = DAOUsuario.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute("UPDATE usuario set nombre = %s, apellido = %s, email = %s, password = %s, telefono = %s, rol = %s, imagen = %s, estado = %s, direccion = %s, dni = %s, carrera = %s, fecha = %s, facebook_url = %s, instagram_url = %s, linkedin_url = %s where id = %s", (data['nombre'],data['apellido'],data['email'],data['password'],data['telefono'],data['rol'],data['imagen'],data['estado'], data['direccion'], data['dni'], data['carrera'], data['fecha'], data['facebook_url'], data['instagram_url'], data['linkedin_url'],id,))
            con.commit()
            return True
        except:
            con.rollback()
            return False
        finally:
            con.close()

    def delete(self, id):
        con = DAOUsuario.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute("DELETE FROM usuario where id = %s", (id,))
            con.commit()
            return True
        except:
            con.rollback()
            return False
        finally:
            con.close()