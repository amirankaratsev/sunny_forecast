#загружаем библиотеки
import streamlit as st
import pandas as pd
import datetime
from geopy.geocoders import Nominatim
import requests
import random
import string
import time
import locale
from PIL import Image
import os


#установим задний фон
def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://drscdn.500px.org/photo/1065458626/q%3D80_m%3D2000/v2?sig=32a168ec57de6357655210b9b63d195598102f2b17cb5865b721b1803bf88155");
             background-attachment: fixed;
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_bg_from_url() 

#напишем заголовок и описание приложения
st.header('Sunny forecast')
st.caption('<p style="font-size:20px;color:orange">Here comes the sun!</p>',
unsafe_allow_html=True)
st.markdown("""Запланируйте внезапное путешествие с нашим приложением.  
Введите названия городов и получите прогноз погоды до семи дней вперед!
""")

#сначала опишем все функции
#это функция, которая получает прогноз погоды в виде таблицы(forecast) и общего вывода о погоде(final)
def get_weather(city, start_date, end_date):
    geolocator = Nominatim(user_agent="Amiran")
    #получим координаты введенного пользователем города с помощью geolocator
    location = geolocator.geocode(city)
    lat=location.latitude
    lon=location.longitude
    #отправим запрос к тестовой версии api яндекс погоды
    params= {'lat': lat,
             'lon': lon,
             'lang': 'ru_RU',
             #прогноз возьмем на максимальное количество дней для тестовой версии api - 7 дней
             'limit': '7',
             'hours': 'false',
             'extra': 'false'}

    response = requests.get('https://api.weather.yandex.ru/v2/forecast?', 
                            params=params, 
                            headers={"X-Yandex-API-Key":"286f86aa-31e0-4175-97a0-0b58da7ee629"})
    response=response.json()
    forecast_list=[]
    #из полученного json выберем только нужные характеристики: температуру, иконку погоды, описание погоды (condition)
    for i in range(len(response['forecasts'])):
        date=response['forecasts'][i]['date']
        temp=response['forecasts'][i]['parts']['day_short']['temp']
        icon=response['forecasts'][i]['parts']['day_short']['icon']
        condition=response['forecasts'][i]['parts']['day_short']['condition']
        new_observation={'date':date,
                         'temp':temp,
                         'icon':icon,
                         'condition':condition}
        forecast_list.append(new_observation)
    #создадим датасет с прогнозом для каждого города
    forecast=pd.DataFrame(forecast_list)
    #оставим в датасете только промежуток дат, который ввел пользователь
    forecast['date'] =pd.to_datetime(forecast['date']).dt.date   
    mask = (forecast['date'] >= start_date) & (forecast['date'] <= end_date)
    forecast = forecast.loc[mask].reset_index()
    final=''
    
    #в этом блоке прописаны условия, при которых формируем вывод о погоде:
    #для пасмурной погоды:
    if (forecast['condition']=='overcast').sum())/len(forecast) > 0.5:
        final = 'будет пасмурно...'
    #для дождливой погоды:
    if ((forecast['condition']=='drizzle').sum()+
        (forecast['condition']=='light-rain').sum()+
       (forecast['condition']=='rain').sum()+
       (forecast['condition']=='moderate_rain').sum()+
       (forecast['condition']=='heavy-rain').sum()+
        (forecast['condition']=='hail').sum()+
       (forecast['condition']=='thunderstorm').sum()+
       (forecast['condition']=='thunderstorm-with-rain').sum()+
        (forecast['condition']=='thunderstorm-with-hail').sum())/len(forecast) > 0.5:
        final = 'будет дождливо('
    
    #если будет дождливая погода и грозы
    if (((forecast['condition']=='drizzle').sum()+
        (forecast['condition']=='light-rain').sum()+
        (forecast['condition']=='rain').sum()+
        (forecast['condition']=='moderate_rain').sum()+
        (forecast['condition']=='heavy-rain').sum()+
        (forecast['condition']=='hail').sum()+
        (forecast['condition']=='thunderstorm').sum()+
        (forecast['condition']=='thunderstorm-with-rain').sum()+
        (forecast['condition']=='thunderstorm-with-hail').sum())/len(forecast) > 0.5
    and 
    (((forecast['condition']=='thunderstorm').sum()+
      (forecast['condition']=='thunderstorm-with-rain').sum()+
      (forecast['condition']=='thunderstorm-with-hail').sum())/len(forecast) > 0.28)):
        final = 'будут дожди и грозы!'
        
    #если будет пасмурно и осадки    
    if (((forecast['condition']=='drizzle').sum()+
        (forecast['condition']=='light-rain').sum()+
        (forecast['condition']=='rain').sum()+
        (forecast['condition']=='moderate_rain').sum()+
        (forecast['condition']=='heavy-rain').sum()+
        (forecast['condition']=='hail').sum()+
        (forecast['condition']=='thunderstorm').sum()+
        (forecast['condition']=='thunderstorm-with-rain').sum()+
        (forecast['condition']=='thunderstorm-with-hail').sum()+
        ((forecast['condition']=='light-snow').sum()+
        (forecast['condition']=='snow').sum()+
       (forecast['condition']=='snow-showers').sum())/len(forecast) > 0.28
    and
         (((forecast['condition']=='overcast').sum())/len(forecast) > 0.28))):
        final = 'будет пасмурно и осадки'

    #для снежной погоды
    if ((forecast['condition']=='light-snow').sum()+
        (forecast['condition']=='snow').sum()+
       (forecast['condition']=='snow-showers').sum())/len(forecast) > 0.5:
        final = 'будет снежно!'
  
    #для снежной погоды
    if ((forecast['condition']=='wet-snow').sum()/len(forecast) >= 0.114 
    and 
     ((forecast['condition']=='drizzle').sum()+
      (forecast['condition']=='light-rain').sum()+
      (forecast['condition']=='rain').sum()+
      (forecast['condition']=='moderate_rain').sum()+
      (forecast['condition']=='heavy-rain').sum()+
      (forecast['condition']=='hail').sum()+
      (forecast['condition']=='thunderstorm').sum()+
      (forecast['condition']=='thunderstorm-with-rain').sum()+
      (forecast['condition']=='thunderstorm-with-hail').sum())
        /len(forecast) >= 0.28):
            final = 'будут дожди и мокрый снег!'


    if (forecast['condition']=='wet-snow').sum()/len(forecast) > 0.5:
        final = 'будет дождь со снегом...'
    if ((forecast['condition']=='clear').sum()+(forecast['condition']=='partly-cloudy')+(forecast['condition']=='cloudy').sum())/len(forecast) > 0.5:
        final = 'будет солнечно! Ура!)'
    #если погода не подошла ни под одно из условий, скажем, что она переменчивая
    if final=='':
        final='будет переменчивая погода'
    return forecast,final

#это эмодзи, которые по порядку присваиваются ячейке ввода, когда пользователь вводит новый город
emojis = [':desert_island:',':national_park:',':european_castle:',':mountain_cableway:',':ship:',':woman-mountain-biking:',':hut:',':small_airplane:',':canoe:',':clinking_glasses:']
#создаем кнопку, чтобы пользователь мог добавить нужное количество городов, но не больше десяти
input_values=[]
if 'n_rows' not in st.session_state:
    st.session_state.n_rows = 1
for i in range(st.session_state.n_rows):
    city=st.text_input(label=emojis[i], key=i) 
    input_values.append(city)
if st.session_state.n_rows<10:
    add = st.button(label="Добавить еще один город")
if st.session_state.n_rows<10:
    if add:
        st.session_state.n_rows += 1
        st.experimental_rerun()

#создаем кнопки для ввода дат начала и конца путешествия
geolocator = Nominatim(user_agent="Amiran")
today = datetime.date.today()
week_after = today + datetime.timedelta(days=6)
start_date = st.date_input('Выберите дату начала поездки:', today,min_value=today,max_value=week_after)
end_date= st.date_input('Выберите дату возвращения домой:', week_after,min_value=today,max_value=week_after)


period=(end_date-start_date).days+1
m = st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #0099ff;
    color:#ffffff;
}
div.stButton > button:hover {
    background-color: #ff6347;
    color:#ffffff;
    }
</style>""", unsafe_allow_html=True)

button = st.button('Получить прогноз!')

table=[]
itog=[]
text=[]
names=[]
no_weather=[]
images=[]
sun=0

#когда пользователь нажимает на кнопку, включается спиннер на 10 секунд, потом летят шарики
if button:
    with st.spinner('Узнаём погоду'):
        time.sleep(10)
        st.balloons()
    #если дата начала раньше даты конца, то есть пользователь ввел ее правильно, то начинаем обрабатывать запрос
    if start_date < end_date:
        for i in range(len(input_values)):
            #если поле не пустое:
            if input_values[i]!='':
                #если геолокатор может закодировать этот город
                if geolocator.geocode(input_values[i]):
                    #получаем прогноз - в отдельные списки помещаем таблицу и вывод (forecast в table, final - в append)
                    vse=get_weather(input_values[i],start_date,end_date)
                    table.append(vse[0])
                    itog.append(vse[1])
                    names.append(input_values[i])
                else:
                    #занесем в отдельный список названия городов, которые геолокатор не может закодировать
                    vyvod=input_values[i]
                    no_weather.append(vyvod)
                    input_values[i]=''

        for i in range(len(itog)):
            #составим сообщения для пользователей
            text.append(':exclamation:В городе ')   
        for i in range(len(itog)):
            #если во время путешествия в каком-то будет солнечная погода, выведем это значение первым
            if itog[i]=='будет солнечно!)':
                itog.insert(0,itog.pop(i))
                table.insert(0,forecast.pop(i))
            try:
                #если в трех городах подряд будет определенное описание погоды, 
                #во втором добавим 'тоже'-например, 'тоже будет пасмурно'
                #в третьем в начале добавим 'и': 'и в городе Архангельск будет солнечно!)'
                if itog[i]==itog[i+1] and itog[i+1]==itog[i+2]:
                    itog[i+1]='тоже '+itog[i]
                    text[i+2]='И в городе '
            except IndexError:
                pass
            #если одинаковая погода будет только в двух городах подряд, то добавим 'тоже' к описанию погоды во втором городе
            try:
                if itog[i]==itog[i+1]:
                    itog[i+1]='тоже '+itog[i]
            except IndexError:
                pass
        #для каждого города создадим стримлит-контейнер
        for city in range(len(itog)):
            with st.container():
                #напишем вывод по погоде в городе на заданный период
                st.subheader(text[city]+names[city].capitalize()+' '+itog[city])
                #создадим метку, которая меняется, если встретился солнечный прогноз 
                if itog[i]=='будет солнечно! Ура!)':
                    sun=1
                #чтобы отобразить погоду в городе на каждый день, создадим стримлит-колонны
                weather_for_days=st.columns(period)
                #для каждого дня разместим иконку - получим ее по методу яндекс api через столбец 'icon' в table
                images=[]
                for day in range(len(table[i])):
                    with weather_for_days[day]:
                        #для каждого дня покажем дату, иконку и температуру:
                        st.write(table[city]['date'][day].strftime('%d.%m'))
                        pic=(f"{'https://yastatic.net/weather/i/icons/funky/dark/'}{table[city]['icon'][day]}{'.svg'}")
                        st.image(pic, use_column_width=True)
                        st.metric(label='',value=(f"{table[city]['temp'][day]} °C"))
                #после прогноза для города разместим иконку яндекс погоды - по требованию яндекс api
                st.image('https://i.ibb.co/ZLZSDKx/image.png',width=250)
        #в конце отметим города, для которых не создался прогноз. это может случиться, если пользователь ввел случайные символы.
        for i in no_weather:
            st.error('Для города '+i+' погода не нашлась',icon="✈️")
        #если солнечный прогноз не встретился, предложим пользователю посмотреть погоду для других городов:
        if sun!=1:
            st.info('Для получения более солнечного прогноза попробуйте ввести новые города', icon='😎')
         
    #выведем предупреждение, если дата конца путешествия раньше, чем дата начала
    else:
        st.error('Пожалуйста, пусть конец вашего путешествия будет позже, чем начало')




    


