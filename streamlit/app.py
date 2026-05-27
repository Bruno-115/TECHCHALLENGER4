import streamlit as st
import requests

#Criando dicionarios para ser usado:

opcoes_agua = {
    1: "🥤 Menos de 1 litro",
    2: "💧 Entre 1 e 2 litros",
    3: "🚰 Mais de 2 litros"
}

opcoes_genero = {
   "Male": "♂️ Masculino",
   "Female": "♀️ Feminino"
}

opcoes_NoToSometimes = {
    1 : "➖ Raramente",
    2 : "🟰 Às vezes",
    3 : "➕ Sempre"
}

opcoes_NoToAlways = {
    'Sometimes' : "🤔 As Vezes",
    'Frequently': "🔄 Frequentemente" ,
    'Always' : "✅ Sempre",
    'no' : "🚫 Não"
}

opcoes_YesOurNo = {
    "yes" : "✅ Sim",
    "no" : "❌ Não"
}

opcoes_NumeroExercicio = {
    0 : "🚫 Nenhuma",
    1 : "🧘️ 1 até  2 vezes por semana",
    2 : "🏃🏻‍♀️ 3 até 4 vezes por semana",
    3 : "🏋 5 vezes ou mais por semana",
}
opcoes_NumeroRefeicao = {
    1 : "𝟙 Uma refeição",
    2 : "❷ Duas refeições",
    3 : "3️ Três refeições",
    4 : "➕ Quatro ou mais refeições"
}

opcoes_TempoEletronico = {
    0 : "⏳ De 0 até 2 horas",
    1 : "⏰ De 3 até 5 horas",
    2 : "🕒 Mais de 5 horas"
}

opcoes_MeioDeTransporte = {
    'Public_Transportation' : "🚌 Transporte Público",
    'Automobile' : "🚗 Carro ",
    'Motorbike' : "🏍️ Moto",
    'Walking' : "🚶 A pé",
    'Bike' : "🚲 Bicicleta"
}

#Apresentação
st.title("Medical Application: Previsão de Obessidade")
st.write("Insira abaixo os valores das variáveis da característica da pessoa:")

#Campos de entrada:
Gender = st.radio("Escolha o genêro da pessoa ", options=list(opcoes_genero.keys()),format_func= lambda x: opcoes_genero[x])

Age = st.slider("Qual a idade da pessoa?", 0, 150, 0)

Height = st.number_input("Qual a altura da pessoa?")

Weight = st.number_input("Qual o peso da pessoa?")

BMI = Weight / (Height ** 2) if Height > 0 else 0

st.write(f"BMI calculado: {BMI:.2f}")

family_history  = st.radio(
    "A pessoa tem histórico familiar de obesidade?",
    options=list(opcoes_YesOurNo.keys()),format_func= lambda x: opcoes_YesOurNo[x]
)

FAVC = st.radio(
    "Essa pessoa consome muito alimento de alta caloria?",
    options= list(opcoes_YesOurNo.keys()), format_func= lambda x: opcoes_YesOurNo[x]
)

FCVC = st.radio(
    "Essa pessoa tem frequência em consumir vegetal?",
    options=list(opcoes_NoToSometimes.keys()), format_func= lambda x: opcoes_NoToSometimes[x]
)

NCP = st.radio(
    "Essa pessoa consome quantas refeições por dia?",
    list(opcoes_NumeroRefeicao.keys()),format_func= lambda x: opcoes_NumeroRefeicao[x]
)

CAEC = st.radio(
    "Essa pessoa consome comida entre refeições?",
    list(opcoes_NoToAlways.keys()),format_func=lambda x : opcoes_NoToAlways[x]
)

SMOKE = st.radio(
    "Essa pessoa fuma?",
    list(opcoes_YesOurNo.keys()),format_func= lambda x : opcoes_YesOurNo[x]
)

CH2O = st.radio(
    "Essa pessoa consome quantos litros de água por dia?",
    options=list(opcoes_agua.keys()),format_func=lambda x: opcoes_agua[x]
)

SCC = st.radio(
    "Essa pessoa monitora o consumo de calorias?",
    list(opcoes_YesOurNo.keys()), format_func= lambda  x : opcoes_YesOurNo[x]
)

FAF = st.radio(
    label="Essa pessoa tem frequência em se exercitar?",
    options=list(opcoes_NumeroExercicio.keys()),format_func= lambda x: opcoes_NumeroExercicio[x]
)

TUE = st.radio(
    "Quanto tempo essa pessoa usa dispositivos eletrônicos",
    list(opcoes_TempoEletronico.keys()),format_func= lambda x: opcoes_TempoEletronico[x]
)

CALC = st.radio(
    "Essa pessoa consome bebida alcoólica?",
    list(opcoes_NoToAlways.keys()),format_func= lambda x: opcoes_NoToAlways[x]
)

MTRANS = st.radio(
    "Qual meio de transporte essa pessoa utiliza?",
    list(opcoes_MeioDeTransporte.keys()),format_func= lambda x: opcoes_MeioDeTransporte[x]
)

# Botão para realizar a predição
# Botão para realizar a predição
if st.button("Verificar"):

    # Preparar os dados para envio à API
    input_data = {
        "Gender": Gender,
        "Age": Age,
        "Height": Height,
        "Weight": Weight,
        "family_history": family_history,
        "FAVC": FAVC,
        "FCVC": FCVC,
        "NCP": NCP,
        "CAEC": CAEC,
        "SMOKE": SMOKE,
        "CH2O": CH2O,
        "SCC": SCC,
        "FAF": FAF,
        "TUE": TUE,
        "CALC": CALC,
        "MTRANS": MTRANS,
        "BMI": BMI
    }

    try:

        response = requests.post(
            "http://api:5000/predict",
            json=input_data,
            timeout=10
        )

        if response.status_code == 200:

            result = response.json()

            st.success(
                f"Essa pessoa é: {result['data']['prediction']}"
            )

        else:
            st.error(
                f"Erro da API: {response.status_code}"
            )

    except requests.exceptions.ConnectionError:
        st.error("Não foi possível conectar na API.")

    except requests.exceptions.Timeout:
        st.error("A API demorou para responder.")

    except Exception as e:
        st.error(f"Erro inesperado: {e}")