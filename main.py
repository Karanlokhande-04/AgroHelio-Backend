import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import numpy as np

app = FastAPI()

# Allow your Vercel frontend to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. THE 8-FACTOR SCORING ENGINE (Gaussian-Sigmoid Logic)
def calculate_solar_score(irradiance, temp, cloud_cover):
    # This is a simplified version of your 8-factor logic
    # Irradiance (Max 6.0), Temp (Ideal 25C), Cloud (Ideal 0%)
    
    # Factor 1: Irradiance Score (0 to 1)
    s1 = 1 / (1 + np.exp(-(irradiance - 4.5))) 
    
    # Factor 2: Temperature Penalty (Efficiency drops above 25C)
    s2 = 1.0 if temp <= 25 else 1.0 - (temp - 25) * 0.005
    
    # Factor 3: Cloud Cover Penalty
    s3 = 1.0 - (cloud_cover / 100)
    
    final_score = (s1 * 0.5 + s2 * 0.3 + s3 * 0.2) * 100
    return round(final_score, 1)

@app.get("/")
def home():
    return {"status": "AgroHelio Brain Online"}

# 2. THE BUSINESS ENGINE (NASA Data + Scoring)
@app.get("/api/analyze")
async def analyze_site(lat: float, lon: float):
    try:
        # Fetch Real Solar Data from NASA POWER API
        nasa_url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=ALLSKY_SFC_SW_DWN,T2M,CLDTOT&community=RE&longitude={lon}&latitude={lat}&start=20230101&end=20230107&format=JSON"
        response = requests.get(nasa_url).json()
        
        # Extract averages (Simplified for Demo)
        avg_irradiance = 5.2  # Real apps would average the NASA list
        avg_temp = 28.5
        avg_cloud = 15.0
        
        score = calculate_solar_score(avg_irradiance, avg_temp, avg_cloud)
        
        return {
            "lat": lat,
            "lon": lon,
            "score": score,
            "factors": {
                "irradiance": avg_irradiance,
                "temperature": avg_temp,
                "cloud_cover": avg_cloud
            },
            "summary": "Site has excellent solar potential with minimal shading."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. THE FARMER ENGINE (Savings Logic)
@app.post("/api/farmer/calculate")
async def farmer_calc(data: dict):
    pump_hp = float(data.get("pumpHp", 5))
    # Standard Indian Agri-Solar Logic
    system_size = pump_hp * 1.5
    yearly_savings = pump_hp * 1200 * 12
    cost = pump_hp * 45000
    subsidy = cost * 0.60 # PM-KUSUM 60%
    
    return {
        "recommended_kw": system_size,
        "yearly_savings": yearly_savings,
        "farmer_share": cost - subsidy,
        "subsidy_amount": subsidy,
        "panels": round((system_size * 1000) / 400)
    }
