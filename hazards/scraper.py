import pathlib
from fastkml import kml
import requests
import lxml.html


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"


def get_parkname(string):
    delim = "\n"
    return string.split(delim)[0]


def get_link(string):
    components = string.split()
    for char in components:
        if char.startswith("href"):
            link = char[6:-5]
    return link


def parse_kml(max=5):
    result = {}
    filename = pathlib.Path(__file__).parent / "data/nps-nightsky-monitoring.kml"
    with open(filename) as myfile:
        doc = myfile.read()

    k = kml.KML()
    k.from_string(doc.encode("utf-8"))
    features = list(k.features())
    placemarks = list(features[0].features())

    for monitoring_loc in placemarks:
        if len(result) == max:
            break
        park_name = get_parkname(monitoring_loc.description)
        link = get_link(monitoring_loc.description)
        if park_name not in result:
            result[park_name] = []
        result[park_name].append(link)

    return result
        

def get_light_data():
    links = parse_kml()
    for park in links:
        observations = park.values
        for observation in observations:
            response = requests.get(observation, headers={"User-Agent": USER_AGENT})
            root = lxml.html.fromstring(response.text)
            table = root.xpath('//table[@class="MsoTableGrid"]')[2]
            row = table.xpath('//tr')[34].text_content()