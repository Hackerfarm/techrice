# techrice

## API resource routes

### Sites
A site is a logical grouping of nodes.
*   GET /sites
*   GET /site/<int:site_id>
*   DELETE /site/<int:site_id> (auth required)
*   POST /site (auth required, form params: 'name')

### Nodes
A node is a physical piece of hardware/board. A node must belong to one and only one site.
*   GET /nodes (query args: 'site_id')
*   GET /node/<int:node_id>
*   DELETE /node/<int:node_id> (auth required)
*   POST /node (auth required, form params: 'name', 'site_id', 'longitude', 'latitude')

### Sensors
A node can have any positive number of sensors. Any sensor must belong to a node. Each sensor must also belong to one and only one sensor type. Solar panel voltage and battery voltage are also considered as sensors.
*   GET /sensor (query args: 'node_id')
*   GET /sensor/<int:sensor_id>
*   DELETE /sensor/<int:sensor_id> (auth required)
*   POST /sensor (auth required, form params: 'node_id', 'sensortype_id')


### SensorTypes
The same physical phenomenon can be measured by many different types of sensors. The API forces you to assign each sensor to a sensor type (or create a new one if you need to). 
*   GET /sensortype/<int:sensortype_id>
*   DELETE /sensortype/<int:sensortype_id> (auth required)
*   POST /sensortype (auth required, form params: 'name', 'unit')

### Readings
Readings represent actual sensor data. A reading must belong to one and only one sensor.
*   GET /readings (query args: 'sensor_id')
*   POST /readings (auth required, query args: 'format=compact|json', form params: 'readings')
*   GET /reading/<int:reading_id>
*   DELETE /reading/<int:reading_id> (auth required)
*   POST /reading (auth required, form params: 'sensor_id', 'value', 'timestamp')

## API other routes
### POST /seed/node/techrice (auth required)
Creates a new techrice node and returns
1. node JSON representation
2. C code that must be pasted into the node sketch

### /utils/node_header/<int:node_id>
Returns a dict {"header": escaped string of structs and constants used in the node embedded code}
