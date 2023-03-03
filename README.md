# Introducción a los hilos

**Nombre:** Kevin Alan Martinez Virgen

**Código:** 219294382

**Materia:** Computación tolerante a fallas

### Introducción

Para esta práctica cree un pequeño programa en python que permite guardar una
lista de urls, cada una de las cuales será monitoreada cada 30 segundos para
comprobar su disponibilidad y tiempo de respuesta

### Desarrollo

Para la aplicación se utilizó TKinter para diseñar la interfaz y se utilizó la
librería incluída en python de SQLite3 para almacenar los datos de forma
persistente. Para consultar los dominios se utilizó el paquete requests

![screenshot](https://i.ibb.co/nfZKmDs/Screen-Shot-2023-03-03-at-10-47-32.png)

En lo que respecta a los hilos, los hilos se crean una vez se forma la interfaz.
Se crean dos hilos, con una estructura de consumidor-productor. El productor
realiza las peticiones para cada de las urls solicitadas, mientras que el
consumidor es el que actualiza la interfaz para mostrar los nuevos valores

Se utilizaron demonios para que cuando se finalice el proceso tambien los
hilos terminen su proceso

```py
    def consumer(self, event: ThreadEvent, queue: Queue):
        db = DB("pinged.db")
        while not event.is_set() or not queue.empty():
            item = queue.get()
            self.update_table_entry(item, db)

    def producer(self, queue: Queue):
        while True:
            for index, item in enumerate(self.list):
                data = self.fetch(item)
                queue.put((index, data))
            sleep(30)

    def exec_trheads(self):
        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=format, level=logging.INFO,
                            datefmt="%H:%M:%S")
        pipeline = Queue(maxsize=10)
        event = ThreadEvent()
        threading.Thread(target=self.producer, args=(
            pipeline,), daemon=True).start()
        threading.Thread(target=self.consumer, args=(
            event, pipeline), daemon=True).start()
```
