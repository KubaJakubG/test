from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import pickle
import io
import base64


application = Flask(__name__)

# Load the SARIMAX model
model_filename = 'sarimax_model.pkl'
with open(model_filename, 'rb') as file:
    loaded_model = pickle.load(file)

@application.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        chart = display_chart(start_date, end_date)
        return render_template('index.html', chart=chart)
    return render_template('index.html', chart=None)

def display_chart(start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Assuming the model is already fitted and loaded
    forecast_steps = 6 * 12  # Adjust this as needed
    forecast = loaded_model.get_forecast(steps=forecast_steps)

    # Getting the forecast mean
    forecast_mean = forecast.predicted_mean
    df = pd.DataFrame(forecast_mean).reset_index().rename(columns={'index': 'Date'})
    df['Date'] = pd.to_datetime(df['Date'])

    # Filtering data based on the provided dates
    df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    # Create a plot
    plt.figure(figsize=(15, 10))
    sns.barplot(x=df['Date'].dt.month, y=df['predicted_mean'], hue=df['Date'].dt.year, dodge=False)
    plt.title('Forecasted Emissions')
    plt.xlabel('Month')
    plt.ylabel('Predicted Mean (µg/m³)')

    # Adding text on top of each bar
    for i in plt.gca().patches:
        plt.text(i.get_x() + i.get_width() / 2, i.get_height(), 
                 f'{i.get_height():.2f}', ha='center', va='bottom')

    # Convert plot to PNG image
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    plt.close()  # Close the figure to prevent it from displaying here
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return plot_url

if __name__ == '__main__':
    application.run(debug=True)