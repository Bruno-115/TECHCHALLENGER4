from flask import Flask,request,jsonify,Response
from pydantic import  BaseModel, ValidationError
import joblib
import pandas as pd

app = Flask(__name__)


#Carregar a pipeline criada pelo Giovanni
pipeline_path = 'model_data/pipeline.pkl'
with open(pipeline_path, 'rb') as f:
    pipeline = joblib.load(f)


#Criar a classe de entrada
class InputData(BaseModel):
     Gender : str
     Age  : float
     Height : float
     Weight  : float
     family_history : str
     FAVC : str
     FCVC  : float
     NCP  : float
     CAEC : str
     SMOKE : str
     CH2O  : float
     SCC  : str
     FAF : float
     TUE  : float
     CALC  : str
     MTRANS : str
     BMI : float

@app.route("/predict",methods=["POST"])
def predict():
    try:
        input_data = InputData(**request.get_json())
        features = pd.DataFrame([{
            "Gender": input_data.Gender,
            "Age": input_data.Age,
            "Height": input_data.Height,
            "Weight": input_data.Weight,
            "family_history": input_data.family_history,
            "FAVC": input_data.FAVC,
            "FCVC": input_data.FCVC,
            "NCP": input_data.NCP,
            "CAEC": input_data.CAEC,
            "SMOKE": input_data.SMOKE,
            "CH2O": input_data.CH2O,
            "SCC": input_data.SCC,
            "FAF": input_data.FAF,
            "TUE": input_data.TUE,
            "CALC": input_data.CALC,
            "MTRANS": input_data.MTRANS,
            "BMI": input_data.BMI,
        }])
        prediction = pipeline.predict(features)
        status_codes = 200
        status_message = Response(status = status_codes).status
        return jsonify({
            "status":status_message,
            "data": {"prediction": prediction[0]}
        }),status_codes
    except ValidationError as e:
        return jsonify({
            "error": e.errors()
        }), 400

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)