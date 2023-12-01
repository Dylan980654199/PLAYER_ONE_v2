import pymysql

class DAOCategoria:
    def connect(self):
        return pymysql.connect(host="localhost",user="root",password="",db="db_poo" )
    
    def read(self, id):
        con = DAOCategoria.connect(self)
        cursor = con.cursor()

        try:
            if id == None:
                cursor.execute("SELECT * FROM categoria order by nombre asc")
            else:
                cursor.execute("SELECT * FROM categoria where id = %s order by nombre asc", (id,))
            return cursor.fetchall()
        except:
            return ()
        finally:
            con.close()

    def insert(self, data):
        con = DAOCategoria.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute(
                "INSERT INTO categoria(nombre,descripcion,imagen,estado) VALUES(%s, %s, %s, %s)",(data['nombre'], data['descripcion'], data['imagen'], data['estado'],))
            con.commit()
            return True
        except:
            print("Error insertar categoria")
            con.rollback()
            return False
        finally:
            con.close()

    def update(self, id, data):
        con = DAOCategoria.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute("UPDATE categoria SET nombre = %s, descripcion = %s, imagen = %s, estado = %s WHERE id = %s", (data['nombre'], data['descripcion'], data['imagen'], data['estado'], id,))
            con.commit()
            return True
        except:
            con.rollback()
            return False
        finally:
            con.close()

    def delete(self, id):
        con = DAOCategoria.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute("DELETE FROM categoria WHERE id = %s", (id,))
            con.commit()
            return True
        except:
            con.rollback()
            return False
        finally:
            con.close()

    