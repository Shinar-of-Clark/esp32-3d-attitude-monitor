#include <Arduino.h>
#include <Wire.h>
#include <math.h>
#include "MHEtLiveLIS3DH.h"

LIS3DH myIMU(I2C_MODE, 0x18);

void setup() {
    Serial.begin(115200);
    Wire.begin(21, 22);
    
    if (myIMU.begin() == IMU_SUCCESS) {
        myIMU.writeRegister(LIS3DH_TEMP_CFG_REG, 0xC0); 
    }
}

void loop() {
    float ax = myIMU.readFloatAccelX();
    float ay = myIMU.readFloatAccelY();
    float az = myIMU.readFloatAccelZ();

    // 1. Resultant acceleration
    float totalAcc = sqrt(ax * ax + ay * ay + az * az);
    if (totalAcc < 0.01) totalAcc = 1.0; // Prevent division by zero

    // 2. Total tilt angle (Tilt)
    float horizontalMag = sqrt(ax * ax + ay * ay);
    float tilt = atan2(horizontalMag, az) * 180.0 / PI;

    // 3. Euler angles (pitch/roll)
    float pitch = atan2(ax, az) * 180.0 / PI;
    float roll = atan2(ay, az) * 180.0 / PI;

    // 4. Temperature calibration
    uint16_t tempRaw = myIMU.read10bitADC3();
    float tempC = 25.0 + (tempRaw - 325);

    // --- Key: Output only comma-separated numbers for easy Python reception ---
    // Order: Total Tilt, Pitch, Roll, Resultant Acc, Temp
    Serial.printf("%.2f,%.2f,%.2f,%.2f,%.1f\n", tilt, pitch, roll, totalAcc, tempC);

    delay(50); // Increase refresh rate for smoother 3D animation
}