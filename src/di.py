import abc
import logging
import traceback

from utils_i import wrap_into_list

logger = logging.getLogger('root')


class DependencyProvider:
    def __init__(self):
        self.overrider = None
        self.traceback_where_created = traceback.format_stack()

    def override(self, overrider):
        if self.overrider is not None:
            logger.info('Redefining overrider: %s to %s', self.overrider, overrider)
        if not isinstance(overrider, DependencyProvider):
            overrider = Instance(overrider)
        self.overrider = overrider

    def __ilshift__(self, overrider):
        self.override(overrider)
        return self

    def __call__(self):
        if self.overrider is not None:
            return self.overrider()
        return self._get_instance()

    def _get_instance(self):
        raise NotImplementedError


class Instance(DependencyProvider):
    def __init__(self, instance):
        super().__init__()
        self.instance = instance

    def _get_instance(self):
        return self.instance

    def __str__(self):
        return 'di.Instance(%s)' % self.instance

    __repr__ = __str__


def lazy_dict(**kwargs):
    return Singleton(dict, **kwargs)


class Singleton(DependencyProvider):
    def __init__(self, factory, *args, **kwargs):
        super().__init__()
        if isinstance(factory, Singleton):
            factory, args, kwargs = self._override_params_when_factory_is_another_singleton(
                factory, args, kwargs
            )
        self.factory = factory
        self.args = args
        self.kwargs = kwargs
        self.instance = None

    @property
    def factory(self):
        return self._factory

    @factory.setter
    def factory(self, factory):
        if not callable(factory):
            raise ValueError(f'Factory is supposed to be callable, instead got: {factory}')
        self._factory = factory

    @staticmethod
    def _override_params_when_factory_is_another_singleton(another_singleton, args, kwargs):
        if args:
            raise ValueError(
                'Usage of args is not allowed when factory is '
                'another singleton. args=%s' % str(args)
            )
        merged_kwargs = dict(another_singleton.kwargs)
        merged_kwargs.update(kwargs)
        return another_singleton.factory, list(another_singleton.args), merged_kwargs

    def update_kwargs(self, **kwargs):
        self.kwargs.update(kwargs)

    def _get_instance(self):
        if self.instance is None:
            self.instance = self._create_instance()
        return self.instance

    def _create_instance(self):
        factory = self.factory
        args = self.args
        kwargs = self.kwargs
        try:
            args = [self._extract_plain_dependency(d) for d in self.args]
            kwargs = {
                k: self._extract_plain_dependency(d)
                for k, d in self.kwargs.items()
            }
            if isinstance(factory, Instance):
                factory = factory()
            return factory(*args, **kwargs)
        except (TypeError, AttributeError) as ex:
            raise ValueError(
                'Cannot create an instance from %s. args=%s, kwargs=%s' % (
                    factory, args, kwargs
                )) from ex

    @staticmethod
    def _extract_plain_dependency(dependency):
        if isinstance(dependency, DependencyProvider):
            return dependency()
        return dependency

    def __str__(self):
        return 'di.Singleton(%s)' % self.factory


class DiConfig(abc.ABC):
    DEFAULT_DEPENDENCY_PROVIDER = Singleton

    @classmethod
    def wrap(cls, item):
        if isinstance(item, cls):
            return item
        return cls(item)

    def __str__(self):
        return f'{type(self).__name__}.{str(self.create)}'

    __repr__ = __str__

    @classmethod
    @wrap_into_list
    def get_filtered_dependency_providers(cls, di_configs, *vargs, **kwargs):
        for di_config in di_configs:
            if di_config:
                di_config = cls.wrap(di_config)
                if di_config.should_use(*vargs, **kwargs):
                    yield di_config.create
                else:
                    logger.info(f'{di_config} was skipped')

    def __init__(self, create):
        if not isinstance(create, DependencyProvider):
            create = self.DEFAULT_DEPENDENCY_PROVIDER(create)
        self.create = create

    @abc.abstractmethod
    def should_use(self, *args, **kwargs) -> bool:
        ...
