def change(per_second, dtime, speed=1):
    return per_second * dtime * speed


def divide(divide_by, dtime, speed=1):
    k = (dtime * 1000)/17
    return (divide_by ** (k * speed))
