

import cv2
import numpy as np
import os
import random
import time
#from matplotlib import pyplot as plt

def loadAndResizeImage(path):
    image = cv2.imread(path)#leitura de foto que foi baixada
    if len(image) > len(image[0]):# faz o resize levando em consideração se a imagem é portrait ou landscape
        image = cv2.resize(image,(874,1032))
    elif len(image) < len(image[0]):
        image = cv2.resize(image,(1032,874))
    else:
        image = cv2.resize(image,(int(len(image[0])/4),int(len(image)/4)))
    cv2.imwrite("imsaidaResize.jpg",image)
    return image


def process(experimento):
    print("calculando valores para o experimento "+experimento['nome'] +"...")
    path = experimento['nome']+str(experimento['count']-1)+".jpg"
    image = loadAndResizeImage(path)#carrega e diminui tamanho da imagem
    #inclui blur nas imagens
    blurRed = addBlur(image,"red")
    blurGreen = addBlur(image,"green")
    threstholdRed = getThreshold(blurRed)
    threstholdGreen = getThreshold(blurGreen)
    #faz a contagem de pixels das areas de interesse
    redPixels = countPixels(blurRed,threstholdRed,experimento,"red")
    greenPixels  = countPixels(blurGreen,threstholdGreen,experimento,"green")

    generateImageOutput(experimento)

    experimento = calculateValues(redPixels, greenPixels,experimento)
    experimento['novaFoto'] = False#avisa que deu certo dizendo ue nao a foto nova
        #faz a remocao de todas as fotos geradas durante o processo para evitar desperdicio de disco
    os.remove(experimento['nome']+str(experimento['count']-1)+".jpg")
    os.remove("imsaidaRed_"+experimento['nome']+str(experimento['count']-1)+"_.jpg")
    os.remove("imsaidaGreen_"+experimento['nome']+str(experimento['count']-1)+"_.jpg")
    return experimento#retorna o experimento j´´aatualizado para a classe start


def generateImageOutput(experimento):
    time.sleep(2)
    red = cv2.cvtColor(cv2.imread("imsaidaRed_"+experimento['nome']+str(experimento['count']-1)+"_.jpg"), cv2.COLOR_BGR2GRAY)
    green = cv2.cvtColor(cv2.imread("imsaidaGreen_"+experimento['nome']+str(experimento['count']-1)+"_.jpg"), cv2.COLOR_BGR2GRAY)
    imsaidaColorida = np.ones((len(red),len(red[0]),3),dtype=np.uint8)
    for i in range(0,len(red)):
        for j in range(0,len(red[0])):
            if red[i][j] == 255:
                imsaidaColorida[i][j][0] = 0
                imsaidaColorida[i][j][1] = 0
                imsaidaColorida[i][j][2] = 255
            if green[i][j] == 255:
                imsaidaColorida[i][j][0] = 0
                imsaidaColorida[i][j][1] = 255
                imsaidaColorida[i][j][2] = 0
    cv2.imwrite("imsaidaColorida.jpg",imsaidaColorida)


def getThreshold(image):
    hist = cv2.calcHist([np.uint8(image)],[0],None,[256],[0,256])
    anterior = 0
    pico1 = 0
    for i in range(255,100,-1):
        #print(str(i))
        anterior = pico1
        if hist[i] > hist[pico1]:
            pico1 = i
        if hist[i] < hist[anterior]:
            break;
    print("pico1 "+ str(pico1))
    pico2 = 0
    for i in range(pico1-1,0,-1):
        if hist[i] >= hist[pico1]:
            pico2 = i
            break;
    print("pico2 "+ str(pico2))
    v = int( ((pico1-pico2)/2)+pico2)
    vale = hist[v]
    print("valor do corte  "+ str(v))
    print("valor do pixel  "+ str(vale))
    print("------------------\n")
    if pico1-pico2 < 5:# se nao existir o pico um ou seja se ja for direto pro pico grande
        return 120
    return v

def countPixels(blurImage,threshold,experimento,color):

    output = np.ones((len(blurImage),len(blurImage[0])),dtype=np.uint8)#instancia uma matriz numpy
    count = 0#contador
    for i in range(0,len(blurImage)):
    	for j in range(0,len(blurImage[0])):
    		if blurImage[i][j] > threshold :
    			output[i][j] = 255
    			count +=1
    		else:
    			output[i][j] = 0
    if color == "red":
        cv2.imwrite("imsaidaRed_"+experimento['nome']+str(experimento['count']-1)+"_.jpg",output)
    elif color == "green":
        cv2.imwrite("imsaidaGreen_"+experimento['nome']+str(experimento['count']-1)+"_.jpg",output)
    return count

def addBlur(img,color):
    r = img[:,:,2]
    g = img[:,:,1]
    b = img[:,:,0]
    if color == "red":
        imGray =  ((r) + (455-(g)))/4
    elif color == "green":
        imGray =  (g + (455 - (b))) /4
    blur = cv2.blur(imGray,(3,3))
    blur = cv2.blur(blur,(3,3))
    cv2.imwrite("blur.jpg",blur)
    blur = cv2.cvtColor(cv2.imread("blur.jpg"), cv2.COLOR_BGR2GRAY)
    return blur

def calculateValues(redPixels, greenPixels,experimento):
    areaInicial = experimento['crescimento']['areaInicial']
    if redPixels == 0 :
        redPixels = (greenPixels * 4)+1;# evita possiveis divisao por 0 e crash's no script

    if areaInicial == 0:#se for a primeira foto
        areaGreen = (4 * greenPixels) / redPixels#calculo area verde
        print("Area verde total	"+ str(areaGreen))
        experimento['crescimento']['areaInicial'] = round(areaGreen,2)
        lista = []
        lista.append({"dataCaptura":experimento['ultimaCaptura'],"percentualCrescimento":round(0,2),"areaVerde":round(areaGreen,2)})#use rounf(numero,2) pra limitar casas
        experimento['crescimento']['capturas'] = lista
    else:# entra a partir da segunda foto
        lista = experimento['crescimento']['capturas']#pega a lista de capturas
        areaGreen = (4 * greenPixels) / redPixels#calcula area verde
        print("Area verde total	"+ str(areaGreen))
        percentualCrescimento = ((areaGreen-areaInicial) * 100)/areaInicial#calcula percentual crescimento
        print("Taxa de crescimento em percentual é "+str(percentualCrescimento))
        lista.append({"dataCaptura":experimento['ultimaCaptura'],"percentualCrescimento":round(percentualCrescimento,2),"areaVerde":round(areaGreen,2)})#use rounf(numero,2) pra limitar casas
        experimento['crescimento']['capturas'] = lista

    return experimento
