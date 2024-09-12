import contextlib
import functools
import json
import time



def colored(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text} \033[38;2;255;255;255m"

def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except Exception:
        return False
    
call_stack_register = {}
counter = 0
counter_first_trigger_function = 0 
name_first_trigger_function = 0
index_first_trigger_function = 0 

def log_function_runtime(func, **kwargs):
    """
    Args:
        * level:str :
                - 'simple'
                - 'medium'
                - 'full'
                - default value : 'full'
        
    """

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        global counter
        global counter_first_trigger_function
        global name_first_trigger_function
        global index_first_trigger_function
        level = kwargs.get('level', 'full' )
        counter = counter + 1
        
        if counter == 1:
            name_first_trigger_function = func.__name__
        if name_first_trigger_function == func.__name__:
            index_first_trigger_function = counter
            counter_first_trigger_function = counter_first_trigger_function + 1 
            
        times_calls =  call_stack_register.get(func.__name__, 0)
        call_stack_register[func.__name__] = times_calls + 1
        times_calls = call_stack_register[func.__name__]
        started_at = time.monotonic()
        time_h_m_s = time.strftime("%H:%M:%S")
        print(colored( 69, 208, 102, "______________________________________________"))
        print(colored( 69, 208, 102, f"{counter} > Start function: {colored(0, 255, 255, func.__name__)}"))
        print(colored( 69, 208, 101, f"    · nº of times called: {colored(0, 255, 255, times_calls)}"))
        print(colored( 69, 208, 100, f"    · current time: {colored(0, 255, 255, time_h_m_s)}"))
        print(colored( 69, 208, 101, f"    · name first trigger function: {colored(0, 255, 255, name_first_trigger_function)}"))
        print(colored( 69, 208, 101, f"    · counter first trigger function: {colored(0, 255, 255, counter_first_trigger_function)}"))
        print(colored( 69, 208, 101, f"    · index first trigger function: {colored(0, 255, 255, index_first_trigger_function)}"))

        value = func(*args, **kwargs)
        return_type = type(value) 
        total_slept_for = time.monotonic() - started_at
        total_slept_for = f"{total_slept_for:.4f}"
        print(colored(69, 208, 101, f"    · type of return  : {colored(0, 255, 255, return_type)}")   )

        if level != 'simple:':
            if hasattr(value, '__iter__'):
                for index, content in enumerate(value):
                    content_type = type(content) 
                    print(colored(52, 142, 3, f"      · -> {index} content type : {colored(0, 203, 203, content_type)}")   )
            
            if level == 'full':
                if hasattr(value, '__dict__'):
                    print(colored(52, 142, 3, f"      · -> jsom serializable __dict__ of {return_type}: {colored(0, 169, 169, get_jsom(value=value))}")  )
                elif isinstance(value, dict):
                    print(colored(52, 142, 3, f"      · -> jsom serializable dictionary : {colored(0, 169, 169, get_jsom(value=value))}")  )
                elif hasattr(value, '__slots__'):
                    slots_value  = [{slots_name:getattr(value, slots_name)}  for slots_name in value.__slots__]
                    print(colored(52, 142, 3, f"      · -> jsom serializable __slots__ of {return_type} : {colored(0, 169, 169, slots_value)}")  )
                elif isinstance(value, list):
                    print(colored(52, 142, 3, f"      · -> content of the list: {colored(0, 169, 169, value)}")  )
            else:
                if level == 'full':
                    if hasattr(value, '__dict__'):
                        print(colored(52, 142, 3, f"      · -> attributes : {colored(0, 203, 203, get_jsom(value=value))}")   )
                
        print(colored(69, 208, 101, f"    · total time : {colored(0, 255, 255, total_slept_for)}seconds")   )
        print(colored(220, 106, 39, f"    · end function: {colored(0, 255, 255,func.__name__)}"))
        return value

    return wrapper_timer

def get_jsom(value) -> str:
    if type(value) == str:
        return value
    with contextlib.suppress(Exception):
        json_obj:str = ""
        attrs = vars(value) if not isinstance(value, dict) else value
        serializable_attrs = {key:value for (key,value) in attrs.items() if is_jsonable(value)}
        json_obj = json.dumps(serializable_attrs, indent=8)
    return json_obj

# print(colored(255, 0, 0, 'Hello, World'))
# print(get_nodes_from_route("#ventas.denis"))
traceback_template = '''Traceback (most recent call last):
File "%(filename)s", line %(lineno)s, in %(id_name)s
%(type)s: %(message)s\n'''