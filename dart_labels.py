import json

import attr

from adq_labels import AdqLabels


@attr.s(slots=True, frozen=False)
class DartLabels:
    twconverted = attr.ib(default=None, validator=attr.validators.instance_of(str))
    mode = attr.ib(default="annotation", validator=attr.validators.instance_of(str))
    template_version = attr.ib(default="0.1", validator=attr.validators.instance_of(str))
    images = attr.ib(default=[], validator=attr.validators.instance_of(list))

    # {
    #     "mode": "annotation",
    #     "twconverted": "96E7D8C8-44E4-4055-8487-85B3208E51A2",
    #     "template_version": "0.1",
    #     "images": [

    def __iter__(self):
        yield from {
            "twconverted": self.twconverted,
            "mode": self.mode,
            "template_version": self.template_version,
            "images": self.images
        }.items()

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)

    def to_json(self):
        return {
            "twconverted": self.twconverted,
            "mode": self.mode,
            "template_version": self.template_version,
            "images": self.images
        }

    @staticmethod
    def from_json(json_dict):
        return DartLabels(
            twconverted=json_dict['twconverted'],
            mode=json_dict['mode'],
            template_version=json_dict['template_version'],
            images=json_dict['images']
        )

    @staticmethod
    def from_adq_labels(adq_labels: AdqLabels):
        return DartLabels(
            twconverted=adq_labels.twconverted,
            mode=adq_labels.mode,
            template_version=adq_labels.template_version,
            images=[DartLabels.Image.from_adq_image(image) for image in adq_labels.images]
        )

    @attr.s(slots=True, frozen=False)
    class Image:
        image_id = attr.ib(validator=attr.validators.instance_of(str))
        name = attr.ib(validator=attr.validators.instance_of(str))
        width = attr.ib(validator=attr.validators.instance_of(int))
        height = attr.ib(validator=attr.validators.instance_of(int))
        objects = attr.ib(default=[], validator=attr.validators.instance_of(list))

        # {
        #     "image_id": "0",
        #     "name": "WIN_20220913_14_01_16_Pro.jpg",
        #     "width": "3840",
        #     "height": "2160",
        #     "objects": [
        #
        # {
        #
        def __iter__(self):
            yield from {
                "image_id": self.image_id,
                "name": self.name,
                "width": self.width,
                "height": self.height,
                "objects": self.objects
            }.items()

        def __str__(self):
            return json.dumps(dict(self), ensure_ascii=False)

        def to_json(self):
            return {
                "image_id": self.image_id,
                "name": self.name,
                "width": self.width,
                "height": self.height,
                "objects": self.objects
            }

        @staticmethod
        def from_json(json_dict):
            return DartLabels.Image(
                image_id=json_dict['image_id'],
                name=json_dict['name'],
                width=json_dict['width'],
                height=json_dict['height'],
                objects=json_dict['objects']
            )

        @staticmethod
        def from_adq_image(adq_image: AdqLabels.Image):
            return DartLabels.Image(
                image_id=adq_image.image_id,
                name=adq_image.name,
                width=int(adq_image.width),
                height=int(adq_image.height),
                objects=[DartLabels.Object.from_adq_object(obj) for obj in adq_image.objects])

    @attr.s(slots=True, frozen=False)
    class Object:
        label = attr.ib(validator=attr.validators.instance_of(str))
        type = attr.ib(validator=attr.validators.instance_of(str))
        occluded = attr.ib(validator=attr.validators.instance_of(str))
        z_order = attr.ib(validator=attr.validators.instance_of(str))
        group_id = attr.ib(validator=attr.validators.instance_of(str))
        points = attr.ib(validator=attr.validators.instance_of(list))
        # a list of attribute_name and attribute_value pairs
        attributes = attr.ib(default=[], validator=attr.validators.instance_of(dict))
        verification_result = attr.ib(default=None)

        # {
        #   "label": "4FM",
        #   "type": "box",
        #   "occluded": "0",
        #   "z_order": "7",
        #   "group_id": "",
        #   "position": "387.50000000, 195.90039062, 2034.10156250, 1256.60036621",
        #   "attributes": [],
        #   "verification_result": {
        #     "error_code": "DVE_RANGE",
        #     "comment": ""
        #   }
        # },
        # {
        #   "label": "UNTAG",
        #   "type": "box",
        #   "position": "1730, 1502, 1740, 1512",
        #   "occluded": "0",
        #   "z_order": "1",
        #   "verification_result": {
        #     "error_code": "DVE_UNTAG",
        #     "comment": ""
        #   }
        # }

        def __iter__(self):
            yield from {
                "label": self.label,
                "type": self.type,
                "occluded": self.occluded,
                "z_order": self.z_order,
                "group_id": self.group_id,
                "points": self.points,
                "attributes": self.attributes,
                "verification_result": self.verification_result,
            }.items()

        def __str__(self):
            return json.dumps(dict(self), ensure_ascii=False)

        def to_json(self):
            return {
                "label": self.label,
                "type": self.type,
                "occluded": self.occluded,
                "z_order": self.z_order,
                "group_id": self.group_id,
                "points": self.points,
                "attributes": self.attributes,
                "verification_result": self.verification_result,
            }

        @staticmethod
        def from_json(json_dict):
            return DartLabels.Object(label=json_dict['label'],
                                     type=json_dict['type'],
                                     occluded=json_dict['occluded'],
                                     z_order=json_dict['z_order'],
                                     group_id=json_dict['group_id'],
                                     points=json_dict['points'],
                                     attributes=json_dict['attributes'],
                                     verification_result=json_dict['verification_result'])

        @staticmethod
        def from_adq_object(adq_object: AdqLabels.Object):
            points_str = adq_object.position.split()
            points = [float(point.replace(",", "")) for point in points_str]

            attributes = dict()
            for attribute in adq_object.attributes:
                key = attribute["attribute_name"]
                value = attribute["attribute_value"]
                attributes[key] = value

            return DartLabels.Object(label=adq_object.label,
                                     type=adq_object.type,
                                     occluded=adq_object.occluded,
                                     z_order=adq_object.z_order,
                                     group_id=adq_object.group_id,
                                     points=points,
                                     attributes=attributes,
                                     verification_result=adq_object.verification_result)