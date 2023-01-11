def clamp(
    num: int | float, min_value: int | float, max_value: int | float
) -> int | float:
    return max(min(num, max_value), min_value)


# def get_color_for_val(val, vmin, vmax, pl_colors):

#     if pl_colors[0][:3] != "rgb":
#         raise ValueError("This function works only with Plotly rgb-colorscales")
#     if vmin >= vmax:
#         raise ValueError("vmin should be < vmax")

#     scale = [k / (len(pl_colors) - 1) for k in range(len(pl_colors))]

#     colors_01 = (
#         np.array([literal_eval(color[3:]) for color in pl_colors]) / 255.0
#     )  # color codes in [0,1]

#     v = (val - vmin) / (vmax - vmin)  # val is mapped to v in [0,1]
#     # find two consecutive values in plotly_scale such that   v is in  the corresponding interval
#     idx = 1

#     while v > scale[idx]:
#         idx += 1
#     vv = (v - scale[idx - 1]) / (scale[idx] - scale[idx - 1])

#     # get   [0,1]-valued color code representing the rgb color corresponding to val
#     val_color01 = colors_01[idx - 1] + vv * (colors_01[idx] - colors_01[idx - 1])
#     val_color_0255 = (255 * val_color01 + 0.5).astype(int)
#     return f"rgb{str(tuple(val_color_0255))}"
