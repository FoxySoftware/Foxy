import sys
import time

class CounterLog():
    
    def __init__(self, print_message:bool =True) -> None:
        self.print_message = print_message
        self.dict_message = {}
    
    def count_ms(self, func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed_time_ms = (time.time() - start_time) * 1000
            name_fn = func.__name__.replace("__", "").replace("_", " ")
            message = f"Task '{name_fn}' take {elapsed_time_ms:.2f} ms."
            self.dict_message[func.__name__] = message
            if self.print_message: 
                print(message)
            return result
        return wrapper
    
    def count_kb(self, func):
        def count_size(*args, **kwargs):
            result = func(*args, **kwargs)
            size_bytes = sys.getsizeof(result)
            size_kb = size_bytes / 1024
            name_fn = func.__name__.replace("__", "").replace("_", " ")
            message = f"Task  '{name_fn}' return {size_kb:.2f} KB of memory."
            if self.print_message:
                print(message)
            self.dict_message[func.__name__] = message
            return result
        return count_size
    
if __name__ == "__main__":
    
    ct = CounterLog(print_message=False)
    
    @ct.count_ms
    def test():
        time.sleep(1)
        return "a"
    a = test()
    print(a)
    print(ct.dict_message)
    