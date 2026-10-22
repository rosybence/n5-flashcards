# wrap the master page into the standalone PWA index.html for GitHub Pages
s=open('/home/claude/n5-flashcards.html').read()
head='''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0E1320">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="日本語">
<link rel="manifest" href="app.webmanifest">
<link rel="icon" type="image/png" sizes="192x192" href="icon2-192.png">
<link rel="apple-touch-icon" href="icon2-180.png">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
'''
tail='''
<script>if('serviceWorker' in navigator)addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}))</script>
</body>
</html>
'''
open('/home/claude/n5-flashcards/jp/index.html','w').write(head+s+tail)
