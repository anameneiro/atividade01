from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
 return render_template('index.html')

@app.route("/cad/usuario")
def usuario():
 return render_template('usuario.html', titulo="Cadastro de Usuário")

@app.route("/cad/caduser", methods=['POST'])
def caduser():
 return request.form

@app.route("/cad/anuncio")
def anuncio():
 return render_template('anuncio.html')

@app.route("/anuncios/pergunta")
def pergunta():
 return render_template('pergunta.html')

@app.route("/anuncios/compra")
def compra():
 print("Anuncio comprado")
 return ""

@app.route("/anuncio/favoritos")
def favoritos():
 print("Favorito inserido")
 return "<h3>Favoritado</h3>"

@app.route("/config/categoria")
def categoria():
 return render_template('categoria.html')

@app.route("/relatorios/vendas")
def relVendas():
 return render_template('relVendas.html')

@app.route("/relatorios/compras")
def relCompras():
 return render_template('relCompras.html')

