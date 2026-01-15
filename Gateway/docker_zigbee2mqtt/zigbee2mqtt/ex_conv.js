const fz = require('zigbee-herdsman-converters/converters/fromZigbee');
const exposes = require('zigbee-herdsman-converters/lib/exposes');
const e = exposes.presets;

const fzLocal = {
    cluster: 'msTemperatureMeasurement',
    type: ['attributeReport', 'readResponse'],
    convert: (model, msg, publish, options, meta) => {
    
        if (msg.data['measuredValue'] == null) return;
    
        const val = parseFloat(msg.data['measuredValue']) / 100.0;
       
        switch (msg.endpoint.ID) {
            
            case 1: return { temperature: val };
            case 2: return { humidity: val };
            case 3: return { vibration: val };
            case 4: return { pm1: val };
            case 5: return { pm25: val };
            case 6: return { pm10: val };
            default: return null;
        }
    },
};

const definition = {
    zigbeeModel: ['Sensor_Lab_V7_NoCO2'], // Tem de corresponder ao código Arduino
    model: 'Sensor_Lab_V7_NoCO2',
    vendor: 'DIY',
    description: 'Sensor_Lab_V7_NoCO2 (PM + Contagem 0.3/0.5)',
   
    fromZigbee: [fzLocal],
    toZigbee: [],
   
    exposes: [
        e.temperature(),
        e.humidity(),
        e.numeric('vibration', 'vibs').withDescription('Vibração'),
        e.numeric('pm25', 'µg/m³').withDescription('PM2.5 Concentração'),
        e.numeric('pm1', 'µg/m³').withDescription('PM1.0 Concentração'),
        e.numeric('pm10', 'µg/m³').withDescription('PM10 Concentração'),
    ],

    meta: {
        multiEndpoint: true,
    },
};

module.exports = definition;
