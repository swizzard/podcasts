import falcon


class InvalidCollection(falcon.HTTPNotFound):
    def __init__(self, invalid, valid, path):
        super().__init__()
        self.path = path
        self.invalid = invalid
        self.valid = valid

    def to_dict(self, obj_type=dict):
        out = obj_type()
        out['path'] = self.path
        msg = '{} is not a valid collection. Please choose from\n{}'
        out['message'] = msg.format(self.invalid, '\n'.join(self.valid))
        return out


class InvalidSubcoll(falcon.HTTPNotFound):
    def __init__(self, model, invalid, valid, path):
        super().__init__()
        self.model_name = model.__name__
        self.path = path
        self.invalid = invalid
        self.valid = valid

    def to_dict(self, obj_type=dict):

        msg = '{} is not a valid subcollection of {}. Please choose from\n'
        msg = msg.format(invalid, self.model_name) + '\n'.join(self.valid)
        out['message'] = msg
        return out


class MissingSubcollParent(falcon.HTTPNotFound):
    def __init__(self, model, obj_id, path):
        super().__init__()
        self.model_name = model.__name__
        self.path = path
        self.obj_id = obj_id

    def to_dict(self, obj_type=dict):
        out = obj_type()
        out['path'] = self.path
        msg = 'No {} with id {}'.format(self.model_name, self.obj_id)
        out['message'] = msg
        return out


