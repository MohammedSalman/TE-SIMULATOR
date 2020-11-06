from config import ROUTING_SCHEMES
from config import YATES_SCHEME


# @staticmethod
def chunks(ll, nn):
    for index in range(0, len(ll), nn):
        yield ll[index:index + nn]


def return_algorithms_names():
    all_algo = []
    for route_selection in ROUTING_SCHEMES:
        for adaptation_rate in ROUTING_SCHEMES[route_selection]:
            # for weight_setting in ['fixed', 'inv_cap']:
            if route_selection == 'RAEKE' and adaptation_rate == 'RAEKE':
                all_algo.append(route_selection)
            else:
                all_algo.append(route_selection + '+' + adaptation_rate)

    if YATES_SCHEME:
        all_algo.append('YATES_SCHEME')
    return all_algo
