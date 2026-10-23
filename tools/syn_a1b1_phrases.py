"""A1-B1 Spanish phrase cards: add other natural ways a Spanish speaker would say the same thing."""
import glob
D = '/home/claude/spanish/data/'
ADD = {
'¿Qué tal?':['¿cómo te va?'],
'Estoy bien, gracias.':['muy bien gracias','bien y tú'],
'Mucho gusto.':['encantado de conocerte','encantada de conocerte','un placer'],
'¿De dónde eres?':['¿de dónde vienes?'],
'¿Cuántos años tienes?':[],
'Hablo un poco de español.':['hablo algo de español'],
'No entiendo.':['no te entiendo'],
'¿Puedes repetir, por favor?':['¿puedes repetirlo?','¿me lo puedes repetir?','¿perdona?','¿cómo?'],
'Más despacio, por favor.':['más lento por favor','¿puede hablar más despacio?'],
'No sé.':['no lo sé'],
'Lo siento.':['lo siento mucho','disculpa'],
'De nada.':['no hay de qué','a ti'],
'¡Hasta mañana!':[],
'¡Que tengas un buen día!':['que pases un buen día','buen día'],
'La carta, por favor.':['¿nos trae la carta?','la carta'],
'Quiero un café, por favor.':['quisiera un café','póngame un café','¿me pones un café?'],
'¿Me pone un vaso de agua?':['¿me pones un vaso de agua?','¿me puede traer un vaso de agua?'],
'La cuenta, por favor.':['¿me cobras?','¿me cobra?'],
'Es muy caro.':['es carísimo'],
'¿Puedo pagar con tarjeta?':['¿aceptan tarjeta?'],
'¿Dónde está el baño?':['¿dónde está el aseo?','¿dónde están los baños?'],
'Todo recto.':['todo derecho'],
'¿Qué hora es?':['¿qué hora tienes?'],
'No me gusta.':['no me gusta mucho'],
'Estoy cansado.':['estoy agotado','estoy agotada'],
'Hace calor.':[],
'Está lloviendo.':[],
'Estudio español.':['aprendo español'],
'¡Vale!':['¡de acuerdo!','¡venga!'],
'¡Qué bien!':['¡estupendo!','¡qué bueno!'],
# A2
'¿Qué hiciste ayer?':['¿qué hiciste ayer?'],
'He estado en España.':['ya he estado en España','conozco España'],
'¿Has comido ya?':['¿ya comiste?'],
'¿Qué vas a hacer el fin de semana?':['¿qué vas a hacer el finde?','¿qué planes tienes para el fin de semana?'],
'¿Quedamos mañana?':['¿quedamos para mañana?'],
'¿Te apetece un café?':['¿te apetece tomar un café?','¿vamos a tomar un café?'],
'Me encantaría.':['me encantaría ir','con mucho gusto'],
'Tengo que trabajar.':['tengo que currar'],
'Necesito ir al médico.':['tengo que ir al médico'],
'Quería reservar una mesa.':['me gustaría reservar una mesa'],
'Estaba muy rico.':['estaba riquísimo','estaba muy bueno'],
'¿Me lo puedo probar?':['¿me lo puedo probar?','¿puedo probármelo?'],
'¿Tiene una talla más grande?':['¿tienen una talla más grande?','¿lo tiene en una talla más grande?'],
'Solo estoy mirando.':['solo estoy echando un vistazo','solo miro'],
'¿A qué hora sale el tren?':['¿a qué hora sale el tren?'],
'Me he perdido.':['me he perdido'],
'¿Está lejos?':['¿queda lejos?'],
'Está a cinco minutos andando.':['está a cinco minutos caminando'],
'Hace buen tiempo.':['hace un buen día','hace un día estupendo'],
'Hace mal tiempo.':['hace un tiempo horrible'],
'¿A qué te dedicas?':['¿de qué trabajas?'],
'Me gusta mucho leer.':['me gusta mucho la lectura'],
'Me gusta más el té.':['prefiero té'],
'Estoy de acuerdo.':['estoy de acuerdo contigo'],
'No estoy de acuerdo.':['no estoy de acuerdo contigo'],
'¿Qué te pasa?':['¿estás bien?'],
'No pasa nada.':['no importa','no hay problema'],
'No te preocupes.':['tranquilo','tranquila'],
'¡Que te mejores!':['¡mejórate!','¡que te mejores pronto!'],
'¡Felicidades!':['¡felicitaciones!'],
'¡Buen viaje!':['¡que tengas un buen viaje!'],
'¡Qué pena!':['¡qué lástima!'],
# B1
'Espero que te guste.':['ojalá que te guste'],
'Quiero que vengas.':[],
'Es importante que lo hagas.':[],
'Me parece que tienes razón.':['creo que llevas razón'],
'En mi opinión…':['en mi opinión','a mi parecer','yo creo que'],
'No me importa.':['me da lo mismo'],
'¡Ojalá!':[],
'¿Te importa si abro la ventana?':['¿te molesta si abro la ventana?'],
'¿Podrías ayudarme?':['¿me ayudas?','¿puedes ayudarme?'],
'¿Me harías un favor?':['¿me puedes hacer un favor?'],
'Tengo ganas de verte.':[],
'Me alegro de verte.':['me alegra verte','qué bien verte'],
'Me he equivocado.':['me he confundido'],
'Tienes razón.':['llevas razón'],
'No tienes razón.':['te equivocas','no llevas razón'],
'Es que…':['es que'],
'O sea…':['o sea'],
'Por cierto…':['por cierto','a propósito'],
'Menos mal.':['menos mal','gracias a dios'],
'¡Qué vergüenza!':['¡qué corte!','¡qué bochorno!'],
'¡No me digas!':['¡anda!','¿de verdad?'],
'¡Madre mía!':['¡madre mía!'],
'¡Que te vaya bien!':['¡mucha suerte!'],
'He perdido mi cartera.':['he perdido la cartera'],
'Me han robado el móvil.':['me han robado el teléfono'],
'Llame a una ambulancia.':['¡una ambulancia!'],
'Estoy buscando trabajo.':['estoy buscando empleo'],
'Me gustaría solicitar el puesto.':['me gustaría presentarme al puesto','quiero solicitar el puesto'],
'Deberíamos reciclar más.':['habría que reciclar más'],
'Hay que cuidar el medio ambiente.':['tenemos que cuidar el medio ambiente'],
}
used = set()
for f in sorted(glob.glob(D + '[ab][12]_phrases.txt')):
    out = []
    for l in open(f, encoding='utf-8'):
        if l.startswith('#') or not l.strip(): out.append(l); continue
        c = l.rstrip('\n').split('|')
        while len(c) < 5: c.append('')
        k = c[0].strip()
        if k in ADD:
            used.add(k)
            have = [x.strip() for x in c[2].split(',') if x.strip()]
            low = {h.lower().lstrip('~').strip('¿?¡!.… ') for h in have} | {k.lower().strip('¿?¡!.… ')}
            have += [x for x in ADD[k] if x.lower().strip('¿?¡!.… ') not in low]
            c[2] = ','.join(have)
        out.append('|'.join(c) + '\n')
    open(f, 'w', encoding='utf-8').writelines(out)
print('phrase cards touched', len(used), 'missing', sorted(set(ADD) - used))
