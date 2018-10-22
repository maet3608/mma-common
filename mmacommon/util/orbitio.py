"""
.. module:: orbit
   :synopsis: Methods to handle IO in Orbit workers.
"""

import json


class OrbitIO(object):
    """
    Encapsulates parsing and construction of JSON/dictionary data structures
    that are used for communication between Orbit workers. It ensures that
    input and output data match the schema definition in `registration.json`
    and simplifies data access through data paths, e.g.

    .. code:: python

      >>> in_data = {'data': {'image':'data:image,/9j/4SXNRFABRQB//Z'}}
      >>> io = OrbitIO(in_data)
      >>> io.read('data/image')
      'data:image,/9j/4SXNRFABRQB//Z'

      >>> io.write('result/data/grade', 42)
      >>> io.write('result/data/label', 'grade')
      >>> io.response()
      {'result': {'data': {'grade': 42, 'label': 'grade'}}}
    """

    PATH_SEPARATOR = '/'
    GEO_TYPES = {'Point', 'LineString', 'Polygon', 'MultiPoint',
                 'MultiLineString', 'MultiPolygon'}

    def __init__(self, in_data, logger=None):
        """
        Create IO object for given input data.

        :param dict in_data: Dictionary with input data, e.g.
                               {'data': {'number': 42}}
        :param logger: Logger used by the Orbit framework.
        :raises: ValueError input data empty or not a dictionary.
        """
        self._logger = logger
        self.registration = Registration()
        self.__in_data = in_data
        self.__response = {}
        self.log('started ...')
        if not in_data:
            raise ValueError('No input data!')
        if not isinstance(in_data, dict):
            raise ValueError('Expect dictionary but got: ' + str(in_data))
        self.registration.check_required(in_data)
        self.log('input data: ' + OrbitIO.__ellipsis(str(in_data)))

    @staticmethod
    def __ellipsis(text):
        max_len = 30
        return text[:max_len] + '...' if len(text) >= max_len else text

    def log(self, message):
        """
        Log message using the injected logger.
        :param str message: Message to log.
        """
        if self._logger:
            worker_info = self.registration.worker_info()
            self._logger.info(worker_info + ' : ' + message)

    def read(self, data_path, index=None):
        """
        Read value from `in_data` stored under the given path.

        :param str data_path: Path to data to read, e.g. 'data/image'
        :param int index: For array of images, select index image
        :return: Returns the value for the given path.
        :rtype: any
        :raises: ValueError if path is incorrect.
        """
        # TODO: match against registration.json
        self.log('reading from ' + data_path)
        data = self.__in_data
        for elem in data_path.split(OrbitIO.PATH_SEPARATOR):
            if elem not in data:
                raise ValueError('Incorrect data path {}. {} not found!'.
                                 format(data_path, elem))
            data = data[elem]
        if index is not None:
            data = data[index]
        return data

    def write(self, data_path, data):
        """
        Write data to the given data path.

        :param str data_path:  Data path, e.g 'data/result/grade'.
        :param any data: Data to write.
        :raises: ValueError if path is empty.
        """
        # TODO: match against registration.json
        self.log('writing to ' + data_path)
        if not data_path:
            raise ValueError('Data path is empty!')
        res, prev, elem = self.__response, {}, None
        for elem in data_path.split(OrbitIO.PATH_SEPARATOR):
            res, prev = res.setdefault(elem, res.get(elem, {})), res
        prev[elem] = data

    def write_geo(self, kind, coordinates, **props):
        """
        Writes a geo feature, e.g. polygon coordinates and properties.

        Features are written in GeoJSON format. For details see
        http://geojson.org/geojson-spec.html. Here an example:

        .. code:: python

            io.write_geo('Point', [1.0, 2.0], label='My point')

        :param str kind: Type of geo feature. Must be one of
                        'Point', 'LineString', 'Polygon', 'MultiPoint',
                        'MultiLineString', 'MultiPolygon'
        :param list coordinates: Coordinates for this feature.
                         See: http://geojson.org/geojson-spec.html
        :param kwargs props: Arbitrary feature properties.
        """
        self.log('writing geo to ' + kind)

        # IMG_KEY is temporary. Just to get it working with Orbit v1
        img_anno = 'image_annotations'
        img_key = 'result'

        if kind not in OrbitIO.GEO_TYPES:
            raise ValueError('Invalid geo type :' + kind)
        if not coordinates or not isinstance(coordinates, list):
            raise ValueError('Invalid coordinates :' + str(coordinates))
        if img_anno not in self.__response:
            self.__response[img_anno] = {}
            self.__response[img_anno][img_key] = {'type': 'FeatureCollection',
                                                  'features': []}

        feature = {"type": "Feature",
                   "geometry": {"type": kind, "coordinates": coordinates},
                   "properties": props}
        self.__response[img_anno][img_key]['features'].append(feature)

    def response(self):
        """
        Return response dictionary created from :py:meth:`.write` calls.

        :return: Returns dictionary.
        :rtype: dict
        :raises: ValueError if response is empty.
        """
        if not self.__response:
            raise ValueError('No response available! Call write.')
        self.log('response: ' + OrbitIO.__ellipsis(str(self.__response)))
        self.log('completed.')
        return self.__response


class Registration(object):
    """
    Wrapper around the registration.json file that is used to register workers.
    """

    REGISTRATION_FILE = 'registration.json'

    def __init__(self):
        """
        Construct Registration object load the registration file.
        """
        with open(Registration.REGISTRATION_FILE) as f:
            self.__rego = json.loads(f.read())

    def _request_schema(self):
        """
        Return request schema from registration.
        :return:  Request schema.
        :rtype: dict
        """
        return self.__rego['tasks'][0]['inputDataComponentSchema']

    def check_required(self, in_data):
        """
        Check if input data contain required fields.

        :param dict in_data: Input data.
        :raises: ValueError if required fields are missing.
        """

        # Disabling schema check during transition to Orbit 1.0
        # Orbit now handles image and data inputs differently

        #request_schema = self._request_schema()
        #if 'required' in request_schema:
        #    for required in request_schema['required']:
        #        if 'data' not in in_data or required not in in_data['data']:
        #            raise ValueError('Required input missing: ' + required)

    def worker_info(self):
        """
        Return short info about worker.
        :return: Worker name and version number.
        :rtype: str
        """
        return '{r[name]} ({r[version]})'.format(r=self.__rego)
