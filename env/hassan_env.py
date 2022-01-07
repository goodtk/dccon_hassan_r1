class _hassan_env:
    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise Exception('변수에 값 할당 불가')
        self.__dict__[name] = value
    def __delattr__(self, name):
        if name in self.__dict__:
            raise Exception('변수 삭제 불가')