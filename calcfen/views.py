from django.shortcuts import render
import cv2
import easyocr


# Create your views here.

def home(request):
    return render(request, 'fen/home.html')

###############################

def calcula(request):    

    im = cv2.imread('fencolatina.jpg')

    # faz o tratamento da imagem antes da leitura pelo easyocr

    grayImage = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    thresh, im_bw = cv2.threshold(grayImage, 190, 300, cv2.THRESH_BINARY)

    cv2.imwrite('nova.jpg', im_bw)

    # funcao para resuzir o ruido da imagem

    def noise_removal(image):
        
        import numpy as np
        kernel = np.ones((1, 1), np.uint8)
        image = cv2.dilate(image, kernel, iterations=1)
        kernel = np.ones((1, 1), np.uint8)
        image = cv2.erode(image, kernel, iterations=1)
        image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        image = cv2.medianBlur(image, 3)
        return(image)
    
    no_noise = noise_removal(im_bw)

    cv2.imwrite('nova2.jpg', no_noise)

    # le a imagem tratada

    im = cv2.imread('nova2.jpg')

    reader = easyocr.Reader(['en'], gpu = False)

    text_ = reader.readtext(im, add_margin=0.1) 

    #####################################
    # Calculo dos volumes do navio
    #####################################
    
    # referencia para pegar a coluna dos volumes do navio

    referencia_navio  = "145,505"
    valor_final_navio = "148,853"

    nova_referencia = []
    novo_final = []
            
    nova_referencia = referencia_navio[:6]
    novo_final = valor_final_navio[:6]

    w_coordxn = 0
    coordxn = 0

    x = 0
    y = 1

    for t in text_:
        
        coo, text, rate = t    
        
        if text[:6] == nova_referencia:
            
            if x == y:
                
                coordxn = coo[0][0]
                w_coordxn = coo[1][0] - coo[0][0]
                coordyn = coo[0][1]     
                            
            x = x + 1     
            
    centro_navio = coordxn + int(w_coordxn/2)

    volume_navio = []

    for t in text_:
        
        coo, text, rate = t
        
        if (coo[0][0] + int((coo[1][0] - coo[0][0]) / 2)) >= centro_navio - 40 and (coo[0][0] + int((coo[1][0] - coo[0][0]) / 2)) <= centro_navio + 40 and coo[0][1] >= coordyn:
            
            volume_navio.append(text)        
            
            if text[:6] == novo_final:

                break

    #####################################
    # Calculo dos volumes de terra
    #####################################

    # referencia para pegar a coluna dos volumes de terra

    referencia_terra  = "144,196"
    valor_final_terra = "150,588"

    nova_referencia = []
    novo_final = []
            
    nova_referencia = referencia_terra[:6]
    novo_final = valor_final_terra[:6]

    w_coordxt = 0
    coordxt = 0

    x = 0
    y = 0

    for t in text_:   
    
        coo, text, rate = t     
        
        if text[:6] == nova_referencia:
        
            if x == y:
            
                coordxt = coo[0][0]
                w_coordxt = coo[1][0] - coo[0][0]
                coordyt = coo[0][1]    
                        
            x = x + 1    

    centro_terra = coordxt + int(w_coordxt/2)

    volume_terra = []

    for t in text_:
    
        coo, text, rate = t
    
        if (coo[0][0] + int((coo[1][0] - coo[0][0]) / 2)) >= centro_terra - 40 and (coo[0][0] + int((coo[1][0] - coo[0][0]) / 2)) <= centro_terra + 40 and coo[0][1] >= coordyt:
        
            volume_terra.append(text)        
            
            if text[:6] == novo_final:

                break

    volumes = zip(volume_navio, volume_terra)
    
    volumes = {
        'volumes' : volumes,                
    }
    
    return render(request, 'fen/resultado.html', volumes)

######################################

def seleciona(request):

    query_dict = request.POST

    myDict = dict(query_dict.lists())

    tamanho = len(myDict['navio'])
    
    valores_navio = []
    valores_terra = []

    for i in range(len(myDict['navio'])):

        valores_navio.append(myDict['navio'][i])
        valores_terra.append(myDict['terra'][i])

    valores = zip(valores_navio, valores_terra)

    resposta = {

        'volumes' : valores,
        'tamanho' : tamanho
    }

    return render(request, 'fen/seleciona.html', resposta)
