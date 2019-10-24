
from getmac import getmac
from getmac import get_mac_address
import pymysql.cursors
from threading import Thread
import time
import datetime

import TopSecret #File with password, ip-host, name-user and DB.
# Программа: Получение мак адресса по ip
#Programms for get mac-adress by ip in local net!

# основная часть программы.

# Получение настроек. // Settings
# Создание переменных под будущие настройки.
ip_1Lvl_min = 0
ip_2Lvl_min = 0
ip_3Lvl_min = 0
ip_4Lvl_min = 0

ip_1Lvl_max = 0
ip_2Lvl_max = 0
ip_3Lvl_max = 0
ip_4Lvl_max = 0

WaitTimeMinuts = 5 # Сколько минут ждать, прежде чем посчитать что устройство пропало из сети.
            
# Подключение к БД.
connection = pymysql.connect(host=TopSecret.host, user=TopSecret.user, password=TopSecret.password, db=TopSecret.db, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
print ("Подключение успешно!")

# Тут Дополнительные модули (МЕТОДЫ) (Они должны создаваться до выполнения)
def UpdateLastSelect(MAC, FROM): # Метод, который обновляет время последнего обнаружения цели.
    with connection.cursor() as cursor:
        T = time.strftime('%Y-%m-%d %H:%M:%S') # Время в формате БД.
        sql = "UPDATE `"+FROM+"` SET `LastSelect` = '"+ T +"' WHERE `Mac` = '"+MAC+"';" # Запрос на обновление данных.
        cursor.execute(sql)
        connection.commit() 


def InsertToListOfUnknown(ip, MAC, FROM): # Метод, который вставляет в список неизвестных, нового неизвестного.
    with connection.cursor() as cursor:
        T = time.strftime('%Y-%m-%d %H:%M:%S') # Время в формате БД.
        sql = "INSERT INTO `"+FROM+"` (`ip`, `Mac`, `FirstSelect`, `LastSelect`) VALUES ('"+ip+"', '"+MAC+"', '"+T+"', '"+T+"');" # Запрос на добавление данных.
        cursor.execute(sql)
        connection.commit() 


def InsertToListOfCurrentScan(ip, MAC, FROM, Who, Note): # Метод, который вставляет в список текущего сканирования, новую запись.
    with connection.cursor() as cursor:
        T = time.strftime('%Y-%m-%d %H:%M:%S') # Время в формате БД.
        sql = "INSERT INTO `CurrentScan` (`TimeStart`, `CurrentTime`, `Status`, `ip`, `Mac`, `Why`, `Note`) VALUES ('"+T+"', '"+T+"', '"+Status+"', '"+ip+"', '"+MAC+"', '"+Who+"', '"+Note+"');" # Запрос на добавление данных.
        cursor.execute(sql)
        connection.commit() 

def UpdateToListOfCurrentScan(MAC): # Метод, который обновляет в списке текущего сканирования, время последнего обнаружения.
    with connection.cursor() as cursor:
        T = time.strftime('%Y-%m-%d %H:%M:%S') # Время в формате БД.
        sql = "UPDATE `CurrentScan` SET `CurrentTime` = '"+ T +"' WHERE `Mac` = '"+MAC+"';" # Запрос на обновление данных.
        cursor.execute(sql)
        connection.commit()

def CheckCurrentScan(): # Метод, что проверяет таблицу с текущим сканированием, что-бы найти не обновляемых клиентов.
    with connection.cursor() as cursor:
        sql = "select `TimeStart`, `CurrentTime`, `Status`, `ip`, `Mac`, `Why`, `Note` FROM `CurrentScan`;"
        cursor.execute(sql)
        for row in cursor: #
            MAC = row["Mac"]
            ttttiiiiimmmmeee = str(row["CurrentTime"])
            Now = datetime.datetime.now()
            Ranee = datetime.datetime.strptime(ttttiiiiimmmmeee, '%Y-%m-%d %H:%M:%S')
            delta = Now - Ranee
            DeltaNotMicro = datetime.datetime.strptime(str(delta)[:str(delta).rfind('.')], '%H:%M:%S') # Отрезает милисекунды
            deferent = int(delta.seconds / 60)

            if deferent > WaitTimeMinuts: # Если устройство давно не появлялось, то удаляет запись.
                with connection.cursor() as CursInsert:
                    sqlInsert = "INSERT INTO `HistoryOfScaned` (`TimeStart`, `TimeEnd`, `TimePresent`, `Status`, `ip`, `Mac`, `Why`, `Note`) VALUES ('"+str(row["TimeStart"])+"', '"+str(Ranee)+"', '"+str(DeltaNotMicro)+"', '"+row["Status"]+"', '"+row["ip"]+"', '"+row["Mac"]+"', '"+row["Why"]+"', '"+row["Note"]+"');"
                    CursInsert.execute(sqlInsert)
                    connection.commit()
                with connection.cursor() as CursDelete:
                    sqlDelete = "DELETE FROM `CurrentScan` WHERE `Mac` = '"+MAC+"';"
                    CursDelete.execute(sqlDelete)
                    connection.commit()

try:
    with connection.cursor() as cursor:
        sql = "SELECT `id`, `Arguments`, `Value` FROM `Setting`"
        cursor.execute(sql)
        #result = cursor.fetchone()
        #print(result)

        for row in cursor: # Импорт и Вывод на экран всех настроек.
            print(row)

            if row["Arguments"] == "ip_1Lvl_min":
                ip_1Lvl_min = int(row["Value"])
            elif row["Arguments"] == "ip_2Lvl_min":
                ip_2Lvl_min = int(row["Value"])
            elif row["Arguments"] == "ip_3Lvl_min":
                ip_3Lvl_min = int(row["Value"])
            elif row["Arguments"] == "ip_4Lvl_min":
                ip_4Lvl_min = int(row["Value"])

            elif row["Arguments"] == "ip_1Lvl_max":
                ip_1Lvl_max = int(row["Value"])
            elif row["Arguments"] == "ip_2Lvl_max":
                ip_2Lvl_max = int(row["Value"])
            elif row["Arguments"] == "ip_3Lvl_max":
                ip_3Lvl_max = int(row["Value"])
            elif row["Arguments"] == "ip_4Lvl_max":
                ip_4Lvl_max = int(row["Value"])

            elif row["Arguments"] == "WaitTimeMinuts":
                WaitTimeMinuts = int(row["Value"])
finally:
    #connection.close()
    print("Настройки импортированы")

ip_1Lvl_current = int(ip_1Lvl_min)
ip_2Lvl_current = int(ip_2Lvl_min)
ip_3Lvl_current = int(ip_3Lvl_min)
ip_4Lvl_current = int(ip_4Lvl_min)

# Модуль для сканирования сети.
print("Начало сканирования:")
print("ip - адресс" + "\t" + "МАС - адресс" + "\t\t" + "Подпись" + "\t\t\t" + "Сообщение")

ip_4Lvl_current = int(ip_4Lvl_current) - 1 # Поправка на цикл

while 1:
    time.sleep(0.3) # Ждать 300 милисекунд, что-бы НЕ перенагревать процессор.

    ip_4Lvl_current += 1
    Why = ""
    Status = ""
    
    # Корректировка адреса под диапазон.
    if (ip_4Lvl_current > ip_4Lvl_max): ip_4Lvl_current = ip_4Lvl_min; ip_3Lvl_current += 1
    if (ip_3Lvl_current > ip_3Lvl_max): ip_3Lvl_current = ip_3Lvl_min; ip_2Lvl_current += 1
    if (ip_2Lvl_current > ip_2Lvl_max): ip_2Lvl_current = ip_2Lvl_min; ip_1Lvl_current += 1
    if (ip_1Lvl_current > ip_1Lvl_max): 
        ip_1Lvl_current = ip_1Lvl_min
        CheckCurrentScan() # Тут должно быть проверка на "пропавших" После полного цикла сканирования.

    Fullip = str(ip_1Lvl_current) + "." + str(ip_2Lvl_current) + "." + str(ip_3Lvl_current) + "." + str(ip_4Lvl_current) # Создание полного адресса.
    #Thread(target=GetMacAndCalculation, args=(Fullip)).start()
    answer = get_mac_address(ip = Fullip, network_request = True)
    answerString = str(answer).replace(":","-").upper()
    if answerString == "NONE" or answerString == "00-00-00-00-00-00": continue
    #print(Fullip + " - " + answerString)

    #CheckMacIntoDB(answerString)
    Why = ""
    Status = ""
    FromTB = ""
    Messange = ""

    try:
        with connection.cursor() as cursor:
            sql = "select COUNT(*) AS `MaxRow` FROM `ListOfKnown` WHERE `Mac` = '"+answerString+"';" # Запрос в список известных.
            cursor.execute(sql)
            for row in cursor: # По факту переинициализирует массив с полученными данными.
                pass

            if int(row["MaxRow"]) > 0: # Если обнаружено совпадение МАКа в белом списке (список известных).
                Status = "Friend"
                FromTB = "ListOfKnown"
                Messange = ("Найден в белом списке.")

                sql = "select `Why` FROM `ListOfKnown` WHERE `Mac` = '"+answerString+"';" # Запрос в список известных.
                cursor.execute(sql)
                for row in cursor: # По факту переинициализирует массив с полученными данными.
                    Why = row["Why"]

            elif int(row["MaxRow"]) == 0: # Если нету совпадений в белом списке
                Messange = ("Нету в белом списке")
                sql = "select COUNT(*) AS `MaxRow` FROM `BlackList` WHERE `Mac` = '"+answerString+"';" # Запрос в список заблокированных.
                cursor.execute(sql)
                for row in cursor: # По факту переинициализирует массив с полученными данными.
                    pass

                if int(row["MaxRow"]) > 0: # Если обнаружено совпадение МАКа в черном списке.
                    Status = "Blocked"
                    FromTB = "BlackList"
                    Messange = ("Найден в черном списке")
                elif int(row["MaxRow"]) == 0: # Если нету совпадений в черном списке
                    Messange = ("Нету в черном списке.")
                    sql = "select COUNT(*) AS `MaxRow` FROM `ListOfUnknowns` WHERE `Mac` = '"+answerString+"';" # Запрос в список неизвестных.
                    cursor.execute(sql)
                    for row in cursor: # По факту переинициализирует массив с полученными данными.
                        pass

                    Status = "Unknown"
                    FromTB = "ListOfUnknowns"
                    if int(row["MaxRow"]) > 0: # Если обнаружено совпадение МАКа в списке неизвестных.
                        Messange = ("Найден в списке неизвестных")
                    elif int(row["MaxRow"]) == 0: # Если нету совпадений в списке неизвестных.
                        Messange = ("Нету в списке неизвестных")
                        InsertToListOfUnknown(Fullip, answerString, FromTB) # Вставляет нового неизвестного в БД.

    finally:
        #connection.close()
        pass

    UpdateLastSelect(answerString, FromTB)
    with connection.cursor() as cursor:
        sql = "select COUNT(*) AS `MaxRow` FROM `CurrentScan` WHERE `Mac` = '"+answerString+"';" # Запрос в список известных.
        cursor.execute(sql)
        for row in cursor: # По факту переинициализирует массив с полученными данными.
            pass
        if int(row["MaxRow"]) > 0: # Если обнаружено совпадение МАКа в списке текущего сканирования.
            UpdateToListOfCurrentScan(answerString)
        elif int(row["MaxRow"]) == 0: # Если нету совпадений в списке текущего сканирования.
            InsertToListOfCurrentScan(Fullip, answerString, FromTB, Why, Messange) # Вставляет запись в список текущего сканирования.


    print(Fullip + "\t" + answerString + "\t" + Why + "\t" + Messange)
    time.sleep(1) # Ждать 1000 милисекунд, что-бы НЕ перенагревать процессор. После успешного обнаружения.
    
    

           
    