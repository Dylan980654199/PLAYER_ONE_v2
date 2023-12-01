import pymysql

class DAOCliente:
    def connect(self):
        return pymysql.connect(host="localhost", user="root", password="", db="db_poo")

    def read(self, id):
        con = DAOCliente.connect(self)
        cursor = con.cursor()
        print('id;: ',id)
        try:
            if id is None:
                cursor.execute("SELECT * FROM cliente order by nombre asc")
            else:
                cursor.execute("SELECT * FROM cliente where id = %s order by nombre asc", (id,))
            return cursor.fetchall()
        except:
            return ()
        finally:
            con.close()

    def insert(self, data):
        con = DAOCliente.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute(
                "INSERT INTO cliente(nombre,apellido,foto_perfil,email,password,telefono,dni) VALUES(%s, %s, %s, %s, %s, %s, %s)",
                (data['nombre'], data['apellido'], data['foto_perfil'], data['email'], data['password'], data['telefono'], data['dni'],))
            print("Insertar cliente")
            con.commit()
            return True
        except:
            print("Error insertar cliente")
            con.rollback()
            return False
        finally:
            con.close()

    def update(self, id, data):
        con = DAOCliente.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute("UPDATE cliente set nombre = %s, apellido = %s,foto_perfil = %s, email = %s,password = %s, telefono = %s, dni = %s where id = %s",
                           (data['nombre'], data['apellido'], data['foto_perfil'], data['email'], data['password'], data['telefono'], data['dni'], id,))
            con.commit()
            return True
        except:
            con.rollback()
            return False
        finally:
            con.close()

    def delete(self, id):
        con = DAOCliente.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute("DELETE FROM cliente where id = %s", (id,))
            con.commit()
            return True
        except:
            con.rollback()
            return False
        finally:
            con.close()