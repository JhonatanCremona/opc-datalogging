import mysql.connector
from datetime import datetime


USER_DB =   'root'
PASS_DB =   ''
HOST_DB =   'localhost'
DB      =   'dato'
PORT    =   '1010'

CONSOLE_DB_ACTIVE=True
CONSOLE_ACTIVE=True

def Print_Console(srt):
    print(srt) if CONSOLE_ACTIVE else None

def Print_DB(str):
    print(str) if CONSOLE_DB_ACTIVE else None

def conectrar_dB(user,pasw,host,db,port):
    try:
        conexion = mysql.connector.connect(user=user, password=pasw, host=host, database=db, port=port)
        Print_DB("Conectado a la base de datos")
        return conexion
    except:
        Print_DB("Error al conectar a la db")
        
def verificar_conexion(conexion):
    if conexion.is_connected():
        return True
    Print_DB("ERROR En la reconecxion de la base de datos ")
    return False

def cargar_inicio_ciclo(id_equipo,id_receta,fecha_inicico,estado,lote,nombre,peso):
    
    conexion=conectrar_dB(USER_DB,PASS_DB,HOST_DB,DB,PORT)

    try:

        cursor = conexion.cursor()
        consulta_insert = """
                            INSERT INTO ciclo (id_equipo, id_receta, fecha_inicio, estado_inicio, lote)
                            VALUES (%s, %s, %s, %s,%s)
                        """
        valores_insert = (id_equipo, id_receta, fecha_inicico, estado,lote)
        cursor.execute(consulta_insert, valores_insert)
        last_id = cursor.lastrowid
        conexion.commit()
        cursor.close()
        Print_DB("CARGAR inicio de ciclo")
        cargar_receta(id_receta,nombre,peso)
        return last_id
    except  Exception as e :
        Print_DB(f"Fallo al cargar INICIO de ciclo: {str(e)}")
    finally: 
        desconectar_dB(conexion)

def cargar_componentes_2(nombre_SENS, datos, id_ciclo):
    conexion=conectrar_dB(USER_DB,PASS_DB,HOST_DB,DB,PORT)
    if verificar_conexion(conexion)==False:
        print("Fallo en la conecion")
        pass
    try:
        cursor = conexion.cursor()
        consulta_inicio = f"""
            INSERT INTO c_{nombre_SENS} (valor, fecha, id_ciclo)
            VALUES
        """
        valores_insert = []
        for dato in datos:
            valor = float(dato.Get_Valor())
            tiempo = str(dato.Get_Tiempo())
            valores_insert.append(f"({valor}, '{tiempo}', {int(id_ciclo)})")
        consulta_final = f"{consulta_inicio} {', '.join(valores_insert)}"
        cursor.execute(consulta_final)
        conexion.commit()
        cursor.close()
        Print_DB("CARGAR Componentes OK")
    except Exception as e:
        Print_DB("fallo al cargar Componentes")
        print(f"error en cargar lso componentes a la db: {str(e)} ")
    finally: 
        desconectar_dB(conexion)

def cerrar_ciclo(id_ciclo,estado,tiempo,cant_pausas):
    conexion=conectrar_dB(USER_DB,PASS_DB,HOST_DB,DB,PORT)
    if verificar_conexion(conexion)==False:
        print("Fallo en la conecion")
        pass  
    try:
        cursor=conexion.cursor()
        cierre = """
                    INSERT INTO cierre (id_ciclo, estado_fin,tiempo,cant_p)
                    VALUES (%s,%s,%s,%s)                    
                """
        Valores=(id_ciclo,estado,tiempo,cant_pausas)
        cursor.execute(cierre,Valores)
        conexion.commit()
        cursor.close()
        Print_DB("Se genero el cierre de un ciclo")
    except Exception as e :
        Print_DB(f"Error en el cierre de ciclo{str(e)}")
    finally: 
        desconectar_dB(conexion)

def desconectar_dB(conexion):
    conexion.close()

def cargar_receta(id_receta,nombre,peso):
    
    conexion=conectrar_dB(USER_DB,PASS_DB,HOST_DB,DB,PORT)

    if verificar_conexion(conexion)==False:
        print("Fallo en la conecion")
        pass    
    try:
        cursor = conexion.cursor()

        # Consulta SQL
        consulta = """
            SELECT id_receta,descripcion ,peso_t
            FROM recetas
            WHERE id_receta = %s
            GROUP BY id_receta,descripcion ,peso_t;
        """
        valores_insert = (id_receta,)
        cursor.execute(consulta, valores_insert)

        resultados = cursor.fetchall()
        print(resultados)
        print(len(resultados))
        
        if len(resultados)==1:    
            if(resultados[0][1] != str(nombre) or resultados[0][2] != peso):
                editar_receta_dB(id_receta,nombre,peso)
        if(len(resultados)==0):
            cargar_receta_dB(id_receta,nombre,peso)
        if(len(resultados)>1):
            Print_Console("Error en dB Recetas")
        
    except Exception as e:
        Print_Console(f"Error: en cargar recetas {str(e)}")
    finally:
        cursor.close()
        conexion.close()
        
def editar_receta_dB(id_receta, nombre, peso):
    try:
        
        conexion=conectrar_dB(USER_DB,PASS_DB,HOST_DB,DB,PORT)
        cursor = conexion.cursor()

        # Consulta SQL para actualizar la receta
        consulta = """
            UPDATE recetas
            SET descripcion = %s, peso_t = %s
            WHERE id_receta = %s;
        """

        valores_insert = (nombre, peso, id_receta)
        cursor.execute(consulta, valores_insert)

        conexion.commit()

        Print_Console("Receta editada exitosamente")

    except Exception as e:
        Print_Console(f"Error al editar la receta: {str(e)}")

    finally:
        cursor.close()
        conexion.close()

def cargar_receta_dB(id_receta, nombre, peso):
    try:
        conexion=conectrar_dB(USER_DB,PASS_DB,HOST_DB,DB,PORT)

        cursor = conexion.cursor()

        # Consulta SQL para insertar una nueva receta
        consulta = """
            INSERT INTO recetas (id_receta, descripcion, peso_t)
            VALUES (%s, %s, %s);
        """

        valores_insert = (id_receta,nombre, peso)
        cursor.execute(consulta, valores_insert)

        conexion.commit()

        Print_Console("Receta cargada exitosamente")

    except Exception as e:
        Print_Console(f"Error al cargar la receta: {str(e)}")

    finally:
        cursor.close()
        conexion.close()

def cargar_componentes(id_ciclo,datos):

    conexion=conectrar_dB(USER_DB,PASS_DB,HOST_DB,DB,PORT)
    if verificar_conexion(conexion)==False:
        print("Fallo en la conecion")
        pass
    try:
        cursor = conexion.cursor()
        consulta_inicio = f"""
            INSERT INTO componente (id_ciclo,fecha,nivel,t_agua,t_producto,t_ingreso)
            VALUES
        """
        valores_insert = []
        for i in range(len(datos[0])):
            tiempo      = str(datos[0][i])
            nivel       = float(datos[1][i])
            t_agua      = float(datos[2][i])
            t_producto  = float(datos[3][i])
            t_ingreso   = float(datos[4][i])
    
            valores_insert.append(f"({int(id_ciclo)},'{tiempo}',{nivel},{t_agua},{t_producto},{t_ingreso})")
        consulta_final = f"{consulta_inicio} {', '.join(valores_insert)}"
        cursor.execute(consulta_final)
        conexion.commit()
        cursor.close()
        Print_DB("CARGAR Componentes OK")
    except Exception as e:
        Print_DB("fallo al cargar Componentes")
        print(f"error en cargar lso componentes a la db: {str(e)} ")
    finally: 
        desconectar_dB(conexion)

def cargar_sensor(id_ciclo,nombre,datos):
    valores_insert=[]
    t_init=None
    t_fin=None
    valor=1
    valor_anterior=None
    try:
        for valor,tiempo in datos:
            if valor != valor_anterior:
                if t_init is not None:
                    t_fin = tiempo
                    valores_insert.append(f"({int(id_ciclo)}, '{t_init}', {valor_anterior}, '{t_fin}', '{nombre}')")
                t_init=tiempo
            valor_anterior=valor
        
        ultimo_v,ultimo_t=datos[-1]
        valores_insert.append(f"({int(id_ciclo)}, '{t_fin}', {ultimo_v}, '{ultimo_t}', '{nombre}')")
        conexion=conectrar_dB(USER_DB,PASS_DB,HOST_DB,DB,PORT)
        cursor = conexion.cursor()
        consulta_inicio = f"""
                INSERT INTO sensores (id_ciclo,t_init,valor,t_fin,nombre)
                VALUES
            """
        consulta_final = f"{consulta_inicio} {', '.join(valores_insert)}"
        print("Consulta final:", consulta_final)
        cursor.execute(consulta_final)
        conexion.commit()
        cursor.close()
        Print_DB("CARGAR sensor OK")
    except Exception as e:
        Print_DB("fallo al cargar Sensor")
        print(f"error en cargar los estados de lso sensoeres a la db: {str(e)} ")
    finally: 
        desconectar_dB(conexion)