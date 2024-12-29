# curl -X GET http://localhost:8888/Etudiant
# curl -X POST http://localhost:8888/Etudiant/\?Nom\=Cionaire\&Prenom\=Dick\&idAd\=2

import http.server, urllib.parse, sqlite3, threading, socketserver, signal, sys, requests
from os import curdir, sep

from serv_utils import generate_factures_chart, generate_weather_page, get_weather_forecast


def createHandler(mysql):
    class MyHandler(http.server.BaseHTTPRequestHandler):
        global mysql
        def __init__(self, *args, **kwargs):
            super(MyHandler, self).__init__(*args, **kwargs)

        def do_GET(self):
            """Respond to a GET request."""
            print("GET " + self.path)
            if self.path == '/favicon.ico':
                return
            elif self.path == "/FacturesChart":
                # Récupérer les données des factures depuis la base de données
                data = mysql.select("/Facture")
                if data:
                    # Générer la page HTML avec le camembert
                    html = generate_factures_chart(data)
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(bytes(html, 'UTF-8'))
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(bytes("Aucune donnée disponible pour les factures.", 'UTF-8'))
            elif self.path == "/Weather":
                # Récupérer les prévisions météo
                city = "Paris"  # Ville par défaut (vous pouvez passer en paramètre)
                weather_data = get_weather_forecast(city)
                if weather_data:
                    # Générer une page HTML pour afficher les prévisions météo
                    print(weather_data)
                    html = generate_weather_page(city, weather_data)
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(bytes(html, 'UTF-8'))
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(bytes("Impossible de recuperer les donnees meteo.", 'UTF-8'))
            else:
                res = urllib.parse.urlparse(self.path)
                rep = mysql.select(res.path)
                if len(rep) > 0:
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(bytes(str(rep)+'\n', 'UTF-8'))
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()

        def do_POST(self):
            """Respond to a POST request."""
            print("POST " + self.path)
            if self.path == "/index.html":
                print("ici")
                q = self.rfile.read(int(self.headers['content-length'])).decode(encoding="utf-8")
                query = urllib.parse.parse_qs(q,keep_blank_values=1,encoding='utf-8')
                print(query)
                path = "/Etudiant"
            else:
                print("là")
                res = urllib.parse.urlparse(self.path)
                path = res.path
                query = urllib.parse.parse_qs(res.query)
            rep = mysql.insert(path,query)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

    return MyHandler

class MySQL():
    def __init__(self, name):
        self.c = None
        self.req = None
        self.conn = sqlite3.connect(name,check_same_thread=False)
        self.c = self.conn.cursor()

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def select(self,path):
        elem = path.split('/')
        print(elem)
        if len(elem) == 2:
            req = "select * from %s" %(elem[1])
            print(req)
        else:
            req = "select %s from %s where id=%s" %(elem[3],elem[1],elem[2])
        try:   
            ans = self.c.execute(req).fetchall()
        except Exception as e:
            print(f"une erreur est survenue lors de l'executuin de la requette sql: {e}")
            ans = []
        return ans
    
    def insert(self,path,query):
        print(query)
        attr = ', '.join(query.keys())
        val = ', '.join('"%s"' %v[0] for v in query.values())
        print(attr,val)
        req = "insert into %s (%s) values (%s)" %(path.split('/')[1], attr, val)
        print(req)
        self.c.execute(req)
        self.conn.commit()

class ThreadingHTTPServer(socketserver.ThreadingMixIn,  http.server.HTTPServer):
    pass

def serve_on_port(port,mysql):
    handler_class = createHandler(mysql)
    server = ThreadingHTTPServer(("localhost",port), handler_class)
    server.serve_forever()
    
if __name__ == '__main__':
    mysql = MySQL('logement.db')
    # Mono connection
    #server_class = http.server.HTTPServer
    #httpd = server_class(("localhost", 8888), MyHandler)
    # Multiple connections
    try:
        threading.Thread(target=serve_on_port, args=[7777,mysql]).start()
        threading.Thread(target=serve_on_port, args=[8888,mysql]).start()
        threading.Thread(target=serve_on_port, args=[9999,mysql]).start()
        signal.pause()
    except KeyboardInterrupt:
        print("toto ")
        sys.exit()
    #try:
        # Mono connection
        #httpd.serve_forever()
        # Multiple connections
        #t1 = threading.Thread(target=serve_on_port, args=[7777]).start()
        #t2 = threading.Thread(target=serve_on_port, args=[8888]).start()
        #t3 = threading.Thread(target=serve_on_port, args=[9999]).start()
    #except KeyboardInterrupt:
        #pass
    #httpd.server_close()
