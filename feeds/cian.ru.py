#-*- coding: utf8 -*-

__author__ = "ardevelop"


import urllib

import lxml.etree


url = "http://temp.luxdom.ru/cian/luxdom.xml"
xsd = "https://github.com/difiz/maindoor-public/blob/master/feeds/schema.xsd"


def lxml_dumps(src, root_name="node"):
    def populate_element(element, d):
        for k, v in d.iteritems():
            if type(v) is dict:
                child = lxml.etree.Element(k)
                populate_element(child, v)
                element.append(child)
            elif type(v) is list:
                child = lxml.etree.Element(k)
                element.append(child)
                for item in v:
                    populate_element(child, item)
            else:
                if v is not None:
                    child = lxml.etree.Element(k)
                    if isinstance(v, unicode):
                        child.text = v
                    else:
                        child.text = str(v).decode("utf8")
                    element.append(child)

    root = lxml.etree.Element(root_name)
    populate_element(root, src)

    return lxml.etree.tostring(root)


xml_stream = urllib.urlopen(url)
offers = lxml.etree.fromstring(xml_stream.read())
out = open("/tmp/sample.xml", "w+")
out.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
out.write("<feed xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"%s\">" % xsd)
out.write("<date>2014-01-01</date>")
out.write("<offers>")


for i, offer in enumerate(offers):
    remote_id = offer.find("id").text
    _address = offer.find("address")
    _rooms_num = offer.find("rooms_num")
    _price = offer.find("price")
    _floor = offer.find("floor")
    _note = offer.find("note")
    _area = offer.find("area")
    _options = offer.find("options")
    _separated_bathrooms = _options.attrib.get("su_r")
    _combined_bathrooms = _options.attrib.get("su_s")
    _floors = _floor.attrib.get("total")

    offer_type = "sell"
    offer_price_value = int(_price.text)
    offer_price_unit = _price.attrib["currency"].lower()

    property_type = "apartment:flat"

    property_title_ru = u"Квартира: %s, %s, %s" % (_address.attrib.get("locality"), _address.attrib.get("street"),
                                                   _address.attrib.get("house_str"))
    property_title_en = "Flat"

    property_article_ru = _note.text

    property_images = [element.text for element in offer.getchildren() if element.tag == "photo"]

    property_properties_area_gross = float(_area.attrib["total"].replace(",", "."))
    property_properties_area_living = float(_area.attrib["living"].replace(",", "."))
    property_properties_area_kitchen = float(_area.attrib["kitchen"].replace(",", "."))

    property_properties_rooms_living = int(_rooms_num.text) if _rooms_num.text else None
    property_properties_rooms_bathrooms_bathrooms = bb = int(_separated_bathrooms) if _separated_bathrooms else None
    property_properties_rooms_bathrooms_combined = bc = int(_combined_bathrooms) if _combined_bathrooms else None
    property_properties_rooms_bathrooms_total = ((bb or 0) + (bc or 0)) or None

    if property_properties_rooms_bathrooms_bathrooms == 0:
        property_properties_rooms_bathrooms_bathrooms = None

    if property_properties_rooms_bathrooms_combined == 0:
        property_properties_rooms_bathrooms_combined = None

    property_properties_building_floor = int(_floor.text) if _floor.text else None
    property_properties_building_floors = int(_floors) if _floors else None

    property_tags = []
    if _options.attrib.get("balcon"):
        property_tags.append("balcony")

    out.write(lxml_dumps({
        "identifiers": {
            "remote": remote_id
        },
        "type": offer_type,
        "price": {
            "value": offer_price_value,
            "unit": offer_price_unit
        },
        "property": {
            "type": property_type,
            "location": {
                "latitude": 55.761702090644896,
                "longitude": 37.606201171875
            },
            "title": {
                "ru": property_title_ru,
                "en": property_title_en
            },
            "article": {
                "ru": property_article_ru,
            },
            "images": [{"image": image} for image in property_images],
            "properties": {
                "area": {
                    "gross": property_properties_area_gross,
                    "living": property_properties_area_living,
                    "kitchen": property_properties_area_kitchen,
                    "land": None
                },
                "rooms": {
                    "total": None,
                    "living": property_properties_rooms_living,
                    "kitchens": None,
                    "bathrooms": {
                        "total": property_properties_rooms_bathrooms_total,
                        "bathrooms": property_properties_rooms_bathrooms_bathrooms,
                        "toilets": None,
                        "combined": property_properties_rooms_bathrooms_combined
                    }
                },
                "building": {
                    "status": None,
                    "material": None,
                    "year": None,
                    "floor": property_properties_building_floor,
                    "floors": property_properties_building_floors
                }
            },
            "tags": [{"tag": image} for image in property_tags],
        }
    }, "offer"))


out.write("</offers>")
out.write("</feed>")
out.close()