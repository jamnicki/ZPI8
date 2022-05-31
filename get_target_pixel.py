def get_target_pixel(x, y, pixel_size, mid_index):
    if x > 0:
        column = mid_index + (abs(x) // pixel_size)
    elif x < 0:
        column = mid_index - (abs(x) // pixel_size)
    else:
        column = mid_index

    if y > 0:
        row = mid_index - (abs(y) // pixel_size)
    elif y < 0:
        row = mid_index + (abs(y) // pixel_size)
    else:
        row = mid_index

    return int(row), int(column)


print(get_target_pixel(-0.015, 0.035, pixel_size=0.01, mid_index=50))
