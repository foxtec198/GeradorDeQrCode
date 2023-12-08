from os import system, makedirs, mkdir, remove, listdir 
from pyodbc import connect as sql# Connect SQL
from segno import make_qr # Gerador de qr
from time import strftime as st # Data e Hora Atual
from PIL import Image, ImageDraw, ImageFont
from PyPDF2 import PdfReader, PdfMerger
from reportlab.pdfgen import canvas
from PyQt5 import uic, QtWidgets as qw
from qdarktheme import setup_theme as set
from webbrowser import open_new_tab as on
from sqlite3 import connect

class GeradorQR():
    def run(self):
        self.app = qw.QApplication([])
        
        self.main = uic.loadUi('resources/uis/main.ui')
        self.login = uic.loadUi('resources/uis/login.ui')
        set()
        self.connL = connect('resources/scr/dd.db')
        self.c = self.connL.cursor()
        
        self.login.btnLogin.clicked.connect(self.realizarLogin)
        
        self.main.btnGerarQR.clicked.connect(self.gerar)
        self.main.btnAbrirPasta.clicked.connect(self.abrirPastaDeGeracao)
        self.main.gitBtn.clicked.connect(self.gitHub)
        
        u = self.c.execute('SELECT * FROM USERS ORDER BY Id DESC').fetchone()
        if u != None:
            Id = [0]
            self.action(f'DELETE FROM USERS WHERE Id <> "{Id}"')
            self.login.entryServer.setText(u[3])
            self.login.entryUser.setText(u[1])
            self.login.entryPasw.setText(u[2])
            self.login.saveUser.setChecked(True)
        self.login.show()
        
        self.app.exec()

    def realizarLogin(self):
        self.server = self.login.entryServer.text()
        self.user = self.login.entryUser.text()
        self.pwd = self.login.entryPasw.text()
        nome = self.user.replace('.', ' ')
        nome = nome.split()
        
        if self.login.saveUser.isChecked():
            self.action(f"INSERT INTO USERS(user, pwd, servidor)VALUES('{self.user}','{self.pwd}','{self.server}')")
        else:
            self.action(f'DELETE FROM USERS')
        
        try:
            self.conn = sql(f"DRIVER=SQL Server;SERVER={self.server};UID={self.user};PWD={self.pwd}")
            self.c2 = self.conn.cursor()
            self.msg(self.login, 'Logado com Sucesso!', f'Logado com sucesso, bem vindo {nome[0]}')
            self.main.show()
            self.login.close()
        except:
            self.msg(self.login, 'Erro de Login!','Confirme o VPN e/ou suas Credenciais!!! ')
    
    def logicaDeGeração(self):
        cont = 0
        for c in self.estrutura:
            qrc = c[1] # definindo o qr code
            self.nomeLocal = c[0] # o nome do sublocal
            self.nomeLocal = self.nomeLocal.replace('/','') # removendo barras para n ocasionar erro
            qrcode = make_qr(qrc) # gerando o qrcode.png
            qrLocal = f'{self.nomeDir}/{self.nomeLocal}.png' # definido a estrutura do diretorio
            qrcode.save(qrLocal, scale=10) #salvando o qrcode no diretorio
            qrImg = Image.open(qrLocal) # Abrindo o qrcode com o PIL
            modelo = Image.open(f'resources/scr/{self.modelo}.png') # Abrindo o modelo padrão com o PIL
            merge = Image.new('RGBA', modelo.size) # Abrinda uma nova imagem para edição
            x = int((modelo.size[0]-qrImg.size[0])/2) # Valor Dinamico
            merge.paste(modelo) # Carrega o Modelo
            merge.paste(qrImg, (x, 350)) # Cola o qr code no valor relativo
            txt = Image.open('resources/scr/600.png') # Versionamento de texto
            dw = ImageDraw.Draw(txt) # Escreve a estrutura e centraliza
            fnt = ImageFont.truetype('resources/scr/arial_narrow_7.ttf', 35) # Font and size
            x, y = dw.textsize(self.nomeLocal, fnt) # Aplica os valores
            xt = (600-x)/2 # Valor relativo do Texto
            dw.text((xt, 40), self.nomeLocal, font=fnt, fill='black', align='center') # Fazendo o merge do Texto no modelo com o qrcode
            
            # Salva o arquivo!
            txt.save('resources/scr/texto.png')
            imgt = Image.open('resources/scr/texto.png')
            x = int((modelo.size[0]-imgt.size[0])/2)
            merge.paste(imgt, (x, 200))
            merge.save(qrLocal)
            
            # Transforma o arquivo em pdf com todos os QRs
            img = Image.open(qrLocal)
            x, y = img.size
            self.nomePdf = f'{self.nomeDir}/{self.nomeLocal}.pdf'
            pdf = canvas.Canvas(self.nomePdf, pagesize=(x, y))
            pdf.drawImage(qrLocal, 0,0)
            pdf.save()
            cont += 1
            
        # MERGE - Mescla os PDF's
        dir = listdir(self.nomeDir)
        mg = PdfMerger()
        for i in dir:
            if '.pdf' in i:
                with open(f'{self.nomeDir}/{i}', 'rb') as arq:
                    dados = PdfReader(arq)
                    mg.append(dados)
        mg.write(f'{self.nomeDir}/EstruturaCompleta.pdf')
        mg.close()
        
        # REMOVE - Remove copias!
        dir = listdir(self.nomeDir)
        for i in dir:
            if '.pdf' in i and i != 'EstruturaCompleta.pdf':
                remove(f'{self.nomeDir}/{i}')
    
    def gerar(self):
        self.CR = self.main.crEntry.text()
        self.nivel = int(self.main.nivelEntry.text())
        
        if self.nivel != '':
            self.nivel += 3
        elif self.nivel == '':
            self.nivel = 3

        ForceRadio = self.main.ForceRadio
        MiniRadio = self.main.MiniRadio
        OnSegRadio = self.main.OnSegRadio
        PoliRadio = self.main.PoliRadio
        TopRadio = self.main.TopRadio
        TradRadio = self.main.TradRadio
        
        if ForceRadio.isChecked(): self.modelo = 'modeloForce'
        if MiniRadio.isChecked(): self.modelo = 'modeloMini'
        if OnSegRadio.isChecked(): self.modelo = 'modeloOnSeg'
        if PoliRadio.isChecked(): self.modelo = 'modeloPoli'
        if TopRadio.isChecked(): self.modelo = 'modeloTop'
        if TradRadio.isChecked(): self.modelo = 'modeloTrad'
        
        self.cons = f"""
        SELECT E.Descricao as Nome, E.QRCode, E.Grupo
        FROM Estrutura E
        INNER JOIN DW_Vista.dbo.DM_Estrutura as Es on Es.Id_Estrutura = Id
        WHERE Es.CRNo = {self.CR}
        AND E.Nivel >= {self.nivel}"""
        
        self.estrutura = self.c2.execute(self.cons).fetchall()
        self.data = st('%d-%m_%H-%M-%S')
        for i in self.estrutura:self.nomeGrupo=i[2]
        try: mkdir('resources/QRCodes')
        except: ...
        self.nomeDir = f'resources/QRCodes/{self.nomeGrupo}_{self.data}'
        makedirs(self.nomeDir)
        
        self.logicaDeGeração()
        self.msg(self.main, 'Sucesso!',f'QR Codes gerados com sucesso \n {self.nomeGrupo}')
        
    def abrirPastaDeGeracao(self):
        system('Explorer resources\QRCodes')
        
    def gitHub(self):
        on('https://github.com/foxtec198/GeradorQR/issues/new')
    
    def action(self, consulta):
        self.c.execute(consulta)
        self.connL.commit()
         
    def msg(self, win, title, text):
        qw.QMessageBox.about(win, title, text)
        
    
GeradorQR().run()