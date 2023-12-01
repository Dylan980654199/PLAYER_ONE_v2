import pymysql

class DAOPedido:
    def connect(self):
        return pymysql.connect(host="localhost",user="root",password="",db="db_poo" )
    
    def read(self, id):
        con = DAOPedido.connect(self)
        cursor = con.cursor()

        try:
            if id == None:
                cursor.execute("SELECT * FROM pedido order by dni asc")
            else:
                cursor.execute("SELECT * FROM pedido where id = %s order by dni asc", (id,))
            return cursor.fetchall()
        except:
            return ()
        finally:
            con.close()

    def insert(self, data):
        con = DAOPedido.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute(
                "INSERT INTO pedido(dni, transaccion, fecha, monto, pago, estado) VALUES(%s, %s, %s, %s, %s, %s)",(data['dni'], data['transaccion'], data['fecha'], data['monto'], data['pago'], data['estado'],))
            con.commit()
            return True
        except:
            print("Error insertar pedido")
            con.rollback()
            return False
        finally:
            con.close()

    def update(self, id, data):
        con = DAOPedido.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute("UPDATE pedido SET monto = %s, pago = %s, estado = %s WHERE id = %s", 
                       (data['monto'], data['pago'], data['estado'], id,))
            con.commit()
            return True
        except:
            con.rollback()
            return False
        finally:
            con.close()


    def delete(self, id):
        con = DAOPedido.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute("DELETE FROM pedido WHERE id = %s", (id,))
            con.commit()
            return True
        except:
            con.rollback()
            return False
        finally:
            con.close()