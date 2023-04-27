import cv2
import numpy as np

#Momento do video que ele captura a imagem de papel, pedra ou tesoura
frame_per_second = 0
#placar do jogo
scorebd = [0, 0]

#Utilizando um range de valores, identificamos o gesto (papel, pedra ou tesoura) a partir do contorno da mão
def identify_move(area):
    if(62900  < area < 63900):
        return 'Paper'
    if(49900 < area < 51900):
        return 'Rock'    
    if(47900 < area < 49400):
        return 'Scissors'

#Exibe um texto na tela, pegando como parâmetro o texto, a posição que aparecerá e a imagem em que deve ser exibido
def display_txt(txt, y, contour_draws):
    return cv2.putText(contour_draws, str(txt),(50,y), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 20, 105),2,cv2.LINE_AA)

#Calcula o centro de massa de um contorno achado
def obj_center(contour):
    return int(cv2.moments(contour)['m10']/cv2.moments(contour)['m00']) + int(cv2.moments(contour)['m01']/cv2.moments(contour)['m00'])

#Descobre a posição do Player 1 e do Player 2
def discover_player_hand(contours):
    if (obj_center(contours[0]) < obj_center(contours[1])):
        player1 = contours[0]
        player2 = contours[1]
    else:
        player1 = contours[1]
        player2 = contours[0]        
    return player1, player2

#Verifica o player vencedor do turno
def verify_round_outcome(first_player_move, second_player_move):
    if(first_player_move == second_player_move):
        return 'Draw'
    elif(first_player_move == 'Rock'):
        if second_player_move == "Scissors":
            return 'Player 1 won!'
        else:
            return 'Player 2 won!'
    elif(first_player_move == 'Paper'):
        if second_player_move == "Rock":
            return 'Player 1 won!'
        else:
            return 'Player 2 won!'
    elif(first_player_move == 'Scissors'):
        if second_player_move == "Paper":
            return 'Player 1 won!'
        else:
            return 'Player 2 won!'
        
#Incrementa o placar conforme o resultado das rodadas
def calcula_scorebd(outcome):
    if(frame_per_second % 85 == 0):  
        if(outcome == 'Player 1 won!'):
            scorebd[0] += 1
        if(outcome == 'Player 2 won!'):
            scorebd[1] += 1

#Cria a janela que será exibido o video
cv2.namedWindow("pedra papel tesoura")
#Captura o video ao vivo
video = cv2.VideoCapture("pedra-papel-tesoura.mp4")
#Verifica se a captura começou ou não
if video.isOpened(): 
    #Faz a leitura do próximo quadro do video
    rval, frame = video.read()
else:
    rval = False
while rval:
    frame_per_second += 1


    #Converte a imagem do quadro para HSV, para encontrar a escala de cores que identifica as mãos
    img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #Encontra o range de cores das mãos
    mask_hsv_color1 = cv2.inRange(img_hsv, np.array([0, 20, 0]), np.array([255, 255, 255]))
    mask_hsv_color2 = cv2.inRange(img_hsv, np.array([0, 30, 0]), np.array([255, 255, 255]))
    #Soma as máscaras para encontrar a escala de cores, aproximada, das mãos
    mask_hand = cv2.bitwise_or(mask_hsv_color1, mask_hsv_color2)
    #Define os contornos das 2 mãos baseado na máscara
    contours, _ = cv2.findContours(mask_hand, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #ordena os contornos do maior para o menor
    contours = sorted(contours, key=cv2.contourArea, reverse= True)
    #Faz uma cópia do frame atual
    contours_image = frame.copy()
    #Retorna a imagem com os contornos desenhados em cada mão
    contour_draw = cv2.drawContours(contours_image, [contours[0], contours[1]], -1, (200, 20, 105), 5)
    #Descobre a posição dos players na tela e atribui às variáveis
    player1, player2 = discover_player_hand(contours)
    #Calcula a area do contorno de ambos os players
    area_1 = cv2.contourArea(player1)
    area_2 = cv2.contourArea(player2)
    #Identifica a jogada dos players
    first_player_move = identify_move(area_1)
    second_player_move = identify_move(area_2)
    #Realiza a comparação entre as jogadas e retorna o resultado do round
    outcome = verify_round_outcome(first_player_move,second_player_move)
    #Incrementa o placar
    calcula_scorebd(outcome)
    #Mostra os gestos dos 2 jogadores
    display = display_txt(first_player_move+' x '+second_player_move, 50, contour_draw)
    #Mostra o placar
    display = display_txt(str(scorebd), 100, contour_draw)
    #Mostra o resultado do round na tela
    display = display_txt(outcome, 150, contour_draw)
    #Redimensionamento da imagem exibida
    display = cv2.resize(display, (0, 0), None, 0.475, 0.475)
    #Exibe a imagem scriptada.
    cv2.imshow("pedra papel tesoura", display)

    #atualiza o frame do video
    rval, frame = video.read()
    key = cv2.waitKey(20)

    #Se a tecla ESC for pressionada, o video é interrompido
    if key == 27:
        break

    #destroy a janela de exibição ao finalizar a transmissão
cv2.destroyWindow("pedra papel tesoura")
video.release()
