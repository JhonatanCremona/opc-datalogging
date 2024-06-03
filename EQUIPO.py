import time
from sql import *
#================
INACTIVO=28672
CANCELADO=6
SEND_DATA_BASE=True
#================

class Sensor:
    def __init__(self) -> None:
        self.id                 = None
        self.nombre             = None
        self.valor              = None
        self.historico          = []
        self.config_seve        = None
    
    def agregar(self,id,nombre) -> None:
        self.id=id
        self.nombre=nombre
        self.valor=None

    def agregar_valor_historico(self,valor,fecha):
        self.historico.append((valor,fecha))

    def get_id(self):
        return self.id
    
    def get_nombre(self):
        return self.nombre
    
    def get_valor(self):
        return self.valor
    
    def get_historico(self):
        return self.historico
    
    def set_valor(self,valor):
        self.valor=valor

    def borrar_historico(self):
        self.historico.clear()

class Equipo:
    def __init__(self,nombre,id,cliente) -> None:
        self.sensores = {}
        self.nombre=nombre
        self.id=id
        self.estado=None
        self.cliente=cliente
        self.id_ciclo=None
        self.sensores_analog = ["NIVEL_AGUA","NIVEL_AGUA", "T_AGUA", "T_PRODUCTO", "T_INGRESO"]
        self.sensores_digitales=["ESTADO","AMONIACO","VAPOR_VIVO"]
 
    def agregar_sensor(self,id,nombre):
        sensor = Sensor()  
        sensor.agregar(id, nombre)
        self.sensores[nombre]=sensor        

    def cargar_al_historico(self,nombre,valor,fecha):
        self.sensores.get(nombre).agregar_valor_historico(valor,fecha)

    def get_sensores(self):
        return self.sensores

    def leer_nodo_cliente(self,id,cliente):
        return cliente.get_nodo_value(id)
    
    def cambiar_estado(self,estado):
        print("cambio de estado",estado,"id_ciclo",self.id_ciclo)
        if self.estado != INACTIVO and estado == INACTIVO:
            if self.id_ciclo != None:
                print("Enviando componentes")
                self.send_componentes()
                print("Enviando componentes")
                self.send_elementos()
                self.fin_de_ciclo()
        #if self.estado == INACTIVO and estado != INACTIVO:
        if  estado != INACTIVO:
            print("inicio de ciclos: ",self.id_ciclo)
            self.id_ciclo=self.inicio_de_ciclo()
        self.estado=estado
    
    def guardar_nodo_valor(self,nombre):
        id=self.sensores.get(nombre).get_id()
        valor=self.cliente.get_nodo_value(id)
        self.sensores.get(nombre).set_valor(valor)

    def guardar_valores_sensores(self):
        tiempo=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for sensor in self.sensores:
            id=self.sensores.get(sensor).get_id()
            valor=self.cliente.get_nodo_value(id)
            self.sensores.get(sensor).set_valor(valor)
            if self.estado != INACTIVO:
                self.cargar_al_historico(sensor,valor,tiempo)
            #print(f"{sensor}:{valor}")

    def obtener_id_nombre(self,nombre):
        id = self.sensores[nombre].get_id()
        return id
    
    def limpiar_historico(self):
        for sensor in self.get_sensores():
            self.sensores.get(sensor).borrar_historico()

    def obtener_valor_sensor(self, nombre):
        valor = None
        if nombre in self.get_sensores():
            valor=self.sensores.get(nombre).get_valor()
        return valor

    def obtener_historico_sensor(self,nombre):
        valores = None
        if nombre in self.get_sensores():
            valores = self.sensores.get(nombre).get_historico()
        return valores 
##···········································································································
    def fin_de_ciclo(self):
        if SEND_DATA_BASE == True :
            cerrar_ciclo(self.id_ciclo,self.estado,self.sensores.get("TIEMPO_TRANSCURRIDO").get_valor(),0)
        self.limpiar_historico()
    
    def inicio_de_ciclo(self):
        id_ciclo=None

        id_receta           =self.obtener_valor_sensor("NRO_RECETA")
        fecha_receta        =time.time()
        estado              =self.estado
        lote                =self.obtener_valor_sensor("LOTE")
        nombre              =self.obtener_valor_sensor("NOMBRE_RECETA")
        peso                =self.obtener_valor_sensor("PESO")

        if SEND_DATA_BASE == True :
            id_ciclo=cargar_inicio_ciclo(self.id,id_receta,fecha_receta,estado,lote,nombre,peso)

        return id_ciclo

    def send_data_DB(self):
        if SEND_DATA_BASE == True :
            for nombre in self.get_sensores():
                cargar_componentes( nombre, self.sensores.get(nombre).get_historico(),self.id_ciclo)
            Print_Console(f"Se cargo datos en a la db")

    def send_componentes(self):
        try:
            
            datos = [[], [], [], [], []]
            for i,sensor in enumerate(self.sensores_analog):
                if i==0:
                    datos[i].extend([tupla[1] for tupla in self.obtener_historico_sensor(sensor)])
                else:
                    datos[i].extend([tupla[0] for tupla in self.obtener_historico_sensor(sensor)])

            print(datos)
            cargar_componentes(self.id_ciclo,datos)
        except Exception as e:
            print(f"ERROR al enviar componentes-> {e}")

    def send_elementos(self):
        try:
            if SEND_DATA_BASE == True :
                for nombre in self.sensores_digitales:
                    if nombre not in self.sensores_analog:
                        print(nombre)
                        print(self.obtener_historico_sensor(nombre))
                        cargar_sensor(self.id_ciclo, nombre, self.obtener_historico_sensor(nombre))
                Print_Console(f"Se cargo datos en a la db")
        except Exception as e:
            print(f"ERROR al enviar componentes-> {e}")
##···········································································································
    def reporte_home(self):
        dato={
                "NOMBRE"                    :   self.nombre,
                "TIEMPO_TRANSCURRIDO"       :   self.obtener_valor_sensor("TIEMPO_TRANSCURRIDO"),
                "NRO_TORRES"                :   self.obtener_valor_sensor("NRO_TORRES"),
                "NOMBRE_RECETA"             :   self.obtener_valor_sensor("NOMBRE_RECETA"),
                "ID"                        :   self.id,
                "ESTADO"                    :   self.obtener_valor_sensor("ESTADO"),
        }
        return dato
    
    def reporte_sensor(self,nombre):
        
        results = []
        max=0
        min=10000
        for historico in self.sensores.get(nombre).get_historico():
            valor=historico[0]
            tiempo=historico[1]
            results.append  ({
                                "value": valor,
                                "time": int(tiempo)
                            })
            if(valor>max):
                max=valor
            if(valor<min):
                min=valor

        datos_sensor = {
                    "sensor":   nombre,
                    "results":  results,
                    "ULTIMO":   self.obtener_valor_sensor(nombre),
                    "MAX":      max,
                    "MIN":      min
                }
        return datos_sensor
    
    def report_datos(self):
        try:
            equipo_data = {
                            "NOMBRE": self.nombre,                         
                            "componentes": {
                                                "ESTADO"                : self.obtener_valor_sensor("ESTADO"),
                                                "T_AGUA"                : self.obtener_valor_sensor("T_AGUA"),
                                                "T_PRODUCTO"            : self.obtener_valor_sensor("T_PRODUCTO"),
                                                "T_INGRESO"             : self.obtener_valor_sensor("T_INGRESO"),
                                                "NIVEl_AGUA"            : self.obtener_valor_sensor("NIVEl_AGUA"),
                                                "VAPOR_VIVO"            : self.obtener_valor_sensor("VAPOR_VIVO"),
                                                "VAPOR_SERPENTINA"      : self.obtener_valor_sensor("VAPOR_SERPENTINA"),
                                            },
                                "NOMBRE_RECETA"         : self.obtener_valor_sensor("NOMBRE_RECETA"),
                                "NRO_TORRES"            : self.obtener_valor_sensor("NRO_TORRES"),
                                "NRO_PASOS"             : self.obtener_valor_sensor("NRO_PASOS"),
                                "TIEMPO_TRANSCURRIDO"   : self.obtener_valor_sensor("TIEMPO_TRANSCURRIDO"),
                                "LOTE"                  : self.obtener_valor_sensor("LOTE"),                                
                            }

            return equipo_data
        except Exception as e:
            print(f"Error al obtener datos del equipo: {str(e)},En report")
            return None  