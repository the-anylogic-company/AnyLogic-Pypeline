import numpy as np
from tensorflow.keras.models import load_model
from collections import deque


class HospitalPredictor:
    ''' A simple class to easily query the neural networks from inside AnyLogic using Pypeline '''
    def __init__(self):
        # load both policies
        self.los_model = load_model("los_model.h5")
        self.rate_model = load_model("rate_model.h5")
        
        # initialize queue with random values to feed into neural network model
        # note 1: these values will be in range [-1, 1]
        # note 2: the model was trained to predict the next value from last *6*
        # (each sample represents the hourly arrive rate for a 4 hour time span)
        init_values = np.random.random((6,))*2-1
        self.last_rates_queue = deque(init_values, maxlen=6)


    def predict_los(self, patient_data):
        ''' Given the (1, 24) array of patient data, predict the length of stay (days) '''
        
        # convert default list to numpy array
        patient_array = np.array(patient_data)
        
        # query the neural network for the length of stay
        prediction = self.los_model.predict(patient_array)
        return prediction[0][0]


    def predict_rate(self):
        ''' Use the last 6 predicted values (1 day's worth) to predict the next arrival rate (per hour) '''

        # convert deque to numpy array and reshape to proper format
        last_rates_array = np.array(self.last_rates_queue).reshape(1, 6, 1)

        # query the neural network for the length of stay
        prediction = self.rate_model.predict(last_rates_array)

        # store in a variable to avoid re-typing
        predicted_value = prediction[0][0]

        # update deque with latest value (for next prediction)
        self.last_rates_queue.append(predicted_value)

        # original data was scaled to [-1, 1]
        # scale back using pre-calculated formula (based on original ranges)
        unscaled_value = (predicted_value * 207) / 40 + 5.525
        return unscaled_value
