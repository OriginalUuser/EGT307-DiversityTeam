import numpy as np
import tensorflow as tf
import tempfile

def scaleData(raw_data, weights):
    # Assume raw_data is a list of 10 numbers from your sensor DB
    # raw_data = [450, 455, 460, 458, 462, 465, 470, 468, 472, 475]

    # 1. Convert to a NumPy array
    data_array = np.array(raw_data).reshape(-1, 1)

    # 2. Apply the scaling weights from your 'weights' dictionary
    # Scaled = (Raw * Scale) + Min
    scaled_data = (data_array * weights['scaler_scale']) + weights['scaler_min']

    # 3. Reshape for LSTM input: (Batch, Window, Features)
    current_window = scaled_data.reshape(1, 10, 1)

def makeInference(raw_data, weights, model_binary) -> list:
    with tempfile.NamedTemporaryFile(suffix='.keras', delete=False) as tmp:
        tmp.write(bytes(model_binary)) 
        tmp_path = tmp.name

        # Load model
        model = tf.keras.models.load_model(tmp_path)

        previous_data = scaleData(raw_data, weights)

        current_window = previous_data # (Batch Size, Window Size, Features) Shape: (1, 10, 1)
                
        all_real_predictions= []

        for i in range(24): # We loop 24 times to predict 24 hours
            # Run Prediction
            prediction_scaled = model.predict(current_window)
            
            # Revert scaling to get real values
            # Real Value = (Scaled Value - Scaler Min) / Scaler Scale
            real_prediction = (prediction_scaled - weights['scaler_min']) / weights['scaler_scale']
            all_real_predictions.append(real_prediction[0, 0]) # Store this in a list
            # print(f"Predicted Value: {real_prediction[0][0]}")

            # Update the window
            #Remove the oldest hour (index 0) and add the new prediction at the end
            new_prediction_reshaped = prediction_scaled.reshape(1, 1, 1) # Used scaled prediction
            current_window = np.append(current_window[:, 1:, :], new_prediction_reshaped, axis=1)

    return all_real_predictions
        
