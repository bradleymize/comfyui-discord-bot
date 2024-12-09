def print_class_object(class_obj, exclude_private=True):
    if exclude_private:
        attributes = [attr for attr in dir(class_obj) if not attr.startswith('_')]
    else:
        attributes = [attr for attr in dir(class_obj)]

    for attribute in attributes:
        print(f"{attribute} = {getattr(class_obj, attribute)}")