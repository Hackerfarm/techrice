# techrice

## API routes

### Site routes
GET /sites

GET /site/<int:site_id>

DELETE /site/<int:site_id> (auth required)

POST /site (auth required, form params: 'name')

GET /nodes (query args: 'site_id')

GET /node/<int:node_id>

DELETE /node/<int:node_id> (auth required)

POST /node (auth required, form params: 'name', 'site_id', 'longitude', 'latitude')

GET /sensor (query args: 'node_id')

GET /sensor/<int:sensor_id>

DELETE /sensor/<int:sensor_id> (auth required)

POST /sensor (auth required, form params: 'node_id', 'sensortype_id')

GET /sensortype/<int:sensortype_id>
DELETE /sensortype/<int:sensortype_id> (auth required)
POST /sensortype (auth required, form params: 'name', 'unit')

GET /readings (query args: 'sensor_id')
POST /readings (auth required, query args: 'format=compact|json', form params: 'readings')

GET /reading/<int:reading_id>
DELETE /reading/<int:reading_id> (auth required)
POST /reading (auth required, form params: 'sensor_id', 'value', 'timestamp')
