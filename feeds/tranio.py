#-*- coding: utf8 -*-

__author__ = "ardevelop"


import urllib
import argparse

import lxml.etree


url = "http://xml.jcat.ru/export/maindoor/"
xsd = "https://github.com/difiz/maindoor-public/blob/master/feeds/schema.xsd"

offer_types = {
    "s": "sell",
    "r": "rent"
}
offer_price_units = {
    "e": "eur",
    "u": "usd",
    "r": "rub",
    "g": "gbp"
}
property_types = {
    "a": ("house:cottage", "Котедж", "Cottage"),
    "b": ("house:villa", "Вилла", "Villa"),
    "c": ("house", "Дом в городе", "Urban house"),
    "d": ("apartment:flat", "Квартира", "Flat"),
    "x": ("apartment:flat", "Новостройка", "New flat"),
    "e": ("house:townhouse", "Таунхаус", "Townhouse"),
    "f": ("castle", "Замок", "Castle"),
    "g": ("house:manor", "Поместье", "Manor"),
    "h": ("house:manor", "Особняк", "Mansion"),
    "i": ("commercial", "Коммерческий центр", "Commercial center"),
    "l": ("commercial", "Развлекательный комплекс", "Entertaiment complex"),
    "j": ("commercial", "Офис", "Office"),
    "k": ("commercial:hotel", "Отель", "Hotel"),
    "m": ("commercial", "Спорткомплекс", "Sports Complex"),
    "q": ("commercial", "Доходный дом", "Profitable House"),
    "r": ("commercial", "Магазин", "Store"),
    "t": ("commercial", "Ресторан", "Restaurant"),
    "v": ("commercial", "Склад", "Warehouse"),
    "u": ("commercial", "АЗС", " Gas station"),
    "w": ("commercial", "Инвестиционный проект", "Investment project"),
    "o": ("commercial", "Земельный участок", "Land plot"),
    "p": ("commercial", "Ферма, сельхозугодья", "Farm"),
    "n": ("commercial", "Виноградник", "Vineyard"),
    "y": ("commercial", "Остров", "Island"),
    "s": ("house:chalet", "Шале", "Chalet"),
}

property_properties_building_states = {
    "a": "project",             # Чертежи, финансирование и разрешение
    "b": "construction",        # Выемка грунта и фундамента
    "c": "construction",        # Фундаментные стены, дренаж
    "d": "construction",        # Каркас
    "e": "construction",        # Внешняя отделка
    "f": "construction",        # Внутренняя отделка
    "g": "construction",        # Ландшафт и озеленение
}


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
                    child.text = str(v).decode("utf8")
                    element.append(child)

    root = lxml.etree.Element(root_name)
    populate_element(root, src)

    return lxml.etree.tostring(root)


def get(parent, modifier, *path):
    current = parent
    for tag in path:
        current = current.find(tag)
        if current is None:
            return None

    try:
        return modifier(current.text.encode("utf8"))
    except ValueError:
        return None


xml_stream = urllib.urlopen(url)
root = lxml.etree.fromstring(xml_stream.read())
out = open("/tmp/sample.xml", "w+")
out.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
out.write("<feed xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"%s\">" % xsd)
out.write("<date>2014-01-01</date>")
out.write("<offers>")

for element in root.getchildren():
    if element.tag == "object":
        remote_id = get(element, str, "id")

        offer_type = offer_types.get(get(element, str, "purpose"))
        offer_price_unit = offer_price_units.get(get(element, str, "currency") or "e")
        offer_price_value = get(element, int, "price_sell") or get(element, int, "price_rent")

        property_type, property_type_title_ru, property_type_title_en = property_types.get(get(element, str, "type"))

        property_article_ru = (get(element, str, "description_full") or "").replace("\n", "<br>") + "<br>"

        contact_value = get(element, str, "contact", "lastname")
        if contact_value:
            property_article_ru += "<br>Контактное лицо: %s" % contact_value

        contact_value = get(element, str, "contact", "email")
        if contact_value:
            property_article_ru += "<br>Электронная почта: %s" % contact_value

        contact_value = get(element, str, "contact", "phones", "phone")
        if contact_value:
            property_article_ru += "<br>Телефон: %s" % contact_value

        element_photos = element.find("photos")
        if element_photos is not None:
            property_images = [url.text for url in element_photos.getchildren()]
        else:
            property_images = []

        property_location_latitude = get(element, float, "lat")
        property_location_longitude = get(element, float, "lng")
        property_location_address_ru = get(element, str, "address")

        property_properties_rooms_total = get(element, int, "rooms_total")
        property_properties_rooms_living = get(element, int, "bedrooms")
        property_properties_rooms_bathrooms_bathrooms = bb = get(element, int, "bathrooms")
        property_properties_rooms_bathrooms_toilets = bt = get(element, int, "wc")
        property_properties_rooms_bathrooms_combined = bc = get(element, int, "rooms_combined")
        property_properties_rooms_bathrooms_total = ((bb or 0) + (bt or 0) + (bc or 0)) or None

        property_properties_area_gross = get(element, float, "total_area")
        property_properties_area_living = get(element, float, "area_living")
        property_properties_area_land = get(element, float, "area_land")

        property_properties_building_state = property_properties_building_states.get(get(element,
                                                                                         int, "construction_state"))
        property_properties_building_year = get(element, int, "construction_year")
        property_properties_building_floor = get(element, int, "floor")
        property_properties_building_floors = get(element, int, "floors")

        property_tags = []
        if element.find("parking") is not None:
            property_tags.append("parking")
        if element.find("golf") is not None:
            property_tags.append("golf")
        if element.find("balcony") is not None:
            property_tags.append("balcony")
        if element.find("furnished") is not None:
            property_tags.append("furnished")

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
                    "latitude": property_location_latitude,
                    "longitude": property_location_longitude
                },
                "title": {
                    "ru": " ".join([property_type_title_ru, property_location_address_ru or ""]),
                    "en": property_type_title_en
                },
                "article": {
                    "ru": property_article_ru,
                },
                "images": [{"image": image} for image in property_images],
                "properties": {
                    "area": {
                        "gross": property_properties_area_gross,
                        "living": property_properties_area_living,
                        "kitchen": None,
                        "land": property_properties_area_land
                    },
                    "rooms": {
                        "total": property_properties_rooms_total,
                        "living": property_properties_rooms_living,
                        "kitchens": None,
                        "bathrooms": {
                            "total": property_properties_rooms_bathrooms_total,
                            "bathrooms": property_properties_rooms_bathrooms_bathrooms,
                            "toilets": property_properties_rooms_bathrooms_toilets,
                            "combined": property_properties_rooms_bathrooms_combined
                        }
                    },
                    "building": {
                        "status": property_properties_building_state,
                        "material": None,
                        "year": property_properties_building_year,
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