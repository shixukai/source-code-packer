# di_container.py
from singleton import SingletonMeta

class DIContainer(metaclass=SingletonMeta):
    def __init__(self):
        self._dependencies = {}
        self._singletons = {}
        self._resolving = set()

    def register(self, name, provider, singleton=False):
        """注册依赖"""
        self._dependencies[name] = {
            "provider": provider,
            "singleton": singleton
        }

    def resolve(self, name):
        """解析依赖"""
        if name in self._resolving:
            raise ValueError(f"Circular dependency detected for '{name}'")
        
        if name in self._singletons:
            return self._singletons[name]

        self._resolving.add(name)
        try:
            provider_info = self._dependencies.get(name)
            if provider_info is None:
                raise ValueError(f"Dependency '{name}' not found in DIContainer")
            
            provider = provider_info["provider"]
            singleton = provider_info["singleton"]

            if isinstance(provider, type):
                instance = self._resolve_class(provider)
            elif callable(provider):
                instance = provider(self)
            else:
                instance = provider

            if singleton:
                self._singletons[name] = instance

            return instance
        finally:
            self._resolving.remove(name)

    def _resolve_class(self, cls):
        """解析类依赖"""
        constructor = cls.__init__
        if constructor is object.__init__:
            return cls()
        
        param_names = constructor.__code__.co_varnames[1:constructor.__code__.co_argcount]
        dependencies = [self.resolve(name) for name in param_names]
        
        return cls(*dependencies)

    def clear(self):
        """清除所有注册和单例依赖"""
        self._dependencies.clear()
        self._singletons.clear()
        self._resolving.clear()
