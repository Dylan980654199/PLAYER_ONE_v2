import pymysql

class DAOMensaje:
    def connect(self):
        return pymysql.connect(host="localhost", user="root", password="", db="db_poo")

    def read(self, id):
        con = DAOMensaje.connect(self)
        cursor = con.cursor()
        print('id;: ',id)
        try:
            if id is None:
                cursor.execute("SELECT * FROM mensaje order by nombre asc")
            else:
                cursor.execute("SELECT * FROM mensaje where id = %s order by nombre asc", (id,))
            return cursor.fetchall()
        except:
            return ()
        finally:
            con.close()

    def insert(self, data):
        con = DAOMensaje.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute(
                "INSERT INTO mensaje(nombre,email,message) VALUES(%s, %s, %s)",
                (data['nombre'], data['email'], data['message'],))
            print("Insertar mensaje")
            con.commit()
            return True
        except:
            print("Error insertar mensaje")
            con.rollback()
            return False
        finally:
            con.close()

    def update(self, id, data):
        con = DAOMensaje.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute("UPDATE mensaje SET nombre = %s, email = %s, message = %s WHERE id = %s", (data['nombre'], data['email'], data['message'], id,))
            con.commit()
            return True
        except:
            con.rollback()
            return False
        finally:
            con.close()

    def delete(self, id):
        con = DAOMensaje.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute("DELETE FROM mensaje WHERE id = %s", (id,))
            con.commit()
            return True
        except:
            con.rollback()
            return False
        finally:
            con.close()