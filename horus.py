# -*- coding: utf-8 -*-
import time
import autentica
import pdi
import threading
import os



def main():
    #resposável por logar no firebase
    database,storage = autentica.logar("AIzaSyA17s6IPxoZ_hfPcJj6Ejh7xmzQcIv1zN4","horus110886.firebaseapp.com","https://horus110886.firebaseio.com/","horus110886.appspot.com","horus110886-firebase.json","tonmelodicmetal@gmail.com","suelliton")#o objeto autenticar retorna o banco e o storage
    if database and storage:
        print("Usuario logado, banco e storage disponiveis")
    else:
        print("Erro no login")
    listener(database,storage)#inicia o monitoramento do banco

def downloadImage(usuario,experimento,storage):
    print("Download image...")
    try:
        print(usuario +"/"+experimento['nome']+str(experimento['count']-1))
        storage.child("/"+usuario+"/"+experimento['nome']+"/"+experimento['nome']+str(experimento['count']-1)+".jpg").download(experimento['nome']+str(experimento['count']-1)+".jpg")
        return True
    except :
        print("Error in download !!")
        return False

def uploadImage(usuario,experimento,storage):
    print("Uploading image result...")
    #time.sleep(80)
    try:
        print(usuario +"/"+experimento['nome']+str(experimento['count']))
        storage.child("/"+usuario+"/"+experimento['nome']+"/result/"+experimento['nome']+str(experimento['count'])+".jpg").put("imsaidaColorida.jpg")
    except :
        print("Error in uploading !!")
    print("Uploading image resize...")
    #time.sleep(80)
    try:
        print(usuario +"/"+experimento['nome']+str(experimento['count']))
        storage.child("/"+usuario+"/"+experimento['nome']+"/result/resize/"+experimento['nome']+str(experimento['count'])+".jpg").put("imsaidaResize.jpg")
    except :
        print("Error in uploading !!")
    #os.remove("imsaidaColorida.jpg")



def listener(database,storage):#ouve o banco
    while True:
        print("Listening database...")
         #pega referencia do firebase
        try:
            data = database.child().get()
        except Exception as e:
            main()
            raise
        # print(str(data.val()))
        if data.val() != None :#verifica se tem algo no banco
            for usuario in data.val():#itera sobre os usuarios
                lista = []
                for attribute in data.val()[usuario]:#itera sobre os atributos de cada usuario
                    if attribute == "experimentos":# se o atributo for a lista de experimentos
                        for experimento in data.val()[usuario]['experimentos']:#itera sobre a lista de experimentos
                             existeNova = experimento['novaFoto']#boobleano de controle
                             status = experimento['status']
                             if existeNova and status == "ativo":# se tiver foto nova e se o status for ativo
                                 print("nova foto ")
                                 print("Usuario :"+ usuario)
                                 print("\nExperimento: "+str(experimento['nome']))
                                 print("\nfoto :"+str(experimento['count']))
                                 task(usuario,experimento,database,storage)#rotina de processamento

        time.sleep(5)#intervalo de reuisicoes

def updateData(database,usuario,experimento):
    data = database.child().get()#pega o banco
    lista = []
    for exp in data.val()[usuario]['experimentos']:#itera diretamente nos experimentos do usuario
        if exp['nome'] == experimento['nome']:# se encontrar o experimento que será modificado
            exp = experimento# o exp recebe o experimento atualizado com informações novas
        lista.append(exp)# adiciona cadaum dos exp a uma nova lista
    database.update({usuario+"/experimentos":lista})#atualiza a lista do banco com a lista nova


def task(usuario,experimento,database,storage):
    print("Task running for " + experimento['nome']+" ..." )
    if downloadImage(usuario,experimento,storage):
        exp = pdi.process(experimento)#chama objeto da classe pdi
        uploadImage(usuario,experimento,storage)
        updateData(database,usuario,exp)
    else:
        print("Image not found")

if __name__ == '__main__':
    main()
