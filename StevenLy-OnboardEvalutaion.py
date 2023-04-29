from datetime import datetime
from sqlite3 import Timestamp
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns 
from dateutil import parser
import os

class __main__:
    T2_df = pd.read_csv("./T2/Telemetry_R00000036_2020-01-08T11.47.38Z.csv")
    T1_df = pd.read_csv("./T1/Telemetry_R00000036_2020-01-08T11.43.21Z.csv")

    #region Plot Telemetry Data
    df = pd.concat([T1_df,T2_df])
    df.drop(["GatewayTime","ArchiveTime","Process", "Asset", "PrimitiveType", "Unit", "GatewayEpochMs", "Measure", "Host"], axis="columns", inplace=True)
    df.to_csv("./Results.csv", index=False)
    
    #convert originTime to dateTime
    df["OriginTime"] = pd.to_datetime(df["OriginTime"])
    
    #region Air Temperature Dataframe
    #dataframe filtered for outside air temps
    AirTemp_df = df[(df["Uri"] == "Ownship/Flight/OutsideAirTemperature")]

    #convert Air temp value to float
    AirTemp_df = AirTemp_df.astype({ "Value": "float"})
    
    #plot and show line graph
    ax = AirTemp_df.plot(x="OriginTime", y="Value", kind="line", title="Air Temperature",  )
    ax.set_xlabel("Time")
    ax.set_ylabel("Celsius")
   # plt.show()
    #endregion
 
    #region Altitude Dataframe
    #dataframe fitlered for altitude above sea level
    SeaLvlAltitude_df = df[(df["Uri"] == "Ownship/Flight/Altitude/AboveSeaLevel")]
    
    #convert Altitude to float
    SeaLvlAltitude_df = SeaLvlAltitude_df.astype({"Value": "float"})
    
    #plot and show line graph
    ax = SeaLvlAltitude_df.plot(x="OriginTime", y="Value", kind="line", title="Altitude Above Sea Level")
    ax.set_xlabel("Time")
    ax.set_ylabel("Feet")
    #plt.show()
    #endregion

    #region Ground Speed Dataframe
    #dataframe filtered for ground speed
    GroundSpeed_df = df[(df["Uri"] == "Ownship/Flight/GroundSpeed/U")]
   
    #convert Altitude to float
    GroundSpeed_df = GroundSpeed_df.astype({"Value": "float"})
    
    #plot and show line graph
    ax = GroundSpeed_df.plot(x="OriginTime", y="Value", kind="line", title="Ground Speed")
    ax.set_xlabel("Time")
    ax.set_ylabel("Feet per Second")
    #plt.show()  
    #endregion

    #region Pitch Nagle Datagframe
    #dataframe filtered for pitch angle
    PitchAngle_df = df[(df["Uri"] == "Ownship/Flight/Pitch/Angle")]

    #convert Altitude to float
    PitchAngle_df = PitchAngle_df.astype({"Value": "float"})
    
    #plot and show line graph
    ax = PitchAngle_df.plot(x="OriginTime", y="Value", kind="line", title="Pitch Angle")
    ax.set_xlabel("Time")
    ax.set_ylabel("Degree")
   
    #endregion
    
    #region Aircraft on ground flag dataframe
    #dataframe filtered for AC on ground flag
    AcOnGround_df = df[(df["Uri"] == "Ownship/Flight/AircraftOnGround")]

    #convert Altitude to float
    AcOnGround_df = AcOnGround_df.astype({"Value": "float"})
    
    #plot and show line graph
    ax = AcOnGround_df.plot(x="OriginTime", y="Value", kind="line", title="Aircraft on Ground Flag")
    ax.set_xlabel("Time")
    ax.set_ylabel("On Ground")
    plt.show()  
    #endregion
    #endregion
    
    
    #Visual Inspection
    #The aircraft is performing a landing because upon inspection of all line graphs created, at 08 11:46 the Altitude, Ground Speed and Aircraft on ground flag indicate that
    # the aircraft has touched the ground. The pitch angle graph also indicates at 08 11:46 the angle was 7 Degrees therefore also performing a touchdown so the nose must be pitched up.
    
    #region Metrics Computation
    
    #get time at touchdown as a timestamp
    timeAtTouchDown = AcOnGround_df.sort_values(by="OriginTime").query("Value == 1").head(1).values[0][1]
    
    #region Avg Airspeed while Ac is in air
    
    #create dataframe for airspeed 
    
    AirSpeed_df = df[(df["Uri"] == "Ownship/Flight/Airspeed/U")]

    #sort dataframe by time
    AirSpeed_df.sort_values(by="OriginTime", inplace=True)
    
    #convert Altitude to float
    AirSpeed_df = AirSpeed_df.astype({"Value": "float"})
    
    #filter for all data points where time is before touchdown and generate the mean
    AvgAirSpeed = AirSpeed_df.loc[AirSpeed_df["OriginTime"] < timeAtTouchDown, "Value"].mean()
    
    print("The average airspeed of the aircraft while in air is " + str(round(AvgAirSpeed, 2)) + " feet per second")
    #endregion
    
    #region Pitch angle at touchdown
    
    #Get pitch angle where time is at touchdown
    PitchAngleAtTouchDown = PitchAngle_df.loc[PitchAngle_df["OriginTime"] == timeAtTouchDown, "Value"]
    
    print("The pitch angle at touch down is " + str(round(PitchAngleAtTouchDown.values[0],2)) + " Degrees")
    
    #endregion
    
    #region Distance travelled on the runway after the touchdown
    
    #Get avg ground speed after touchdown
    GroundSpeed_df.sort_values(by="OriginTime", inplace=True)
    filteredRows = GroundSpeed_df.loc[GroundSpeed_df["OriginTime"] > timeAtTouchDown]
    AvgGrndSpeed = filteredRows["Value"].mean()
    
    #getime of last data point
    lastDataPointsTime = GroundSpeed_df.tail(1)["OriginTime"].values[0]

    #perform arithmetic to get amount of seconds since touch down and last data point
    t1= pd.Timestamp(lastDataPointsTime).replace(tzinfo=None)
    t2= pd.Timestamp(timeAtTouchDown).replace(tzinfo=None)

    difference = t1-t2

    distanceTravelled = AvgGrndSpeed * difference.seconds

    
    print("The distance travelled on the runway after touchdown is " + str(round(distanceTravelled,2)) + " Feet" )
        
    #endregion
    
    #endregion
    

