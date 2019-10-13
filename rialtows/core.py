import copy


class Registry:

    __slots__ = ['content', 'target']

    def __init__(self, target):
        self.content = {}
        self.target = target

    # добавить цену в группу
    def add(self, date, item):
        if date not in self.content:
            self.content[date] = list()
        self.content[date].append(item)

    # получить цены за опр дату
    def get(self, date):
        return self.content[date]

    # получить цены начиная с опр. даты и выполнить аггрегацию cb()
    def get_after(self, after, cb):
        data = []
        for key in self.content:
            if key >= after:
                data.extend(self.content[key])
        return cb(map(lambda o: getattr(o, self.target), data))


class Mapping:
    def __init__(self, key, converter):
        self.key = key
        self.value = ''
        self.converter = converter

    def setup(self, data):
        self.value = self.converter(data[self.key])


class Meta(type):
    def __call__(cls, *args, **kwargs):
        inst = super().__call__(*args, **kwargs)
        data = inst._data
        for name, field in cls.__dict__.items():
            if not isinstance(field, Mapping): continue
            field = copy.copy(field)
            field.setup(data)
            inst.__dict__[name] = field.value
            del field
        return inst


class BaseDto(metaclass=Meta):
    def __init__(self, data):
        self._data = data
