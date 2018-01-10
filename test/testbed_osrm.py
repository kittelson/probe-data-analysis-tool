import osrm

points = [38.856349, -77.377485, 38.8588922, -77.3634152]

client = osrm.Client(host='http://localhost:5000')

response = client.route(coordinates=[[-74.0056, 40.6197], [-74.0034, 40.6333]], overview=osrm.overview.full)

print(response)