import pymysql

class DAOProducto:
    def connect(self):
        return pymysql.connect(host="localhost",user="root",password="",db="db_poo" )
    
    def read(self, id):
        con = DAOProducto.connect(self)
        cursor = con.cursor()

        try:
            if id == None:
                cursor.execute("SELECT * FROM producto order by nombre asc")
            else:
                cursor.execute("SELECT * FROM producto where id = %s order by nombre asc", (id,))
            return cursor.fetchall()
        except:
            return ()
        finally:
            con.close()

    def insert(self, data):
        con = DAOProducto.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute(
                "INSERT INTO producto(sku,nombre,precio,descripcion,imagen,categorias,desarrolladora) VALUES(%s, %s, %s,%s, %s, %s, %s)",(data['sku'],data['nombre'],data['precio'], data['descripcion'], data['imagen'], data['categorias'], data['desarrolladora'],))
            con.commit()
            return True
        except:
            print("Error insertar producto")
            con.rollback()
            return False
        finally:
            con.close()

    def update(self, id, data):
        con = DAOProducto.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute("UPDATE producto SET sku = %s, nombre = %s, precio = %s, descripcion = %s, imagen = %s, categorias = %s, desarrolladora = %s WHERE id = %s", (data['sku'],data['nombre'],data['precio'], data['descripcion'], data['imagen'], data['categorias'], data['desarrolladora'], id,))
            con.commit()
            return True
        except:
            con.rollback()
            return False
        finally:
            con.close()

    def delete(self, id):
        con = DAOProducto.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute("DELETE FROM producto WHERE id = %s", (id,))
            con.commit()
            return True
        except:
            con.rollback()
            return False
        finally:
            con.close()