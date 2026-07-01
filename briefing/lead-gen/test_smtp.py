#!/usr/bin/env python3
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL = "formulasia76@gmail.com"
APP_PASSWORD = "tvlskdfuqfmlvxto"

context = ssl.create_default_context()
server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
server.login(EMAIL, APP_PASSWORD)
print("✅ SMTP LOGIN OK")

msg = MIMEMultipart("alternative")
msg["Subject"] = "Test NEO Agent - Pipeline OK"
msg["From"] = EMAIL
msg["To"] = EMAIL

text = "Hola David,\n\nEsto es una prueba del pipeline de captacion NEO.\n\nSMTP funcionando OK\nEnvio desde Python OK\n\nAhora a por la primera venta.\n\n\u2014 NEO Agent"
html = """<html><body style="font-family:sans-serif;background:#0a0a0a;color:#fff;padding:40px">
<div style="max-width:500px;margin:auto">
<h1 style="color:#ff00ff">Test NEO Agent</h1>
<p>SMTP con App Password <span style="color:#00ff88">OK</span></p>
<p>Envio desde Python <span style="color:#00ff88">OK</span></p>
<p>Ahora a por la <span style="color:#ff00ff">primera venta</span>.</p>
<hr style="border-color:#333">
<p style="color:#888;font-size:12px">\u2014 NEO Agent</p>
</div></body></html>"""

msg.attach(MIMEText(text, "plain"))
msg.attach(MIMEText(html, "html"))

server.sendmail(EMAIL, EMAIL, msg.as_string())
server.quit()
print("EMAIL ENVIADO a", EMAIL)
