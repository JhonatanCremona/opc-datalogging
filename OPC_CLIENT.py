from opcua import Client

class DataChangeHandler(object):
    def __init__(self, cl):
        self.cliente = cl
    
    def datachange_notification(self, node, val,event_data):
        id = node.nodeid.Identifier
        self.cliente.cargar_valor_nodo(id,val)

class Cliente_OPC:
    def __init__(self, nombre,url,ns) -> None:
        self.nombre = nombre
        self.cliente = Client(url)
        self.nodos={}
        self.name_espace=ns


    def conectar(self):
        try:
            self.cliente.connect()
            print("Conectado al servidor OPC UA")
            self.cliente.activate_session()
        
        except Exception as e:
            print("Error al conectar al servidor OPC UA:", e)

    def desconectar(self):
        self.cliente.disconnect()
        print("Desconectado del servidor OPC UA")

    def suscribir_nodo(self,id,time):
        try:
            ns=self.name_espace
            node = self.cliente.get_node(f"ns={ns};i={id}") 
            handler = DataChangeHandler(self)
            sub = self.cliente.create_subscription(time, handler)
            sub.subscribe_data_change(node)
            print(f"ns={ns};i={id}")
        except Exception as e:
            print("ERROR AL SUSCRIBIR EL NODO: ",e)


    def agregar_nodo(self,id):
        if   id not in self.nodos:
            self.nodos[id]=None

    def cargar_valor_nodo(self,id,valor):
        self.nodos[id]=valor
    
    def get_nodo_value(self,id):
        return self.nodos[id]
        
    def leer_nodos(self):
        for id in self.nodos :
            try:
                nodo_tag = self.cliente.get_node(f"ns={self.name_espace};i={id}")
                value = nodo_tag.get_value()
                self.cargar_valor_nodo(id,value)
            except Exception as e:
                print(f"ns={self.name_espace};i={id}")    
                print(f"Error al leer nodos, ",str(e))
                self.desconectar()
                self.conectar()
